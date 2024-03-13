from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u

from typing import List


class Network(ModelingObject):
    def __init__(self, name: str, bandwidth_energy_intensity: SourceValue):
        super().__init__(name)
        self.data_upload = None
        self.data_download = None
        self.energy_footprint = None
        self.bandwidth_energy_intensity = bandwidth_energy_intensity.set_label(f"bandwith energy intensity of {self.name}")

    @property
    def calculated_attributes(self):
        return ["data_download", "data_upload", "energy_footprint"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List:
        return []

    @property
    def usage_patterns(self):
        return self.modeling_obj_containers

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    def update_data_upload(self):
        if len(self.usage_patterns) > 0:
            data_upload = 0
            for usage_pattern in self.usage_patterns:
                data_upload += usage_pattern.user_journey.data_upload * usage_pattern.user_journey_freq

            self.data_upload = data_upload.to(u.TB / u.year).set_label(
                f"Data upload in {self.name}")
        else:
            self.data_download = ExplainableQuantity(
                0 * u.MB / u.year, f"No data upload for {self.name} because no associated usage pattern")

    def update_data_download(self):
        if len(self.usage_patterns) > 0:
            data_download = 0
            for usage_pattern in self.usage_patterns:
                data_download += usage_pattern.user_journey.data_download * usage_pattern.user_journey_freq

            self.data_download = data_download.to(u.TB / u.year).set_label(
                f"Data download in {self.name}")
        else:
            self.data_download = ExplainableQuantity(
                0 * u.MB / u.year, f"No data download for {self.name} because no associated usage pattern")

    def update_energy_footprint(self):
        if len(self.usage_patterns) > 0:
            power_footprint = 0
            for usage_pattern in self.usage_patterns:
                user_journey = usage_pattern.user_journey
                uj_network_consumption = (
                            self.bandwidth_energy_intensity
                            * (user_journey.data_download + user_journey.data_upload)
                ).to(u.Wh / u.user_journey)
                uj_network_consumption.set_label(
                    f"{self.name} consumption during {user_journey.name}")
                power_footprint += (
                        usage_pattern.user_journey_freq * uj_network_consumption
                        * usage_pattern.device_population.country.average_carbon_intensity)

            self.energy_footprint = power_footprint.to(u.kg / u.year).set_label(
                f"Energy footprint of {self.name}")

        else:
            self.energy_footprint = ExplainableQuantity(
                0 * u.kg / u.year, f"No energy footprint for {self.name} because no associated usage pattern")
