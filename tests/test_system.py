import os.path
from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock
import unittest

from efootprint.abstract_modeling_classes.explainable_objects import EmptyExplainableObject
from efootprint.core.system import System
from efootprint.constants.units import u
from efootprint.abstract_modeling_classes.source_objects import SourceHourlyValues
from efootprint.builders.time_builders import create_hourly_usage_df_from_list


root_dir = os.path.dirname(os.path.abspath(__file__))


class TestSystem(TestCase):
    def setUp(self):
        self.usage_pattern = MagicMock()
        self.usage_pattern.name = "usage_pattern"
        self.server = MagicMock()
        self.server.name = "server"
        self.storage = MagicMock()
        self.storage.name = "storage"
        self.network = MagicMock()
        self.network.name = "network"

        self.usage_pattern.user_journey.servers = {self.server}
        self.usage_pattern.user_journey.storages = {self.storage}
        self.usage_pattern.network = self.network

        self.server.instances_fabrication_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))
        self.storage.instances_fabrication_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))
        self.usage_pattern.devices_fabrication_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))

        self.server.energy_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))
        self.storage.energy_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))
        self.usage_pattern.devices_energy_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))
        self.network.energy_footprint = SourceHourlyValues(
            create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))

        self.system = System(
            "Non cloud system",
            usage_patterns=[self.usage_pattern]
        )

    def test_servers(self):
        self.assertEqual([self.server], self.system.servers)

    def test_storages(self):
        self.assertEqual([self.storage], self.system.storages)

    def test_networks(self):
        self.assertEqual([self.network], self.system.networks)
        
    def test_fabrication_footprints(self):
        expected_dict = {
            "Servers": {"server": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Storage": {"storage": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Devices": {"usage_pattern": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Network": {"networks": EmptyExplainableObject()}
        }
        
        self.assertDictEqual(expected_dict, self.system.fabrication_footprints)

    def test_energy_footprints(self):
        expected_dict = {
            "Servers": {"server": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Storage": {"storage": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Devices": {"usage_pattern": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Network": {"network": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))}
        }

        self.assertDictEqual(expected_dict, self.system.energy_footprints)

    def test_total_fabrication_footprints(self):
        expected_dict = {
            "Servers": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg)),
            "Storage": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg)),
            "Devices": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg)),
            "Network": EmptyExplainableObject()
        }
        self.assertDictEqual(expected_dict, self.system.total_fabrication_footprints)

    def test_total_energy_footprints(self):
        energy_footprints = self.system.total_energy_footprints
        expected_dict = {
            "Servers": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg)),
            "Storage": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg)),
            "Devices": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg)),
            "Network": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))
        }

        self.assertDictEqual(expected_dict, energy_footprints)

    def test_footprints_by_category_and_object(self):
        fab_footprints = {
            "Servers": {"server": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Storage": {"storage": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Devices": {"usage_pattern": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Network": {"networks": EmptyExplainableObject()}
        }

        energy_footprints = {
            "Servers": {"server": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Storage": {"storage": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Devices": {"usage_pattern": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))},
            "Network": {"network": SourceHourlyValues(
                create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.kg))}
        }

        with patch.object(System, "fabrication_footprints", new_callable=PropertyMock) as fab_mock,\
            patch.object(System, "energy_footprints", new_callable=PropertyMock) as en_mock:
            fab_mock.return_value = fab_footprints
            en_mock.return_value = energy_footprints
            self.system.plot_footprints_by_category_and_object(
                filename=os.path.join(root_dir, "footprints by category and object unit test.html"))


if __name__ == '__main__':
    unittest.main()
