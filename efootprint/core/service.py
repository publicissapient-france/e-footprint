from typing import List

from efootprint.abstract_modeling_classes.explainable_objects import EmptyExplainableObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.hardware.storage import Storage
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.constants.units import u


class Service(ModelingObject):
    def __init__(self, name: str, server: Server, storage: Storage, base_ram_consumption: SourceValue,
                 base_cpu_consumption: SourceValue = None):
        super().__init__(name)
        self.storage_needed = None
        self.hour_by_hour_cpu_need = None
        self.hour_by_hour_ram_need = None
        self.hourly_job_occurrences_across_usage_patterns_per_job = ExplainableObjectDict()
        self.hourly_avg_job_occurrences_across_usage_patterns_per_job = ExplainableObjectDict()
        self.hourly_data_upload_across_usage_patterns_per_job = ExplainableObjectDict()
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
            "hourly_job_occurrences_across_usage_patterns_per_job",
            "hourly_avg_job_occurrences_across_usage_patterns_per_job",
            "hour_by_hour_ram_need", "hour_by_hour_cpu_need", "hourly_data_upload_across_usage_patterns_per_job",
            "storage_needed"]

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

    def update_expl_dict_with_calculated_attribute_summed_across_usage_patterns_per_job(
            self, hourly_calc_attr_summed_across_ups_per_job: ExplainableObjectDict,
            calculated_attribute_name: str, calculated_attribute_label: str):
        for job in self.jobs:
            job_hourly_calc_attr_summed_across_ups = EmptyExplainableObject()
            for usage_pattern in job.usage_patterns:
                job_hourly_calc_attr_summed_across_ups += getattr(usage_pattern, calculated_attribute_name)[job]

            hourly_calc_attr_summed_across_ups_per_job[job] = job_hourly_calc_attr_summed_across_ups.set_label(
                    f"Hourly {job.name} {calculated_attribute_label} across usage patterns")

    def update_hourly_job_occurrences_across_usage_patterns_per_job(self):
        self.hourly_job_occurrences_across_usage_patterns_per_job = ExplainableObjectDict()

        self.update_expl_dict_with_calculated_attribute_summed_across_usage_patterns_per_job(
            self.hourly_job_occurrences_across_usage_patterns_per_job,
            "hourly_job_occurrences_per_job", "occurrences")

    def update_hourly_avg_job_occurrences_across_usage_patterns_per_job(self):
        self.hourly_avg_job_occurrences_across_usage_patterns_per_job = ExplainableObjectDict()

        self.update_expl_dict_with_calculated_attribute_summed_across_usage_patterns_per_job(
            self.hourly_avg_job_occurrences_across_usage_patterns_per_job,
            "hourly_avg_job_occurrences_per_job", "average occurrences")

    def compute_hour_by_hour_resource_need(self, resource):
        resource_unit = u(self.resources_unit_dict[resource])
        hour_by_hour_resource_needs = EmptyExplainableObject()
        for job in self.jobs:
            try:
                hour_by_hour_resource_needs += (
                        self.hourly_avg_job_occurrences_across_usage_patterns_per_job[job]
                        * getattr(job, f"{resource}_needed"))
            except:
                a = 1

        return hour_by_hour_resource_needs.to(resource_unit).set_label(f"{self.name} hour by hour {resource} need")

    def update_hour_by_hour_ram_need(self):
        self.hour_by_hour_ram_need = self.compute_hour_by_hour_resource_need("ram")

    def update_hour_by_hour_cpu_need(self):
        self.hour_by_hour_cpu_need = self.compute_hour_by_hour_resource_need("cpu")

    def update_hourly_data_upload_across_usage_patterns_per_job(self):
        self.hourly_data_upload_across_usage_patterns_per_job = ExplainableObjectDict()

        self.update_expl_dict_with_calculated_attribute_summed_across_usage_patterns_per_job(
            self.hourly_data_upload_across_usage_patterns_per_job,
            "hourly_data_upload_per_job", "data upload")
            
    def update_storage_needed(self):
        storage_needed = EmptyExplainableObject()

        if self.jobs:
            for job in self.jobs:
                storage_needed += self.hourly_data_upload_across_usage_patterns_per_job[job]

        self.storage_needed = storage_needed.to(u.TB).set_label(f"Hour by hour storage need for {self.name}")
