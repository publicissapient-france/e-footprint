import unittest
from datetime import timedelta
from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock

from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.core.usage.job import Job
from efootprint.constants.units import u


class TestJob(TestCase):
    def setUp(self):
        self.service = MagicMock()
        self.service.name = "service"

        self.job = Job(
            "test job", service=self.service, data_download=SourceValue(200 * u.MB),
            data_upload=SourceValue(100 * u.MB),
            ram_needed=SourceValue(400 * u.MB), cpu_needed=SourceValue(2 * u.core),
            request_duration=SourceValue(2 * u.min))

    def test_self_delete_should_raise_error_if_self_has_associated_uj_step(self):
        uj_step = MagicMock()
        uj_step.name = "uj_step"
        self.job.modeling_obj_containers = [uj_step]
        with self.assertRaises(PermissionError):
            self.job.self_delete()

    def test_self_delete_removes_backward_links_and_recomputes_server_and_storage(self):
        with patch.object(Job, "mod_obj_attributes", new_callable=PropertyMock) as mock_mod_obj_attributes:
            mock_mod_obj_attributes.return_value = [self.service]
            self.service.modeling_obj_containers = [self.job]
            self.job.self_delete()
            self.assertEqual([], self.service.modeling_obj_containers)
            self.service.launch_attributes_computation_chain.assert_called_once()

    def test_duration_in_full_hours(self):
        self.assertEqual(1 * u.dimensionless, self.job.duration_in_full_hours.value)

    def test_compute_hourly_job_occurrences_simple_case(self):
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj1.uj_steps = [uj_step11]
        uj_step11.jobs = [self.job]
        uj_step11.user_time_spent = SourceValue(90 * u.min)
        usage_pattern = MagicMock()
        usage_pattern.user_journey = uj1
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        usage_pattern.utc_hourly_user_journey_starts = hourly_uj_starts

        job_occurrences = self.job.compute_hourly_occurrences_for_usage_pattern(usage_pattern)
        self.assertEqual(hourly_uj_starts.value.index.min(), job_occurrences.value.index.min())
        self.assertEqual(hourly_uj_starts.value.index.max(), job_occurrences.value.index.max())
        self.assertEqual(hourly_uj_starts.value_as_float_list, job_occurrences.value_as_float_list)

    def test_compute_hourly_job_occurrences_uj_lasting_less_than_an_hour_before(self):
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        job2 = MagicMock()
        uj1.uj_steps = [uj_step11, uj_step12]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(40 * u.min)
        uj_step12.jobs = [self.job]
        uj_step12.user_time_spent = SourceValue(4 * u.min)
        usage_pattern = MagicMock()
        usage_pattern.user_journey = uj1
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        usage_pattern.utc_hourly_user_journey_starts = hourly_uj_starts

        job_occurrences = self.job.compute_hourly_occurrences_for_usage_pattern(usage_pattern)
        self.assertEqual(hourly_uj_starts.value.index.min(), job_occurrences.value.index.min())
        self.assertEqual(hourly_uj_starts.value.index.max(), job_occurrences.value.index.max())
        self.assertEqual(hourly_uj_starts.value_as_float_list, job_occurrences.value_as_float_list)

    def test_compute_hourly_job_occurrences_uj_lasting_more_than_an_hour_before(self):
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        job2 = MagicMock()
        uj1.uj_steps = [uj_step11, uj_step12]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(61 * u.min)
        uj_step12.jobs = [self.job]
        uj_step12.user_time_spent = SourceValue(4 * u.min)
        usage_pattern = MagicMock()
        usage_pattern.user_journey = uj1
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        usage_pattern.utc_hourly_user_journey_starts = hourly_uj_starts

        job_occurrences = self.job.compute_hourly_occurrences_for_usage_pattern(usage_pattern)
        self.assertEqual(hourly_uj_starts.value.index.min().to_timestamp() + timedelta(hours=1),
                         job_occurrences.value.index.min().to_timestamp())
        self.assertEqual(hourly_uj_starts.value.index.max().to_timestamp() + timedelta(hours=1),
                         job_occurrences.value.index.max().to_timestamp())
        self.assertEqual(hourly_uj_starts.value_as_float_list, job_occurrences.value_as_float_list)

    def test_compute_hourly_job_occurrences_uj_steps_sum_up_to_more_than_one_hour(self):
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        uj_step13 = MagicMock()
        job2 = MagicMock()
        uj1.uj_steps = [uj_step11, uj_step12, uj_step13]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(59 * u.min)
        uj_step12.jobs = [job2]
        uj_step12.user_time_spent = SourceValue(4 * u.min)
        uj_step13.jobs = [self.job, self.job]
        uj_step13.user_time_spent = SourceValue(1 * u.min)
        usage_pattern = MagicMock()
        usage_pattern.user_journey = uj1
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        usage_pattern.utc_hourly_user_journey_starts = hourly_uj_starts

        job_occurrences = self.job.compute_hourly_occurrences_for_usage_pattern(usage_pattern)
        self.assertEqual(
            hourly_uj_starts.value.index.min().to_timestamp() + timedelta(hours=1),
            job_occurrences.value.index.min().to_timestamp())
        self.assertEqual(
            hourly_uj_starts.value.index.max().to_timestamp() + timedelta(hours=1),
            job_occurrences.value.index.max().to_timestamp())
        self.assertEqual([elt * 2 for elt in hourly_uj_starts.value_as_float_list],
                         job_occurrences.value_as_float_list)

    def test_compute_job_hourly_data_exchange_simple_case(self):
        data_exchange = "data_upload"
        usage_pattern = MagicMock()
        hourly_occs_per_up = {usage_pattern: SourceHourlyValues(create_hourly_usage_df_from_list([1, 3, 5]))}

        with patch.object(self.job, "hourly_occurrences_per_usage_pattern", hourly_occs_per_up), \
                patch.object(self.job, "data_upload", SourceValue(1 * u.GB)), \
                patch.object(Job, "duration_in_full_hours", new_callable=PropertyMock) as mock_full_hour_duration:
            mock_full_hour_duration.return_value = SourceValue(1 * u.dimensionless)
            job_hourly_data_exchange = self.job.compute_hourly_data_exchange_for_usage_pattern(
                usage_pattern, data_exchange)

            self.assertEqual([1, 3, 5], job_hourly_data_exchange.value_as_float_list)

    def test_compute_job_hourly_data_exchange_complex_case(self):
        data_exchange = "data_upload"
        usage_pattern = MagicMock()
        hourly_occs_per_up = {usage_pattern: SourceHourlyValues(create_hourly_usage_df_from_list([1, 3, 5]))}

        with patch.object(self.job, "hourly_occurrences_per_usage_pattern", hourly_occs_per_up), \
                patch.object(self.job, "data_upload", SourceValue(1 * u.GB)), \
                patch.object(Job, "duration_in_full_hours", new_callable=PropertyMock) as mock_full_hour_duration:
            mock_full_hour_duration.return_value = SourceValue(2 * u.dimensionless)
            job_hourly_data_exchange = self.job.compute_hourly_data_exchange_for_usage_pattern(
                usage_pattern, data_exchange)

            self.assertEqual([0.5, 2, 4, 2.5], job_hourly_data_exchange.value_as_float_list)
            
    def test_compute_calculated_attribute_summed_across_usage_patterns_per_job(self):
        usage_pattern1 = MagicMock()
        usage_pattern2 = MagicMock()
        hourly_calc_attr_per_up = {
            usage_pattern1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5])),
            usage_pattern2: SourceHourlyValues(create_hourly_usage_df_from_list([3, 2, 4]))}
        self.job.hourly_calc_attr_per_up = hourly_calc_attr_per_up

        with patch.object(Job, "usage_patterns", new_callable=PropertyMock) as mock_ups:
            mock_ups.return_value = [usage_pattern1, usage_pattern2]
            result = self.job.sum_calculated_attribute_across_usage_patterns("hourly_calc_attr_per_up", "my calc attr")

            self.assertEqual([4, 4, 9], result.value_as_float_list)
            self.assertEqual("Hourly test job my calc attr across usage patterns", result.label)

        del self.job.hourly_calc_attr_per_up


if __name__ == "__main__":
    unittest.main()
