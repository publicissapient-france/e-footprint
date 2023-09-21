from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.hardware.server import Server
from tests.utils import create_cpu_need, create_ram_need

from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock

SERVER_MODULE = "footprint_model.core.server.Server"


class TestServer(TestCase):
    def setUp(self):
        self.country = MagicMock()
        self.server_base = Server(
            PhysicalElements.SERVER,
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(0 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(0 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(0 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            country=MagicMock(),
            cloud="Unexisting cloud"
        )

    def test_server_utilization_rate_serverless(self):
        with patch.object(self.server_base, "cloud", new="Serverless"):
            self.server_base.update_server_utilization_rate()

        self.assertEqual(SourceValue(0.9 * u.dimensionless), self.server_base.server_utilization_rate)

    def test_server_utilization_rate_on_premise(self):
        with patch.object(self.server_base, "cloud", new="On premise"):
            self.server_base.update_server_utilization_rate()

        self.assertEqual(SourceValue(0.7 * u.dimensionless), self.server_base.server_utilization_rate)

    def test_server_utilization_rate_unexisting_cloud_config(self):
        with patch.object(self.server_base, "cloud", new="Unexisting Cloud config"):
            self.server_base.update_server_utilization_rate()

        self.assertEqual(None, self.server_base.server_utilization_rate)

    def test_services_server(self):
        usage_pattern1 = MagicMock()
        usage_pattern2 = MagicMock()
        service1 = MagicMock()
        service1.server = self.server_base
        service2 = MagicMock()
        service2.server = "other server"
        usage_pattern1.services = {service1, service2}
        service3 = MagicMock()
        service3.server = self.server_base
        usage_pattern2.services = {service3}
        with patch.object(self.server_base, "usage_patterns", new={usage_pattern1, usage_pattern2}):
            self.assertEqual({service1, service3}, self.server_base.services)

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

    def test_nb_of_instances_on_premise_rounds_up_to_next_integer(self):
        hour_by_hour_ram_need = create_ram_need([[10, 20]], ram=950 * u.GB)
        hour_by_hour_cpu_need = create_cpu_need([[10, 20]])

        with patch.object(self.server_base, "all_services_ram_needs", new= hour_by_hour_ram_need), \
                patch.object(self.server_base, "all_services_cpu_needs", new=hour_by_hour_cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(100 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(25 * u.core)), \
                patch.object(self.server_base, "cloud", new="On premise"):
            self.server_base.update_nb_of_instances()
            self.assertEqual(10 * u.dimensionless, self.server_base.nb_of_instances.value)

    def test_nb_of_instances_serverless(self):
        ram_need = (create_ram_need([[0, 12]], 100 * u.GB) + create_ram_need([[12, 24]], 150 * u.GB))
        cpu_need = create_cpu_need([[0, 24]], 1 * u.core)

        with patch.object(self.server_base, "all_services_ram_needs", new=ram_need), \
                patch.object(self.server_base, "all_services_cpu_needs", new=cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(100 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(25 * u.core)), \
                patch.object(self.server_base, "cloud", new="Serverless"):
            self.server_base.update_nb_of_instances()
            self.assertEqual(1.25 * u.dimensionless, round(self.server_base.nb_of_instances.value, 2))

    def test_nb_of_instances_autoscaling(self):
        ram_need = (create_ram_need([[0, 12]], 100 * u.GB) + create_ram_need([[12, 24]], 150 * u.GB))
        cpu_need = create_cpu_need([[0, 24]], 1 * u.core)

        with patch.object(self.server_base, "all_services_ram_needs", new=ram_need), \
                patch.object(self.server_base, "all_services_cpu_needs", new=cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(100 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(25 * u.core)), \
                patch.object(self.server_base, "cloud", new="Autoscaling"):
            self.server_base.update_nb_of_instances()
            self.assertEqual(1.5 * u.dimensionless, round(self.server_base.nb_of_instances.value, 2))

    def test_compute_instances_power(self):
        with patch.object(self.server_base,
                          "fraction_of_time_in_use", SourceValue(((24 - 10) / 24) * u.dimensionless)), \
                patch.object(self.server_base, "nb_of_instances", SourceValue(10 * u.dimensionless)), \
                patch.object(self.server_base, "cloud", "On premise"), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(1.2 * u.dimensionless)):
            self.server_base.update_instances_power()
            self.assertEqual(20600.1 * u.kWh / u.year,
                             round(self.server_base.instances_power.value, 2))

    def test_compute_instances_power_serverless(self):
        with patch.object(self.server_base,
                          "fraction_of_time_in_use", SourceValue(((24 - 10) / 24) * u.dimensionless)), \
                patch.object(self.server_base, "nb_of_instances", SourceValue(10 * u.dimensionless)), \
                patch.object(self.server_base, "cloud", "Serverless"), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(1.2 * u.dimensionless)):
            self.server_base.update_instances_power()
            self.assertEqual(round((3600 * u.W).to(u.kWh / u.year), 2),
                             round(self.server_base.instances_power.value, 2))

    def test_compute_instances_power_cloud_autoscaling(self):
        with patch.object(self.server_base,
                          "fraction_of_time_in_use", SourceValue(((24 - 10) / 24) * u.dimensionless)), \
                patch.object(self.server_base, "nb_of_instances", SourceValue(10 * u.dimensionless)), \
                patch.object(self.server_base, "cloud", "Autoscaling"), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(1.2 * u.dimensionless)):
            self.server_base.update_instances_power()
            self.assertEqual(round((3600 * u.W).to(u.kWh / u.year), 2),
                             round(self.server_base.instances_power.value, 2))
