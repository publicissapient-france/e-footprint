from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock

from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.sources import Sources
from efootprint.core.hardware.network import Network
from efootprint.constants.units import u
from efootprint.builders.time_builders import create_hourly_usage_df_from_list


class TestNetwork(TestCase):
    def setUp(self):
        self.network = Network("Wifi network", SourceValue(0 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        self.network.dont_handle_input_updates = True

    def test_update_energy_footprint_simple_case(self):
        usage_pattern = MagicMock()
        usage_pattern.country.average_carbon_intensity = SourceValue(100 * u.g / u.kWh)

        job1 = MagicMock()
        usage_pattern.hourly_data_upload_per_job = {
            job1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB))}
        usage_pattern.hourly_data_download_per_job = {
            job1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB))}
        usage_pattern.jobs = [job1]

        with patch.object(Network, "usage_patterns", new_callable=PropertyMock) as mock_ups,\
            patch.object(self.network, "bandwidth_energy_intensity", SourceValue(1 * u.kWh / u.GB)):
            mock_ups.return_value = [usage_pattern]
            self.network.update_energy_footprint()

            self.assertEqual(u.kg, self.network.energy_footprint.unit)
            self.assertEqual([0.2, 0.4, 1], self.network.energy_footprint.value_as_float_list)

    def test_update_energy_footprint_no_up_with_job(self):
        usage_pattern = MagicMock()
        usage_pattern.country.average_carbon_intensity = SourceValue(100 * u.g / u.kWh)
        usage_pattern.jobs = []

        with patch.object(Network, "usage_patterns", new_callable=PropertyMock) as mock_ups,\
            patch.object(self.network, "bandwidth_energy_intensity", SourceValue(1 * u.kWh / u.GB)):
            mock_ups.return_value = [usage_pattern]
            self.network.update_energy_footprint()

            self.assertEqual(0, self.network.energy_footprint)

    def test_update_energy_footprint_complex_case(self):
        usage_pattern = MagicMock()
        usage_pattern.country.average_carbon_intensity = SourceValue(100 * u.g / u.kWh)

        job1 = MagicMock()
        usage_pattern.hourly_data_upload_per_job = {
            job1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB))}
        usage_pattern.hourly_data_download_per_job = {
            job1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB))}
        usage_pattern.jobs = [job1]

        usage_pattern2 = MagicMock()
        usage_pattern2.country.average_carbon_intensity = SourceValue(100 * u.g / u.kWh)

        job2 = MagicMock()
        usage_pattern2.hourly_data_upload_per_job = {
            job1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB)),
            job2: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB))}
        usage_pattern2.hourly_data_download_per_job = {
            job1: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB)),
            job2: SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 5], pint_unit=u.GB))}
        usage_pattern2.jobs = [job1, job2]

        with patch.object(Network, "usage_patterns", new_callable=PropertyMock) as mock_ups,\
            patch.object(self.network, "bandwidth_energy_intensity", SourceValue(1 * u.kWh / u.GB)):
            mock_ups.return_value = [usage_pattern, usage_pattern2]
            self.network.update_energy_footprint()

            self.assertEqual(u.kg, self.network.energy_footprint.unit)
            self.assertEqual([0.6, 1.2, 3], self.network.energy_footprint.value_as_float_list)
