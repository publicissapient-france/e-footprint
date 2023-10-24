import unittest
from unittest.mock import MagicMock

from pint import UnitRegistry
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
import pytz

u = UnitRegistry()


class TestExplainableQuantity(unittest.TestCase):
    def setUp(self):
        self.a = ExplainableQuantity(1 * u.W, "1 Watt")
        self.b = ExplainableQuantity(2 * u.W, "2 Watt")
        self.c = self.a + self.b
        self.c.define_as_intermediate_calculation("int calc")
        self.d = self.c + self.b
        self.d.define_as_intermediate_calculation("int calc 2")
        self.e = ExplainableQuantity(3 * u.W, "e")
        for explainable_quantity in (self.a, self.b, self.e):
            explainable_quantity.modeling_obj_container = MagicMock(name="name", id="id")
        self.f = self.a + self.b + self.e

    def test_compute_calculation(self):
        self.assertEqual([self.a, self.b, self.e], self.f.direct_children_with_id)

    def test_init(self):
        self.assertEqual(self.a.value, 1 * u.W)
        self.assertEqual(self.a.label, "1 Watt")
        self.assertEqual(self.a.left_child, None)
        self.assertEqual(self.a.right_child, None)
        self.assertEqual(self.a.child_operator, None)

        self.assertEqual(self.c.value, 3 * u.W)
        self.assertEqual(self.c.label, "int calc")
        self.assertEqual(self.c.left_child, self.a)
        self.assertEqual(self.c.right_child, self.b)
        self.assertEqual(self.c.child_operator, '+')

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


class TestExplainableHourlyUsage(unittest.TestCase):

    def setUp(self):
        self.usage1 = [ExplainableQuantity(1 * u.W, "1 Watt") for _ in range(24)]
        self.usage2 = [ExplainableQuantity(2 * u.W, "2 Watt") for _ in range(24)]
        self.hourly_usage1 = ExplainableHourlyUsage(self.usage1, "Usage 1")
        self.hourly_usage2 = ExplainableHourlyUsage(self.usage2, "Usage 2")
        self.sum_hourly_usage = self.hourly_usage1 + self.hourly_usage2

    def test_init(self):
        self.assertEqual(self.hourly_usage1.label, "Usage 1")
        self.assertEqual(len(self.hourly_usage1.value), 24)

    def test_addition(self):
        result_usage = [ExplainableQuantity(3 * u.W, "3W") for _ in range(24)]
        for value, expected in zip(self.sum_hourly_usage.value, result_usage):
            self.assertEqual(value, expected)

    def test_subtraction(self):
        result = self.hourly_usage2 - self.hourly_usage1
        for value in result.value:
            self.assertEqual(value, ExplainableQuantity(1 * u.W, "1W"))

    def test_convert_to_utc(self):
        # Create a simple ExplainableHourlyUsage instance with values [1,2,3,4,5]
        usage = ExplainableHourlyUsage([ExplainableQuantity(i * u.dimensionless, f"{i}") for i in range(1, 6)], "usage")

        # Let's say the local timezone is 2 hours ahead of UTC
        local_tz_ahead_utc = ExplainableObject(pytz.timezone('Europe/Berlin'), "local timezone ahead UTC")
        local_tz_behind_utc = ExplainableObject(pytz.timezone('America/New_York'), "local timezone behind UTC")

        converted_ahead_utc = usage.convert_to_utc(local_tz_ahead_utc)
        converted_behind_utc = usage.convert_to_utc(local_tz_behind_utc)

        # Convert the values back to simple list for comparison
        converted_values_ahead_utc = [q.value for q in converted_ahead_utc.value]
        converted_values_behind_utc = [q.value for q in converted_behind_utc.value]

        # If Berlin is 2 hours ahead, converting to UTC would result in the array shifted by 2 positions to the left.
        self.assertEqual(converted_values_ahead_utc, [3 * u.dimensionless, 4 * u.dimensionless, 5 * u.dimensionless,
                                            1 * u.dimensionless, 2 * u.dimensionless])
        self.assertEqual(converted_values_behind_utc, [2 * u.dimensionless, 3 * u.dimensionless, 4 * u.dimensionless,
                                                       5 * u.dimensionless, 1 * u.dimensionless])

        # Check other attributes of converted ExplainableHourlyUsage
        self.assertEqual("", converted_ahead_utc.label)
        self.assertEqual(usage, converted_ahead_utc.left_child)
        self.assertEqual(local_tz_ahead_utc, converted_ahead_utc.right_child)
        self.assertEqual("converted to UTC from", converted_ahead_utc.child_operator)

    def test_compute_usage_time_fraction(self):
        fraction = self.hourly_usage1.compute_usage_time_fraction()
        self.assertEqual(fraction, ExplainableQuantity(1 * u.dimensionless, "1"))

    def test_to_usage(self):
        usage = self.hourly_usage1.to_usage()
        for i, elt in enumerate(usage.value):
            self.assertEqual(elt, ExplainableQuantity(1 * u.dimensionless, f"Usage between {i} and {i+1}"))

    def test_sum(self):
        summed = self.hourly_usage1.sum()
        self.assertEqual(summed, ExplainableQuantity(24 * u.W, "24 W"))

    def test_max(self):
        maximum = self.hourly_usage1.max()
        self.assertEqual(maximum, ExplainableQuantity(1 * u.W, "1 W"))


if __name__ == "__main__":
    unittest.main()
