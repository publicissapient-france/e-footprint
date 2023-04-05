from unittest import TestCase
from unittest.mock import MagicMock
import unittest

from footprint_model.core.system import UsagePattern, Population, System
from footprint_model.constants.physical_elements import Device, Network, PhysicalElements, Devices
from footprint_model.constants.units import u
from footprint_model.constants.countries import Countries


class TestSystem(TestCase):
    def setUp(self):
        self.usage_pattern = MagicMock(spec=UsagePattern)
        self.usage_pattern.estimated_infra_need.ram = 100 * u.Go
        self.usage_pattern.estimated_infra_need.storage = 10.1 * u.To
        self.usage_pattern.daily_usage_window = 8 * u.hour
        self.usage_pattern.population = MagicMock(spec=Population)
        self.usage_pattern.population.country = Countries.FRANCE
        self.usage_pattern.compute_energy_consumption.return_value = {}
        self.usage_pattern.compute_fabrication_emissions.return_value = {}

        self.system = System(
            usage_pattern=self.usage_pattern,
            data_replication_factor=2,
            data_storage_duration=3 * u.year,
            cloud=True
        )

    def test_nb_of_servers_required__raw(self):
        self.assertAlmostEqual(self.system.nb_of_servers_required__raw.magnitude, 0.87, delta=0.01)

    def test_nb_of_terabytes_required(self):
        self.assertEqual(self.system.nb_of_terabytes_required, 61 * u.To)

    def test_compute_servers_consumption(self):
        self.assertEqual(round(self.system.compute_servers_consumption(), 1), 1521.9 * u.kWh)

    def test_compute_servers_fabrication_footprint(self):
        self.assertAlmostEqual(round(self.system.compute_servers_fabrication_footprint(), 1), 48.2 * u.kg)

    def test_compute_storage_consumption(self):
        self.assertAlmostEqual(round(self.system.compute_storage_consumption(), 1), 278.1 * u.kWh)

    def test_compute_storage_fabrication_footprint(self):
        self.assertAlmostEqual(round(self.system.compute_storage_fabrication_footprint(), 1), 1626.7 * u.kg)

    def test_compute_energy_consumption(self):
        energy_consumption = self.system.compute_energy_consumption()
        expected_dict = {PhysicalElements.SERVER: 1521.9 * u.kWh, PhysicalElements.SSD: 278.1 * u.kWh}
        self.assertDictEqual(energy_consumption, expected_dict)

    def test_compute_fabrication_emissions(self):
        fabrication_emissions = self.system.compute_fabrication_emissions()
        expected_dict = {PhysicalElements.SERVER: 48.2 * u.kg, PhysicalElements.SSD: 1626.7 * u.kg}
        self.assertDictEqual(fabrication_emissions, expected_dict)

    def test_compute_energy_emissions(self):
        energy_emissions = self.system.compute_energy_emissions()
        expected_dict = {PhysicalElements.SERVER: 91.3 * u.kg, PhysicalElements.SSD: 16.7 * u.kg}
        self.assertDictEqual(energy_emissions, expected_dict)


if __name__ == '__main__':
    unittest.main()
