from efootprint.constants.units import u
from efootprint.constants.sources import SourceValue, Sources, SourceObject
from efootprint.core.hardware.device_population import DevicePopulation

from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestDevicePopulation(TestCase):
    def setUp(self):
        country = MagicMock()
        country.average_carbon_intensity = SourceValue(100 * u.g / u.kWh)
        self.device1 = MagicMock()
        self.device1.lifespan = SourceValue(1 * u.year, Sources.HYPOTHESIS)
        self.device1.carbon_footprint_fabrication = SourceValue(10 * u.kg, Sources.BASE_ADEME_V19)
        self.device1.fraction_of_usage_time = SourceValue(2 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)
        self.device2 = MagicMock()
        self.device2.lifespan = SourceValue(1 * u.year, Sources.HYPOTHESIS)
        self.device2.carbon_footprint_fabrication = SourceValue(10 * u.kg, Sources.BASE_ADEME_V19)
        self.device2.fraction_of_usage_time = SourceValue(2 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)

        self.device_population = DevicePopulation(
            "Population", SourceValue(2000 * u.user), country, [self.device1, self.device2])
        self.device_population.dont_handle_input_updates = True
        self.usage_pattern = MagicMock()
        self.device_population.modeling_obj_containers = [self.usage_pattern]
        self.usage_pattern.user_journey = MagicMock()
        self.usage_pattern.user_journey_freq_per_user = SourceValue(10 * u.user_journey / (u.user * u.year))
        self.usage_pattern.time_intervals = SourceObject([[8, 16]], Sources.USER_INPUT)

    def test_user_journey_freq(self):
        self.device_population.update_user_journey_freq_per_up()
        self.assertEqual(
            20000 * u.user_journey / u.year, self.device_population.user_journey_freq_per_up[self.usage_pattern].value)

    def test_update_nb_user_journeys_in_parallel_during_usage(self):
        with patch.object(self.usage_pattern, "user_journey_freq", SourceValue(2 * u.user_journey / u.year)), \
                patch.object(self.usage_pattern.user_journey, "duration", SourceValue(1 * u.year / u.user_journey)), \
                patch.object(self.usage_pattern, "usage_time_fraction", SourceValue((12 / 24) * u.dimensionless)):
            self.device_population.update_nb_user_journeys_in_parallel_during_usage_per_up()
            self.assertEqual(
                4 * u.user_journey,
                self.device_population.nb_user_journeys_in_parallel_during_usage_per_up[self.usage_pattern].value)

    def test_update_nb_user_journeys_in_parallel_during_usage_round_up(self):
        with patch.object(self.usage_pattern, "user_journey_freq", SourceValue(2 * u.user_journey / u.year)), \
                patch.object(self.usage_pattern.user_journey, "duration",
                             SourceValue(1 * u.year / u.user_journey)), \
                patch.object(self.usage_pattern, "usage_time_fraction",
                             SourceValue((14 / 24) * u.dimensionless)):
            self.device_population.update_nb_user_journeys_in_parallel_during_usage_per_up()
            self.assertEqual(
                4 * u.user_journey,
                self.device_population.nb_user_journeys_in_parallel_during_usage_per_up[self.usage_pattern].value)

    def test_power(self):
        test_device1 = MagicMock()
        test_device1.power = SourceValue(5 * u.W)
        test_device2 = MagicMock()
        test_device2.power = SourceValue(10 * u.W)

        with patch.object(self.device_population, "_devices", new=[test_device1, test_device2]), \
             patch.object(self.device_population, "user_journey_freq_per_up",
                {self.usage_pattern: SourceValue(365.25 * u.user_journey / u.year)}), \
             patch.object(self.usage_pattern.user_journey, "duration", SourceValue(1 * u.hour / u.user_journey)):
            self.device_population.update_power()

        self.assertEqual(365.25 * 15 * 1e-3 * u.kWh / u.year, self.device_population.power.value)

    def test_energy_footprint(self):
        with patch.object(
                self.device_population, "user_journey_freq_per_up",
                {self.usage_pattern: SourceValue(365.25 * u.user_journey / u.year)}):
            self.device_population.power = SourceValue(1000 * u.kWh / u.year)
            self.device_population.update_energy_footprint()
            self.assertEqual(100 * u.kg / u.year, self.device_population.energy_footprint.value)

    def test_fabrication_footprint(self):
        with patch.object(
                self.device_population, "user_journey_freq_per_up",
                {self.usage_pattern: SourceValue(365.25 * u.user_journey / u.year)}),\
                patch.object(self.usage_pattern.user_journey, "duration", SourceValue(1 * u.hour / u.user_journey)):
            self.device_population.update_instances_fabrication_footprint()
            self.assertEqual(
                2 * 5 * u.kg / u.year, round(self.device_population.instances_fabrication_footprint.value, 2))
