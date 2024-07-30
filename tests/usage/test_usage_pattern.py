import unittest
from unittest.mock import MagicMock, patch
from datetime import timedelta

from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.builders.time_builders import create_random_hourly_usage_df, create_hourly_usage_df_from_list
from efootprint.constants.units import u


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
            hourly_user_journey_starts=SourceHourlyValues(create_random_hourly_usage_df())
        )
        self.usage_pattern.dont_handle_input_updates = True

    def test_services(self):
        self.assertEqual([self.service1, self.service2], self.usage_pattern.services)

    def test_devices_energy(self):
        test_device1 = MagicMock()
        test_device1.power = SourceValue(5 * u.W)
        test_device2 = MagicMock()
        test_device2.power = SourceValue(10 * u.W)
        nb_uj_in_parallel = [10, 20, 30]

        with patch.object(self.usage_pattern, "devices", new=[test_device1, test_device2]), \
             patch.object(self.usage_pattern, "nb_user_journeys_in_parallel",
                          SourceHourlyValues(create_hourly_usage_df_from_list(nb_uj_in_parallel))):
            self.usage_pattern.update_devices_energy()

            self.assertEqual(u.kWh, self.usage_pattern.devices_energy.unit)
            self.assertEqual([0.15, 0.3, 0.45], self.usage_pattern.devices_energy.value_as_float_list)

    def test_devices_energy_footprint(self):
        with patch.object(self.usage_pattern, "devices_energy",
                          SourceHourlyValues(create_hourly_usage_df_from_list([10, 20, 30], pint_unit=u.kWh))):
            self.usage_pattern.update_devices_energy_footprint()
            self.assertEqual(u.kg, self.usage_pattern.devices_energy_footprint.unit)
            self.assertEqual([1, 2, 3], self.usage_pattern.devices_energy_footprint.value_as_float_list)

    def test_devices_fabrication_footprint(self):
        device1 = MagicMock()
        device1.lifespan = SourceValue(1 * u.year, Sources.HYPOTHESIS)
        device1.carbon_footprint_fabrication = SourceValue(365.25 * 24 * u.kg, Sources.BASE_ADEME_V19)
        device1.fraction_of_usage_time = SourceValue(12 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)
        device2 = MagicMock()
        device2.lifespan = SourceValue(1 * u.year, Sources.HYPOTHESIS)
        device2.carbon_footprint_fabrication = SourceValue(365.25 * 24 * 3 * u.kg, Sources.BASE_ADEME_V19)
        device2.fraction_of_usage_time = SourceValue(8 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)
        with patch.object(
                self.usage_pattern, "devices", new=[device1, device2]),\
                patch.object(self.usage_pattern, "nb_user_journeys_in_parallel",
                             SourceHourlyValues(create_hourly_usage_df_from_list([10, 20, 30]))):
            self.usage_pattern.update_devices_fabrication_footprint()
            self.assertEqual(u.kg, self.usage_pattern.devices_fabrication_footprint.unit)
            self.assertEqual(
                [110, 220, 330], self.usage_pattern.devices_fabrication_footprint.value_as_float_list)

    def test_compute_hourly_job_occurrences_simple_case(self):
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj1.uj_steps = [uj_step11]
        uj_step11.jobs = [job]
        uj_step11.user_time_spent = SourceValue(90 * u.min)

        with patch.object(self.usage_pattern, "user_journey", uj1),\
                patch.object(self.usage_pattern, "utc_hourly_user_journey_starts", hourly_uj_starts):
            job_occurrences = self.usage_pattern.compute_hourly_job_occurrences(job)
            self.assertEqual(hourly_uj_starts.value.index.min(), job_occurrences.value.index.min())
            self.assertEqual(hourly_uj_starts.value.index.max(), job_occurrences.value.index.max())
            self.assertEqual(hourly_uj_starts.value_as_float_list, job_occurrences.value_as_float_list)

    def test_compute_hourly_job_occurrences_uj_lasting_less_than_an_hour_before(self):
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        job2 = MagicMock()
        uj1.uj_steps = [uj_step11, uj_step12]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(40 * u.min)
        uj_step12.jobs = [job]
        uj_step12.user_time_spent = SourceValue(4 * u.min)

        with patch.object(self.usage_pattern, "user_journey", uj1), \
                patch.object(self.usage_pattern, "utc_hourly_user_journey_starts", hourly_uj_starts):
            job_occurrences = self.usage_pattern.compute_hourly_job_occurrences(job)
            self.assertEqual(hourly_uj_starts.value.index.min(), job_occurrences.value.index.min())
            self.assertEqual(hourly_uj_starts.value.index.max(), job_occurrences.value.index.max())
            self.assertEqual(hourly_uj_starts.value_as_float_list, job_occurrences.value_as_float_list)

    def test_compute_hourly_job_occurrences_uj_lasting_more_than_an_hour_before(self):
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        job2 = MagicMock()
        uj1.uj_steps = [uj_step11, uj_step12]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(61 * u.min)
        uj_step12.jobs = [job]
        uj_step12.user_time_spent = SourceValue(4 * u.min)

        with patch.object(self.usage_pattern, "user_journey", uj1), \
                patch.object(self.usage_pattern, "utc_hourly_user_journey_starts", hourly_uj_starts):
            job_occurrences = self.usage_pattern.compute_hourly_job_occurrences(job)
            self.assertEqual(hourly_uj_starts.value.index.min().to_timestamp() + timedelta(hours=1),
                             job_occurrences.value.index.min().to_timestamp())
            self.assertEqual(hourly_uj_starts.value.index.max().to_timestamp() + timedelta(hours=1),
                             job_occurrences.value.index.max().to_timestamp())
            self.assertEqual(hourly_uj_starts.value_as_float_list, job_occurrences.value_as_float_list)
            
    def test_compute_hourly_job_occurrences_uj_steps_sum_up_to_more_than_one_hour(self):
        hourly_uj_starts = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5, 7]))
        job = MagicMock()
        uj1 = MagicMock()
        uj_step11 = MagicMock()
        uj_step12 = MagicMock()
        uj_step13 = MagicMock()
        job2 = MagicMock()
        uj1.uj_steps = [uj_step11, uj_step12, uj_step13]
        uj_step11.jobs = [job2]
        uj_step11.user_time_spent = SourceValue(59 * u.min)
        uj_step12.jobs = [job2]
        uj_step12.user_time_spent = SourceValue(4 * u.min)
        uj_step13.jobs = [job, job]
        uj_step13.user_time_spent = SourceValue(1 * u.min)

        with patch.object(self.usage_pattern, "user_journey", uj1), \
                patch.object(self.usage_pattern, "utc_hourly_user_journey_starts", hourly_uj_starts):
            job_occurrences = self.usage_pattern.compute_hourly_job_occurrences(job)
            self.assertEqual(
                hourly_uj_starts.value.index.min().to_timestamp() + timedelta(hours=1), job_occurrences.value.index.min().to_timestamp())
            self.assertEqual(
                hourly_uj_starts.value.index.max().to_timestamp() + timedelta(hours=1), job_occurrences.value.index.max().to_timestamp())
            self.assertEqual([elt * 2 for elt in hourly_uj_starts.value_as_float_list], job_occurrences.value_as_float_list)

    def test_compute_job_hourly_data_exchange_simple_case(self):
        data_exchange = "data_upload"
        job = MagicMock()
        job.data_upload = SourceValue(1 * u.GB)
        job.duration_in_full_hours = SourceValue(1 * u.dimensionless)
        hourly_job_occs_per_job = {job: SourceHourlyValues(create_hourly_usage_df_from_list([1, 3, 5]))}

        with patch.object(self.usage_pattern, "hourly_job_occurrences_per_job", hourly_job_occs_per_job):
            job_hourly_data_exchange = self.usage_pattern.compute_job_hourly_data_exchange(job, data_exchange)

            self.assertEqual([1, 3, 5], job_hourly_data_exchange.value_as_float_list)

    def test_compute_job_hourly_data_exchange_complex_case(self):
        data_exchange = "data_upload"
        job = MagicMock()
        job.data_upload = SourceValue(1 * u.GB)
        job.duration_in_full_hours = SourceValue(2 * u.dimensionless)
        hourly_job_occs_per_job = {job: SourceHourlyValues(create_hourly_usage_df_from_list([1, 3, 5]))}

        with patch.object(self.usage_pattern, "hourly_job_occurrences_per_job", hourly_job_occs_per_job):
            job_hourly_data_exchange = self.usage_pattern.compute_job_hourly_data_exchange(job, data_exchange)

            self.assertEqual([0.5, 2, 4, 2.5], job_hourly_data_exchange.value_as_float_list)


if __name__ == '__main__':
    unittest.main()
