from unittest import TestCase
from unittest.mock import MagicMock, patch

from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.units import u
from footprint_model.core.device_population import DevicePopulation

DEVICE_POP_MODULE = "footprint_model.core.device_population.DevicePopulation"


class TestDevicePopulation(TestCase):
    def setUp(self):
        country = MagicMock()
        country.average_carbon_intensity = ExplainableQuantity(100 * u.g / u.kWh)
        self.device1 = MagicMock()
        self.device2 = MagicMock()
        self.device_population = DevicePopulation("Population", 2000, country, [self.device1, self.device2])
        self.usage_pattern = MagicMock()
        self.device_population.usage_patterns = {self.usage_pattern}
        self.usage_pattern.user_journey_freq = ExplainableQuantity(250 * u.user_journey / u.year)

    def test_power(self):
        device_consumptions = {
            self.device1: ExplainableQuantity(5 * u.Wh / u.user_journey),
            self.device2: ExplainableQuantity(10 * u.Wh / u.user_journey),
        }

        def compute_device_consumption_side_effect(device):
            return device_consumptions[device]

        self.usage_pattern.user_journey.compute_device_consumption.side_effect = compute_device_consumption_side_effect

        self.assertEqual(250 * 15 * 1e-3 * u.kWh / u.year, self.device_population.power.value)

    def test_power_footprint(self):
        with patch(f"{DEVICE_POP_MODULE}.power", new=ExplainableQuantity(1000 * u.kWh / u.year)):
            self.assertEqual(100 * u.kg / u.year, self.device_population.energy_footprint.value)

    def test_fabrication_footprint(self):
        device_fabrication_footprints = {
            self.device1: ExplainableQuantity(5 * u.g / u.user_journey),
            self.device2: ExplainableQuantity(10 * u.g / u.user_journey),
        }

        def compute_device_fabrication_footprint_side_effect(device):
            return device_fabrication_footprints[device]

        self.usage_pattern.user_journey.compute_fabrication_footprint.side_effect = \
            compute_device_fabrication_footprint_side_effect

        self.assertEqual(250 * 15 * 1e-3 * u.kg / u.year, self.device_population.fabrication_footprint.value)

