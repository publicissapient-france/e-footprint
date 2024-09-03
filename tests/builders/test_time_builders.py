import unittest
from datetime import datetime, timedelta

from efootprint.builders.time_builders import create_random_hourly_usage_df, create_hourly_usage_df_from_list
from efootprint.constants.units import u


class TestTimeBuilders(unittest.TestCase):
    def test_create_random_hourly_usage_df(self):
        nb_days = 2
        min_val = 1
        max_val = 27
        start_date = datetime.strptime("2025-07-14", "%Y-%m-%d")
        pint_unit = u.dimensionless
        df = create_random_hourly_usage_df(nb_days, min_val, max_val, start_date, pint_unit)

        self.assertEqual(start_date, datetime.strptime(df.index.min().strftime("%Y-%m-%d"), "%Y-%m-%d"))
        self.assertEqual(nb_days * 24 + 1, len(df))
        self.assertEqual(pint_unit, df.dtypes.iloc[0].units)
        self.assertGreaterEqual(df["value"].min(), min_val * pint_unit)
        self.assertLessEqual(df["value"].max(), max_val * pint_unit)

    def test_create_hourly_usage_df_from_list(self):
        start_date = datetime.strptime("2025-07-14", "%Y-%m-%d")
        pint_unit = u.dimensionless
        input_list = [1, 2, 5, 7]
        df = create_hourly_usage_df_from_list(input_list, start_date, pint_unit)

        self.assertEqual(len(input_list), len(df))
        self.assertEqual(input_list, list(df["value"].values._data))
        self.assertEqual(start_date, datetime.strptime(df.index.min().strftime("%Y-%m-%d"), "%Y-%m-%d"))
        self.assertEqual(start_date + timedelta(hours=len(input_list) - 1),
                         df.index.max().to_timestamp().to_pydatetime())