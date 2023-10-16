import unittest
from unittest.mock import MagicMock

from footprint_model.core.user_journey import UserJourney
from footprint_model.core.usage_pattern import Population, InfraNeed, UsagePattern
from footprint_model.constants.physical_elements import Device, Network, PhysicalElements, Devices
from footprint_model.constants.units import u
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from tests.test_utils import extract_values_from_dict


class TestUsagePattern(unittest.TestCase):
    def setUp(self):
        user_journey = MagicMock(spec=UserJourney)
        user_journey.duration = ExplainableQuantity(2.0 * u.min / u.user_journey, "duration")
        user_journey.data_upload = ExplainableQuantity(2.0 * u.Mo / u.user_journey, "data_upload")
        user_journey.data_download = ExplainableQuantity(3.0 * u.Mo / u.user_journey, "data_download")
        user_journey.compute_device_consumption.return_value = ExplainableQuantity(
            10.0 * u.J / u.user_journey, "device_consumption")
        user_journey.compute_fabrication_footprint.return_value = ExplainableQuantity(
            0.5 * u.g / u.user_journey, "fabrication_footprint")
        user_journey.compute_network_consumption.return_value = ExplainableQuantity(
            7.0 * u.J / u.user_journey, "network_consumption")

        population = MagicMock(spec=Population)
        population.nb_users = ExplainableQuantity(10000 * u.user, "population")

        self.usage_pattern = UsagePattern(
            "usage_pattern", user_journey, population, frac_smartphone=0.5, frac_mobile_network_for_smartphones=0.6,
            user_journey_freq_per_user=10 * u.user_journey / (u.user * u.year), usage_time_fraction=8 * u.hour / u.day
        )

        self.expected_nb_user_journeys_per_year = 100000 * u.user_journey / u.year

    def test_frac_laptop(self):
        self.assertEqual(self.usage_pattern.frac_laptop.value, 0.5)

    def test_wifi_usage_fraction(self):
        self.assertAlmostEqual(self.usage_pattern.wifi_usage_fraction.value, 0.7)

    def test_nb_user_journeys_per_year(self):
        self.assertEqual(self.usage_pattern.user_journeys_freq.value, self.expected_nb_user_journeys_per_year)

    def test_compute_device_consumption(self):
        device = MagicMock(spec=Device)
        device.name = "device name"
        result = self.usage_pattern.compute_device_consumption(
            device, ExplainableQuantity(0.6 * u.dimensionless, "frac_smartphones"))
        expected_result = (0.6 * self.expected_nb_user_journeys_per_year * 10.0 * u.J / u.user_journey)
        self.assertEqual(result.value, expected_result.to(u.kWh / u.year))

    def test_compute_device_fabrication_footprint(self):
        device = MagicMock(spec=Device)
        device.name = "device name"
        result = self.usage_pattern.compute_device_fabrication_footprint(
            device, ExplainableQuantity(0.6 * u.dimensionless, "frac_smartphones"))
        expected_result = 0.6 * self.expected_nb_user_journeys_per_year * 0.5 * u.g / u.user_journey
        self.assertEqual(result.value, expected_result.to(u.kg / u.year))

    def test_compute_network_consumption(self):
        network = MagicMock(spec=Network)
        network.name = "network name"
        result = self.usage_pattern.compute_network_consumption(
            network, ExplainableQuantity(0.6 * u.dimensionless, "frac_smartphones"))
        expected_result = 0.6 * self.expected_nb_user_journeys_per_year * 7.0 * u.J / u.user_journey
        self.assertEqual(result.value, expected_result.to(u.kWh / u.year))

    def test_compute_energy_consumption(self):
        energy_consumption = self.usage_pattern.compute_energy_consumption()
        expected_energy_consumption = {
            PhysicalElements.SMARTPHONE: (
                    0.5 * self.expected_nb_user_journeys_per_year * 10.0 * u.J / u.user_journey).to(u.kWh / u.year),
            PhysicalElements.LAPTOP: (
                    0.5 * self.expected_nb_user_journeys_per_year * 10.0 * u.J / u.user_journey).to(u.kWh / u.year),
            PhysicalElements.BOX: (
                    0.7 * self.expected_nb_user_journeys_per_year * 10.0 * u.J / u.user_journey).to(u.kWh / u.year),
            PhysicalElements.SCREEN: (
                    0.5 * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN.value
                    * self.expected_nb_user_journeys_per_year * 10.0 * u.J / u.user_journey).to(u.kWh / u.year),
            PhysicalElements.MOBILE_NETWORK: (
                    0.3 * self.expected_nb_user_journeys_per_year * 7.0 * u.J / u.user_journey).to(u.kWh / u.year),
            PhysicalElements.WIFI_NETWORK: (
                    0.7 * self.expected_nb_user_journeys_per_year * 7.0 * u.J / u.user_journey).to(u.kWh / u.year),
        }
        self.assertDictEqual(extract_values_from_dict(energy_consumption), expected_energy_consumption)

    def test_compute_fabrication_emissions(self):
        fabrication_emissions = self.usage_pattern.compute_fabrication_emissions()
        expected_fabrication_emissions = {
            PhysicalElements.SMARTPHONE: (
                    0.5 * self.expected_nb_user_journeys_per_year * 0.5 * u.g / u.user_journey).to(u.kg / u.year),
            PhysicalElements.LAPTOP: (
                    0.5 * self.expected_nb_user_journeys_per_year * 0.5 * u.g / u.user_journey).to(u.kg / u.year),
            PhysicalElements.BOX: (
                    0.7 * self.expected_nb_user_journeys_per_year * 0.5 * u.g / u.user_journey).to(u.kg / u.year),
            PhysicalElements.SCREEN: (
                    0.5 * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN.value
                    * self.expected_nb_user_journeys_per_year * 0.5 * u.g / u.user_journey).to(u.kg / u.year),
        }

        self.assertDictEqual(extract_values_from_dict(fabrication_emissions), expected_fabrication_emissions)

    def test_estimated_infra_need(self):
        infra_need = self.usage_pattern.estimated_infra_need
        self.assertEqual(round(infra_need.ram.value, 3), 0.029 * u.Go)
        self.assertEqual(round(infra_need.storage.value, 1), 0.2 * u.To / u.year)

    def test_data_upload(self):
        data_upload = self.usage_pattern.data_upload
        expected_data_upload = 0.2 * u.To / u.year
        self.assertEqual(round(data_upload.value, 1), expected_data_upload)

    def test_data_download(self):
        data_download = self.usage_pattern.data_download
        expected_data_download = 0.3 * u.To / u.year
        self.assertEqual(round(data_download.value, 1), expected_data_download)


if __name__ == '__main__':
    unittest.main()
