from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timedelta

from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.core.hardware.storage import Storage


class TestStorage(TestCase):
    def setUp(self):
        self.storage_base = Storage(
            "storage_base",
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(0 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(0 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(0 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
            data_replication_factor=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            data_storage_duration=SourceValue(0 * u.years, Sources.HYPOTHESIS),
            initial_storage_need=SourceValue(0 * u.TB, Sources.HYPOTHESIS)
        )

        self.storage_base.dont_handle_input_updates = True

    def test_update_all_services_storage_needs_single_service(self):
        service1 = MagicMock()
        service2 = MagicMock()

        service1.storage_needed = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.TB))
        service2.storage_needed = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.TB))

        with patch.object(Storage, "services", new_callable=PropertyMock) as services_mock, \
                patch.object(self.storage_base, "data_replication_factor", SourceValue(3 * u.dimensionless)):
            services_mock.return_value = [service1, service2]
            self.storage_base.update_all_services_storage_needs()

        self.assertEqual([6, 12, 18], self.storage_base.all_services_storage_needs.value_as_float_list)
        self.assertEqual(u.TB, self.storage_base.all_services_storage_needs.unit)

    def test_update_storage_dumps(self):
        input_data = [2, 4, 6]
        storage_duration = 1
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        all_needed_storage = SourceHourlyValues(
            create_hourly_usage_df_from_list( input_data, start_date, pint_unit=u.TB))

        expected_min_date = start_date + timedelta(hours=1)
        expected_max_date = start_date + timedelta(hours=len(input_data) - storage_duration)

        with patch.object(self.storage_base, "all_services_storage_needs", all_needed_storage), \
            patch.object(self.storage_base, "data_storage_duration", SourceValue(storage_duration * u.hours)):
            self.storage_base.update_storage_dumps()

            self.assertEqual([-2, -4], self.storage_base.storage_dumps.value_as_float_list)
            self.assertEqual(expected_min_date, self.storage_base.storage_dumps.value.index.min().to_timestamp())
            self.assertEqual(expected_max_date, self.storage_base.storage_dumps.value.index.max().to_timestamp())

    def test_storage_delta(self):
        input_data = [2, 4, 6]
        dumps_data = [-2, -4]
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        all_needed_storage = SourceHourlyValues(
            create_hourly_usage_df_from_list(input_data, start_date, pint_unit=u.TB))
        dump_min_date = start_date + timedelta(hours=1)
        dump_need_update = SourceHourlyValues(
            create_hourly_usage_df_from_list(dumps_data, dump_min_date, pint_unit=u.TB))

        with patch.object(self.storage_base, "all_services_storage_needs", all_needed_storage), \
            patch.object(self.storage_base, "storage_dumps", dump_need_update):
            self.storage_base.update_storage_delta()

            self.assertEqual([2, 2, 2], self.storage_base.storage_delta.value_as_float_list)

    def test_update_full_cumulative_storage_need(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        delta_data = SourceHourlyValues(
            create_hourly_usage_df_from_list([2, -2, 4, -5, 6], start_date, pint_unit=u.TB))

        with patch.object(self.storage_base, "storage_delta", delta_data), \
                patch.object(self.storage_base, "initial_storage_need", SourceValue(5 * u.TB)):
            self.storage_base.update_full_cumulative_storage_need()

            self.assertEqual([7, 5, 9, 4, 10], self.storage_base.full_cumulative_storage_need.value_as_float_list)

    def test_nb_of_active_instances_simple_case(self):
        storage_capacity = SourceValue(1 * u.TB)
        storage_delta = SourceHourlyValues(create_hourly_usage_df_from_list([1, 2, 3], pint_unit=u.TB))
        storage_dumps = SourceHourlyValues(create_hourly_usage_df_from_list([0, -1, -0.5], pint_unit=u.TB))

        with patch.object(self.storage_base, "storage_delta", storage_delta), \
                patch.object(self.storage_base, "storage_dumps", storage_dumps), \
                patch.object(self.storage_base, "storage_capacity", storage_capacity):
            self.storage_base.update_nb_of_active_instances()
            self.assertEqual([1, 3, 3.5], self.storage_base.nb_of_active_instances.value_as_float_list)

    def test_raw_nb_of_instances(self):
        full_storage_data = SourceHourlyValues(create_hourly_usage_df_from_list([10, 12, 14], pint_unit=u.TB))
        storage_capacity = SourceValue(2 * u.TB)
        expected_data = [5, 6, 7]

        with patch.object(self.storage_base, "full_cumulative_storage_need", full_storage_data), \
                patch.object(self.storage_base, "storage_capacity", storage_capacity):
            self.storage_base.update_raw_nb_of_instances()
            self.assertEqual(expected_data, self.storage_base.nb_of_instances.value_as_float_list)

    def test_nb_of_instances(self):
        raw_nb_of_instances = SourceHourlyValues(
            create_hourly_usage_df_from_list([1.5, 2.5, 3.5], pint_unit=u.dimensionless))
        expected_data = [2, 3, 4]

        with patch.object(self.storage_base, "raw_nb_of_instances", raw_nb_of_instances):
            self.storage_base.update_nb_of_instances()
            self.assertEqual(expected_data, self.storage_base.nb_of_instances.value_as_float_list)
            self.assertEqual(u.dimensionless, self.storage_base.nb_of_instances.unit)

    def test_update_instances_energy(self):
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        all_instance_data = [2, 4, 6]
        all_active_data = [1, 2, 3]
        power_data = 100 * u.W
        power_idle_data = 50 * u.W

        expected_energy=[150, 300, 450]

        all_instance = SourceHourlyValues(create_hourly_usage_df_from_list(all_instance_data, start_date))
        all_active = SourceHourlyValues(create_hourly_usage_df_from_list(all_active_data, start_date))

        with patch.object(self.storage_base, "nb_of_instances", all_instance), \
            patch.object(self.storage_base, "nb_of_active_instances", all_active), \
            patch.object(self.storage_base, "power", SourceValue(power_data)), \
            patch.object(self.storage_base, "idle_power", SourceValue(power_idle_data)), \
            patch.object(self.storage_base, "power_usage_effectiveness", SourceValue(1 * u.dimensionless)):
            self.storage_base.update_instances_energy()

            self.assertEqual(expected_energy, self.storage_base.instances_energy.value_as_float_list)