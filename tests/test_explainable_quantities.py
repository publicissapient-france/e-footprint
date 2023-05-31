import unittest
from pint import UnitRegistry
from footprint_model.constants.explainable_quantities import ExplainableQuantity

u = UnitRegistry()


class TestExplainableQuantity(unittest.TestCase):
    def setUp(self):
        self.a = ExplainableQuantity(1 * u.W, "1 Watt")
        self.b = ExplainableQuantity(2 * u.W, "2 Watt")
        self.c = self.a + self.b
        self.c.define_as_intermediate_calculation("int calc")
        self.d = self.c + self.b
        self.d.define_as_intermediate_calculation("int calc 2")

    def test_init(self):
        self.assertEqual(self.a.value, 1 * u.W)
        self.assertEqual(self.a.formulas, {0: "1 Watt"})
        self.assertEqual(self.a.name_values_dict, {0: {"1 Watt": 1 * u.W}})
        self.assertEqual(self.a.name_formulas_dict, {0: {"1 Watt": "1 Watt"}})

    def test_define_as_intermediate_calculation(self):
        self.assertEqual(self.c.height_level, 1)
        self.assertDictEqual(self.c.formulas, {0: '1 Watt + 2 Watt', 1: 'int calc'})
        self.assertDictEqual(
            self.c.name_values_dict, {0: {'1 Watt': 1 * u.W, '2 Watt': 2 * u.W}, 1: {'int calc': 3 * u.W}})
        self.assertDictEqual(
            self.c.name_formulas_dict,
            {0: {'1 Watt': '1 Watt', '2 Watt': '2 Watt'}, 1: {'int calc': '1 Watt + 2 Watt'}})

    def test_operators(self):
        self.assertEqual(self.c.value, 3 * u.W)
        self.assertRaises(ValueError, self.a.__add__, 1)
        self.assertRaises(ValueError, self.a.__gt__, 1)
        self.assertRaises(ValueError, self.a.__lt__, 1)
        self.assertRaises(ValueError, self.a.__eq__, 1)

    def test_explain_order_0(self):
        self.assertEqual(
            (self.a + self.b).explain(), '## High-level formula:\n\n1 Watt + 2 Watt = 1 watt + 2 watt = 3 watt')

    def test_explain_order_1(self):
        self.assertEqual(
            self.c.explain(pretty_print=False),
            '## High-level formula:\n\n\n##### int calc:\nint calc = 1 Watt + 2 Watt = 1 watt + 2 watt = 3 watt\n')

    def test_second_order_calc(self):
        self.assertEqual(self.d.height_level, 2)
        self.assertDictEqual(self.d.formulas, {0: '1 Watt + 2 Watt + 2 Watt', 1: 'int calc + 2 Watt', 2: 'int calc 2'})
        self.assertDictEqual(
            self.d.name_values_dict,
            {0: {'1 Watt': 1 * u.W, '2 Watt': 2 * u.W},
             1: {'int calc': 3 * u.W},
             2: {'int calc 2': 5 * u.W}})
        self.assertDictEqual(
            self.d.name_formulas_dict,
            {0: {'1 Watt': '1 Watt', '2 Watt': '2 Watt'},
             1: {'int calc': '1 Watt + 2 Watt'},
             2: {'int calc 2': 'int calc + 2 Watt'}})

    def test_explain_order_2(self):
        self.assertEqual(
            self.d.explain(pretty_print=False),
            '## High-level formula:\n\n\n##### int calc 2:\nint calc 2 = int calc + 2 Watt = 3 watt + 2 watt = 5 watt\n\n\n#### with int calc defined as:\n\n##### int calc:\nint calc = 1 Watt + 2 Watt = 1 watt + 2 watt = 3 watt\n'
        )
        self.assertEqual(
            self.d.explain(pretty_print=True),
            '## High-level formula:\n\n\n##### int calc 2:\nint calc 2\n=\n int calc + 2 Watt\n=\n 3 watt + 2 watt\n=\n 5 watt\n\n\n#### with int calc defined as:\n\n##### int calc:\nint calc\n=\n 1 Watt + 2 Watt\n=\n 1 watt + 2 watt\n=\n 3 watt\n'
        )

    def test_to(self):
        self.a.to(u.mW)
        self.assertEqual(self.a.value, 1000 * u.mW)

    def test_magnitude(self):
        self.assertEqual(self.a.magnitude, 1)


if __name__ == "__main__":
    unittest.main()
