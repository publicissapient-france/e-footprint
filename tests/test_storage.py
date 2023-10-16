from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.storage import Storage
from tests.utils import create_infra_need

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock


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
        self.usage_pattern_single_service.services = {self.service1}
        self.needs1 = create_infra_need([[0, 8]])
        self.usage_pattern_single_service.estimated_infra_need = {self.service1: self.needs1}
        self.storage_single_service.usage_patterns = {self.usage_pattern_single_service}

        self.usage_pattern_multiple_services = MagicMock()
        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.service2.storage = self.storage_multiple_services
        self.service3.storage = self.storage_multiple_services
        self.usage_pattern_multiple_services.services = {self.service1, self.service2, self.service3}
        self.needs2 = create_infra_need([[6, 14]])
        self.needs3 = create_infra_need([[8, 16]])
        self.usage_pattern_multiple_services.estimated_infra_need = {
            self.service1: self.needs1, self.service2: self.needs2, self.service3: self.needs3
        }
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

    def test_active_storage(self):
        active_storage_expected = (
                ExplainableQuantity(10.1 * u.To / u.year)
                * SourceValue(1 * u.hour, Sources.HYPOTHESIS, "Time interval during which active storage is considered")
        ).to(u.Go)
        self.assertEqual(active_storage_expected.value, self.storage_single_service.active_storage_required.value)

    def test_long_term_storage_required(self):
        long_term_storage_expected = (
                ExplainableQuantity(10.1 * u.To / u.year) * self.storage_base.data_replication_factor
                * self.storage_base.data_storage_duration - self.storage_base.active_storage_required)

        self.assertEqual(
            long_term_storage_expected.value, round(self.storage_single_service.long_term_storage_required.value, 1))

    def test_nb_of_active_instances(self):
        self.assertEqual(0.0012 * u.dimensionless, round(self.storage_single_service.nb_of_active_instances.value, 4))

    def test_nb_of_idle_instances(self):
        self.assertEqual(151.5 * u.dimensionless, round(self.storage_single_service.nb_of_idle_instances.value, 1))

    def test_instances_power(self):
        expected_power = ExplainableQuantity(478 * u.kWh / u.year)
        self.assertEqual(expected_power.value, round(self.storage_single_service.instances_power.value, 0))
