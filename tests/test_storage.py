from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.storage import Storage

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestStorage(TestCase):
    def setUp(self):
        self.country = MagicMock()
        self.storage_base = Storage(
            "storage_base",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0.3 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=1.2,
            country=self.country,
            data_replication_factor=3,
            data_storage_duration=5 * u.year
        )
        self.storage_single_service = deepcopy(self.storage_base)
        self.storage_multiple_services = deepcopy(self.storage_base)

        self.usage_pattern_single_service = MagicMock()
        self.service1 = MagicMock()
        self.service1.storage = self.storage_single_service
        self.service1.storage_needed = ExplainableQuantity(2 * u.To / u.year)
        self.usage_pattern_single_service.services = {self.service1}
        self.storage_single_service.usage_patterns = {self.usage_pattern_single_service}

        self.usage_pattern_multiple_services = MagicMock()
        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.service2.storage = self.storage_multiple_services
        self.service3.storage = self.storage_multiple_services
        self.service2.storage_needed = ExplainableQuantity(2 * u.To / u.year)
        self.service3.storage_needed = ExplainableQuantity(3 * u.To / u.year)
        self.usage_pattern_multiple_services.services = {self.service1, self.service2, self.service3}
        self.storage_multiple_services.usage_patterns = {self.usage_pattern_multiple_services}

    def test_services_single_usage_pattern_single_service(self):
        self.assertEqual({self.service1}, self.storage_single_service.services)

    def test_services_single_usage_pattern_multiple_services(self):
        self.assertEqual({self.service2, self.service3}, self.storage_multiple_services.services)

    def test_services_multiple_usage_patterns_multiple_services(self):
        self.storage_single_service.usage_patterns = {
            self.usage_pattern_single_service, self.usage_pattern_multiple_services}
        self.assertEqual({self.service1}, self.storage_single_service.services)
        self.storage_single_service.usage_patterns = {self.usage_pattern_single_service}

    def test_update_all_services_storage_needs_single_service(self):
        self.storage_single_service.update_all_services_storage_needs()
        self.assertEqual(self.service1.storage_needed, self.storage_single_service.all_services_storage_needs)

    def test_update_all_services_storage_needs_multiple_services(self):
        self.storage_multiple_services.update_all_services_storage_needs()
        expected_value = self.service2.storage_needed + self.service3.storage_needed
        self.assertEqual(expected_value, self.storage_multiple_services.all_services_storage_needs)

    def test_active_storage_required(self):
        active_storage_expected = (
                ExplainableQuantity(10.1 * u.To / u.year)
                * SourceValue(1 * u.hour, Sources.HYPOTHESIS, "Time interval during which active storage is considered")
        ).to(u.Go)
        with patch.object(self.storage_single_service, "all_services_storage_needs", new=ExplainableQuantity(10.1 * u.To / u.year)):
            self.storage_single_service.update_active_storage_required()
            self.assertEqual(active_storage_expected.value, self.storage_single_service.active_storage_required.value)

    def test_long_term_storage_required(self):
        long_term_storage_expected = (
                ExplainableQuantity(10.1 * u.To / u.year) * self.storage_base.data_replication_factor
                * self.storage_base.data_storage_duration - ExplainableQuantity(1.5 * u.Go))
        with patch.object(self.storage_single_service, "all_services_storage_needs", new=ExplainableQuantity(10.1 * u.To / u.year)), \
                patch.object(self.storage_single_service, "active_storage_required", new=ExplainableQuantity(1.5 * u.Go)):
            self.storage_single_service.update_long_term_storage_required()

            self.assertEqual(
                round(long_term_storage_expected.value, 1), round(self.storage_single_service.long_term_storage_required.value, 1))

    def test_nb_of_active_instances(self):
        active_instances_expected = (ExplainableQuantity(2 * u.Go) / self.storage_single_service.storage_capacity)
        with patch.object(self.storage_single_service, "active_storage_required", new=ExplainableQuantity(2 * u.Go)):
            self.storage_single_service.update_nb_of_active_instances()
            self.assertEqual(active_instances_expected.value, round(self.storage_single_service.nb_of_active_instances.value, 4))

    def test_nb_of_idle_instances(self):
        idle_instances_expected = ExplainableQuantity(5 * u.Go) / self.storage_single_service.storage_capacity
        with patch.object(self.storage_single_service, "long_term_storage_required", new=ExplainableQuantity(5 * u.Go)):
            self.storage_single_service.update_nb_of_idle_instances()
            self.assertEqual(idle_instances_expected.value, self.storage_single_service.nb_of_idle_instances.value)

    def test_nb_of_instances(self):
        with patch.object(self.storage_single_service, "nb_of_active_instances",
                          new=ExplainableQuantity(3 * u.dimensionless)), \
                patch.object(self.storage_single_service, "nb_of_idle_instances", new=ExplainableQuantity(2 * u.dimensionless)):
            self.storage_single_service.update_nb_of_instances()
            self.assertEqual(ExplainableQuantity(5 * u.dimensionless), self.storage_single_service.nb_of_instances)

    def test_instances_power(self):
        with patch.object(self.storage_single_service, "nb_of_active_instances",
                          new=ExplainableQuantity(10 * u.dimensionless)), \
                patch.object(self.storage_single_service, "nb_of_idle_instances", new=ExplainableQuantity(1 * u.dimensionless)), \
                patch.object(self.storage_single_service, "fraction_of_time_in_use", new=ExplainableQuantity(0.5 * u.dimensionless)):
            self.storage_single_service.update_instances_power()
            expected_power = ExplainableQuantity((15.6 / 2 + 0.36) * u.W).to(u.kWh / u.year)
            self.assertEqual(round(expected_power.value, 0), round(self.storage_single_service.instances_power.value, 0))
