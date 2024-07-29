from typing import List

from efootprint.constants.countries import Country
from efootprint.constants.units import u
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.service import Service
from efootprint.core.hardware.network import Network
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage, ExplainableQuantity


class UsagePattern(ModelingObject):
    @staticmethod
    def check_time_intervals_validity(sorted_time_intervals):
        for i in range(len(sorted_time_intervals)):
            start_time, end_time = sorted_time_intervals[i]
            if start_time >= end_time:
                raise ValueError(
                    f"Invalid time interval {sorted_time_intervals[i]}, start time must be earlier than end time")
            if i < len(sorted_time_intervals) - 1:
                next_start_time = sorted_time_intervals[i + 1][0]
                if next_start_time < end_time:
                    raise ValueError(
                        f"Time interval {sorted_time_intervals[i + 1]} starts before time interval"
                        f" {sorted_time_intervals[i]} ends")

    def __init__(self, name: str, user_journey: UserJourney, devices: List[Hardware], network: Network,
                 country: Country, user_journey_freq: SourceValue, time_intervals: SourceObject):
        super().__init__(name)
        self.hourly_usage = None
        self.usage_time_fraction = None
        self.utc_time_intervals = None
        self.nb_user_journeys_in_parallel_during_usage = None
        self.devices_power = None
        self.devices_energy_footprint = None
        self.devices_fabrication_footprint = None
        self.energy_footprint = None
        self.instances_fabrication_footprint = None
        self.user_journey = user_journey
        self.devices = devices
        self.network = network
        self.country = country
        if not user_journey_freq.value.check("[user_journey] / ([time])"):
            raise ValueError(f"User journey frequency defined in {self.name} should have "
                             f"[user_journey] / [time] dimensionality")
        self.user_journey_freq = user_journey_freq.set_label(f"Usage frequency in {self.name}")
        self.check_time_intervals_validity(time_intervals.value)
        self.time_intervals = time_intervals.set_label(f"{self.name} time intervals in local timezone")

    @property
    def calculated_attributes(self):
        return ["hourly_usage", "usage_time_fraction", "utc_time_intervals",
                "nb_user_journeys_in_parallel_during_usage", "devices_power", "devices_energy_footprint",
                "devices_fabrication_footprint", "energy_footprint", "instances_fabrication_footprint"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return self.services + [self.network]

    @property
    def services(self) -> List[Service]:
        return self.user_journey.services

    @property
    def systems(self) -> List:
        return self.modeling_obj_containers

    def update_hourly_usage(self):
        hourly_usage = [0 * u.dimensionless] * 24
        for time_interval in self.time_intervals.value:
            start, end = time_interval
            for i in range(start, end):
                hourly_usage[i] = 1 * u.dimensionless

        self.hourly_usage = ExplainableHourlyUsage(
            hourly_usage, f"{self.name} local timezone hourly usage", left_child=self.time_intervals,
            child_operator="Hourly usage conversion")
        
    def update_utc_time_intervals(self):
        utc_time_intervals = self.hourly_usage.convert_to_utc(local_timezone=self.country.timezone)
        self.utc_time_intervals = utc_time_intervals.set_label(f"{self.name} UTC")

    def update_usage_time_fraction(self):
        usage_time_fraction = self.hourly_usage.compute_usage_time_fraction()
        self.usage_time_fraction = usage_time_fraction.set_label(
            f"Usage time fraction of {self.name}")

    def update_nb_user_journeys_in_parallel_during_usage(self):
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        nb_user_journeys_in_parallel_during_usage = (
            (one_user_journey *
             (self.user_journey_freq * self.user_journey.duration / self.usage_time_fraction)
             ).to(u.user_journey))

        self.nb_user_journeys_in_parallel_during_usage = nb_user_journeys_in_parallel_during_usage.set_label(
            f"Number of user journeys in parallel during {self.name}")

    def update_devices_power(self):
        devices_power = 0
        for device in self.devices:
            devices_power += (self.user_journey_freq * (device.power * self.user_journey.duration)).to(u.kWh / u.year)

        self.devices_power = devices_power.set_label(f"Power of {self.name} devices")

    def update_devices_energy_footprint(self):
        energy_footprint = (self.devices_power * self.country.average_carbon_intensity).to(u.kg / u.year)
        
        self.devices_energy_footprint = energy_footprint.set_label(f"Energy footprint of {self.name}")

    def update_devices_fabrication_footprint(self):
        devices_fabrication_footprint = 0
        for device in self.devices:
            device_uj_fabrication_footprint = (
                    device.carbon_footprint_fabrication * self.user_journey.duration
                    / (device.lifespan * device.fraction_of_usage_time)
            ).to(u.g / u.user_journey).set_label(
                f"{device.name} fabrication footprint over {self.user_journey.name}")
            devices_fabrication_footprint += (self.user_journey_freq * device_uj_fabrication_footprint
                                              ).to(u.kg / u.year)

        self.devices_fabrication_footprint = devices_fabrication_footprint.set_label(
            f"Devices fabrication footprint of {self.name}")

    def update_energy_footprint(self):
        self.energy_footprint = (self.devices_energy_footprint + 0).set_label(f"{self.name} total energy footprint")

    def update_instances_fabrication_footprint(self):
        self.instances_fabrication_footprint = (self.devices_fabrication_footprint + 0).set_label(
            f"{self.name} total fabrication footprint")
