from unittest import TestCase
from unittest.mock import MagicMock
import unittest
from copy import deepcopy

from footprint_model.core.system import System
from footprint_model.core.usage_pattern import Population, UsagePattern
from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.constants.units import u
from footprint_model.constants.countries import Countries
from footprint_model.utils.tools import round_dict
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from tests.test_utils import extract_values_from_dict


class TestSystem(TestCase):
    def setUp(self):
        self.usage_pattern = MagicMock(spec=UsagePattern)
        self.usage_pattern.estimated_infra_need.ram = ExplainableQuantity(100 * u.Go, "ram need")
        self.usage_pattern.estimated_infra_need.storage = ExplainableQuantity(10.1 * u.To / u.year, "infra need")
        self.usage_pattern.usage_time_fraction = ExplainableQuantity(8 * u.hour / u.day, "usage_time_fraction")
        self.usage_pattern.non_usage_time_fraction = ExplainableQuantity(16 * u.hour / u.day, "non_usage_time_fraction")
        self.usage_pattern.population = MagicMock(spec=Population)
        self.usage_pattern.name = "usage_pattern"
        self.usage_pattern.population.country = Countries.FRANCE
        self.usage_pattern.compute_energy_consumption.return_value = {}
        self.usage_pattern.compute_fabrication_emissions.return_value = {}

        self.system = System(
            "System",
            usage_patterns=[self.usage_pattern],
            data_replication_factor=2,
            data_storage_duration=3 * u.year,
            cloud=True
        )

        self.non_cloud_system = System(
            "Non cloud system",
            usage_patterns=[self.usage_pattern],
            data_replication_factor=2,
            data_storage_duration=3 * u.year,
            cloud=False
        )

    def test_nb_of_servers_required__raw(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.system.nb_of_servers_required), 2),
            {self.usage_pattern: 0.87 * u.dimensionless})

    def test_nb_of_servers_required__raw__non_cloud(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.non_cloud_system.nb_of_servers_required), 2),
            {self.usage_pattern: 2 * u.dimensionless})

    def test_storage_required(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.system.storage_required), 1), {self.usage_pattern: 60.6 * u.To})

    def test_compute_servers_consumption(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.system.compute_servers_consumption()), 1),
            {self.usage_pattern: 1521.9 * u.kWh / u.year})

    def test_compute_servers_consumption_non_cloud(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.non_cloud_system.compute_servers_consumption()), 1),
            {self.usage_pattern: 6311.5 * u.kWh / u.year})

    def test_compute_servers_fabrication_footprint(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.system.compute_servers_fabrication_footprint()), 1),
            {self.usage_pattern: 48.2 * u.kg / u.year})

    def test_compute_storage_consumption(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.system.compute_storage_consumption()), 1),
            {self.usage_pattern: 276.2 * u.kWh / u.year})

    def test_compute_storage_fabrication_footprint(self):
        self.assertDictEqual(
            round_dict(extract_values_from_dict(self.system.compute_storage_fabrication_footprint()), 1),
            {self.usage_pattern: 1616.0 * u.kg / u.year})

    def test_compute_energy_consumption(self):
        energy_consumption = extract_values_from_dict(self.system.compute_energy_consumption(), imbricated_dict=True)
        expected_dict = {
            self.usage_pattern: {PhysicalElements.SERVER: 1521.9 * u.kWh / u.year,
                                 PhysicalElements.SSD: 276.2 * u.kWh / u.year}
                         }
        self.assertDictEqual(energy_consumption, expected_dict)

    def test_compute_fabrication_emissions(self):
        fabrication_emissions = extract_values_from_dict(
            self.system.compute_fabrication_emissions(), imbricated_dict=True)
        expected_dict = {
            self.usage_pattern: {PhysicalElements.SERVER: 48.2 * u.kg / u.year,
                                 PhysicalElements.SSD: 1616.0 * u.kg / u.year}
                         }
        self.assertDictEqual(fabrication_emissions, expected_dict)

    def test_compute_energy_emissions(self):
        energy_emissions = extract_values_from_dict(self.system.compute_energy_emissions(), imbricated_dict=True)
        expected_dict = {
            self.usage_pattern: {PhysicalElements.SERVER: 129.4 * u.kg / u.year,
                                 PhysicalElements.SSD: 23.5 * u.kg / u.year}
                         }
        self.assertDictEqual(energy_emissions, expected_dict)

    def test_fabrication_emissions_with_multiple_usage_patterns(self):
        usage_pattern2 = deepcopy(self.usage_pattern)
        usage_pattern2.name = "usage_pattern2"
        usage_pattern2.estimated_infra_need.ram = ExplainableQuantity(200 * u.Go, "infra need up 2")

        system2 = deepcopy(self.system)
        system2.usage_patterns = [self.usage_pattern, usage_pattern2]

        fabrication_emissions = extract_values_from_dict(system2.compute_fabrication_emissions(), imbricated_dict=True)
        expected_dict = {
            self.usage_pattern: {
                PhysicalElements.SERVER: 48.2 * u.kg / u.year, PhysicalElements.SSD: 1616.0 * u.kg / u.year},
            usage_pattern2: {
                PhysicalElements.SERVER: 96.5 * u.kg / u.year, PhysicalElements.SSD: 1616.0 * u.kg / u.year}
                         }

        self.assertDictEqual(fabrication_emissions, expected_dict)

    def test_system_created_with_2_usage_patterns_with_same_name_should_raise_error(self):
        usage_pattern_dcopy = deepcopy(self.usage_pattern)

        with self.assertRaises(ValueError):
            System("System",
                [usage_pattern_dcopy, self.usage_pattern], data_replication_factor=2, data_storage_duration=3 * u.year,
                cloud=True)


if __name__ == '__main__':
    unittest.main()
