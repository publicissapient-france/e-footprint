from footprint_model.constants.explainable_quantities import ModelingObject, \
    ExplainableObject, ExplainableHourlyUsage, ExplainableQuantity
from footprint_model.constants.units import u

from typing import List
import pytz


class TimeIntervals(ModelingObject):
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

    def __init__(self, name: str, time_intervals: List[List[int]], timezone: str):
        super().__init__(name)
        self.utc_time_intervals = None
        sorted_time_intervals = sorted(time_intervals, key=lambda x: x[0])
        self.check_time_intervals_validity(sorted_time_intervals)
        self.time_intervals = ExplainableObject(sorted_time_intervals)
        self.timezone = ExplainableObject(pytz.timezone(timezone) if timezone is not None else None)
        self.hourly_usage = None

        self.compute_calculated_attributes()

    @property
    def pubsub_topics_to_listen_to(self) -> List[str]:
        return [self.utc_time_intervals]

    def compute_calculated_attributes(self):
        self.update_hourly_usage()
        self.update_utc_time_intervals()

    def update_hourly_usage(self):
        hourly_usage = [
            ExplainableQuantity(0 * u.dimensionless, f"Non usage hour between {i} and {i+1}") for i in range(24)]
        for time_interval in self.time_intervals.value:
            start, end = time_interval
            for i in range(start, end):
                hourly_usage[i] = ExplainableQuantity(1 * u.dimensionless, f"Usage between {i} and {i+1}")

        self.hourly_usage = ExplainableHourlyUsage(
            hourly_usage, f"{self.name} local time zone hourly usage", left_child=self.time_intervals,
            child_operator="conversion to hourly usage")

    def update_utc_time_intervals(self):
        utc_time_intervals = self.hourly_usage.convert_to_utc(local_timezone=self.timezone)
        self.utc_time_intervals = utc_time_intervals.define_as_intermediate_calculation(
            f"UTC time intervals of {self.name}")

        # TODO: to refactor and test
