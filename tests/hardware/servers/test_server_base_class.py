from datetime import timedelta, datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock

from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.core.hardware.servers.server_base_class import Server


class TestServerBaseClass(TestCase):
    def setUp(self):
        class TestServer(Server):
            def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                         lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, cpu_cores: SourceValue,
                         power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                         server_utilization_rate: SourceValue, base_ram_consumption: SourceValue,
                         base_cpu_consumption: SourceValue):
                super().__init__(
                    name, carbon_footprint_fabrication, power, lifespan, idle_power, ram, cpu_cores,
                    power_usage_effectiveness,
                    average_carbon_intensity, server_utilization_rate, base_ram_consumption, base_cpu_consumption)

            def update_nb_of_instances(self):
                return SourceValue(10 * u.dimensionless)

        self.country = MagicMock()
        self.server_base = TestServer(
            "Test server",
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(0 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(0 * u.GB, Sources.HYPOTHESIS),
            cpu_cores=SourceValue(0 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
            server_utilization_rate=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            base_ram_consumption=SourceValue(0 * u.GB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(0 * u.core, Sources.HYPOTHESIS)
        )
        self.server_base.dont_handle_input_updates = True

    def test_update_hour_by_hour_cpu_need(self):
        job1 = MagicMock()
        job2 = MagicMock()

        job1.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([10, 20, 1, 0]))
        job2.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([20, 15, 5, 3]))
        job1.cpu_needed = SourceValue(2 * u.core)
        job2.cpu_needed = SourceValue(3 * u.core)

        with patch.object(Server, "jobs", new_callable=PropertyMock) as mock_jobs:
            mock_jobs.return_value = {job1, job2}
            self.server_base.update_hour_by_hour_cpu_need()

        self.assertEqual([80, 85, 17, 9], self.server_base.hour_by_hour_cpu_need.value_as_float_list)

    def test_update_hour_by_hour_ram_need(self):
        job1 = MagicMock()
        job2 = MagicMock()

        job1.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([10, 20, 1, 0]))
        job2.hourly_avg_occurrences_across_usage_patterns = SourceHourlyValues(
            create_hourly_usage_df_from_list([20, 15, 5, 3]))
        job1.ram_needed = SourceValue(2 * u.GB)
        job2.ram_needed = SourceValue(3 * u.GB)

        with patch.object(Server, "jobs", new_callable=PropertyMock) as mock_jobs:
            mock_jobs.return_value = {job1, job2}
            self.server_base.update_hour_by_hour_ram_need()

        self.assertEqual([80, 85, 17, 9], self.server_base.hour_by_hour_ram_need.value_as_float_list)


    def test_available_cpu_per_instance(self):
        with patch.object(self.server_base, "base_cpu_consumption", SourceValue(2 * u.core)), \
                patch.object(self.server_base, "cpu_cores", SourceValue(24 * u.core)), \
                patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            self.server_base.update_available_cpu_per_instance()
            expected_value = SourceValue((24 * 0.7 - 2) * u.core)

            self.assertEqual(expected_value.value, self.server_base.available_cpu_per_instance.value)

    def test_available_ram_per_instance(self):
        with patch.object(self.server_base, "base_ram_consumption", SourceValue(2 * u.GB)), \
                patch.object(self.server_base, "ram", SourceValue(24 * u.GB)), \
                patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            self.server_base.update_available_ram_per_instance()
            expected_value = SourceValue((24 * 0.7 - 2) * u.GB)

            self.assertEqual(expected_value.value, self.server_base.available_ram_per_instance.value)


    def test_available_ram_per_instance_should_raise_value_error_when_demand_exceeds_server_capacity(self):
        with patch.object(self.server_base, "ram", SourceValue(128 * u.GB)), \
            patch.object(self.server_base, "base_ram_consumption", SourceValue(129 * u.GB)), \
            patch.object(self.server_base, "server_utilization_rate", SourceValue(0.7 * u.dimensionless)):
            with self.assertRaises(ValueError):
                self.server_base.update_available_ram_per_instance()

    def test_raw_nb_of_instances_autoscaling_simple_case(self):
        ram_need = SourceHourlyValues(create_hourly_usage_df_from_list([0, 1, 3, 3, 10], pint_unit=u.GB))
        cpu_need = SourceHourlyValues(create_hourly_usage_df_from_list([2, 4, 2, 6, 3], pint_unit=u.core))

        with patch.object(self.server_base, "hour_by_hour_ram_need", new=ram_need), \
                patch.object(self.server_base, "hour_by_hour_cpu_need", new=cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(2 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(4 * u.core)):
            self.server_base.update_raw_nb_of_instances()

            self.assertEqual([0.5, 1, 1.5, 1.5, 5], self.server_base.raw_nb_of_instances.value_as_float_list)

    def test_raw_nb_of_instances_autoscaling_different_timespan_case(self):
        start_date_a = datetime.strptime("2025-01-01", "%Y-%m-%d")
        start_date_b = datetime.strptime("2025-01-02", "%Y-%m-%d")

        ram_need_a = SourceHourlyValues(
            create_hourly_usage_df_from_list([0, 1, 3, 3, 10], start_date_a, pint_unit=u.GB))
        ram_need_b = SourceHourlyValues(
            create_hourly_usage_df_from_list([0, 1, 3, 3, 10], start_date_b, pint_unit=u.GB))
        cpu_need_a = SourceHourlyValues(
            create_hourly_usage_df_from_list([2, 4, 2, 6, 3], start_date_a, pint_unit=u.core))
        cpu_need_b = SourceHourlyValues(
            create_hourly_usage_df_from_list([2, 4, 2, 6, 3], start_date_b, pint_unit=u.core))
        all_ram_need = ram_need_a + ram_need_b
        all_cpu_need = cpu_need_a + cpu_need_b

        expected_data = [0.5, 1, 1.5, 1.5, 5, 0.5, 1, 1.5, 1.5, 5]
        expected_max_date = start_date_b + timedelta(hours=(len(ram_need_b)-1))

        with patch.object(self.server_base, "hour_by_hour_ram_need", new=all_ram_need), \
                patch.object(self.server_base, "hour_by_hour_cpu_need", new=all_cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(2 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(4 * u.core)):
            self.server_base.update_raw_nb_of_instances()

            self.assertEqual(expected_data, self.server_base.raw_nb_of_instances.value_as_float_list)
            self.assertEqual(start_date_a, self.server_base.raw_nb_of_instances.value.index.min().to_timestamp())
            self.assertEqual(expected_max_date, self.server_base.raw_nb_of_instances.value.index.max().to_timestamp())

    def test_compute_instances_energy_simple_case(self):
        with patch.object(self.server_base, "nb_of_instances",
                          SourceHourlyValues(create_hourly_usage_df_from_list([1, 0, 2]))), \
                patch.object(self.server_base, "raw_nb_of_instances",
                             SourceHourlyValues(create_hourly_usage_df_from_list([1, 0, 2]))), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(3 * u.dimensionless)):
            self.server_base.update_instances_energy()
            self.assertEqual(u.kWh, self.server_base.instances_energy.unit)
            self.assertEqual([0.9, 0, 1.8], self.server_base.instances_energy.value_as_float_list)

    def test_compute_instances_energy_complex_case(self):
        with patch.object(self.server_base, "nb_of_instances",
                          SourceHourlyValues(create_hourly_usage_df_from_list([1, 0, 2]))), \
                patch.object(self.server_base, "raw_nb_of_instances",
                             SourceHourlyValues(create_hourly_usage_df_from_list([1, 0, 1.5]))), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(3 * u.dimensionless)):
            self.server_base.update_instances_energy()
            self.assertEqual(u.kWh, self.server_base.instances_energy.unit)
            self.assertEqual([0.9, 0, 0.9 + 0.525], self.server_base.instances_energy.value_as_float_list)
