from efootprint.constants.units import u
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.service import Service
from efootprint.core.hardware.network import Network
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage

from typing import List


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

    def __init__(self, name: str, user_journey: UserJourney, device_population: DevicePopulation,
                 network: Network, user_journey_freq_per_user: SourceValue, time_intervals: SourceObject):
        super().__init__(name)
        self.hourly_usage = None
        self.usage_time_fraction = None
        self.user_journey = user_journey
        self.device_population = device_population
        self.network = network
        if not user_journey_freq_per_user.value.check("[user_journey] / ([person] * [time])"):
            raise ValueError(f"User journey frequency defined in {self.name} should have "
                             f"[user_journey] / ([user] * [time]) dimensionality")
        self.user_journey_freq_per_user = user_journey_freq_per_user.set_label(f"Usage frequency in {self.name}")
        self.check_time_intervals_validity(time_intervals.value)
        self.time_intervals = time_intervals.set_label(f"{self.name} time intervals in local timezone")

    @property
    def calculated_attributes(self):
        return ["hourly_usage", "usage_time_fraction"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return [self.device_population]

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

    def update_usage_time_fraction(self):
        usage_time_fraction = self.hourly_usage.compute_usage_time_fraction()
        self.usage_time_fraction = usage_time_fraction.set_label(
            f"Usage time fraction of {self.name}")

    @property
    def user_journey_freq(self):
        return self.device_population.user_journey_freq_per_up[self]

    @property
    def nb_user_journeys_in_parallel_during_usage(self):
        return self.device_population.nb_user_journeys_in_parallel_during_usage_per_up[self]

    @property
    def utc_time_intervals(self):
        return self.device_population.utc_time_intervals_per_up[self]
