from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
import pint

from efootprint.constants.units import u


def create_random_hourly_usage_df(
        nb_days: int = 1, min_val: int = 1, max_val: int = 10,
        start_date: datetime = datetime.strptime("2025-01-01", "%Y-%m-%d"),
        pint_unit: pint.Unit = u.dimensionless):
    end_date = start_date + timedelta(days=nb_days)
    period_index = pd.period_range(start=start_date, end=end_date, freq='h')

    data = np.random.randint(min_val, max_val, size=len(period_index))
    df = pd.DataFrame(data, index=period_index, columns=['value'], dtype=f"pint[{str(pint_unit)}]")

    return df


def create_hourly_usage_df_from_list(
        input_list: List[float], start_date: datetime = datetime.strptime("2025-01-01", "%Y-%m-%d"),
        pint_unit: pint.Unit = u.dimensionless):
    end_date = start_date + timedelta(hours=len(input_list) - 1)
    period_index = pd.period_range(start=start_date, end=end_date, freq='h')

    df = pd.DataFrame(input_list, index=period_index, columns=['value'], dtype=f"pint[{str(pint_unit)}]")

    return df
