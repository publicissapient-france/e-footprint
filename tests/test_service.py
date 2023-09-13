import unittest
from unittest.mock import MagicMock, patch

from footprint_model.constants.explainable_quantities import ExplainableQuantity, ExplainableHourlyUsage
from footprint_model.constants.units import u
from footprint_model.core.service import Service


class TestService(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        self.storage = MagicMock()
        self.base_ram = 4 * u.Go
        self.base_cpu = 2 * u.core
        self.service = Service("Test Service", self.server, self.storage, self.base_ram, self.base_cpu)

    def test_service_initialization(self):
        self.assertEqual(self.service.name, "Test Service")
        self.assertEqual(self.service.server, self.server)
        self.assertEqual(self.service.storage, self.storage)
        self.assertEqual(self.service.base_ram_consumption.value, self.base_ram)
        self.assertEqual(self.service.base_cpu_consumption.value, self.base_cpu)
        self.assertEqual(self.service.hour_by_hour_ram_need, None)
        self.assertEqual(self.service.hour_by_hour_cpu_need, None)
        self.assertEqual(self.service.storage_needed, None)

    def test_service_invalid_ram_consumption(self):
        invalid_ram = 4 * u.min
        with self.assertRaises(ValueError):
            Service("Invalid RAM Service", self.server, self.storage, invalid_ram)

    def test_service_invalid_cpu_consumption(self):
        invalid_cpu = 2 * u.min
        with self.assertRaises(ValueError):
            Service("Invalid CPU Service", self.server, self.storage, self.base_ram, invalid_cpu)

    def test_service_equality(self):
        service1 = Service("Service A", self.server, self.storage, self.base_ram, self.base_cpu)
        service2 = Service("Service A", self.server, self.storage, self.base_ram, self.base_cpu * 2)
        service3 = Service("Service B", self.server, self.storage, self.base_ram, self.base_cpu)
        self.assertEqual(service1, service2)
        self.assertNotEqual(service1, service3)

    def test_update_storage_needed(self):
        usage_pattern1 = MagicMock()
        usage_pattern1.user_journey_freq = ExplainableQuantity(10 * u.user_journey / u.day)
        usage_pattern2 = MagicMock()
        usage_pattern2.user_journey_freq = ExplainableQuantity(100 * u.user_journey / u.day)
        
        uj_step1 = MagicMock()
        uj_step1.service = self.service
        uj_step1.data_upload = ExplainableQuantity(1 * u.Mo / u.user_journey)
        uj_step2 = MagicMock()
        uj_step2.service = self.service
        uj_step2.data_upload = ExplainableQuantity(3 * u.Mo / u.user_journey)
        uj_step3 = MagicMock()
        uj_step3.service = "other service"
        uj_step3.data_upload = ExplainableQuantity(5 * u.Mo / u.user_journey)
        
        usage_pattern1.user_journey.uj_steps = [uj_step1, uj_step3]
        usage_pattern2.user_journey.uj_steps = [uj_step2, uj_step3]
        
        with patch.object(self.service, "usage_patterns", {usage_pattern1, usage_pattern2}):
            self.service.update_storage_needed()
            self.assertEqual(
                round((310 * u.Mo / u.day).to(u.To / u.year), 3), round(self.service.storage_needed.value, 3))

    def test_update_hour_by_hour_ram_need(self):
        uj_step = MagicMock()
        uj_step.service = self.service
        uj_step.ram_needed = ExplainableQuantity(1.8 * u.Go)
        uj_step.request_duration = ExplainableQuantity(10 * u.min)

        uj_step2 = MagicMock()
        uj_step2.service = self.service
        uj_step2.ram_needed = ExplainableQuantity(0.6 * u.Go)
        uj_step2.request_duration = ExplainableQuantity(10 * u.min)

        uj_step3 = MagicMock()
        uj_step3.service = "other service"
        uj_step3.ram_needed = ExplainableQuantity(29 * u.Go)
        uj_step3.request_duration = ExplainableQuantity(10 * u.min)

        usage_pattern = MagicMock()
        usage_pattern.user_journey.uj_steps = [uj_step, uj_step2, uj_step3]
        usage_pattern.user_journey.duration = ExplainableQuantity(1 * u.hour)
        usage_pattern.nb_user_journeys_in_parallel_during_usage = ExplainableQuantity(10 * u.user_journey)
        usage_pattern.time_intervals.utc_time_intervals = ExplainableHourlyUsage(
            [ExplainableQuantity(1 * u.dimensionless)] * 24)
        with patch.object(self.service, "usage_patterns", {usage_pattern}):
            self.service.update_hour_by_hour_ram_need()

            self.assertEqual(
                [4 * u.Go] * 24,
                [round(elt.value, 2) for elt in self.service.hour_by_hour_ram_need.value])

    def test_update_hour_by_hour_cpu_need(self):
        uj_step = MagicMock()
        uj_step.service = self.service
        uj_step.cpu_needed = ExplainableQuantity(1.8 * u.core)
        uj_step.request_duration = ExplainableQuantity(10 * u.min)

        uj_step2 = MagicMock()
        uj_step2.service = self.service
        uj_step2.cpu_needed = ExplainableQuantity(0.6 * u.core)
        uj_step2.request_duration = ExplainableQuantity(10 * u.min)

        uj_step3 = MagicMock()
        uj_step3.service = "other service"
        uj_step3.cpu_needed = ExplainableQuantity(29 * u.core)
        uj_step3.request_duration = ExplainableQuantity(10 * u.min)

        usage_pattern = MagicMock()
        usage_pattern.user_journey.uj_steps = [uj_step, uj_step2, uj_step3]
        usage_pattern.user_journey.duration = ExplainableQuantity(1 * u.hour)
        usage_pattern.nb_user_journeys_in_parallel_during_usage = ExplainableQuantity(10 * u.user_journey)
        usage_pattern.time_intervals.utc_time_intervals = ExplainableHourlyUsage(
            [ExplainableQuantity(1 * u.dimensionless)] * 24)
        with patch.object(self.service, "usage_patterns", {usage_pattern}):
            self.service.update_hour_by_hour_cpu_need()

            self.assertEqual(
                [4 * u.core] * 24,
                [round(elt.value, 2) for elt in self.service.hour_by_hour_cpu_need.value])


if __name__ == '__main__':
    unittest.main()
