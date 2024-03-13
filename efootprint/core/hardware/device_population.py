from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.constants.countries import Country
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u

from typing import List
import math


class DevicePopulation(ModelingObject):
    def __init__(self, name: str, nb_devices: SourceValue, country: Country, devices: List[Hardware]):
        super().__init__(name)
        self.instances_fabrication_footprint = None
        self.energy_footprint = None
        self.power = None
        self.user_journey_freq_per_up = ExplainableObjectDict()
        self.nb_user_journeys_in_parallel_during_usage_per_up = ExplainableObjectDict()
        self.utc_time_intervals_per_up = ExplainableObjectDict()
        self.nb_devices = nb_devices.set_label(f"Nb devices in {self.name}")
        self.country = country
        self.devices = devices

    @property
    def calculated_attributes(self):
        return [
            "user_journey_freq_per_up", "nb_user_journeys_in_parallel_during_usage_per_up",
            "utc_time_intervals_per_up", "power", "energy_footprint", "instances_fabrication_footprint"]

    @property
    def usage_patterns(self):
        return self.modeling_obj_containers

    @property
    def services(self):
        return list(set(sum([up.services for up in self.usage_patterns], [])))

    @property
    def networks(self):
        return list(set([up.network for up in self.usage_patterns]))

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List:
        return self.services + self.networks

    def update_utc_time_intervals_per_up(self):
        for usage_pattern in self.usage_patterns:
            utc_time_intervals = usage_pattern.hourly_usage.convert_to_utc(local_timezone=self.country.timezone)
            self.utc_time_intervals_per_up[usage_pattern] = utc_time_intervals.set_label(
                f"{usage_pattern.name} UTC")

    def update_user_journey_freq_per_up(self):
        for usage_pattern in self.usage_patterns:
            self.user_journey_freq_per_up[usage_pattern] = (
                    self.nb_devices * usage_pattern.user_journey_freq_per_user).set_label(
                    f"User journey frequency of {usage_pattern.name}")

    def update_nb_user_journeys_in_parallel_during_usage_per_up(self):
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        for usage_pattern in self.usage_patterns:
            nb_uj_in_parallel__raw = (
                (one_user_journey *
                 (usage_pattern.user_journey_freq * usage_pattern.user_journey.duration
                  / usage_pattern.usage_time_fraction)
                 ).to(u.user_journey))
            if nb_uj_in_parallel__raw.magnitude != int(nb_uj_in_parallel__raw.magnitude):
                nb_user_journeys_in_parallel_during_usage = (
                        nb_uj_in_parallel__raw +
                        ExplainableQuantity(
                            (math.ceil(nb_uj_in_parallel__raw.magnitude) - nb_uj_in_parallel__raw.magnitude)
                            * u.user_journey, "Rounding up of user journeys in parallel to next integer"))
            else:
                nb_user_journeys_in_parallel_during_usage = nb_uj_in_parallel__raw

            self.nb_user_journeys_in_parallel_during_usage_per_up[usage_pattern] = \
                nb_user_journeys_in_parallel_during_usage.set_label(
                    f"Number of user journeys in parallel during {usage_pattern.name}")

    def update_power(self):
        if len(self.usage_patterns) > 0:
            power = 0
            for device in self.devices:
                for usage_pattern in self.usage_patterns:
                    power += (
                            self.user_journey_freq_per_up[usage_pattern]
                            * (device.power * usage_pattern.user_journey.duration)
                    ).to(u.kWh / u.year)

            self.power = power.set_label(f"Power of {self.name} devices")
        else:
            self.power = ExplainableQuantity(0 * u.W, f"No power for {self.name} because no associated usage pattern")

    def update_energy_footprint(self):
        energy_footprint = (self.power * self.country.average_carbon_intensity).to(u.kg / u.year)
        self.energy_footprint = energy_footprint.set_label(f"Energy footprint of {self.name}")

    def update_instances_fabrication_footprint(self):
        if len(self.usage_patterns) > 0:
            devices_fabrication_footprint = 0
            for device in self.devices:
                for usage_pattern in self.usage_patterns:
                    device_uj_fabrication_footprint = (
                            device.carbon_footprint_fabrication * usage_pattern.user_journey.duration
                            / (device.lifespan * device.fraction_of_usage_time)
                    ).to(u.g / u.user_journey).set_label(
                        f"{device.name} fabrication footprint over {usage_pattern.user_journey.name}")
                    devices_fabrication_footprint += (
                            self.user_journey_freq_per_up[usage_pattern] * device_uj_fabrication_footprint
                    ).to(u.kg / u.year)

            self.instances_fabrication_footprint = devices_fabrication_footprint.set_label(
                f"Devices fabrication footprint of {self.name}")
        else:
            self.instances_fabrication_footprint = ExplainableQuantity(
                0 * u.kg / u.year, f"No fabrication footprint for {self.name} because no associated usage pattern")
