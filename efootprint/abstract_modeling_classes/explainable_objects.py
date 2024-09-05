import json
import numbers
from datetime import datetime
from typing import Type

import pandas as pd
import pint_pandas
import pytz
from pint import Quantity, Unit
import numpy as np

from efootprint.abstract_modeling_classes.explainable_object_base_class import (
    ExplainableObject, Source, ObjectLinkedToModelingObj)


class EmptyExplainableObject(ObjectLinkedToModelingObj):
    def set_modeling_obj_container(self, new_modeling_obj_container: Type["ModelingObject"], attr_name: str):
        self.modeling_obj_container = new_modeling_obj_container
        self.attr_name_in_mod_obj_container = attr_name

    def to(self, unit):
        return self

    def set_label(self, label):
        return self

    def ceil(self):
        return EmptyExplainableObject()

    def max(self):
        return EmptyExplainableObject()

    def abs(self):
        return EmptyExplainableObject()

    @property
    def magnitude(self):
        return self

    @property
    def value(self):
        return self

    def __eq__(self, other):
        if isinstance(other, EmptyExplainableObject):
            return True
        elif other == 0:
            return True

        return False

    def __add__(self, other):
        if issubclass(type(other), ExplainableObject):
            return other.__add__(self)
        elif isinstance(other, EmptyExplainableObject):
            return EmptyExplainableObject()
        else:
            raise ValueError

    def __sub__(self, other):
        if isinstance(other, EmptyExplainableObject):
            return EmptyExplainableObject()
        else:
            raise ValueError


class ExplainableQuantity(ExplainableObject):
    def __init__(
            self, value: Quantity, label: str = None, left_parent: Type["ExplainableQuantity"] = None,
            right_parent: Type["ExplainableQuantity"] = None, operator: str = None, source: Source = None):
        if not isinstance(value, Quantity):
            raise ValueError(
                f"Variable 'value' of type {type(value)} does not correspond to the appropriate 'Quantity' type, "
                "it is indeed mandatory to define a unit"
            )
        super().__init__(value, label, left_parent, right_parent, operator, source)

    def to(self, unit_to_convert_to):
        self.value = self.value.to(unit_to_convert_to)

        return self

    @property
    def magnitude(self):
        return self.value.magnitude

    def compare_with_and_return_max(self, other):
        if issubclass(type(other), ExplainableQuantity):
            if self.value >= other.value:
                return ExplainableQuantity(self.value, left_parent=self, right_parent=other, operator="max")
            else:
                return ExplainableQuantity(other.value, left_parent=self, right_parent=other, operator="max")
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {type(other)}")

    def ceil(self):
        self.value = np.ceil(self.value)
        return self

    def __gt__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.value > other.value
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {type(other)}")

    def __lt__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.value < other.value
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {type(other)}")

    def __eq__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.value == other.value
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {type(other)}")

    def __add__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return ExplainableQuantity(self.value, left_parent=self)
        elif isinstance(other, EmptyExplainableObject):
            return ExplainableQuantity(self.value, left_parent=self)
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value + other.value, "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return ExplainableQuantity(self.value, left_parent=self)
        elif isinstance(other, EmptyExplainableObject):
            return ExplainableQuantity(self.value, left_parent=self)
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value - other.value, "", self, other, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __mul__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return 0
        elif isinstance(other, EmptyExplainableObject):
            return EmptyExplainableObject()
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value * other.value, "", self, other, "*")
        elif issubclass(type(other), ExplainableHourlyQuantities):
            return other.__mul__(self)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value / other.value, "", self, other, "/")
        elif issubclass(type(other), ExplainableHourlyQuantities):
            return other.__rtruediv__(self)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(other.value - self.value, "", other, self, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return 0
        elif isinstance(other, EmptyExplainableObject):
            return EmptyExplainableObject()
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(other.value / self.value, "", other, self, "/")
        elif issubclass(type(other), ExplainableHourlyQuantities):
            return other.__truediv__(self)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __round__(self, round_level):
        self.value = round(self.value, round_level)
        return self

    def to_json(self, with_calculated_attributes_data=False):
        output_dict = {
            "label": self.label, "value": self.value.magnitude, "unit": str(self.value.units)}

        if self.source is not None:
            output_dict["source"] = {"name": self.source.name, "link": self.source.link}

        if with_calculated_attributes_data:
            output_dict["id"] = self.id
            output_dict["direct_ancestors_with_id"] = [elt.id for elt in self.direct_ancestors_with_id]
            output_dict["direct_children_with_id"] = [elt.id for elt in self.direct_children_with_id]

        return output_dict

    def __repr__(self):
        return json.dumps(self.to_json())

    def __str__(self):
        if isinstance(self.value, Quantity):
            return f"{round(self.value, 2)}"
        else:
            return str(self.value)


class ExplainableHourlyQuantities(ExplainableObject):
    def __init__(
            self, value: pd.DataFrame, label: str = None, left_parent: ExplainableObject = None,
            right_parent: ExplainableObject = None, operator: str = None, source: Source = None):
        if not isinstance(value, pd.DataFrame):
            raise ValueError(f"ExplainableHourlyQuantities values must be pandas DataFrames, got {type(value)}")
        if value.columns != ["value"]:
            raise ValueError(
                f"ExplainableHourlyQuantities values must have only one column named value, got {value.columns}")
        if not isinstance(value.dtypes.iloc[0], pint_pandas.pint_array.PintType):
            raise ValueError(f"The pd DataFrame value of an ExplainableHourlyQuantities object must be typed with Pint,"
                             f" got {type(value.dtypes.iloc[0])} dtype")
        super().__init__(value, label, left_parent, right_parent, operator, source)

    def to(self, unit_to_convert_to: Unit, rounding=None):
        self.value["value"] = self.value["value"].pint.to(unit_to_convert_to)
        if rounding is not None:
            self.value["value"] = pint_pandas.PintArray(
                [round(elt, rounding) for elt in self.value["value"].values._data], dtype=self.unit)

        return self

    def return_shifted_hourly_quantities(self, hours: int):
        return ExplainableHourlyQuantities(
            self.value.shift(hours, freq="h"), left_parent=self, operator=f"shift by {hours}")

    @property
    def unit(self):
        return self.value.dtypes.iloc[0].units

    @property
    def value_as_float_list(self):
        return [float(elt) for elt in self.value["value"].values._data]

    def convert_to_utc(self, local_timezone):
        utc_tz = pytz.timezone('UTC')
        current_time = datetime.now()
        time_diff = (utc_tz.utcoffset(current_time) - local_timezone.value.utcoffset(current_time))
        time_diff_in_hours = int(time_diff.total_seconds() / 3600)

        return ExplainableHourlyQuantities(
            self.value.copy().shift(time_diff_in_hours, freq="h"),
            left_parent=self, right_parent=local_timezone, operator="converted to UTC from")

    def sum(self):
        return ExplainableQuantity(self.value["value"].sum(), left_parent=self, operator="sum")

    def mean(self):
        return ExplainableQuantity(self.value["value"].mean() / 24, left_parent=self, operator="mean")

    def max(self):
        return ExplainableQuantity(self.value["value"].max(), left_parent=self, operator="max")

    def abs(self):
        return ExplainableHourlyQuantities(
            pd.DataFrame(
                {"value": pint_pandas.PintArray(np.abs(self.value["value"].values.data), dtype=self.unit)},
                index=self.value.index),
            left_parent=self, operator="abs")

    def ceil(self):
        return ExplainableHourlyQuantities(
            pd.DataFrame(
                {"value": pint_pandas.PintArray(np.ceil(self.value["value"].values.data), dtype=self.unit)},
                index=self.value.index),
            left_parent=self, operator="ceil")

    def copy(self):
        return ExplainableHourlyQuantities(self.value.copy(), left_parent=self, operator="duplicate")

    def __eq__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return False
        elif isinstance(other, EmptyExplainableObject):
            return False
        if issubclass(type(other), ExplainableHourlyQuantities):
            if len(self.value) != len(other.value):
                raise ValueError(
                    f"Can only compare ExplainableHourlyUsages with values of same length. Here we are trying to "
                    f"compare {self.value} and {other.value}.")

            return (self.value["value"] == other.value["value"]).all()
        else:
            raise ValueError(f"Can only compare with another ExplainableHourlyUsage, not {type(other)}")

    def __len__(self):
        return len(self.value)

    def __add__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return ExplainableHourlyQuantities(self.value, left_parent=self)
        elif isinstance(other, EmptyExplainableObject):
            return ExplainableHourlyQuantities(self.value, left_parent=self)
        elif issubclass(type(other), ExplainableHourlyQuantities):
            df_sum = self.value.add(other.value, fill_value=0 * self.unit)
            return ExplainableHourlyQuantities(df_sum, "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return ExplainableHourlyQuantities(self.value, left_parent=self)
        elif isinstance(other, EmptyExplainableObject):
            return ExplainableHourlyQuantities(self.value, left_parent=self)
        elif issubclass(type(other), ExplainableHourlyQuantities):
            return ExplainableHourlyQuantities(self.value - other.value, "", self, other, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __rsub__(self, other):
        if issubclass(type(other), ExplainableHourlyQuantities):
            return ExplainableHourlyQuantities(other.value - self.value, "", other, self, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __mul__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return 0
        elif isinstance(other, EmptyExplainableObject):
            return EmptyExplainableObject()
        elif issubclass(type(other), ExplainableHourlyQuantities):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyQuantities(self.value * other.value, "", self, other, "*")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, "
                f"not with {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableHourlyQuantities):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyQuantities(self.value / other.value, "", self, other, "/")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, "
                f"not with {type(other)}")

    def __rtruediv__(self, other):
        if issubclass(type(other), ExplainableHourlyQuantities):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyQuantities(other.value / self.value, "", other, self, "/")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity,"
                f" not with {type(other)}")

    def to_json(self, with_calculated_attributes_data=False):
        output_dict = {
            "label": self.label,
            "values": list(map(lambda x: round(float(x), 2), self.value["value"].values._data)),
            "unit": str(self.value.dtypes.iloc[0].units),
            "start_date": self.value.index[0].strftime("%Y-%m-%d %H:%M:%S")
        }

        if self.source is not None:
            output_dict["source"] = {"name": self.source.name, "link": self.source.link}

        if with_calculated_attributes_data:
            output_dict["id"] = self.id
            output_dict["direct_ancestors_with_id"] = [elt.id for elt in self.direct_ancestors_with_id]
            output_dict["direct_children_with_id"] = [elt.id for elt in self.direct_children_with_id]

        return output_dict

    def __repr__(self):
        return json.dumps(self.to_json(), cls=NpEncoder)

    def __str__(self):
        compact_unit = "{:~}".format(self.unit)
        str_rounded_values = ", ".join(
            [str(round(hourly_value.magnitude, 2)) for hourly_value in self.value["value"].tolist()])

        return f"in {compact_unit}: [{str_rounded_values}]"


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super(NpEncoder, self).default(obj)
