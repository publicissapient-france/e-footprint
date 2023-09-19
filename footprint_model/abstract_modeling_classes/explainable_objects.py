import numbers
from datetime import datetime
from typing import Type, List

import pytz
from pint import Quantity

from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from footprint_model.constants.units import u


class ExplainableQuantity(ExplainableObject):
    def __init__(
            self, value: Quantity, label: str = "no label", left_child: Type["ExplainableQuantity"] = None,
            right_child: Type["ExplainableQuantity"] = None, child_operator: str = None):
        if not isinstance(value, Quantity):
            raise ValueError(
                f"Variable 'value' of type {type(value)} does not correspond to the appropriate 'Quantity' type, "
                "it is indeed mandatory to define a unit"
            )
        super().__init__(value, label, left_child, right_child, child_operator)

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
            return self
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value + other.value, "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return self
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

    def to(self, unit_to_convert_to):
        self.value = self.value.to(unit_to_convert_to)

        return self

    @property
    def magnitude(self):
        return self.value.magnitude


class ExplainableHourlyUsage(ExplainableObject):
    def __init__(
            self, value: List[ExplainableQuantity], label: str = "no label", left_child: ExplainableObject = None,
            right_child: ExplainableObject = None, child_operator: str = None):
        super().__init__(value, label, left_child, right_child, child_operator)

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
            if type(elt) != ExplainableQuantity:
                raise ValueError("compute_usage_time_fraction should be called on ExplainableQuantity elements")
            else:
                if elt.magnitude == 0:
                    unused_hours += 1

        return ExplainableQuantity(
            ((24 - unused_hours) / 24) * u.dimensionless, "", self, None, "usage time fraction computation")

    def to_usage(self):
        usage_hours = []
        for i, elt in enumerate(self.value):
            if type(elt) != ExplainableQuantity:
                raise ValueError("to_usage method should be called with ExplainableQuantity elements")
            if elt.magnitude != 0:
                usage_hours.append(ExplainableQuantity(1 * u.dimensionless, f"Usage between {i} and {i + 1}"))
            else:
                usage_hours.append(ExplainableQuantity(0 * u.dimensionless, f" Non usage between {i} and {i + 1}"))

        return ExplainableHourlyUsage(usage_hours, "", left_child=self, child_operator="retrieving usage hours")

    def sum(self):
        result = sum(self.value)
        result.left_child = self
        result.right_child = None
        result.child_operator = "sum"

        return result

    def mean(self):
        result = sum(self.value) / ExplainableQuantity(24 * u.dimensionless, "24 hours in a day")
        result.left_child = self
        result.right_child = None
        result.child_operator = "mean"

        return result

    def max(self):
        result = max(self.value)
        result.left_child = self
        result.right_child = None
        result.child_operator = "max"

        return result

    def __add__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return self
        elif issubclass(type(other), ExplainableHourlyUsage):
            return ExplainableHourlyUsage(
                [elt1 + elt2 for elt1, elt2 in zip(self.value, other.value)], "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return self
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
            return ExplainableHourlyUsage([other * elt for elt in self.value], "", self, other, "*")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, not with {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyUsage([elt / other for elt in self.value], "", self, other, "/")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, not with {type(other)}")

    def __rtruediv__(self, other):
        if issubclass(type(other), ExplainableHourlyUsage):
            raise NotImplementedError
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableHourlyUsage([other / elt for elt in self.value], "", other, self, "/")
        else:
            raise ValueError(
                f"Can only make operation with another ExplainableHourlyUsage or ExplainableQuantity, not with {type(other)}")