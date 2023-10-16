from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import InfraHardware, ObjectLinkedToUsagePatterns
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from tests.utils import create_infra_need

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock


class TestInfraHardware(TestCase):
    def setUp(self):
        class InfraHardwareTestClass(InfraHardware):
            def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                         lifespan: SourceValue, country: Country):
                super().__init__(name, carbon_footprint_fabrication, power, lifespan, country)
                self.services__raw = set()

            @property
            def services(self):
                return self.services__raw

            @property
            def nb_of_instances(self):
                return ExplainableQuantity(2 * u.dimensionless)

            @property
            def instances_power(self):
                return ExplainableQuantity(16 * u.W)

        test_country = MagicMock()
        test_country.average_carbon_intensity = ExplainableQuantity(100 * u.g / u.kWh)
        self.test_infra_hardware = InfraHardwareTestClass(
            "test_infra_hardware", carbon_footprint_fabrication=SourceValue(120 * u.kg, Sources.USER_INPUT),
            power=SourceValue(2 * u.W, Sources.USER_INPUT), lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            country=test_country)

        self.usage_pattern_single_service = MagicMock()
        self.needs1 = create_infra_need([[0, 8]])
        self.usage_pattern_single_service.estimated_infra_need = {"service1": self.needs1}
        self.test_infra_hardware_single_service = deepcopy(self.test_infra_hardware)
        self.test_infra_hardware_single_service.usage_patterns = {self.usage_pattern_single_service}
        self.test_infra_hardware_single_service.services__raw = {"service1"}

        self.usage_pattern_multiple_services = MagicMock()
        self.needs2 = create_infra_need([[6, 14]])
        self.needs3 = create_infra_need([[8, 16]])
        self.usage_pattern_multiple_services.estimated_infra_need = {
            "service1": self.needs1, "service2": self.needs2, "service3": self.needs3
        }
        self.test_infra_hardware_multiple_services = deepcopy(self.test_infra_hardware)
        self.test_infra_hardware_multiple_services.usage_patterns = {self.usage_pattern_multiple_services}
        self.test_infra_hardware_multiple_services.services__raw = {"service2", "service3"}

    def test_all_services_infra_needs_single_service(self):
        self.assertEqual(self.needs1, self.test_infra_hardware_single_service.all_services_infra_needs)

    def test_all_services_infra_needs_multiple_services(self):
        self.assertEqual(self.needs2 + self.needs3, self.test_infra_hardware_multiple_services.all_services_infra_needs)

    def test_fraction_of_time_in_use_single_service(self):
        expected_value = ExplainableQuantity(8 * u.hour / u.day, "fraction_of_time_in_use")
        self.assertEqual(expected_value.value, self.test_infra_hardware_single_service.fraction_of_time_in_use.value)

    def test_fraction_of_time_in_use_multiple_services_with_different_usage(self):
        expected_fraction_of_time_in_use = ExplainableQuantity(10 * u.hour / u.day, "fraction_of_time_in_use")
        self.assertEqual(
            expected_fraction_of_time_in_use.value,
            self.test_infra_hardware_multiple_services.fraction_of_time_in_use.value)

    def test_instances_fabrication_footprint(self):
        self.assertEqual(
            40 * u.kg / u.year, self.test_infra_hardware_single_service.instances_fabrication_footprint.value)

    def test_energy_footprints(self):
        self.assertEqual(
            round(16 * 24 * 365.25 * 100 * 1e-6 * u.kg / u.year, 2),
            round(self.test_infra_hardware_single_service.energy_footprint.value, 2))


class TestObjectLinkedToUsagePatterns(TestCase):
    def setUp(self):
        self.test_object_linked_to_usage_patterns = ObjectLinkedToUsagePatterns()

    def test_link_usage_pattern_should_return_same_set_if_usage_pattern_already_in_set(self):
        test_object_linked_to_usage_patterns = deepcopy(self.test_object_linked_to_usage_patterns)
        test_object_linked_to_usage_patterns.usage_patterns = {"usage_pattern_1"}
        test_object_linked_to_usage_patterns.link_usage_pattern("usage_pattern_1")
        self.assertEqual({"usage_pattern_1"}, test_object_linked_to_usage_patterns.usage_patterns)

    def test_link_usage_pattern_should_add_new_usage_pattern_to_usage_patterns_set(self):
        test_object_linked_to_usage_patterns = deepcopy(self.test_object_linked_to_usage_patterns)
        test_object_linked_to_usage_patterns.usage_patterns = {"usage_pattern_1"}
        test_object_linked_to_usage_patterns.link_usage_pattern("usage_pattern_2")
        self.assertEqual({"usage_pattern_1", "usage_pattern_2"}, test_object_linked_to_usage_patterns.usage_patterns)

    def test_unlink_usage_pattern(self):
        test_object_linked_to_usage_patterns = deepcopy(self.test_object_linked_to_usage_patterns)
        test_object_linked_to_usage_patterns.usage_patterns = {"usage_pattern_1"}
        test_object_linked_to_usage_patterns.unlink_usage_pattern("usage_pattern_1")
        self.assertEqual(set(), test_object_linked_to_usage_patterns.usage_patterns)
