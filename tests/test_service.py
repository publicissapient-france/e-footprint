import unittest
from unittest.mock import MagicMock, patch, PropertyMock

from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.core.service import Service
from efootprint.builders.time_builders import create_hourly_usage_df_from_list


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

    def test_update_hour_by_hour_ram_need(self):
        job1 = MagicMock()
        job2 = MagicMock()

        job1.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([10, 20, 1, 0]))
        job2.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([20, 15, 5, 3]))
        job1.ram_needed = SourceValue(2 * u.GB)
        job2.ram_needed = SourceValue(3 * u.GB)

        with patch.object(Service, "jobs", new_callable=PropertyMock) as service_jobs:
            service_jobs.return_value = [job1, job2]
            self.service.update_hour_by_hour_ram_need()
            self.assertEqual(u.GB, self.service.hour_by_hour_ram_need.unit)
            self.assertEqual([80, 85, 17, 9], self.service.hour_by_hour_ram_need.value_as_float_list)

    def test_update_hour_by_hour_cpu_need(self):
        job1 = MagicMock()
        job2 = MagicMock()

        job1.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([10, 20, 1, 0]))
        job2.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([20, 15, 5, 3]))
        job1.cpu_needed = SourceValue(2 * u.core)
        job2.cpu_needed = SourceValue(3 * u.core)

        with patch.object(Service, "jobs", new_callable=PropertyMock) as service_jobs:
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
        with patch.object(Service, "mod_obj_attributes", new_callable=PropertyMock) as mock_mod_obj_attributes, \
                patch.object(self.server, "modeling_obj_containers", [self.service]), \
                patch.object(self.storage, "modeling_obj_containers", [self.service]), \
                patch.object(self.server, "attributes_computation_chain", [self.server]), \
                patch.object(self.storage, "attributes_computation_chain", [self.storage]):
            mock_mod_obj_attributes.return_value = [self.server, self.storage]
            self.service.self_delete()
            self.assertEqual([], self.server.modeling_obj_containers)
            self.assertEqual([], self.storage.modeling_obj_containers)
            self.server.compute_calculated_attributes.assert_called_once()
            self.storage.compute_calculated_attributes.assert_called_once()


if __name__ == '__main__':
    unittest.main()
