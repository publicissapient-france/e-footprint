from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject, Source
from efootprint.constants.units import u

import numbers
from datetime import datetime
from typing import Type, List
import pytz
from pint import Quantity
import json


class ExplainableQuantity(ExplainableObject):
    def __init__(
            self, value: Quantity, label: str = None, left_child: Type["ExplainableQuantity"] = None,
            right_child: Type["ExplainableQuantity"] = None, child_operator: str = None, source: Source = None):
        if not isinstance(value, Quantity):
            raise ValueError(
                f"Variable 'value' of type {type(value)} does not correspond to the appropriate 'Quantity' type, "
                "it is indeed mandatory to define a unit"
            )
        super().__init__(value, label, left_child, right_child, child_operator, source)

    def to(self, unit_to_convert_to):
        self.value = self.value.to(unit_to_convert_to)

        return self

    @property
    def magnitude(self):
        return self.value.magnitude

    def compare_with_and_return_max(self, other):
        if issubclass(type(other), ExplainableQuantity):
            if self.value >= other.value:
                return ExplainableQuantity(self.value, left_child=self, right_child=other, child_operator="max")
            else:
                return ExplainableQuantity(other.value, left_child=self, right_child=other, child_operator="max")
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {type(other)}")

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
            return ExplainableQuantity(self.value, left_child=self)
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value + other.value, "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return ExplainableQuantity(self.value, left_child=self)
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value - other.value, "", self, other, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __mul__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value * other.value, "", self, other, "*")
        elif issubclass(type(other), ExplainableHourlyUsage):
            return other.__mul__(self)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value / other.value, "", self, other, "/")
        elif issubclass(type(other), ExplainableHourlyUsage):
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
        if issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(other.value / self.value, "", other, self, "/")
        elif issubclass(type(other), ExplainableHourlyUsage):
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
        return f"{round(self.value, 2)}"


class ExplainableHourlyUsage(ExplainableObject):
    def __init__(
            self, value: List[Quantity], label: str = None, left_child: ExplainableObject = None,
            right_child: ExplainableObject = None, child_operator: str = None, source: Source = None):
        super().__init__(value, label, left_child, right_child, child_operator, source)

    def convert_to_utc(self, local_timezone):
        utc_tz = pytz.timezone('UTC')
        current_time = datetime.now()
        time_diff = (local_timezone.value.utcoffset(current_time) - utc_tz.utcoffset(current_time))
        time_diff_in_hours = int(time_diff.total_seconds() / 3600)

        return ExplainableHourlyUsage(
            self.value[time_diff_in_hours:] + self.value[:time_diff_in_hours], "",
            left_child=self, right_child=local_timezone, child_operator="converted to UTC from")

    def compute_usage_time_fraction(self):
        unused_hours = 0
        for elt in self.value:
            if not issubclass(type(elt), Quantity):
                raise ValueError("compute_usage_time_fraction should be called on pint Quantity elements")
            else:
                if elt.magnitude == 0:
                    unused_hours += 1

        return ExplainableQuantity(
            ((24 - unused_hours) / 24) * u.dimensionless, "", self, None, "usage time fraction computation")

    def to_usage(self):
        usage_hours = []
        for i, elt in enumerate(self.value):
            if not issubclass(type(elt), Quantity):
                raise ValueError("to_usage method should be called with pint Quantity elements")
            if elt.magnitude != 0:
                usage_hours.append(1 * u.dimensionless)
            else:
                usage_hours.append(0 * u.dimensionless)

        return ExplainableHourlyUsage(usage_hours, "", left_child=self, child_operator="retrieving usage hours")

    def sum(self):
        return ExplainableQuantity(sum(self.value), left_child=self, child_operator="sum")

    def mean(self):
        return ExplainableQuantity(sum(self.value) / 24, left_child=self, child_operator="mean")

    def max(self):
        return ExplainableQuantity(max(self.value), left_child=self, child_operator="max")

    def __eq__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            if len(self.value) != len(other.value):
                raise ValueError(
                    f"Can only compare ExplainableHourlyUsages with values of same length. Here we are trying to "
                    f"compare {self.value} and {other.value}.")
            return_bool = True
            for i in range(len(self.value)):
                if self.value[i] != other.value[i]:
                    return_bool = False
            return return_bool
        else:
            raise ValueError(f"Can only compare with another ExplainableHourlyUsage, not {type(other)}")

    def __add__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return ExplainableHourlyUsage(self.value, left_child=self)
        elif issubclass(type(other), ExplainableHourlyUsage):
            return ExplainableHourlyUsage(
                [elt1 + elt2 for elt1, elt2 in zip(self.value, other.value)], "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return ExplainableHourlyUsage(self.value, left_child=self)
        elif issubclass(type(other), ExplainableHourlyUsage):
            return ExplainableHourlyUsage(
                [elt1 - elt2 for elt1, elt2 in zip(self.value, other.value)], "", self, other, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __rsub__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            return ExplainableHourlyUsage(
                [elt1 - elt2 for elt1, elt2 in zip(other.value, self.value)], "", other, self, "-")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __mul__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyUsage([other.value * elt for elt in self.value], "", self, other, "*")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, not with {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyUsage([elt / other.value for elt in self.value], "", self, other, "/")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, not with {type(other)}")

    def __rtruediv__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyUsage([other.value / elt for elt in self.value], "", other, self, "/")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, not with {type(other)}")

    def to_json(self, with_calculated_attributes_data=False):
        output_dict = {
            "label": self.label, "values": [elt.magnitude for elt in self.value], "unit": str(self.value[0].units)}

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
        return ("[" + ", ".join([str(round(hourly_value, 2)) for hourly_value in self.value]) + "]").replace(
            "dimensionless", "")
