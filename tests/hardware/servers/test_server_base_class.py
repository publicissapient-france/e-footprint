from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u
from efootprint.core.hardware.servers.server_base_class import Server

from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock


class TestServerBaseClass(TestCase):
    def setUp(self):
        class TestServer(Server):
            def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                         lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: SourceValue,
                         power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                         server_utilization_rate: SourceValue):
                super().__init__(
                    name, carbon_footprint_fabrication, power, lifespan, idle_power, ram, nb_of_cpus,
                    power_usage_effectiveness,
                    average_carbon_intensity, server_utilization_rate)

            def update_nb_of_instances(self):
                return SourceValue(10 * u.dimensionless)

            def update_instances_power(self):
                return SourceValue(100 * u.W)

        self.country = MagicMock()
        self.server_base = TestServer(
            "Test server",
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(0 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(0 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(0 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
            server_utilization_rate=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS)
        )
        self.server_base.dont_handle_input_updates = True

    def test_available_cpu_per_instance_single_service(self):
        service = MagicMock()
        service.base_cpu_consumption = SourceValue(2 * u.core)
        with patch.object(Server, "services", new_callable=PropertyMock) as mock_service, \
                patch.object(self.server_base, "nb_of_cpus", SourceValue(24 * u.core)), \
                patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            mock_service.return_value = {service}
            self.server_base.update_available_cpu_per_instance()
            expected_value = SourceValue((24 * 0.7 - 2) * u.core)

            self.assertEqual(expected_value.value, self.server_base.available_cpu_per_instance.value)

    def test_available_ram_per_instance_multiple_services(self):
        service1 = MagicMock()
        service1.base_ram_consumption = SourceValue(10 * u.GB)
        service2 = MagicMock()
        service2.base_ram_consumption = SourceValue(30 * u.GB)
        with patch.object(Server, "services", new_callable=PropertyMock) as mock_service, \
                patch.object(self.server_base, "ram", SourceValue(128 * u.GB)), \
                patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            mock_service.return_value = {service1, service2}
            self.server_base.update_available_ram_per_instance()
            expected_value = SourceValue((128 * 0.7 - 10 - 30) * u.GB)

            self.assertEqual(expected_value.value, self.server_base.available_ram_per_instance.value)

    def test_available_cpu_per_instance_multiple_services(self):
        service1 = MagicMock()
        service1.base_cpu_consumption = SourceValue(2 * u.core)
        service2 = MagicMock()
        service2.base_cpu_consumption = SourceValue(1 * u.core)
        with patch.object(Server, "services", new_callable=PropertyMock) as mock_service, \
                patch.object(self.server_base, "nb_of_cpus", SourceValue(24 * u.core)), \
                patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            mock_service.return_value = {service1, service2}
            self.server_base.update_available_cpu_per_instance()
            expected_value = SourceValue((24 * 0.7 - 2 - 1) * u.core)

            self.assertEqual(expected_value.value, self.server_base.available_cpu_per_instance.value)

    def test_available_ram_per_instance_should_raise_value_error_when_demand_exceeds_server_capacity(self):
        service = MagicMock()
        service.base_ram_consumption = SourceValue(129 * u.GB)
        with patch.object(Server, "services", new_callable=PropertyMock) as mock_service, \
                patch.object(self.server_base, "ram", SourceValue(128 * u.GB)), \
                patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            mock_service.return_value = {service}
            with self.assertRaises(ValueError):
                self.server_base.update_available_ram_per_instance()
