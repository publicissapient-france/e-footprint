from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.constants.units import u

import unittest
from unittest.mock import MagicMock, patch


class TestUsagePattern(unittest.TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.server = MagicMock()
        self.service1 = MagicMock()
        self.service2 = MagicMock()

        user_journey = MagicMock()
        user_journey.duration = SourceValue(2.0 * u.min / u.user_journey, label="duration")
        user_journey.data_upload = SourceValue(2.0 * u.MB / u.user_journey, label="data_upload")
        user_journey.data_download = SourceValue(3.0 * u.MB / u.user_journey, label="data_download")

        user_journey.services = [self.service1, self.service2]
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

        network = MagicMock()

        self.usage_pattern = UsagePattern(
            "usage_pattern", user_journey, [self.device1, self.device2], network, country,
            user_journey_freq=SourceValue(365.25 * u.user_journey / u.year),
            time_intervals=SourceObject([[8, 16]], Sources.USER_DATA)
        )
        self.usage_pattern.dont_handle_input_updates = True

    def test_check_time_intervals_validity(self):
        self.usage_pattern.check_time_intervals_validity([[0, 5], [6, 10], [15, 20]])

    def test_invalid_start_time(self):
        with self.assertRaises(ValueError):
            self.usage_pattern.check_time_intervals_validity([[5, 3], [7, 10]])

    def test_interval_overlap(self):
        with self.assertRaises(ValueError):
            self.usage_pattern.check_time_intervals_validity([[0, 5], [4, 10]])

    def test_update_usage_time_fraction(self):
        hourly_usage = ExplainableHourlyUsage([1 * u.dimensionless] * 2 + [0 * u.dimensionless] * 22, "hourly usage")
        with patch.object(self.usage_pattern, "hourly_usage", hourly_usage):
            self.usage_pattern.update_usage_time_fraction()
            self.assertEqual((2 / 24) * u.dimensionless, self.usage_pattern.usage_time_fraction.value)

    def test_update_hourly_usage(self):
        with patch.object(self.usage_pattern, "time_intervals", SourceObject([[0, 5], [6, 10], [15, 20]])):
            self.usage_pattern.update_hourly_usage()

            for i in range(24):
                if 0 <= i < 5 or 6 <= i < 10 or 15 <= i < 20:
                    self.assertEqual(self.usage_pattern.hourly_usage.value[i], 1 * u.dimensionless)
                else:
                    self.assertEqual(self.usage_pattern.hourly_usage.value[i], 0 * u.dimensionless)

    def test_services(self):
        self.assertEqual([self.service1, self.service2], self.usage_pattern.services)
    
    def test_update_nb_user_journeys_in_parallel_during_usage(self):
        with patch.object(self.usage_pattern, "usage_time_fraction", SourceValue((12 / 24) * u.dimensionless)), \
                patch.object(self.usage_pattern.user_journey, "duration", SourceValue(12 * u.hour / u.user_journey)):
            self.usage_pattern.update_nb_user_journeys_in_parallel_during_usage()
            self.assertEqual(
                1 * u.user_journey,
                self.usage_pattern.nb_user_journeys_in_parallel_during_usage.value)

    def test_power(self):
        test_device1 = MagicMock()
        test_device1.power = SourceValue(5 * u.W)
        test_device2 = MagicMock()
        test_device2.power = SourceValue(10 * u.W)

        with patch.object(self.usage_pattern, "devices", new=[test_device1, test_device2]), \
             patch.object(self.usage_pattern, "user_journey_freq",
                          SourceValue(365.25 * u.user_journey / u.year)), \
             patch.object(self.usage_pattern.user_journey, "duration", SourceValue(1 * u.hour / u.user_journey)):
            self.usage_pattern.update_devices_power()

        self.assertEqual(365.25 * 15 * 1e-3 * u.kWh / u.year, self.usage_pattern.devices_power.value)

    def test_devices_energy_footprint(self):
        with patch.object(self.usage_pattern, "devices_power", SourceValue(1000 * u.kWh / u.year)):
            self.usage_pattern.update_devices_energy_footprint()
            self.assertEqual(100 * u.kg / u.year, self.usage_pattern.devices_energy_footprint.value)

    def test_devices_fabrication_footprint(self):
        with patch.object(
                self.usage_pattern, "user_journey_freq", SourceValue(365.25 * u.user_journey / u.year)),\
                patch.object(self.usage_pattern.user_journey, "duration", SourceValue(1 * u.hour / u.user_journey)):
            self.usage_pattern.update_devices_fabrication_footprint()
            self.assertEqual(
                2 * 5 * u.kg / u.year, round(self.usage_pattern.devices_fabrication_footprint.value, 2))
            

if __name__ == '__main__':
    unittest.main()
