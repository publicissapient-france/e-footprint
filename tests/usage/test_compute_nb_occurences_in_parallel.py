import unittest

from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.core.usage.compute_nb_occurrences_in_parallel import compute_nb_avg_hourly_occurrences
from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.constants.units import u


class TestUsagePattern(unittest.TestCase):
    def test_compute_nb_occurrences_in_parallel_entire_hour(self):
        input_occs_starts = [20, 10, 14, 15]
        input_occs_starts_hvals = SourceHourlyValues(create_hourly_usage_df_from_list(input_occs_starts))
        event_duration = SourceValue(1 * u.hour)
        result = compute_nb_avg_hourly_occurrences(input_occs_starts_hvals, event_duration)
        self.assertEqual(input_occs_starts, result.value_as_float_list)

    def test_compute_nb_occurrences_in_parallel_2_hours(self):
        input_occs_starts = [20, 10, 14, 15]
        input_occs_starts_hvals = SourceHourlyValues(create_hourly_usage_df_from_list(input_occs_starts))
        event_duration = SourceValue(2 * u.hour)
        result = compute_nb_avg_hourly_occurrences(input_occs_starts_hvals, event_duration)
        self.assertEqual([20, 30, 24, 29, 15], result.value_as_float_list)

    def test_compute_nb_occurrences_in_parallel_partial_hour(self):
        input_occs_starts = [20, 10, 14, 15]
        input_occs_starts_hvals = SourceHourlyValues(create_hourly_usage_df_from_list(input_occs_starts))
        event_duration = SourceValue(30 * u.min)
        result = compute_nb_avg_hourly_occurrences(input_occs_starts_hvals, event_duration)
        self.assertEqual([10, 5, 7, 7.5], result.value_as_float_list)

    def test_compute_nb_occurrences_in_parallel_partial_hour_greater_than_one(self):
        input_occs_starts = [20, 10, 14, 15]
        input_occs_starts_hvals = SourceHourlyValues(create_hourly_usage_df_from_list(input_occs_starts))
        event_duration = SourceValue(150 * u.min)
        result = compute_nb_avg_hourly_occurrences(input_occs_starts_hvals, event_duration)
        self.assertEqual([20, 30, 34, 34, 22, 7.5], result.value_as_float_list)
