from typing import List, Tuple
import math

from datetime import datetime

from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.hardware.storage import Storage
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.usage.compute_nb_occurences_in_parallel import compute_nb_occurences_in_parallel
from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.constants.units import u


class Service(ModelingObject):
    def __init__(self, name: str, server: Server, storage: Storage, base_ram_consumption: SourceValue,
                 base_cpu_consumption: SourceValue = None):
        super().__init__(name)
        self.storage_needed = None
        self.hour_by_hour_cpu_need = None
        self.hour_by_hour_ram_need = None
        self.job_occurences_across_time_per_job = ExplainableObjectDict()
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
        return [
            "job_occurences_across_time_per_job", "hour_by_hour_ram_need", "hour_by_hour_cpu_need", "storage_needed"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return [self.server, self.storage]

    @property
    def jobs(self):
        return self.modeling_obj_containers

    @property
    def usage_patterns(self):
        return list(set(sum([job.usage_patterns for job in self.jobs], start=[])))

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    @property
    def modeling_timespan(self) -> Tuple[datetime]:
        start_date = min([up.utc_hourly_user_journey_starts.value.index.min() for up in self.usage_patterns])
        end_date = max([up.utc_hourly_user_journey_starts.value.index.max() for up in self.usage_patterns])

        return (start_date, end_date)

    def compute_job_occurences_across_time(self, job):
        start_date, end_date = self.modeling_timespan
        nb_hours_in_modeling_timespan = math.floor((end_date - start_date).total_seconds() / 3600)
        job_occurences = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list([0] * (nb_hours_in_modeling_timespan + 1), start_date=start_date), f"Initialization of {job.name} occurences")
        for job_up in job.usage_patterns:
            delay_between_uj_start_and_job_evt = 0
            delay_in_hours_between_uj_start_and_job_evt = 0
            for uj_step in job_up.user_journey.uj_steps:
                for uj_step_job in uj_step.jobs:
                    if uj_step_job == job:
                        job_occurences += job_up.utc_hourly_user_journey_starts.return_shifted_hourly_quantities(
                            delay_in_hours_between_uj_start_and_job_evt)

                delay_between_uj_start_and_job_evt += uj_step.user_time_spent
                delay_in_hours_between_uj_start_and_job_evt = math.floor(
                    delay_between_uj_start_and_job_evt.to(u.hour).magnitude)

        return job_occurences.set_label(f"{job.name} occurences across time")

    def update_job_occurences_across_time_per_job(self):
        for job in self.jobs:
            self.job_occurences_across_time_per_job[job] = self.compute_job_occurences_across_time(job)

    def update_storage_needed(self):
        storage_needed = 0
        for job in self.jobs:
            storage_needed += self.job_occurences_across_time_per_job[job] * job.data_upload

        self.storage_needed = storage_needed.to(u.TB).set_label(f"Hour by hour storage need for {self.name}")

    def compute_hour_by_hour_resource_need(self, resource):
        resource_unit = u(self.resources_unit_dict[resource])
        hour_by_hour_resource_needs = 0
        for job in self.jobs:
            nb_of_job_occurences_in_parallel = compute_nb_occurences_in_parallel(
                self.job_occurences_across_time_per_job[job], job.request_duration).set_label(f"Hour by hour {job.name} occurences")
            hour_by_hour_resource_needs += (
                    nb_of_job_occurences_in_parallel * getattr(job, f"{resource}_needed")).to(resource_unit).set_label(
                    f"Hour by hour average {resource} needed to process {job.name}")

        return hour_by_hour_resource_needs.set_label(f"{self.name} hour by hour {resource} need")

    def update_hour_by_hour_ram_need(self):
        self.hour_by_hour_ram_need = self.compute_hour_by_hour_resource_need("ram")

    def update_hour_by_hour_cpu_need(self):
        self.hour_by_hour_cpu_need = self.compute_hour_by_hour_resource_need("cpu")
