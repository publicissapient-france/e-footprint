import unittest
from unittest.mock import MagicMock

from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.units import u
from footprint_model.core.service import Service, Request


class TestService(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        self.storage = MagicMock()
        self.base_ram = 4 * u.Go
        self.base_cpu = 2 * u.core
        self.service = Service("Test Service", self.server, self.storage, self.base_ram, self.base_cpu)

    def test_service_initialization(self):
        self.assertEqual(self.service.name, "Test Service")
        self.assertEqual(self.service.server, self.server)
        self.assertEqual(self.service.storage, self.storage)
        self.assertEqual(self.service.base_ram_consumption.value, self.base_ram)
        self.assertEqual(self.service.base_cpu_consumption.value, self.base_cpu)

    def test_service_invalid_ram_consumption(self):
        invalid_ram = 4 * u.min
        with self.assertRaises(ValueError):
            Service("Invalid RAM Service", self.server, self.storage, invalid_ram)

    def test_service_invalid_cpu_consumption(self):
        invalid_cpu = 2 * u.min
        with self.assertRaises(ValueError):
            Service("Invalid CPU Service", self.server, self.storage, self.base_ram, invalid_cpu)

    def test_service_equality(self):
        service1 = Service("Service A", self.server, self.storage, self.base_ram, self.base_cpu)
        service2 = Service("Service A", self.server, self.storage, self.base_ram, self.base_cpu * 2)
        service3 = Service("Service B", self.server, self.storage, self.base_ram, self.base_cpu)
        self.assertEqual(service1, service2)
        self.assertNotEqual(service1, service3)


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.service = MagicMock()
        self.data_upload = 100 * u.Mo
        self.data_download = 200 * u.Mo
        self.duration = 10 * u.s
        self.cpu_needed = 1 * u.core
        self.server_ram_per_data_transferred = ExplainableQuantity(5 * u.dimensionless, "server_ram_per_data_transferred")
        self.request = Request("Test Request", self.service, self.data_upload, self.data_download, self.duration,
                               self.cpu_needed)

    def test_request_initialization(self):
        self.assertEqual(self.request.name, "Test Request")
        self.assertEqual(self.request.service, self.service)
        self.assertEqual(self.request.data_upload.value * u.user_journey, self.data_upload)
        self.assertEqual(self.request.data_download.value * u.user_journey, self.data_download)
        self.assertEqual(self.request.duration.value, self.duration)
        self.assertEqual(self.request.ram_needed, self.server_ram_per_data_transferred * self.request.data_download)
        self.assertEqual(self.request.cpu_needed.value * u.user_journey, self.cpu_needed)

    def test_request_invalid_data_upload(self):
        invalid_data_upload = 100 * u.s
        with self.assertRaises(ValueError):
            Request("Invalid Data Upload Request", self.service, invalid_data_upload, self.data_download)

    def test_request_invalid_data_download(self):
        invalid_data_download = 200 * u.s
        with self.assertRaises(ValueError):
            Request("Invalid Data Download Request", self.service, self.data_upload, invalid_data_download)


if __name__ == '__main__':
    unittest.main()
