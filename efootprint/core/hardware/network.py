from typing import List

from efootprint.abstract_modeling_classes.explainable_objects import EmptyExplainableObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u


class Network(ModelingObject):
    def __init__(self, name: str, bandwidth_energy_intensity: SourceValue):
        super().__init__(name)
        self.energy_footprint = None
        if not bandwidth_energy_intensity.value.check("[energy]/[]"):
            raise ValueError(
                "Value of variable 'storage_need_from_previous_year' does not have the appropriate "
                "'energy/data transfer' dimensionality")
        self.bandwidth_energy_intensity = bandwidth_energy_intensity.set_label(
            f"bandwith energy intensity of {self.name}")

    @property
    def calculated_attributes(self):
        return ["energy_footprint"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List:
        return []

    @property
    def usage_patterns(self):
        return self.modeling_obj_containers

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    def update_energy_footprint(self):
        energy_footprint = EmptyExplainableObject()

        usage_patterns_with_jobs = [up for up in self.usage_patterns if len(up.jobs) > 0]

        if usage_patterns_with_jobs:
            for usage_pattern in usage_patterns_with_jobs:
                up_hourly_data_transferred_through_network = EmptyExplainableObject()
                for job in usage_pattern.jobs:
                    up_hourly_data_transferred_through_network += usage_pattern.hourly_data_upload_per_job[job]
                    up_hourly_data_transferred_through_network += usage_pattern.hourly_data_download_per_job[job]
    
                up_network_consumption = (
                            self.bandwidth_energy_intensity
                            * up_hourly_data_transferred_through_network).to(u.kWh).set_label(
                    f"{usage_pattern.name} network energy consumption")
    
                energy_footprint += up_network_consumption * usage_pattern.country.average_carbon_intensity
            
            energy_footprint = energy_footprint.to(u.kg).set_label(f"Hourly {self.name} energy footprint")

        self.energy_footprint = energy_footprint
