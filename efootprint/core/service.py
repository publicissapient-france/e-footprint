from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from efootprint.core.hardware.storage import Storage
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.logger import logger

from typing import List


class Service(ModelingObject):
    def __init__(self, name: str, server: Server, storage: Storage, base_ram_consumption: SourceValue,
                 base_cpu_consumption: SourceValue = None):
        super().__init__(name)
        self.storage_needed = ExplainableQuantity(
            0 * u.TB / u.year, f"No storage need for {self.name} because no associated uj step with usage pattern.")
        self.hour_by_hour_cpu_need = ExplainableHourlyUsage(
                [0 * u.core] * 24,
                f"No CPU need for {self.name} because no associated uj step with usage pattern")
        self.hour_by_hour_ram_need = ExplainableHourlyUsage(
                [0 * u.GB] * 24,
                f"No RAM need for {self.name} because no associated uj step with usage pattern")
        self.server = server
        self.storage = storage
        if not base_ram_consumption.value.check("[]"):
            raise ValueError("variable 'base_ram_consumption' does not have byte dimensionality")
        if base_cpu_consumption is None:
            base_cpu_consumption = SourceValue(1 * u.core)
        if not base_cpu_consumption.value.check("[cpu]"):
            raise ValueError("variable 'base_cpu_consumption' does not have core dimensionality")
        self.base_ram_consumption = base_ram_consumption.set_label(f"Base RAM consumption of {self.name}")
        self.base_cpu_consumption = base_cpu_consumption.set_label(f"Base CPU consumption of {self.name}")

    @property
    def resources_unit_dict(self):
        return {"ram": "GB", "cpu": "core"}

    @property
    def calculated_attributes(self):
        return ["hour_by_hour_ram_need", "hour_by_hour_cpu_need", "storage_needed"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return [self.server, self.storage]

    @property
    def uj_steps(self):
        return self.modeling_obj_containers

    @property
    def usage_patterns(self):
        return list(set(sum([uj_step.usage_patterns for uj_step in self.uj_steps], start=[])))

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    def update_storage_needed(self):
        if len(self.usage_patterns) == 0:
            self.storage_needed = ExplainableQuantity(
                0 * u.TB / u.year,
                f"No storage for {self.name} because no associated user journey steps with usage pattern")
        else:
            storage_needs = 0
            for uj_step in self.uj_steps:
                uj_step_up = uj_step.usage_patterns
                if len(uj_step_up) > 0:
                    storage_needs += uj_step.data_upload * sum(up.user_journey_freq for up in uj_step_up)

            self.storage_needed = storage_needs.to(u.TB / u.year).set_label(
                f"Storage needed for {self.name}")

    def compute_hour_by_hour_resource_need(self, resource):
        resource_unit = u(self.resources_unit_dict[resource])
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        if len(self.usage_patterns) == 0:
            base_resource_consumption = getattr(self, f"base_{resource}_consumption")
            if base_resource_consumption.magnitude > 0:
                logger.warning(
                    f"{self.name} is installed on {self.server.name} but unused, so it consumes "
                    f"{base_resource_consumption.value} of {resource} for nothing.")
            return ExplainableHourlyUsage(
                [0 * resource_unit] * 24,
                f"No {resource} need for {self.name} because no associated user journey steps with usage pattern")
        else:
            hour_by_hour_resource_needs = 0
            for uj_step in self.uj_steps:
                for usage_pattern in uj_step.usage_patterns:
                    average_uj_resource_needed_for_up = (
                        getattr(uj_step, f"{resource}_needed") * uj_step.request_duration /
                        (usage_pattern.user_journey.duration * one_user_journey)).to(
                        resource_unit / u.user_journey).set_label(
                        f"Average {resource} needed over {usage_pattern.name} to process {uj_step.name}")

                    hour_by_hour_resource_needs += (
                            (average_uj_resource_needed_for_up * usage_pattern.nb_user_journeys_in_parallel_during_usage)
                            * usage_pattern.utc_time_intervals)

            return hour_by_hour_resource_needs.set_label(
                f"{self.name} hour by hour {resource} need")

    def update_hour_by_hour_ram_need(self):
            self.hour_by_hour_ram_need = self.compute_hour_by_hour_resource_need("ram")

    def update_hour_by_hour_cpu_need(self):
            self.hour_by_hour_cpu_need = self.compute_hour_by_hour_resource_need("cpu")
