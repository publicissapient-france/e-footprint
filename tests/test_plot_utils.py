import unittest

from footprint_model.utils.plot_utils import group_emissions_by_category
from footprint_model.constants.units import u


class TestGroupByCategory(unittest.TestCase):

    def test_group_emissions_by_category(self):
        d = {"smartphone": 2 * u.kg, "laptop": 1 * u.kg, "screen": 1 * u.kg, "box": 3 * u.kg, "wifi_network": 2 * u.kg,
             "mobile_network": 1 * u.kg, "server": 1 * u.kg, "SSD": 2 * u.kg, "HDD": 1 * u.kg}
        expected = {
            'Smartphones': 2 * u.kg,
            'Laptops': 2 * u.kg,
            'Wifi network': 5 * u.kg,
            'Mobile network': 1 * u.kg,
            'Servers': 1 * u.kg,
            'Storage': 3 * u.kg
        }
        result = group_emissions_by_category(d)
        self.assertDictEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
