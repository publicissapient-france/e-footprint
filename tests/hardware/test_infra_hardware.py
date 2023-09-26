from footprint_model.constants.countries import Country
from footprint_model.core.hardware.hardware_base_classes import ObjectLinkedToUsagePatterns, InfraHardware
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from tests.utils import create_cpu_need, create_ram_need

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
                self.never_send_pubsub_topic_messages = True

            def update_nb_of_instances(self):
                self.nb_of_instances = SourceValue(2 * u.dimensionless)

            def update_instances_power(self):
                self.instances_power = SourceValue(16 * u.W)

            @property
            def services(self):
                return self.services__raw

        test_country = MagicMock()
        test_country.average_carbon_intensity = SourceValue(100 * u.g / u.kWh)
        self.test_infra_hardware = InfraHardwareTestClass(
            "test_infra_hardware", carbon_footprint_fabrication=SourceValue(120 * u.kg, Sources.USER_INPUT),
            power=SourceValue(2 * u.W, Sources.USER_INPUT), lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            country=test_country)

        self.usage_pattern_single_service = MagicMock()
        self.service1 = MagicMock()
        self.ram_needs_service1 = create_ram_need([[0, 8]])
        self.cpu_needs_service1 = create_cpu_need([[0, 8]])
        self.test_infra_hardware_single_service = deepcopy(self.test_infra_hardware)
        self.test_infra_hardware_single_service.usage_patterns = {self.usage_pattern_single_service}
        self.service1.hour_by_hour_ram_need = self.ram_needs_service1
        self.service1.hour_by_hour_cpu_need = self.cpu_needs_service1
        self.test_infra_hardware_single_service.services__raw = {self.service1}

        self.usage_pattern_multiple_services = MagicMock()
        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.ram_needs_service2 = create_ram_need([[6, 14]])
        self.ram_needs_service3 = create_ram_need([[8, 16]])
        self.cpu_needs_service2 = create_cpu_need([[6, 14]])
        self.cpu_needs_service3 = create_cpu_need([[8, 16]])
        self.test_infra_hardware_multiple_services = deepcopy(self.test_infra_hardware)
        self.test_infra_hardware_multiple_services.usage_patterns = {self.usage_pattern_multiple_services}
        self.service2.hour_by_hour_ram_need = self.ram_needs_service2
        self.service3.hour_by_hour_ram_need = self.ram_needs_service3
        self.service2.hour_by_hour_cpu_need = self.cpu_needs_service2
        self.service3.hour_by_hour_cpu_need = self.cpu_needs_service3
        self.test_infra_hardware_multiple_services.services__raw = {self.service2, self.service3}

    def test_update_all_services_ram_needs_single_service(self):
        expected_value = ExplainableHourlyUsage([SourceValue(0 * u.GB)] * 24, "expected_ram_needs")
        for i in range(8):
            expected_value.value[i] = SourceValue(100 * u.GB)

        self.test_infra_hardware_single_service.update_all_services_ram_needs()
        self.assertEqual(expected_value.value, self.test_infra_hardware_single_service.all_services_ram_needs.value)

    def test_all_services_infra_needs_multiple_services(self):
        expected_value = ExplainableHourlyUsage([SourceValue(0 * u.GB)] * 24, "expected_ram_needs")
        for i in range(6, 8):
            expected_value.value[i] = SourceValue(100 * u.GB)
        for i in range(8, 14):
            expected_value.value[i] = SourceValue(200 * u.GB)
        for i in range(14, 16):
            expected_value.value[i] = SourceValue(100 * u.GB)

        self.test_infra_hardware_multiple_services.update_all_services_ram_needs()
        self.assertEqual(expected_value.value, self.test_infra_hardware_multiple_services.all_services_ram_needs.value)

    def test_all_services_cpu_needs_single_service(self):
        expected_value = ExplainableHourlyUsage([SourceValue(0 * u.core)] * 24, "expected_cpu_needs")
        for i in range(8):
            expected_value.value[i] = SourceValue(1 * u.core)

        self.test_infra_hardware_single_service.update_all_services_cpu_needs()
        self.assertEqual(expected_value.value, self.test_infra_hardware_single_service.all_services_cpu_needs.value)

    def test_all_services_cpu_needs_multiple_services(self):
        expected_value = ExplainableHourlyUsage([SourceValue(0 * u.core)] * 24, "expected_cpu_needs")
        for i in range(6, 8):
            expected_value.value[i] = SourceValue(1 * u.core)
        for i in range(8, 14):
            expected_value.value[i] = SourceValue(2 * u.core)
        for i in range(14, 16):
            expected_value.value[i] = SourceValue(1 * u.core)

        self.test_infra_hardware_multiple_services.update_all_services_cpu_needs()
        self.assertEqual(expected_value.value, self.test_infra_hardware_multiple_services.all_services_cpu_needs.value)

    def test_fraction_of_time_in_use_single_service(self):
        self.usage_pattern_single_service.time_intervals.utc_time_intervals = ExplainableHourlyUsage(
            [SourceValue(1 * u.dimensionless)] * 10 + [SourceValue(0 * u.dimensionless)] * 14,
            "expected_fraction_of_time_in_use")
        expected_value = SourceValue((10 / 24) * u.dimensionless, "fraction_of_time_in_use")
        self.test_infra_hardware_single_service.update_fraction_of_time_in_use()
        self.assertEqual(expected_value.value, self.test_infra_hardware_single_service.fraction_of_time_in_use.value)

    def test_fraction_of_time_in_use_multiple_services_with_different_usage(self):
        up_1 = MagicMock()
        up_2 = MagicMock()
        up_1.time_intervals.utc_time_intervals = ExplainableHourlyUsage(
            [SourceValue(1 * u.dimensionless)] * 10 + [SourceValue(0 * u.dimensionless)] * 14, "utc_time_intervals")
        up_2.time_intervals.utc_time_intervals = ExplainableHourlyUsage(
            [SourceValue(0 * u.dimensionless)] * 4 + [SourceValue(1 * u.dimensionless)] * 10
            + [SourceValue(0 * u.dimensionless)] * 10, "utc_time_intervals")
        expected_value = SourceValue((14 / 24) * u.dimensionless, "fraction_of_time_in_use")
        self.test_infra_hardware_multiple_services.usage_patterns = {up_1, up_2}
        self.test_infra_hardware_multiple_services.update_fraction_of_time_in_use()
        self.assertEqual(expected_value.value, self.test_infra_hardware_multiple_services.fraction_of_time_in_use.value)

    def test_instances_fabrication_footprint(self):
        self.test_infra_hardware_single_service.update_nb_of_instances()
        self.test_infra_hardware_single_service.update_instances_fabrication_footprint()
        self.assertEqual(
            40 * u.kg / u.year, self.test_infra_hardware_single_service.instances_fabrication_footprint.value)

    def test_energy_footprints(self):
        self.test_infra_hardware_single_service.update_instances_power()
        self.test_infra_hardware_single_service.update_energy_footprint()
        self.assertEqual(
            round(16 * 24 * 365.25 * 100 * 1e-6 * u.kg / u.year, 2),
            round(self.test_infra_hardware_single_service.energy_footprint.value, 2))


class TestObjectLinkedToUsagePatterns(TestCase):
    def setUp(self):
        self.test_object_linked_to_usage_patterns = ObjectLinkedToUsagePatterns()

    def test_link_usage_pattern_should_return_same_set_if_usage_pattern_already_in_set(self):
        self.test_object_linked_to_usage_patterns.usage_patterns = {"usage_pattern_1"}
        self.test_object_linked_to_usage_patterns.link_usage_pattern("usage_pattern_1")
        self.assertEqual({"usage_pattern_1"}, self.test_object_linked_to_usage_patterns.usage_patterns)

    def test_link_usage_pattern_should_add_new_usage_pattern_to_usage_patterns_set(self):
        self.test_object_linked_to_usage_patterns.usage_patterns = {"usage_pattern_1"}
        self.test_object_linked_to_usage_patterns.link_usage_pattern("usage_pattern_2")
        self.assertEqual({"usage_pattern_1", "usage_pattern_2"}, self.test_object_linked_to_usage_patterns.usage_patterns)

    def test_unlink_usage_pattern(self):
        self.test_object_linked_to_usage_patterns.usage_patterns = {"usage_pattern_1"}
        self.test_object_linked_to_usage_patterns.unlink_usage_pattern("usage_pattern_1")
        self.assertEqual(set(), self.test_object_linked_to_usage_patterns.usage_patterns)
