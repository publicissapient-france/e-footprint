from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.countries import Countries
from efootprint.constants.sources import Sources
from efootprint.core.hardware.network import Network
from efootprint.constants.units import u

from unittest import TestCase
from unittest.mock import MagicMock


class TestNetwork(TestCase):
    def setUp(self):
        self.network = Network("Wifi network", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        self.network.dont_handle_input_updates = True

        self.usage_pattern = MagicMock()
        self.usage_pattern.user_journey.data_upload = SourceValue(100 * u.MB / u.user_journey, label='data_upload')
        self.usage_pattern.user_journey.data_download = SourceValue(
            200 * u.MB / u.user_journey, label='data_download')
        self.usage_pattern.user_journey_freq = SourceValue(250 * u.user_journey / u.year)
        self.network.modeling_obj_containers = {self.usage_pattern}
        self.usage_pattern.device_population.country = Countries.FRANCE()
        self.network_consumption = (
                self.network.bandwidth_energy_intensity * SourceValue(300 * u.MB / u.user_journey)
        ).to(u.Wh / u.user_journey)

    def test_update_data_upload(self):
        self.network.update_data_upload()
        data_upload = (
                self.usage_pattern.user_journey.data_upload * self.usage_pattern.user_journey_freq).to(u.TB/u.year)
        self.assertEqual(data_upload, self.network.data_upload)

    def test_update_data_download(self):
        self.network.update_data_download()
        data_download = (self.usage_pattern.user_journey.data_download * self.usage_pattern.user_journey_freq).to(
            u.TB/u.year)
        self.assertEqual(data_download, self.network.data_download)

    def test_update_energy_footprint(self):
        self.network.update_energy_footprint()
        uj_freq = self.usage_pattern.user_journey_freq
        carbon_intensity = self.usage_pattern.device_population.country.average_carbon_intensity
        network_consumption = self.network_consumption

        energy_footprint = (uj_freq * carbon_intensity * network_consumption).to(u.kg / u.year)
        self.assertEqual(energy_footprint.value, self.network.energy_footprint.value)
