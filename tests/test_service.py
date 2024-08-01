import unittest
from copy import copy
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timedelta

from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.core.service import Service
from efootprint.builders.time_builders import create_random_hourly_usage_df, create_hourly_usage_df_from_list


class TestService(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        self.storage = MagicMock()
        self.server.name = "server"
        self.storage.name = "storage"
        self.base_ram = SourceValue(4 * u.GB, Sources.HYPOTHESIS)
        self.base_cpu = SourceValue(2 * u.core, Sources.HYPOTHESIS)
        self.service = Service("Test Service", self.server, self.storage, self.base_ram, self.base_cpu)
        self.service.dont_handle_input_updates = True

    def test_service_initialization(self):
        self.assertEqual(self.service.name, "Test Service")
        self.assertEqual(self.service.server, self.server)
        self.assertEqual(self.service.storage, self.storage)
        self.assertEqual(self.service.base_ram_consumption, self.base_ram)
        self.assertEqual(self.service.base_cpu_consumption, self.base_cpu)

    def test_service_invalid_ram_consumption(self):
        invalid_ram = SourceValue(4 * u.min)
        with self.assertRaises(ValueError):
            Service("Invalid RAM Service", self.server, self.storage, invalid_ram)

    def test_service_invalid_cpu_consumption(self):
        invalid_cpu = SourceValue(2 * u.min)
        with self.assertRaises(ValueError):
            Service("Invalid CPU Service", self.server, self.storage, self.base_ram, invalid_cpu)

    def test_modeling_timespan(self):
        up1 = MagicMock()
        up1.utc_hourly_user_journey_starts = SourceHourlyValues(
            create_random_hourly_usage_df(nb_days=3, start_date=datetime.strptime("2025-01-01", "%Y-%m-%d")))
        up2 = MagicMock()
        up2.utc_hourly_user_journey_starts = SourceHourlyValues(
            create_random_hourly_usage_df(nb_days=3, start_date=datetime.strptime("2025-01-10", "%Y-%m-%d")))

        with patch.object(Service, "usage_patterns", new_callable=PropertyMock) as usage_patterns:
            usage_patterns.return_value = [up1, up2]
            mod_timespan = self.service.modeling_timespan
            self.assertEqual(datetime.strptime("2025-01-01", "%Y-%m-%d"), mod_timespan[0].to_timestamp())
            self.assertEqual(datetime.strptime("2025-01-13", "%Y-%m-%d"), mod_timespan[1].to_timestamp())

    def test_compute_job_occurences_across_time_simple_case(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        duration_in_hours = 10
        end_date = start_date + timedelta(hours=duration_in_hours)
        up1 = MagicMock()
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()

        job.usage_patterns = [up1]
        usage_data = [0, 1, 0, 15, 10, 5, 1, 4, 0, 2, 3]
        up1.utc_hourly_user_journey_starts = SourceHourlyValues(create_hourly_usage_df_from_list(
            usage_data, start_date=start_date))
        up1.user_journey = uj1
        uj1.uj_steps = [uj_step11]
        uj_step11.jobs = [job]
        uj_step11.user_time_spent = SourceValue(90 * u.min)

        with patch.object(Service, "modeling_timespan", new_callable=PropertyMock) as modeling_timespan:
            modeling_timespan.return_value = (start_date, end_date)
            job_occurences = self.service.compute_job_occurences_across_time(job)
            self.assertEqual(start_date, job_occurences.value.index.min().to_timestamp())
            self.assertEqual(end_date, job_occurences.value.index.max().to_timestamp())
            self.assertEqual(usage_data, job_occurences.value_as_float_list)

    def test_compute_job_occurences_across_time_uj_lasting_less_than_an_hour_before(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        duration_in_hours = 10
        end_date = start_date + timedelta(hours=duration_in_hours)
        up1 = MagicMock()
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        job2 = MagicMock()

        job.usage_patterns = [up1]
        usage_data = [0, 1, 0, 15, 10, 5, 1, 4, 0, 2, 3]
        up1.utc_hourly_user_journey_starts = SourceHourlyValues(create_hourly_usage_df_from_list(
            usage_data, start_date=start_date))
        up1.user_journey = uj1
        uj1.uj_steps = [uj_step11, uj_step12]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(40 * u.min)
        uj_step12.jobs = [job]
        uj_step12.user_time_spent = SourceValue(4 * u.min)

        with patch.object(Service, "modeling_timespan", new_callable=PropertyMock) as modeling_timespan:
            modeling_timespan.return_value = (start_date, end_date)
            job_occurences = self.service.compute_job_occurences_across_time(job)
            self.assertEqual(start_date, job_occurences.value.index.min().to_timestamp())
            self.assertEqual(end_date, job_occurences.value.index.max().to_timestamp())
            self.assertEqual(usage_data, job_occurences.value_as_float_list)

    def test_compute_job_occurences_across_time_uj_lasting_more_than_an_hour_before(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        duration_in_hours = 10
        end_date = start_date + timedelta(hours=duration_in_hours)
        up1 = MagicMock()
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        job2 = MagicMock()

        job.usage_patterns = [up1]
        usage_data = [0, 1, 0, 15, 10, 5, 1, 4, 0, 2, 3]
        self.assertEqual(len(usage_data), duration_in_hours + 1)
        up1.utc_hourly_user_journey_starts = SourceHourlyValues(create_hourly_usage_df_from_list(
            usage_data, start_date=start_date))
        up1.user_journey = uj1
        uj1.uj_steps = [uj_step11, uj_step12]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(61 * u.min)
        uj_step12.jobs = [job]
        uj_step12.user_time_spent = SourceValue(4 * u.min)

        with patch.object(Service, "modeling_timespan", new_callable=PropertyMock) as modeling_timespan:
            modeling_timespan.return_value = (start_date, end_date)
            job_occurences = self.service.compute_job_occurences_across_time(job)
            self.assertEqual(start_date, job_occurences.value.index.min().to_timestamp())
            self.assertEqual(end_date + timedelta(hours=1), job_occurences.value.index.max().to_timestamp())
            self.assertEqual([0] + usage_data, job_occurences.value_as_float_list)

    def test_compute_job_occurences_across_time_uj_steps_sum_up_more_than_one_hour(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        duration_in_hours = 4
        end_date = start_date + timedelta(hours=duration_in_hours)
        up1 = MagicMock()
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        uj_step13 = MagicMock()
        job2 = MagicMock()
        up2 = MagicMock()

        job.usage_patterns = [up1, up2]
        up1_usage_data = [0, 1, 0, 15, 10]
        self.assertEqual(len(up1_usage_data), duration_in_hours + 1)
        up1.utc_hourly_user_journey_starts = SourceHourlyValues(create_hourly_usage_df_from_list(
            up1_usage_data, start_date=start_date))
        up1.user_journey = uj1
        uj1.uj_steps = [uj_step11, uj_step12, uj_step13]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(59 * u.min)
        uj_step12.jobs = [job2]
        uj_step12.user_time_spent = SourceValue(4 * u.min)
        uj_step13.jobs = [job, job]
        uj_step13.user_time_spent = SourceValue(1 * u.min)

        with patch.object(Service, "modeling_timespan", new_callable=PropertyMock) as modeling_timespan:
            modeling_timespan.return_value = (start_date, end_date)
            job_occurences = self.service.compute_job_occurences_across_time(job)
            self.assertEqual(start_date, job_occurences.value.index.min().to_timestamp())
            self.assertEqual(end_date + timedelta(hours=1), job_occurences.value.index.max().to_timestamp())
            self.assertEqual([0] + [elt * 2 for elt in up1_usage_data], job_occurences.value_as_float_list)

    def test_compute_job_occurences_across_time_uj_complex_case(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        duration_in_hours = 4
        end_date = start_date + timedelta(hours=duration_in_hours)
        up1 = MagicMock()
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        uj_step13 = MagicMock()
        job2 = MagicMock()
        up2 = MagicMock()
        uj2 = MagicMock()
        uj_step21 = MagicMock()
        uj_step22 = MagicMock()

        job.usage_patterns = [up1, up2]
        up1_usage_data = [0, 1, 0, 15, 10]
        self.assertEqual(len(up1_usage_data), duration_in_hours + 1)
        up1.utc_hourly_user_journey_starts = SourceHourlyValues(create_hourly_usage_df_from_list(
            up1_usage_data, start_date=start_date))
        up1.user_journey = uj1
        uj1.uj_steps = [uj_step11, uj_step12, uj_step13]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(59 * u.min)
        uj_step12.jobs = [job2]
        uj_step12.user_time_spent = SourceValue(4 * u.min)
        uj_step13.jobs = [job, job]
        uj_step13.user_time_spent = SourceValue(1 * u.min)
        expected_from_up1 = [0] + [elt * 2 for elt in up1_usage_data]

        up2_usage_data = [2, 3, 8, 0, 1]
        up2.utc_hourly_user_journey_starts = SourceHourlyValues(create_hourly_usage_df_from_list(
            up2_usage_data, start_date=start_date))
        up2.user_journey = uj2
        uj2.uj_steps = [uj_step21, uj_step22]
        uj_step21.jobs = [job2, job]
        uj_step21.user_time_spent = SourceValue(15 * u.min)
        uj_step22.jobs = [job]
        uj_step22.user_time_spent = SourceValue(4 * u.min)
        expected_from_up2 = [elt * 2 for elt in up2_usage_data]

        expected_total = copy(expected_from_up1)
        for i in range(0, len(expected_from_up2)):
            expected_total[i] += expected_from_up2[i]

        with patch.object(Service, "modeling_timespan", new_callable=PropertyMock) as modeling_timespan:
            modeling_timespan.return_value = (start_date, end_date)
            job_occurences = self.service.compute_job_occurences_across_time(job)
            self.assertEqual(start_date, job_occurences.value.index.min().to_timestamp())
            self.assertEqual(end_date + timedelta(hours=1), job_occurences.value.index.max().to_timestamp())
            self.assertEqual(expected_total, job_occurences.value_as_float_list)

    def test_update_storage_needed(self):
        job1 = MagicMock()
        job2 = MagicMock()
        job1.data_upload = SourceValue(10 * u.GB)
        job2.data_upload = SourceValue(100 * u.GB)

        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")

        with patch.object(
                self.service, "job_occurences_across_time_per_job",
                {job1: SourceHourlyValues(create_hourly_usage_df_from_list([10, 20, 100, 0], start_date)),
                 job2: SourceHourlyValues(create_hourly_usage_df_from_list([0, 30, 1000, 0], start_date))}
        ), \
            patch.object(Service, "jobs", new_callable=PropertyMock) as service_jobs:
            service_jobs.return_value = [job1, job2]
            self.service.update_storage_needed()
            self.assertEqual(u.TB, self.service.storage_needed.unit)
            self.assertEqual([0.1, 3.2, 101, 0], self.service.storage_needed.value_as_float_list)

    def test_update_hour_by_hour_ram_need(self):
        job1 = MagicMock()
        job2 = MagicMock()

        job1_occurences_across_time = SourceHourlyValues(
            create_hourly_usage_df_from_list([10, 20, 1, 0]))
        job2_occurences_across_time = SourceHourlyValues(
            create_hourly_usage_df_from_list([20, 15, 5, 3]))
        job1.request_duration = SourceValue(1 * u.hour)
        job2.request_duration = SourceValue(1 * u.hour)
        job1.ram_needed = SourceValue(2 * u.GB)
        job2.ram_needed = SourceValue(3 * u.GB)

        with patch.object(self.service, "job_occurences_across_time_per_job",
                          {job1: job1_occurences_across_time, job2: job2_occurences_across_time}), \
            patch.object(Service, "jobs", new_callable=PropertyMock) as service_jobs:
            service_jobs.return_value = [job1, job2]
            self.service.update_hour_by_hour_ram_need()
            self.assertEqual(u.GB, self.service.hour_by_hour_ram_need.unit)
            self.assertEqual([80, 85, 17, 9], self.service.hour_by_hour_ram_need.value_as_float_list)

    def test_update_hour_by_hour_cpu_need(self):
        job1 = MagicMock()
        job2 = MagicMock()

        job1_occurences_across_time = SourceHourlyValues(
            create_hourly_usage_df_from_list([10, 20, 1, 0]))
        job2_occurences_across_time = SourceHourlyValues(
            create_hourly_usage_df_from_list([20, 15, 5, 3]))
        job1.request_duration = SourceValue(1 * u.hour)
        job2.request_duration = SourceValue(1 * u.hour)
        job1.cpu_needed = SourceValue(2 * u.core)
        job2.cpu_needed = SourceValue(3 * u.core)

        with patch.object(self.service, "job_occurences_across_time_per_job",
                          {job1: job1_occurences_across_time, job2: job2_occurences_across_time}), \
                patch.object(Service, "jobs", new_callable=PropertyMock) as service_jobs:
            service_jobs.return_value = [job1, job2]
            self.service.update_hour_by_hour_cpu_need()
            self.assertEqual(u.core, self.service.hour_by_hour_cpu_need.unit)
            self.assertEqual([80, 85, 17, 9], self.service.hour_by_hour_cpu_need.value_as_float_list)

    def test_self_delete_should_raise_error_if_self_has_associated_jobs(self):
        job = MagicMock()
        job.name = "job"
        self.service.modeling_obj_containers = [job]
        with self.assertRaises(PermissionError):
            self.service.self_delete()

    def test_self_delete_removes_backward_links_and_recomputes_server_and_storage(self):
        with patch.object(Service, "mod_obj_attributes", new_callable=PropertyMock) as mock_mod_obj_attributes:
            mock_mod_obj_attributes.return_value = [self.server, self.storage]
            self.server.modeling_obj_containers = [self.service]
            self.storage.modeling_obj_containers = [self.service]
            self.service.self_delete()
            self.assertEqual([], self.server.modeling_obj_containers)
            self.assertEqual([], self.storage.modeling_obj_containers)
            self.server.launch_attributes_computation_chain.assert_called_once()
            self.storage.launch_attributes_computation_chain.assert_called_once()


if __name__ == '__main__':
    unittest.main()
