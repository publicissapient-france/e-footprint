import unittest
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.core.infra_need import InfraNeed
from footprint_model.constants.units import u


class InfraNeedTests(unittest.TestCase):
    def setUp(self):
        self.ram_values = [ExplainableQuantity(4 * u.Go), ExplainableQuantity(8 * u.Go)]
        self.storage_value = ExplainableQuantity(10 * u.To / u.year)
        self.cpu_values = [ExplainableQuantity(2 * u.core), ExplainableQuantity(4 * u.core)]

    def test_post_init_valid(self):
        # Test that __post_init__ doesn't raise any errors for valid input
        infra_need = InfraNeed(ram=self.ram_values, storage=self.storage_value, cpu=self.cpu_values)
        # No assertion needed, if no exception is raised, the test passes

    def test_post_init_invalid_ram(self):
        invalid_ram_values = [ExplainableQuantity(4 * u.min), ExplainableQuantity(8 * u.Go)]
        with self.assertRaises(ValueError):
            InfraNeed(ram=invalid_ram_values, storage=self.storage_value, cpu=self.cpu_values)

    def test_post_init_invalid_storage(self):
        invalid_storage_value = ExplainableQuantity(256 * u.Mo)
        with self.assertRaises(ValueError):
            InfraNeed(ram=self.ram_values, storage=invalid_storage_value, cpu=self.cpu_values)

    def test_post_init_invalid_cpu(self):
        invalid_cpu_values = [ExplainableQuantity(2 * u.GHz), ExplainableQuantity(4 * u.core)]
        with self.assertRaises(ValueError):
            InfraNeed(ram=self.ram_values, storage=self.storage_value, cpu=invalid_cpu_values)

    def test_add_valid(self):
        infra_need1 = InfraNeed(ram=self.ram_values, storage=self.storage_value, cpu=self.cpu_values)
        infra_need2 = InfraNeed(ram=self.ram_values, storage=self.storage_value, cpu=self.cpu_values)
        result = infra_need1 + infra_need2

        expected_ram = [ram_value * ExplainableQuantity(2 * u.dimensionless) for ram_value in self.ram_values]
        expected_storage = self.storage_value * ExplainableQuantity(2 * u.dimensionless)
        expected_cpu = [cpu_value * ExplainableQuantity(2 * u.dimensionless) for cpu_value in self.cpu_values]

        self.assertEqual(result.ram, expected_ram)
        self.assertEqual(result.storage, expected_storage)
        self.assertEqual(result.cpu, expected_cpu)
        self.assertEqual(len(result.ram), len(infra_need1.ram))

    def test_add_invalid(self):
        # Test that __add__ method raises a ValueError for invalid inputs
        infra_need = InfraNeed(ram=self.ram_values, storage=self.storage_value, cpu=self.cpu_values)
        with self.assertRaises(ValueError):
            infra_need + 5  # Adding with a non-InfraNeed object


if __name__ == '__main__':
    unittest.main()

