from unittest import TestCase
from unittest.mock import MagicMock, patch
from copy import deepcopy

from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.units import u
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.core.device_population import DevicePopulation, Device


class TestDevicePopulation(TestCase):
    def setUp(self):
        country = MagicMock()
        country.average_carbon_intensity = ExplainableQuantity(100 * u.g / u.kWh)
        self.device1 = MagicMock()
        self.device1.lifespan = SourceValue(1 * u.year, Sources.HYPOTHESIS)
        self.device1.carbon_footprint_fabrication = SourceValue(10 * u.g, Sources.BASE_ADEME_V19)
        self.device1.fraction_of_usage_time = SourceValue(2 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)
        self.device2 = MagicMock()
        self.device2.lifespan = SourceValue(1 * u.year, Sources.HYPOTHESIS)
        self.device2.carbon_footprint_fabrication = SourceValue(10 * u.g, Sources.BASE_ADEME_V19)
        self.device2.fraction_of_usage_time = SourceValue(2 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)

        self.device_population = DevicePopulation("Population", 2000, country, [self.device1, self.device2])
        self.usage_pattern = MagicMock()
        self.device_population.usage_patterns = {self.usage_pattern}
        self.usage_pattern.user_journey_freq = ExplainableQuantity(250 * u.user_journey / u.year)
        self.usage_pattern.user_journey.duration = ExplainableQuantity(1 * u.hour / u.user_journey)

    def test_power(self):
        test_device_population = deepcopy(self.device_population)
        test_device1 = MagicMock()
        test_device1.power = ExplainableQuantity(5 * u.W)
        test_device2 = MagicMock()
        test_device2.power = ExplainableQuantity(10 * u.W)

        test_device_population.devices = [test_device1, test_device2]
        test_device_population.update_power()

        self.assertEqual(250 * 15 * 1e-3 * u.kWh / u.year, test_device_population.power.value)

    def test_energy_footprint(self):
        test_device_population = deepcopy(self.device_population)
        test_device_population.power = ExplainableQuantity(1000 * u.kWh / u.year)
        test_device_population.update_energy_footprint()
        self.assertEqual(100 * u.kg / u.year, test_device_population.energy_footprint.value)

    def test_fabrication_footprint(self):
        test_device_population = deepcopy(self.device_population)
        test_device_population.update_fabrication_footprint()
        self.assertEqual(2 * 3.42 * 1e-3 * u.kg / u.year, round(test_device_population.fabrication_footprint.value, 5))

