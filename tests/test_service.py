import unittest
from unittest.mock import MagicMock
from copy import deepcopy

from footprint_model.constants.explainable_quantities import ExplainableQuantity, ExplainableHourlyUsage
from footprint_model.constants.units import u
from footprint_model.core.service import Service


def create_test_service(service):
    test_service = deepcopy(service)

    uj_step = MagicMock()
    uj_step.service = test_service
    uj_step.data_upload = ExplainableQuantity(100 * u.Mo / u.user_journey)
    uj_step.ram_needed = ExplainableQuantity(2 * u.Go)
    uj_step.cpu_needed = ExplainableQuantity(2 * u.core)
    uj_step.request_duration = ExplainableQuantity(10 * u.min)

    usage_pattern = MagicMock()
    usage_pattern.user_journey.uj_steps = [uj_step]
    usage_pattern.user_journey_freq = ExplainableQuantity(1 * u.user_journey / u.day)
    usage_pattern.user_journey.duration = ExplainableQuantity(1 * u.hour)
    usage_pattern.nb_user_journeys_in_parallel_during_usage = ExplainableQuantity(10 * u.user_journey)
    usage_pattern.time_intervals.utc_time_intervals = ExplainableHourlyUsage(
        [ExplainableQuantity(1 * u.dimensionless)] * 24)

    test_service.usage_patterns = [usage_pattern]

    return test_service


def add_new_step_to_test_service(test_service):
    test_service2 = MagicMock()

    uj_step2 = MagicMock()
    uj_step2.service = test_service2
    uj_step2.ram_needed = ExplainableQuantity(2 * u.Go)
    uj_step2.cpu_needed = ExplainableQuantity(2 * u.core)
    uj_step2.request_duration = ExplainableQuantity(10 * u.min)

    test_service.usage_patterns[0].user_journey.uj_steps.append(uj_step2)

    return test_service


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

    def test_compute_calculated_attributes(self):
        test_service = create_test_service(self.service)

        test_service.compute_calculated_attributes()

        self.assertNotEqual(test_service.storage_needed.value, None)
        self.assertNotEqual(test_service.hour_by_hour_cpu_need.value, None)
        self.assertNotEqual(test_service.hour_by_hour_ram_need.value, None)

    def test_update_storage_needed(self):
        test_service = create_test_service(self.service)

        test_service.update_storage_needed()

        self.assertEqual((100 * u.Mo / u.day).to(u.To / u.year), test_service.storage_needed.value)

    def test_update_hour_by_hour_ram_need(self):
        test_service = create_test_service(self.service)

        test_service.update_hour_by_hour_ram_need()

        self.assertEqual(
            [3.33 * u.Go] * 24,
            [round(elt.value, 2) for elt in test_service.hour_by_hour_ram_need.value])

    def test_update_hour_by_hour_ram_need_multiple_services(self):
        test_service = create_test_service(self.service)

        test_service_with_new_uj_step = add_new_step_to_test_service(test_service)

        test_service_with_new_uj_step.update_hour_by_hour_ram_need()

        self.assertEqual(
            [3.33 * u.Go] * 24,
            [round(elt.value, 2) for elt in test_service.hour_by_hour_ram_need.value])

    def test_update_hour_by_hour_cpu_need(self):
        test_service = create_test_service(self.service)

        test_service.update_hour_by_hour_cpu_need()

        self.assertEqual(
            [3.33 * u.core] * 24,
            [round(elt.value, 2) for elt in test_service.hour_by_hour_cpu_need.value])

    def test_update_hour_by_hour_cpu_need_multiple_services(self):
        test_service = create_test_service(self.service)

        test_service_with_new_uj_step = add_new_step_to_test_service(test_service)

        test_service_with_new_uj_step.update_hour_by_hour_cpu_need()

        self.assertEqual(
            [3.33 * u.core] * 24,
            [round(elt.value, 2) for elt in test_service.hour_by_hour_cpu_need.value])


if __name__ == '__main__':
    unittest.main()
