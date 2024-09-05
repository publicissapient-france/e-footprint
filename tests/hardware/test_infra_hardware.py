from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch

from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.builders.time_builders import create_hourly_usage_df_from_list


class TestInfraHardware(TestCase):
    def setUp(self):
        class InfraHardwareTestClass(InfraHardware):
            def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                         lifespan: SourceValue, average_carbon_intensity: SourceValue):
                super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
                self.dont_handle_pubsub_topic_messages = True

            def update_raw_nb_of_instances(self):
                self.raw_nb_of_instances = SourceHourlyValues(create_hourly_usage_df_from_list([1.5, 3]))

            def update_nb_of_instances(self):
                self.nb_of_instances = SourceHourlyValues(create_hourly_usage_df_from_list([2, 3]))

            def update_instances_energy(self):
                self.instances_energy = SourceHourlyValues(create_hourly_usage_df_from_list([2, 4], pint_unit=u.kWh))

        self.test_infra_hardware = InfraHardwareTestClass(
            "test_infra_hardware", carbon_footprint_fabrication=SourceValue(120 * u.kg, Sources.USER_DATA),
            power=SourceValue(2 * u.W, Sources.USER_DATA), lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh))

        self.service1 = MagicMock()
        self.ram_needs_service1 = SourceHourlyValues(create_hourly_usage_df_from_list([0, 8], pint_unit=u.GB))
        self.cpu_needs_service1 = SourceHourlyValues(create_hourly_usage_df_from_list([0, 8], pint_unit=u.core))
        self.test_infra_hardware_single_service = deepcopy(self.test_infra_hardware)
        self.service1.hour_by_hour_ram_need = self.ram_needs_service1
        self.service1.hour_by_hour_cpu_need = self.cpu_needs_service1
        self.test_infra_hardware_single_service.modeling_obj_containers = [self.service1]

        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.ram_needs_service2 = SourceHourlyValues(create_hourly_usage_df_from_list([6, 14], pint_unit=u.GB))
        self.ram_needs_service3 = SourceHourlyValues(create_hourly_usage_df_from_list([8, 16], pint_unit=u.GB))
        self.cpu_needs_service2 = SourceHourlyValues(create_hourly_usage_df_from_list([6, 14], pint_unit=u.core))
        self.cpu_needs_service3 = SourceHourlyValues(create_hourly_usage_df_from_list([8, 16], pint_unit=u.core))
        self.test_infra_hardware_multiple_services = deepcopy(self.test_infra_hardware)
        self.service2.hour_by_hour_ram_need = self.ram_needs_service2
        self.service3.hour_by_hour_ram_need = self.ram_needs_service3
        self.service2.hour_by_hour_cpu_need = self.cpu_needs_service2
        self.service3.hour_by_hour_cpu_need = self.cpu_needs_service3
        self.test_infra_hardware_multiple_services.modeling_obj_containers = [self.service2, self.service3]

    def test_update_all_services_ram_needs_single_service(self):
        self.test_infra_hardware_single_service.update_all_services_ram_needs()
        self.assertEqual([0, 8], self.test_infra_hardware_single_service.all_services_ram_needs.value_as_float_list)

    def test_services(self):
        service1 = MagicMock()
        service2 = MagicMock()
        with patch.object(
                self.test_infra_hardware_multiple_services, "modeling_obj_containers", new=[service1, service2]):
            self.assertEqual([service1, service2], self.test_infra_hardware_multiple_services.services)

    def test_all_services_infra_needs_multiple_services(self):
        self.test_infra_hardware_multiple_services.update_all_services_ram_needs()
        self.assertEqual(
            [14, 30], self.test_infra_hardware_multiple_services.all_services_ram_needs.value_as_float_list)

    def test_all_services_cpu_needs_single_service(self):
        self.test_infra_hardware_single_service.update_all_services_cpu_needs()
        self.assertEqual(
            [0, 8], self.test_infra_hardware_single_service.all_services_cpu_needs.value_as_float_list)

    def test_all_services_cpu_needs_multiple_services(self):
        self.test_infra_hardware_multiple_services.update_all_services_cpu_needs()
        self.assertEqual(
            [14, 30], self.test_infra_hardware_multiple_services.all_services_cpu_needs.value_as_float_list)

    def test_instances_fabrication_footprint(self):
        self.test_infra_hardware_single_service.update_nb_of_instances()
        self.test_infra_hardware_single_service.update_instances_fabrication_footprint()
        self.assertEqual(u.kg, self.test_infra_hardware_single_service.instances_fabrication_footprint.unit)
        self.assertEqual([2 * 20 / (365.25 * 24), 3 * 20 / (365.25 * 24)],
                         self.test_infra_hardware_single_service.instances_fabrication_footprint.value_as_float_list)

    def test_energy_footprints(self):
        self.test_infra_hardware_single_service.update_instances_energy()
        self.test_infra_hardware_single_service.update_energy_footprint()
        self.assertEqual(u.kg, self.test_infra_hardware_single_service.energy_footprint.unit)
        self.assertEqual([0.2, 0.4],
                         self.test_infra_hardware_single_service.energy_footprint.value_as_float_list)
