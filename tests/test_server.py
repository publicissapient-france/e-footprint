from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.server import Server
from tests.utils import create_cpu_need, create_ram_need

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch


SERVER_MODULE = "footprint_model.core.server.Server"


class TestServer(TestCase):
    def setUp(self):
        self.country = MagicMock()
        self.server_base = Server(
            PhysicalElements.SERVER,
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(128 * u.Go, Sources.HYPOTHESIS),
            nb_of_cpus=24,
            power_usage_effectiveness=1.2,
            country=self.country,
            cloud=False
        )

        self.server_single_service = deepcopy(self.server_base)
        self.server_multiple_services = deepcopy(self.server_base)

        self.usage_pattern_single_service = MagicMock()
        self.service1 = MagicMock()
        self.service1.server = self.server_single_service
        self.ram_needs_service1 = create_ram_need([[0, 8]])
        self.cpu_needs_service1 = create_cpu_need([[0, 8]])
        self.service1.hour_by_hour_ram_need = self.ram_needs_service1
        self.service1.hour_by_hour_cpu_need = self.cpu_needs_service1
        self.usage_pattern_single_service.services = {self.service1}
        self.server_single_service.usage_patterns = {self.usage_pattern_single_service}

        self.usage_pattern_multiple_services = MagicMock()
        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.service2.server = self.server_multiple_services
        self.service3.server = self.server_multiple_services
        self.ram_needs_service2 = create_ram_need([[6, 14]])
        self.ram_needs_service3 = create_ram_need([[8, 16]])
        self.cpu_needs_service2 = create_cpu_need([[6, 14]])
        self.cpu_needs_service3 = create_cpu_need([[8, 16]])
        self.service2.hour_by_hour_ram_need = self.ram_needs_service2
        self.service3.hour_by_hour_ram_need = self.ram_needs_service3
        self.service2.hour_by_hour_cpu_need = self.cpu_needs_service2
        self.service3.hour_by_hour_cpu_need = self.cpu_needs_service3
        self.usage_pattern_multiple_services.services = {self.service1, self.service2, self.service3}
        self.server_multiple_services.usage_patterns = {self.usage_pattern_multiple_services}

        self.service1.base_ram_consumption = ExplainableQuantity(50 * u.Mo)
        self.service1.base_cpu_consumption = ExplainableQuantity(2 * u.core)
        self.service2.base_ram_consumption = ExplainableQuantity(10 * u.Go)
        self.service2.base_cpu_consumption = ExplainableQuantity(1 * u.core)
        self.service3.base_ram_consumption = ExplainableQuantity(30 * u.Go)
        self.service3.base_cpu_consumption = ExplainableQuantity(2 * u.core)

        self.server_cloud = deepcopy(self.server_single_service)
        self.server_cloud.cloud = True

    def test_server_utilization_rate(self):
        self.server_base.update_server_utilization_rate()
        self.assertEqual(ExplainableQuantity(0.7 * u.dimensionless), self.server_base.server_utilization_rate)

    def test_server_utilization_rate_cloud(self):
        self.server_cloud.update_server_utilization_rate()
        self.assertEqual(ExplainableQuantity(0.9 * u.dimensionless), self.server_cloud.server_utilization_rate)

    def test_services_server_single_service(self):
        self.assertEqual({self.service1}, self.server_single_service.services)

    def test_services_server_multiple_services(self):
        self.assertEqual({self.service2, self.service3}, self.server_multiple_services.services)

    def test_available_ram_per_instance_single_service(self):
        self.server_single_service.update_server_utilization_rate()
        self.server_single_service.update_available_ram_per_instance()
        expected_value = ExplainableQuantity((128 * 0.7 - 0.05) * u.Go)

        self.assertEqual(expected_value.value, self.server_single_service.available_ram_per_instance.value)

    def test_available_cpu_per_instance_single_service(self):
        self.server_single_service.update_server_utilization_rate()
        self.server_single_service.update_available_cpu_per_instance()
        expected_value = ExplainableQuantity((24 * 0.7 - 2) * u.core)

        self.assertEqual(expected_value.value, self.server_single_service.available_cpu_per_instance.value)

    def test_available_ram_per_instance_multiple_services(self):
        self.server_multiple_services.update_server_utilization_rate()
        self.server_multiple_services.update_available_ram_per_instance()

        expected_value = ExplainableQuantity(((128 * 0.7) - 10 - 30) * u.Go)

        self.assertEqual(expected_value.value, self.server_multiple_services.available_ram_per_instance.value)

    def test_available_cpu_per_instance_multiple_services(self):
        self.server_multiple_services.update_server_utilization_rate()
        self.server_multiple_services.update_available_cpu_per_instance()

        expected_value = ExplainableQuantity(((24 * 0.7) - 2 - 1) * u.core)

        self.assertEqual(expected_value.value, self.server_multiple_services.available_cpu_per_instance.value)

    def test_available_ram_per_instance_should_raise_value_error_when_demand_exceeds_server_capacity(self):
        self.service1.base_ram_consumption = 250 * u.Go

        with self.assertRaises(ValueError):
            self.server_single_service.update_server_utilization_rate()
            self.server_single_service.update_available_ram_per_instance()

        self.service1.base_ram_consumption = 50 * u.Mo

    def test_nb_of_instances_non_cloud_rounds_up_to_next_integer(self):
        hour_by_hour_ram_need = create_ram_need([[10, 20]], ram=950 * u.Go)
        hour_by_hour_cpu_need = create_cpu_need([[10, 20]])

        with patch.object(self.server_single_service, "all_services_ram_needs", new= hour_by_hour_ram_need), \
                patch.object(self.server_single_service, "all_services_cpu_needs", new=hour_by_hour_cpu_need), \
                patch.object(self.server_single_service, "available_ram_per_instance", new=ExplainableQuantity(100 * u.Go)), \
                patch.object(self.server_single_service, "available_cpu_per_instance", new=ExplainableQuantity(25 * u.core)), \
                patch.object(self.server_single_service, "cloud", new=False):
            self.server_single_service.update_nb_of_instances()
            self.assertEqual(10 * u.dimensionless, self.server_single_service.nb_of_instances.value)

    def test_nb_of_instances_cloud(self):
        ram_need = (create_ram_need([[0, 12]], 100 * u.Go) + create_ram_need([[12, 24]], 200 * u.Go))
        cpu_need = create_cpu_need([[0, 24]], 1 * u.core)

        with patch.object(self.server_cloud, "all_services_ram_needs", new=ram_need), \
                patch.object(self.server_cloud, "all_services_cpu_needs", new=cpu_need), \
                patch.object(self.server_cloud, "available_ram_per_instance", new=ExplainableQuantity(100 * u.Go)), \
                patch.object(self.server_cloud, "available_cpu_per_instance", new=ExplainableQuantity(25 * u.core)), \
                patch.object(self.server_cloud, "cloud", new=True):
            self.server_cloud.update_nb_of_instances()
            self.assertEqual(1.5 * u.dimensionless, round(self.server_cloud.nb_of_instances.value, 2))

    def test_compute_instances_power(self):
        with patch.object(self.server_single_service,
                          "fraction_of_time_in_use", new=ExplainableQuantity(((24 - 10) / 24) * u.dimensionless)), \
                patch.object(self.server_single_service, "nb_of_instances", new=ExplainableQuantity(10 * u.dimensionless)), \
                patch.object(self.server_single_service, "cloud", new=False):
            self.server_single_service.update_instances_power()
            self.assertEqual(round((55400 / 24 * u.W).to(u.kWh / u.year), 2),
                             round(self.server_single_service.instances_power.value, 2))

    def test_compute_instances_power_cloud(self):
        with patch.object(self.server_single_service, "nb_of_instances", new=ExplainableQuantity(10 * u.dimensionless)), \
                patch.object(self.server_single_service, f"cloud", new=True):
            self.server_single_service.update_instances_power()
            self.assertEqual(round((3600 * u.W).to(u.kWh / u.year), 2),
                             round(self.server_single_service.instances_power.value, 2))
