from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u
from tests.utils import create_cpu_need, create_ram_need

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestInfraHardware(TestCase):
    def setUp(self):
        class InfraHardwareTestClass(InfraHardware):
            def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                         lifespan: SourceValue, average_carbon_intensity: SourceValue):
                super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
                self.dont_handle_pubsub_topic_messages = True

            def update_nb_of_instances(self):
                self.nb_of_instances = SourceValue(2 * u.dimensionless)

            def update_instances_power(self):
                self.instances_power = SourceValue(16 * u.W)

        self.test_infra_hardware = InfraHardwareTestClass(
            "test_infra_hardware", carbon_footprint_fabrication=SourceValue(120 * u.kg, Sources.USER_INPUT),
            power=SourceValue(2 * u.W, Sources.USER_INPUT), lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh))

        self.service1 = MagicMock()
        self.ram_needs_service1 = create_ram_need([[0, 8]])
        self.cpu_needs_service1 = create_cpu_need([[0, 8]])
        self.test_infra_hardware_single_service = deepcopy(self.test_infra_hardware)
        self.service1.hour_by_hour_ram_need = self.ram_needs_service1
        self.service1.hour_by_hour_cpu_need = self.cpu_needs_service1
        self.test_infra_hardware_single_service.modeling_obj_containers = [self.service1]

        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.ram_needs_service2 = create_ram_need([[6, 14]])
        self.ram_needs_service3 = create_ram_need([[8, 16]])
        self.cpu_needs_service2 = create_cpu_need([[6, 14]])
        self.cpu_needs_service3 = create_cpu_need([[8, 16]])
        self.test_infra_hardware_multiple_services = deepcopy(self.test_infra_hardware)
        self.service2.hour_by_hour_ram_need = self.ram_needs_service2
        self.service3.hour_by_hour_ram_need = self.ram_needs_service3
        self.service2.hour_by_hour_cpu_need = self.cpu_needs_service2
        self.service3.hour_by_hour_cpu_need = self.cpu_needs_service3
        self.test_infra_hardware_multiple_services.modeling_obj_containers = [self.service2, self.service3]

    def test_update_all_services_ram_needs_single_service(self):
        expected_value = ExplainableHourlyUsage([SourceValue(0 * u.GB)] * 24, "expected_ram_needs")
        for i in range(8):
            expected_value.value[i] = SourceValue(100 * u.GB)

        self.test_infra_hardware_single_service.update_all_services_ram_needs()
        self.assertEqual(expected_value.value, self.test_infra_hardware_single_service.all_services_ram_needs.value)

    def test_services(self):
        service1 = MagicMock()
        service2 = MagicMock()
        with patch.object(
                self.test_infra_hardware_multiple_services, "modeling_obj_containers", new=[service1, service2]):
            self.assertEqual([service1, service2], self.test_infra_hardware_multiple_services.services)

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

    def test_fraction_of_time_in_use(self):
        self.test_infra_hardware_multiple_services.all_services_cpu_needs = create_cpu_need([[10, 15]])
        self.test_infra_hardware_multiple_services.all_services_ram_needs = create_ram_need([[0, 12]])
        expected_value = SourceValue((15 / 24) * u.dimensionless, "fraction_of_time_in_use")
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
