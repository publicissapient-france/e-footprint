import unittest
from unittest.mock import MagicMock, patch

from footprint_model.constants.countries import Countries
from footprint_model.core.usage.time_intervals import TimeIntervals
from footprint_model.core.usage.usage_pattern import UsagePattern
from footprint_model.constants.units import u
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity


class TestUsagePattern(unittest.TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.server = MagicMock()
        self.service1 = MagicMock()
        self.service2 = MagicMock()

        user_journey = MagicMock()
        user_journey.duration = ExplainableQuantity(2.0 * u.min / u.user_journey, "duration")
        user_journey.data_upload = ExplainableQuantity(2.0 * u.Mo / u.user_journey, "data_upload")
        user_journey.data_download = ExplainableQuantity(3.0 * u.Mo / u.user_journey, "data_download")

        user_journey.services = {self.service1, self.service2}
        population = MagicMock()
        population.nb_devices = ExplainableQuantity(10000 * u.user, "population")
        population.country = Countries.FRANCE

        network = MagicMock()

        self.up_time_intervals = [[8, 16]]
        self.usage_pattern = UsagePattern(
            "usage_pattern", user_journey, population, network,
            user_journey_freq_per_user=10 * u.user_journey / (u.user * u.year), time_intervals=self.up_time_intervals
        )

        self.expected_nb_user_journeys_per_year = 100000 * u.user_journey / u.year
        self.expected_nb_uj_in_parallel = ExplainableQuantity(2 * u.user_journey, "number of uj in parallel")

    def test_usage_time_fraction(self):
        self.assertEqual(self.usage_pattern.usage_time_fraction.value, (8 / 24) * u.dimensionless)

    def test_update_usage_time_fraction(self):
        intervals = TimeIntervals(
            "usage time intervals", [[8, 10]], self.usage_pattern.device_population.country.timezone)
        with patch.object(self.usage_pattern, "time_intervals", intervals):
            self.usage_pattern.update_usage_time_fraction()
            self.assertEqual(self.usage_pattern.usage_time_fraction.value, (2 / 24) * u.dimensionless)

    def test_non_usage_time_fraction(self):
        self.assertEqual(self.usage_pattern.non_usage_time_fraction.value, (1 - 8/24) * u.dimensionless)

    def test_user_journey_setter(self):
        test_uj = MagicMock()
        old_uj = self.usage_pattern._user_journey
        self.usage_pattern.user_journey = test_uj

        old_uj.unlink_usage_pattern.assert_called_once_with(self.usage_pattern)
        test_uj.link_usage_pattern.assert_called_once_with(self.usage_pattern)

    def test_device_population_setter(self):
        test_dp = MagicMock()
        old_dp = self.usage_pattern._device_population
        self.usage_pattern.device_population = test_dp

        old_dp.unlink_usage_pattern.assert_called_once_with(self.usage_pattern)
        test_dp.link_usage_pattern.assert_called_once_with(self.usage_pattern)

    def test_network_setter(self):
        test_network = MagicMock()
        old_network = self.usage_pattern._network
        self.usage_pattern.network = test_network

        old_network.unlink_usage_pattern.assert_called_once_with(self.usage_pattern)
        test_network.link_usage_pattern.assert_called_once_with(self.usage_pattern)

    def test_services(self):
        self.assertEqual({self.service1, self.service2}, self.usage_pattern.services)

    def test_user_journey_freq(self):
        self.assertEqual(self.expected_nb_user_journeys_per_year, self.usage_pattern.user_journey_freq.value)

    def test_update_user_journey_freq(self):
        nb_devices = ExplainableQuantity(2 * u.user, "population")
        uj_freq_per_user = ExplainableQuantity(10 * u.user_journey / (u.user * u.year))

        expected_uj_freq = nb_devices * uj_freq_per_user
        with patch.object(self.usage_pattern.device_population, "nb_devices", new=nb_devices), \
                patch.object(self.usage_pattern, "user_journey_freq_per_user", new=uj_freq_per_user):
            self.usage_pattern.update_user_journey_freq()
            self.assertEqual(expected_uj_freq.value, self.usage_pattern.user_journey_freq.value)

    def test_nb_user_journeys_in_parallel_during_usage(self):
        actual_nb_user_journeys_in_parallel_during_usage = self.usage_pattern.nb_user_journeys_in_parallel_during_usage

        self.assertAlmostEqual(self.expected_nb_uj_in_parallel.value,
                               actual_nb_user_journeys_in_parallel_during_usage.value)

    def test_update_nb_user_journeys_in_parallel_during_usage(self):
        expected_nb_uj_in_parallel = ExplainableQuantity(4 * u.user_journey)
        with patch.object(self.usage_pattern, "user_journey_freq", ExplainableQuantity(2 * u.user_journey / u.year)), \
                patch.object(self.usage_pattern.user_journey, "duration", ExplainableQuantity(1 * u.year / u.user_journey)), \
                patch.object(self.usage_pattern, "usage_time_fraction", ExplainableQuantity((12 / 24) * u.dimensionless)):
            self.usage_pattern.update_nb_user_journeys_in_parallel_during_usage()
            self.assertEqual(expected_nb_uj_in_parallel.value, self.usage_pattern.nb_user_journeys_in_parallel_during_usage.value)

    def test_update_nb_user_journeys_in_parallel_during_usage_round_up(self):
        expected_nb_uj_in_parallel = ExplainableQuantity(4 * u.user_journey)
        with patch.object(self.usage_pattern, "user_journey_freq", ExplainableQuantity(2 * u.user_journey / u.year)), \
                patch.object(self.usage_pattern.user_journey, "duration",
                             ExplainableQuantity(1 * u.year / u.user_journey)), \
                patch.object(self.usage_pattern, "usage_time_fraction",
                             ExplainableQuantity((14 / 24) * u.dimensionless)):
            self.usage_pattern.update_nb_user_journeys_in_parallel_during_usage()
            self.assertEqual(expected_nb_uj_in_parallel.value,
                             self.usage_pattern.nb_user_journeys_in_parallel_during_usage.value)


if __name__ == '__main__':
    unittest.main()
