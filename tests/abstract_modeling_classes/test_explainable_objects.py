import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

import pytz

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.constants.units import u


class TestExplainableQuantity(unittest.TestCase):
    def setUp(self):
        self.a = ExplainableQuantity(1 * u.W, "1 Watt")
        self.b = ExplainableQuantity(2 * u.W, "2 Watt")
        self.c = self.a + self.b
        self.c.set_label("int calc")
        self.d = self.c + self.b
        self.d.set_label("int calc 2")
        self.e = ExplainableQuantity(3 * u.W, "e")
        for index, explainable_quantity in enumerate([self.a, self.b, self.e]):
            explainable_quantity.modeling_obj_container = MagicMock(name="name", id=f"id{index}")
        self.f = self.a + self.b + self.e

    def test_compute_calculation(self):
        self.assertEqual([self.a, self.b, self.e], self.f.direct_ancestors_with_id)

    def test_init(self):
        self.assertEqual(self.a.value, 1 * u.W)
        self.assertEqual(self.a.label, "1 Watt")
        self.assertEqual(self.a.left_parent, None)
        self.assertEqual(self.a.right_parent, None)
        self.assertEqual(self.a.operator, None)

        self.assertEqual(self.c.value, 3 * u.W)
        self.assertEqual(self.c.label, "int calc")
        self.assertEqual(self.c.left_parent, self.a)
        self.assertEqual(self.c.right_parent, self.b)
        self.assertEqual(self.c.operator, '+')

    def test_operators(self):
        self.assertEqual(self.c.value, 3 * u.W)
        self.assertRaises(ValueError, self.a.__add__, 1)
        self.assertRaises(ValueError, self.a.__gt__, 1)
        self.assertRaises(ValueError, self.a.__lt__, 1)
        self.assertRaises(ValueError, self.a.__eq__, 1)

    def test_to(self):
        self.a.to(u.mW)
        self.assertEqual(self.a.value, 1000 * u.mW)

    def test_magnitude(self):
        self.assertEqual(self.a.magnitude, 1)

    def test_add_with_0(self):
        self.assertEqual(self.a, self.a + 0)

    def test_subtract_0(self):
        self.assertEqual(self.a, self.a - 0)

    def test_to_json(self):
        self.assertDictEqual({"label": "1 Watt", "value": 1, "unit": "watt"}, self.a.to_json())

    def test_ceil(self):
        self.a = ExplainableQuantity(1.5 * u.W, "1.5 Watt")
        self.assertEqual(2 * u.W, self.a.ceil().value)

class TestExplainableHourlyQuantities(unittest.TestCase):

    def setUp(self):
        self.usage1 = [1] * 24
        self.usage2 = [2] * 24
        self.start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        self.hourly_usage1 = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(self.usage1, self.start_date, pint_unit=u.W), "Usage 1")
        self.hourly_usage2 = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(self.usage2, self.start_date, pint_unit=u.W), "Usage 2")

    def test_init(self):
        self.assertEqual(self.hourly_usage1.label, "Usage 1")
        self.assertEqual(len(self.hourly_usage1.value), 24)

    def test_addition_between_hourly_quantities_with_same_unit(self):
        sum_hourly_usage = self.hourly_usage1 + self.hourly_usage2
        self.assertEqual([3] * 24, sum_hourly_usage.value_as_float_list)

    def test_addition_between_hourly_quantities_with_homogeneous_but_different_units(self):
        hourly_usage1 = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list([1, 2, 3], self.start_date, pint_unit=u.kW), "Usage 1")
        hourly_usage2 = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list([10, 20, 30], self.start_date, pint_unit=u.W), "Usage 2")
        sum_hourly_usage = hourly_usage1 + hourly_usage2
        self.assertEqual([1.01, 2.02, 3.03], sum_hourly_usage.value_as_float_list)

    def test_addition_between_non_overlapping_hourly_quantities_with_same_units(self):
        hourly_usage1 = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list([1, 2, 3], datetime.strptime("2025-01-01", "%Y-%m-%d"), pint_unit=u.W), "Usage 1")
        hourly_usage2 = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list([10, 20, 30], datetime.strptime("2025-01-02", "%Y-%m-%d"), pint_unit=u.W), "Usage 2")
        sum_hourly_usage = hourly_usage1 + hourly_usage2
        self.assertEqual([1, 2, 3, 10, 20, 30], sum_hourly_usage.value_as_float_list)
        self.assertEqual(hourly_usage1.value.index.min(), sum_hourly_usage.value.index.min())
        self.assertEqual(hourly_usage2.value.index.max(), sum_hourly_usage.value.index.max())

    def test_addition_with_shifted_hourly_quantities(self):
        nb_hours_shifted = 2
        shifted_hour_usage = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(
                self.usage2, self.start_date + timedelta(hours=nb_hours_shifted), pint_unit=u.W), "Usage 2")
        sum_hourly_usage = self.hourly_usage1 + shifted_hour_usage

        self.assertTrue(isinstance(sum_hourly_usage, ExplainableHourlyQuantities))
        self.assertEqual(len(self.hourly_usage1) + nb_hours_shifted, len(sum_hourly_usage))
        self.assertEqual(self.hourly_usage1.value.index.min(), sum_hourly_usage.value.index.min())
        self.assertEqual(self.hourly_usage1.value_as_float_list[:nb_hours_shifted],
                         sum_hourly_usage.value_as_float_list[:nb_hours_shifted])
        self.assertEqual(shifted_hour_usage.value_as_float_list[-nb_hours_shifted:],
                         sum_hourly_usage.value_as_float_list[-nb_hours_shifted:])

    def test_addition_with_quantity_fails(self):
        with self.assertRaises(ValueError):
            addition_result = self.hourly_usage1 + ExplainableQuantity(4 * u.W, "4W")

    def test_mul_with_quantity(self):
        mul_result = self.hourly_usage1 * ExplainableQuantity(4 * u.h, "4 hours")

        self.assertTrue(isinstance(mul_result, ExplainableHourlyQuantities))
        self.assertTrue(u.Wh.is_compatible_with(mul_result.unit))
        self.assertEqual([4] * 24, mul_result.value_as_float_list)

    def test_subtraction(self):
        result = self.hourly_usage2 - self.hourly_usage1
        self.assertEqual([1] * 24, result.value_as_float_list)

    def test_subtraction_with_quantity_fails(self):
        with self.assertRaises(ValueError):
            subtraction_result = self.hourly_usage1 - ExplainableQuantity(4 * u.W, "4W")

    @patch('efootprint.abstract_modeling_classes.explainable_objects.datetime')
    def test_convert_to_utc(self, mock_datetime):
        start_date = datetime(2023, 10, 1)
        # Artificially fix datetime to avoid test crashing because of annual time changes.
        mock_datetime.now.return_value = start_date
        mock_data = [1] * 12
        usage = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(mock_data, start_date=start_date), "usage")

        local_tz_ahead_utc = ExplainableObject(pytz.timezone('Europe/Berlin'), "local timezone ahead UTC")
        local_tz_behind_utc = ExplainableObject(pytz.timezone('America/New_York'), "local timezone behind UTC")

        converted_ahead_utc = usage.convert_to_utc(local_tz_ahead_utc)
        converted_behind_utc = usage.convert_to_utc(local_tz_behind_utc)

        # Berlin is 2 hours ahead, converting to UTC results in the array shifted by 2 positions to the left
        self.assertEqual(mock_data, converted_ahead_utc.value_as_float_list)
        self.assertEqual(mock_data, converted_behind_utc.value_as_float_list)

        self.assertEqual(start_date - timedelta(hours=2), converted_ahead_utc.value.index.min().to_timestamp())
        self.assertEqual(start_date + timedelta(hours=4), converted_behind_utc.value.index.min().to_timestamp())

        # Check other attributes of converted ExplainableHourlyUsage
        self.assertEqual(None, converted_ahead_utc.label)
        self.assertEqual(usage, converted_ahead_utc.left_parent)
        self.assertEqual(local_tz_ahead_utc, converted_ahead_utc.right_parent)
        self.assertEqual("converted to UTC from", converted_ahead_utc.operator)

    def test_sum(self):
        summed = self.hourly_usage1.sum()
        self.assertEqual(summed, ExplainableQuantity(24 * u.W, "24 W"))

    def test_max(self):
        maximum = self.hourly_usage1.max()
        self.assertEqual(maximum, ExplainableQuantity(1 * u.W, "1 W"))

    def test_abs(self):
        self.assertEqual(self.hourly_usage1, self.hourly_usage1.abs())

    def test_abs_complex_case(self):
        test_data = ExplainableHourlyQuantities(create_hourly_usage_df_from_list([1, -1, -4]), "test")

        self.assertEqual([1, 1, 4], test_data.abs().value_as_float_list)

    def test_eq_returns_true_when_equal(self):
        self.assertTrue(self.hourly_usage1 == self.hourly_usage1)

    def test_eq_returns_false_when_not_equal(self):
        self.assertFalse(self.hourly_usage1 == self.hourly_usage2)

    def test_to_json(self):
        self.maxDiff = None
        self.assertDictEqual(
            {"label": "Usage 1", "values": [1] * 24, "unit": "watt", "start_date": "2025-01-01 00:00:00"},
            self.hourly_usage1.to_json())

    def test_ceil_dimensionless(self):
        usage_data = [1.5] * 24
        hourly_usage_data = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(usage_data, pint_unit=u.dimensionless), "test")

        ceil = hourly_usage_data.ceil()
        self.assertEqual([2] * 24, ceil.value_as_float_list)
        self.assertEqual(u.dimensionless, ceil.unit)

    def test_ceil_with_unit_specified(self):
        usage_data = [1.5] * 24
        hourly_usage_data = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(usage_data, pint_unit=u.GB), "test")

        ceil = hourly_usage_data.ceil()
        self.assertEqual([2] * 24, ceil.value_as_float_list)
        self.assertEqual(u.GB, ceil.unit)

    def test_copy(self):
        usage_data = [1.5] * 24
        expected_data = [1.5] * 24
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        end_date = start_date + timedelta(hours=len(usage_data) - 1)

        hourly_usage_data = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(usage_data, start_date=start_date, pint_unit=u.GB, ), "test")

        duplicated = hourly_usage_data.copy()
        self.assertEqual(expected_data, duplicated.value_as_float_list)
        self.assertEqual(u.GB, duplicated.unit)
        self.assertEqual(start_date, duplicated.value.index.min().to_timestamp())
        self.assertEqual(end_date, duplicated.value.index.max().to_timestamp())

    def test_copy_with_changes_on_source(self):
        usage_data = [1.5] * 24
        start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")

        hourly_usage_data = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list(usage_data, start_date=start_date, pint_unit=u.GB, ), "test")

        duplicated = hourly_usage_data.copy()
        hourly_usage_data = ExplainableHourlyQuantities(
            create_hourly_usage_df_from_list([3] * 24, start_date=start_date, pint_unit=u.GB, ), "test")

        self.assertNotEqual(hourly_usage_data.value_as_float_list, duplicated.value_as_float_list)


if __name__ == "__main__":
    unittest.main()
