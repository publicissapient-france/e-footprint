import unittest
from unittest.mock import MagicMock
from copy import deepcopy

from footprint_model.constants.countries import Countries
from footprint_model.core.usage_pattern import UsagePattern
from footprint_model.core.infra_need import InfraNeed
from footprint_model.constants.units import u
from footprint_model.constants.explainable_quantities import ExplainableQuantity


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

        user_journey.ram_needed_per_service = {
            self.service1: ExplainableQuantity(5 * u.Mo / u.user_journey, "RAM for service1"),
            self.service2: ExplainableQuantity(10 * u.Mo / u.user_journey, "RAM for service2")}
        user_journey.storage_need_per_service = {
            self.service1: ExplainableQuantity(500 * u.Go / u.user_journey, "Storage for service1"),
            self.service2: ExplainableQuantity(1000 * u.Go / u.user_journey, "Storage for service2")}
        user_journey.cpu_need_per_service = {
            self.service1: ExplainableQuantity(0.5 * u.core / u.user_journey, "CPU for service1"),
            self.service2: ExplainableQuantity(1 * u.core / u.user_journey, "CPU for service2")}

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

    def test_non_usage_time_fraction(self):
        self.assertEqual(self.usage_pattern.non_usage_time_fraction.value, (1 - 8/24) * u.dimensionless)

    def test_check_time_intervals_validity(self):
        result = self.usage_pattern._check_time_intervals_validity(self.up_time_intervals)
        self.assertIsNone(result)  # Assert that no exception is raised

    def test_invalid_start_time(self):
        self.up_time_intervals = [[16, 8]]  # Update with invalid time interval
        with self.assertRaises(ValueError):
            self.usage_pattern._check_time_intervals_validity(self.up_time_intervals)

    def test_interval_overlap(self):
        self.up_time_intervals = [[8, 12], [10, 14]]  # Update with overlapping time intervals
        with self.assertRaises(ValueError):
            self.usage_pattern._check_time_intervals_validity(self.up_time_intervals)

    def test_user_journey_setter(self):
        test_uj = MagicMock()
        test_up = deepcopy(self.usage_pattern)
        old_uj = test_up._user_journey
        test_up.user_journey = test_uj

        old_uj.unlink_usage_pattern.assert_called_once_with(test_up)
        test_uj.link_usage_pattern.assert_called_once_with(test_up)

    def test_device_population_setter(self):
        test_dp = MagicMock()
        test_up = deepcopy(self.usage_pattern)
        old_dp = test_up._device_population
        test_up.device_population = test_dp

        old_dp.unlink_usage_pattern.assert_called_once_with(test_up)
        test_dp.link_usage_pattern.assert_called_once_with(test_up)

    def test_network_setter(self):
        test_network = MagicMock()
        test_up = deepcopy(self.usage_pattern)
        old_network = test_up._network
        test_up.network = test_network

        old_network.unlink_usage_pattern.assert_called_once_with(test_up)
        test_network.link_usage_pattern.assert_called_once_with(test_up)

    def test_services(self):
        self.assertEqual({self.service1, self.service2}, self.usage_pattern.services)

    def test_nb_user_journeys_per_year(self):
        self.assertEqual(self.expected_nb_user_journeys_per_year, self.usage_pattern.user_journey_freq.value)

    def test_nb_user_journeys_in_parallel_during_usage(self):
        actual_nb_user_journeys_in_parallel_during_usage = self.usage_pattern.nb_user_journeys_in_parallel_during_usage

        self.assertAlmostEqual(self.expected_nb_uj_in_parallel.value,
                               actual_nb_user_journeys_in_parallel_during_usage.value)

    def test_estimated_infra_need(self):
        # Initializing empty lists of 24 ExplainableQuantity instances for each attribute
        ram_needed_1 = [ExplainableQuantity(0 * u.Mo)] * 24
        storage_needed_1 = (self.usage_pattern.user_journey.storage_need_per_service[self.service1]
                            * self.usage_pattern.user_journey_freq).to(u.To / u.year)
        cpu_needed_1 = [ExplainableQuantity(0 * u.core)] * 24
        ram_needed_2 = [ExplainableQuantity(0 * u.Mo)] * 24
        storage_needed_2 = (self.usage_pattern.user_journey.storage_need_per_service[self.service2]
                            * self.usage_pattern.user_journey_freq).to(u.To / u.year)
        cpu_needed_2 = [ExplainableQuantity(0 * u.core)] * 24

        for hour in range(self.up_time_intervals[0][0], self.up_time_intervals[0][1]):
            ram_needed_1[hour - 2] = self.usage_pattern.user_journey.ram_needed_per_service[
                                     self.service1] * self.expected_nb_uj_in_parallel
            cpu_needed_1[hour - 2] = self.usage_pattern.user_journey.cpu_need_per_service[
                                     self.service1] * self.expected_nb_uj_in_parallel

            ram_needed_2[hour - 2] = self.usage_pattern.user_journey.ram_needed_per_service[
                                     self.service2] * self.expected_nb_uj_in_parallel
            cpu_needed_2[hour - 2] = self.usage_pattern.user_journey.cpu_need_per_service[
                                     self.service2] * self.expected_nb_uj_in_parallel

        # Creating expected_infra_needs
        expected_infra_needs = {
            self.service1: InfraNeed(
                ram=ram_needed_1,
                storage=storage_needed_1,
                cpu=cpu_needed_1
            ),
            self.service2: InfraNeed(
                ram=ram_needed_2,
                storage=storage_needed_2,
                cpu=cpu_needed_2
            )
        }

        assert expected_infra_needs == self.usage_pattern.estimated_infra_need


if __name__ == '__main__':
    unittest.main()
