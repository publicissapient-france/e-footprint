from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from footprint_model.core.hardware.storage import Storage
from footprint_model.core.hardware.server import Server
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.hardware.hardware_base_classes import ObjectLinkedToUsagePatterns

from pint import Quantity


class Service(ModelingObject, ObjectLinkedToUsagePatterns):
    def __init__(self, name: str, server: Server, storage: Storage, base_ram_consumption: Quantity,
                 base_cpu_consumption: Quantity = 1 * u.core):
        super().__init__(name)
        ObjectLinkedToUsagePatterns.__init__(self)
        self.storage_needed = None
        self.hour_by_hour_cpu_need = None
        self.hour_by_hour_ram_need = None
        self.server = server
        self.storage = storage
        if not base_ram_consumption.check("[]"):
            raise ValueError("variable 'base_ram_consumption' does not have byte dimensionality")
        if not base_cpu_consumption.check("[cpu]"):
            raise ValueError("variable 'base_cpu_consumption' does not have core dimensionality")
        self.base_ram_consumption = SourceValue(
            base_ram_consumption, Sources.USER_INPUT, f"Base RAM consumption of {self.name}")
        self.base_cpu_consumption = SourceValue(
            base_cpu_consumption, Sources.USER_INPUT, f"Base CPU consumption of {self.name}")

        self.compute_calculated_attributes()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Service):
            return self.name == other.name
        return False

    def compute_calculated_attributes(self):
        if len(self.usage_patterns) > 0:
            self.update_hour_by_hour_cpu_need()
            self.update_hour_by_hour_ram_need()
            self.update_storage_needed()

    def update_storage_needed(self):
        if len(self.usage_patterns) == 0:
            self.storage_needed = ExplainableQuantity(
                0 * u.TB, f"No storage for {self.name} because no associated usage pattern")
        else:
            usage_patterns_storage_needs = 0
            for usage_pattern in self.usage_patterns:
                uj_steps_storage_needs = 0
                for uj_step in usage_pattern.user_journey.uj_steps:
                    if uj_step.service == self:
                        uj_steps_storage_needs += uj_step.data_upload
                usage_patterns_storage_needs += uj_steps_storage_needs * usage_pattern.user_journey_freq

            self.storage_needed = usage_patterns_storage_needs.to(u.TB / u.year).define_as_intermediate_calculation(
            f"Storage needed for {self.name}")

    @staticmethod
    def compute_resource_needed_averaged_over_user_journey(
            resource_needed, request_duration, user_journey_duration, unit):
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        average_uj_resource_needed = (
                resource_needed * request_duration / (user_journey_duration * one_user_journey)
        ).to(unit)

        return average_uj_resource_needed

    def update_hour_by_hour_ram_need(self):
        if len(self.usage_patterns) == 0:
            self.hour_by_hour_ram_need = ExplainableHourlyUsage(
                [ExplainableQuantity(0 * u.GB)] * 24,
                f"no RAM need for {self.name} because no associated usage pattern")
        else:
            hour_by_hour_ram_needs = 0
            for usage_pattern in self.usage_patterns:
                usage_pattern_ram_need = 0
                for uj_step in usage_pattern.user_journey.uj_steps:
                    if uj_step.service == self:
                        average_uj_ram_needed = self.compute_resource_needed_averaged_over_user_journey(
                            uj_step.ram_needed, uj_step.request_duration, usage_pattern.user_journey.duration,
                            u.GB / u.user_journey)
                        average_uj_ram_needed = average_uj_ram_needed.define_as_intermediate_calculation(
                            f"ram needed on server {self.server.name} to process {uj_step.name}, "
                            f"averaged over user journey duration")
                        usage_pattern_ram_need += average_uj_ram_needed
                hour_by_hour_ram_needs += (
                        (usage_pattern_ram_need * usage_pattern.nb_user_journeys_in_parallel_during_usage)
                        * usage_pattern.time_intervals.utc_time_intervals)

            self.hour_by_hour_ram_need = hour_by_hour_ram_needs.define_as_intermediate_calculation(
                f"{self.name} hour by hour RAM need")

    def update_hour_by_hour_cpu_need(self):
        if len(self.usage_patterns) == 0:
            self.hour_by_hour_cpu_need = ExplainableHourlyUsage(
                [ExplainableQuantity(0 * u.GB)] * 24,
                f"no CPU need for {self.name} because no associated usage pattern")
        else:
            hour_by_hour_cpu_needs = 0
            for usage_pattern in self.usage_patterns:
                usage_pattern_cpu_need = 0
                for uj_step in usage_pattern.user_journey.uj_steps:
                    if uj_step.service == self:
                        average_uj_cpu_needed = self.compute_resource_needed_averaged_over_user_journey(
                            uj_step.cpu_needed, uj_step.request_duration, usage_pattern.user_journey.duration,
                            u.core / u.user_journey)
                        average_uj_cpu_needed = average_uj_cpu_needed.define_as_intermediate_calculation(
                            f"cpu needed on server {self.server.name} to process {uj_step.name}, "
                            f"averaged over user journey duration")
                        usage_pattern_cpu_need += average_uj_cpu_needed
                hour_by_hour_cpu_needs += (usage_pattern_cpu_need * usage_pattern.nb_user_journeys_in_parallel_during_usage
                                           * usage_pattern.time_intervals.utc_time_intervals)

            self.hour_by_hour_cpu_need = hour_by_hour_cpu_needs.define_as_intermediate_calculation(
                f"{self.name} hour by hour CPU need")
