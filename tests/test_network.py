from footprint_model.constants.countries import Countries
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.sources import Sources, SourceValue
from footprint_model.core.network import Network
from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.constants.units import u

from unittest import TestCase
from unittest.mock import MagicMock


class TestNetwork(TestCase):
    def setUp(self):
        self.network = Network(PhysicalElements.WIFI_NETWORK, SourceValue(0.05 * u("kWh/Go"), Sources.TRAFICOM_STUDY))

        self.usage_pattern = MagicMock()
        self.usage_pattern.user_journey.data_upload = ExplainableQuantity(100 * u.Mo / u.user_journey, 'data_upload')
        self.usage_pattern.user_journey.data_download = ExplainableQuantity(
            200 * u.Mo / u.user_journey, 'data_download')
        self.usage_pattern.user_journey_freq = ExplainableQuantity(250 * u.user_journey / u.year)
        self.network.usage_patterns = {self.usage_pattern}
        self.usage_pattern.device_population.country = Countries.FRANCE
        self.usage_pattern.user_journey.compute_network_consumption.return_value = ExplainableQuantity(
            50 * u.Wh/u.user_journey)

    def test_data_upload(self):
        data_upload = (
                self.usage_pattern.user_journey.data_upload * self.usage_pattern.user_journey_freq).to(u.To/u.year)
        self.assertEqual(data_upload, self.network.data_upload)

    def test_data_download(self):
        data_download = (self.usage_pattern.user_journey.data_download * self.usage_pattern.user_journey_freq).to(
            u.To/u.year)
        self.assertEqual(data_download, self.network.data_download)

    def test_power_footprint(self):
        uj_freq = self.usage_pattern.user_journey_freq
        carbon_intensity = self.usage_pattern.device_population.country.average_carbon_intensity
        network_consumption = self.usage_pattern.user_journey.compute_network_consumption(self.network)

        power_footprint = (uj_freq * carbon_intensity * network_consumption).to(u.kg / u.year)
        self.assertEqual(power_footprint, self.network.energy_footprint)
