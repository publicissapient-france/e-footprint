from unittest import TestCase
from unittest.mock import MagicMock
import unittest

from efootprint.core.system import System
from efootprint.constants.units import u
from efootprint.constants.sources import SourceValue


class TestSystem(TestCase):
    def setUp(self):
        self.usage_pattern = MagicMock()
        self.server = MagicMock()
        self.storage = MagicMock()
        self.device_population = MagicMock()
        self.network = MagicMock()

        self.usage_pattern.user_journey.servers = {self.server}
        self.usage_pattern.user_journey.storages = {self.storage}
        self.usage_pattern.device_population = self.device_population
        self.usage_pattern.network = self.network

        self.server.instances_fabrication_footprint = SourceValue(100 * u.kg / u.year)
        self.storage.instances_fabrication_footprint = SourceValue(100 * u.kg / u.year)
        self.device_population.instances_fabrication_footprint = SourceValue(100 * u.kg / u.year)

        self.server.energy_footprint = SourceValue(100 * u.kg / u.year)
        self.storage.energy_footprint = SourceValue(100 * u.kg / u.year)
        self.device_population.energy_footprint = SourceValue(100 * u.kg / u.year)
        self.network.energy_footprint = SourceValue(100 * u.kg / u.year)

        self.system = System(
            "Non cloud system",
            usage_patterns=[self.usage_pattern]
        )

    def test_servers(self):
        self.assertEqual({self.server}, self.system.servers)

    def test_storages(self):
        self.assertEqual({self.storage}, self.system.storages)

    def test_device_populations(self):
        self.assertEqual({self.device_population}, self.system.device_populations)

    def test_networks(self):
        self.assertEqual({self.network}, self.system.networks)

    def test_fabrication_footprints(self):
        expected_dict = {
            "Servers": SourceValue(100 * u.kg / u.year),
            "Storage": SourceValue(100 * u.kg / u.year),
            "Devices": SourceValue(100 * u.kg / u.year),
            "Network": SourceValue(0 * u.kg / u.year)
        }
        self.assertDictEqual(expected_dict, self.system.fabrication_footprints())

    def test_energy_footprints(self):
        energy_footprints = self.system.energy_footprints()
        expected_dict = {
            "Servers": SourceValue(100 * u.kg / u.year),
            "Storage": SourceValue(100 * u.kg / u.year),
            "Devices": SourceValue(100 * u.kg / u.year),
            "Network": SourceValue(100 * u.kg / u.year)
        }

        self.assertDictEqual(expected_dict, energy_footprints)


if __name__ == '__main__':
    unittest.main()
