import unittest
from unittest.mock import MagicMock

from footprint_model.core.system import UsagePattern, UserJourney, Population, InfraNeed
from footprint_model.constants.physical_elements import Device, Network, PhysicalElements, Devices
from footprint_model.constants.units import u


class TestUsagePattern(unittest.TestCase):
    def setUp(self):
        user_journey = MagicMock(spec=UserJourney)
        user_journey.duration = 2.0 * u.min
        user_journey.data_upload = 2.0 * u.Mo
        user_journey.data_download = 3.0 * u.Mo
        user_journey.compute_device_consumption.return_value = 10.0 * u.J
        user_journey.compute_fabrication_footprint.return_value = 0.5 * u.g
        user_journey.compute_network_consumption.return_value = 7.0 * u.J

        population = MagicMock(spec=Population)
        population.nb_users = 10000

        self.usage_pattern = UsagePattern(
            user_journey, population, frac_smartphone=0.5, frac_mobile_network_for_smartphones=0.6,
            nb_visits_per_user_per_year=10, daily_usage_window=8 * u.hour
        )

        self.expected_nb_visits_per_year = 100000

    def test_frac_laptop(self):
        self.assertEqual(self.usage_pattern.frac_laptop, 0.5)

    def test_wifi_usage_fraction(self):
        self.assertAlmostEqual(self.usage_pattern.wifi_usage_fraction, 0.7)

    def test_nb_visits_per_year(self):
        self.assertEqual(self.usage_pattern.nb_visits_per_year, self.expected_nb_visits_per_year)

    def test_compute_device_consumption(self):
        device = MagicMock(spec=Device)
        result = self.usage_pattern.compute_device_consumption(device, 0.6)
        self.assertEqual(result, 0.6 * self.expected_nb_visits_per_year * 10.0 * u.J)

    def test_compute_device_fabrication_footprint(self):
        device = MagicMock(spec=Device)
        result = self.usage_pattern.compute_device_fabrication_footprint(device, 0.6)
        self.assertEqual(result, 0.6 * self.expected_nb_visits_per_year * 0.5 * u.g)

    def test_compute_network_consumption(self):
        network = MagicMock(spec=Network)
        result = self.usage_pattern.compute_network_consumption(network, 0.6)
        self.assertEqual(result, 0.6 * self.expected_nb_visits_per_year * 7.0 * u.J)

    def test_compute_energy_consumption(self):
        energy_consumption = self.usage_pattern.compute_energy_consumption()
        expected_energy_consumption = {
            PhysicalElements.SMARTPHONE: (0.5 * self.expected_nb_visits_per_year * 10.0 * u.J).to(u.kWh),
            PhysicalElements.LAPTOP: (0.5 * self.expected_nb_visits_per_year * 10.0 * u.J).to(u.kWh),
            PhysicalElements.BOX: (0.7 * self.expected_nb_visits_per_year * 10.0 * u.J).to(u.kWh),
            PhysicalElements.SCREEN: (0.5 * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN *
                                     self.expected_nb_visits_per_year * 10.0 * u.J).to(u.kWh),
            PhysicalElements.MOBILE_NETWORK: (0.3 * self.expected_nb_visits_per_year * 7.0 * u.J).to(u.kWh),
            PhysicalElements.WIFI_NETWORK: (0.7 * self.expected_nb_visits_per_year * 7.0 * u.J).to(u.kWh),
        }
        self.assertDictEqual(energy_consumption, expected_energy_consumption)

    def test_compute_fabrication_emissions(self):
        fabrication_emissions = self.usage_pattern.compute_fabrication_emissions()
        expected_fabrication_emissions = {
            PhysicalElements.SMARTPHONE: (0.5 * self.expected_nb_visits_per_year * 0.5 * u.g).to(u.kg),
            PhysicalElements.LAPTOP: (0.5 * self.expected_nb_visits_per_year * 0.5 * u.g).to(u.kg),
            PhysicalElements.BOX: (0.7 * self.expected_nb_visits_per_year * 0.5 * u.g).to(u.kg),
            PhysicalElements.SCREEN: (0.5 * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN
                                      * self.expected_nb_visits_per_year * 0.5 * u.g).to(u.kg),
        }

        self.assertDictEqual(fabrication_emissions, expected_fabrication_emissions)

    def test_estimated_infra_need(self):
        infra_need = self.usage_pattern.estimated_infra_need
        expected_infra_need = InfraNeed(0.029 * u.Go, 0.2 * u.To)
        self.assertEqual(round(infra_need.ram, 3), expected_infra_need.ram)
        self.assertEqual(round(infra_need.storage, 1), expected_infra_need.storage)

    def test_data_upload(self):
        data_upload = self.usage_pattern.data_upload
        expected_data_upload = 0.2 * u.To
        self.assertEqual(round(data_upload, 1), expected_data_upload)

    def test_data_download(self):
        data_download = self.usage_pattern.data_download
        expected_data_download = 0.3 * u.To
        self.assertEqual(round(data_download, 1), expected_data_download)


if __name__ == '__main__':
    unittest.main()
