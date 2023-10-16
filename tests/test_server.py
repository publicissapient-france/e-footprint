from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.server import Server
from tests.utils import create_infra_need

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
        self.usage_pattern_single_service.services = {self.service1}
        self.needs1 = create_infra_need([[0, 8]])
        self.usage_pattern_single_service.estimated_infra_need = {self.service1: self.needs1}
        self.server_single_service.usage_patterns = {self.usage_pattern_single_service}

        self.usage_pattern_multiple_services = MagicMock()
        self.service2 = MagicMock()
        self.service3 = MagicMock()
        self.service2.server = self.server_multiple_services
        self.service3.server = self.server_multiple_services
        self.usage_pattern_multiple_services.services = {self.service1, self.service2, self.service3}
        self.needs2 = create_infra_need([[6, 14]])
        self.needs3 = create_infra_need([[8, 16]])
        self.usage_pattern_multiple_services.estimated_infra_need = {
            self.service1: self.needs1, self.service2: self.needs2, self.service3: self.needs3
        }

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
        self.assertEqual(ExplainableQuantity(0.7 * u.dimensionless), self.server_base.server_utilization_rate)

    def test_server_utilization_rate_cloud(self):
        self.assertEqual(ExplainableQuantity(0.9 * u.dimensionless), self.server_cloud.server_utilization_rate)

    def test_services_server_single_service(self):
        self.assertEqual({self.service1}, self.server_single_service.services)

    def test_services_server_multiple_services(self):
        self.assertEqual({self.service2, self.service3}, self.server_multiple_services.services)

    def test_available_resource_per_instance_single_service_ram(self):
        server_resource = SourceValue(200 * u.Go, Sources.HYPOTHESIS)
        service_base_resource_consumption = 'base_ram_consumption'
        result = self.server_single_service.available_resource_per_instance(
            server_resource, service_base_resource_consumption)
        expected_value = ExplainableQuantity((200 * 0.7 - 0.05) * u.Go)

        self.assertEqual(expected_value.value, result.value)

    def test_available_resource_per_instance_single_service_cpu(self):
        server_resource = SourceValue(24 * u.core, Sources.HYPOTHESIS)
        service_base_resource_consumption = 'base_cpu_consumption'
        result = self.server_single_service.available_resource_per_instance(
            server_resource, service_base_resource_consumption)
        expected_value = ExplainableQuantity((24 * 0.7 - 2) * u.core)

        self.assertEqual(result.value, expected_value.value)

    def test_available_resource_per_instance_multiple_services_ram(self):
        server_resource = SourceValue(200 * u.Go, Sources.HYPOTHESIS)
        service_base_resource_consumption = 'base_ram_consumption'

        result = self.server_multiple_services.available_resource_per_instance(
            server_resource, service_base_resource_consumption)
        expected_value = ExplainableQuantity(((200 * 0.7) - 10 - 30) * u.Go)

        self.assertEqual(result.value, expected_value.value)

    def test_available_resource_per_instance_multiple_services_cpu(self):
        server_resource = SourceValue(24 * u.core, Sources.HYPOTHESIS)
        service_base_resource_consumption = 'base_cpu_consumption'

        result = self.server_multiple_services.available_resource_per_instance(
            server_resource, service_base_resource_consumption)
        expected_value = ExplainableQuantity(((24 * 0.7) - 2 - 1) * u.core)

        self.assertEqual(result.value, expected_value.value)

    def test_available_resource_per_instance_should_raise_value_error_when_demand_exceeds_server_capacity(self):
        server_resource = SourceValue(200 * u.Go, Sources.HYPOTHESIS)
        service_base_resource_consumption = 'base_ram_consumption'
        self.service1.base_ram_consumption = 250 * u.Go

        with self.assertRaises(ValueError):
            self.server_single_service.available_resource_per_instance(
                server_resource, service_base_resource_consumption)

        self.service1.base_ram_consumption = 50 * u.Mo

    def test_nb_of_instances_non_cloud_rounds_up_to_next_integer(self):
        with patch(
                f"{SERVER_MODULE}.all_services_infra_needs",
                new=create_infra_need([[10, 20]], ExplainableQuantity(950 * u.Go), ExplainableQuantity(1 * u.core))), \
            patch(f"{SERVER_MODULE}.available_ram_per_instance", new=ExplainableQuantity(100 * u.Go)), \
            patch(f"{SERVER_MODULE}.available_cpu_per_instance", new=ExplainableQuantity(25 * u.core)), \
                patch.object(self.server_single_service, f"cloud", new=False):
            self.assertEqual(10 * u.dimensionless, self.server_single_service.nb_of_instances.value)

    def test_nb_of_instances_cloud(self):
        infra_need = (create_infra_need([[0, 12]], ExplainableQuantity(100 * u.Go), ExplainableQuantity(1 * u.core))
                      + create_infra_need([[12, 24]], ExplainableQuantity(200 * u.Go), ExplainableQuantity(1 * u.core)))
        with patch(
                f"{SERVER_MODULE}.all_services_infra_needs", new=infra_need), \
                patch(f"{SERVER_MODULE}.available_ram_per_instance", new=ExplainableQuantity(100 * u.Go)), \
                patch(f"{SERVER_MODULE}.available_cpu_per_instance", new=ExplainableQuantity(25 * u.core)), \
                patch.object(self.server_single_service, f"cloud", new=True):
            self.assertEqual(1.5 * u.dimensionless, round(self.server_cloud.nb_of_instances.value, 2))

    def test_compute_instances_power(self):
        with patch(
                f"{SERVER_MODULE}.fraction_of_time_in_use", new=ExplainableQuantity(10 * u.hour / u.day)), \
                patch(f"{SERVER_MODULE}.nb_of_instances", new=ExplainableQuantity(10 * u.dimensionless)), \
                patch.object(self.server_single_service, f"cloud", new=False):
            self.assertEqual(round((43000 * u.W * u.hour / u.day).to(u.kWh / u.year), 2),
                             round(self.server_single_service.instances_power.value, 2))

    def test_compute_instances_power_cloud(self):
        with patch(
                f"{SERVER_MODULE}.fraction_of_time_in_use", new=ExplainableQuantity(10 * u.hour / u.day)), \
                patch(f"{SERVER_MODULE}.nb_of_instances", new=ExplainableQuantity(10 * u.dimensionless)), \
                patch.object(self.server_single_service, f"cloud", new=True):
            self.assertEqual(round((3600 * u.W).to(u.kWh / u.year), 2),
                             round(self.server_single_service.instances_power.value, 2))
