import numbers

from pint import Quantity
from typing import Type

from copy import deepcopy

DEFAULT_ROUNDING_LEVEL = 2


class ExplainableQuantity:
    def __init__(
            self, value: Quantity, label: str = "no label",  height_level: int = 0,
            left_child: Type["ExplainableQuantity"] = None, right_child: Type["ExplainableQuantity"] = None,
            child_operator: str = None):
        if not isinstance(value, Quantity):
            raise ValueError(
                "Variable 'value' does not correspond to the appropriate 'Quantity' type, "
                "it is indeed mandatory to define a unit"
            )

        self.value = value
        self.label = label
        self.height_level = height_level
        self.left_child = left_child
        self.right_child = right_child
        self.child_operator = child_operator

    def define_as_intermediate_calculation(self, intermediate_calculation_label):
        self.height_level += 1
        self.label = intermediate_calculation_label

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

    @staticmethod
    def compute_operation(left_child, right_child, operator, return_value):
        highest_height_level = max(left_child.height_level, right_child.height_level)

        return ExplainableQuantity(
            return_value, label="", height_level=highest_height_level, left_child=left_child, right_child=right_child,
            child_operator=operator)

    def __add__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return self
        elif issubclass(type(other), ExplainableQuantity):
            if self.magnitude == 0:
                return other
            elif other.magnitude == 0:
                return self
            else:
                return self.compute_operation(self, other, "+", self.value + other.value)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return self
        elif issubclass(type(other), ExplainableQuantity):
            if self.magnitude == 0:
                return other
            elif other.magnitude == 0:
                return self
            else:
                return self.compute_operation(self, other, "-", self.value - other.value)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __mul__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.compute_operation(self, other, "*", self.value * other.value)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.compute_operation(self, other, "/", self.value / other.value)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.compute_operation(other, self, "-", other.value - self.value)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.compute_operation(other, self, "/", other.value / self.value)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __round__(self, round_level):
        self.value = round(self.value, round_level)
        return self

    @staticmethod
    def _replace_values_in_formula(formula, values_dict):
        formula_with_values = formula
        for var, val in values_dict.items():
            formula_with_values = formula_with_values.replace(var, str(val))

        return formula_with_values

    def explain(self, pretty_print=True):
        highest_height_level = max(self.formulas.keys())
        calc_str = "## High-level formula:\n\n"

        if highest_height_level > 0:
            for height_level in range(highest_height_level, 0, -1):
                if height_level != highest_height_level:
                    calc_str += f"\n\n#### with {', '.join(list(self.name_values_dict[height_level].keys()))} defined as:\n"
                for int_calc in self.name_values_dict[height_level].keys():
                    calc_str += f"\n##### {int_calc}:\n"
                    int_calc_formula = self.name_formulas_dict[height_level][int_calc]
                    formula_with_values = int_calc_formula
                    for int_height_level in range(height_level, -1, -1):
                        formula_with_values = self._replace_values_in_formula(
                            formula_with_values, self.name_values_dict[int_height_level])
                    intermediate_formula = f"{int_calc} = {int_calc_formula} = {formula_with_values} " \
                                           f"= {round(self.name_values_dict[height_level][int_calc], DEFAULT_ROUNDING_LEVEL)}\n"

                    if pretty_print and height_level >= 1:
                        calc_str += self.pretty_print_calculation(intermediate_formula)
                    else:
                        calc_str += intermediate_formula
        else:
            formula = self.formulas[0]
            formula_with_values = self._replace_values_in_formula(formula, self.name_values_dict[0])

            calc_str += f"{formula} = {formula_with_values} = {round(self.value, DEFAULT_ROUNDING_LEVEL)}"

        return calc_str

    def to(self, unit_to_convert_to):
        self.value = self.value.to(unit_to_convert_to)

        return self

    @property
    def magnitude(self):
        return self.value.magnitude

    @staticmethod
    def pretty_print_calculation(calc_str):
        indentation_level = 0
        formatted_str = ""

        for char in calc_str:
            if char == '(':
                indentation_level += 1
                formatted_str += '\n' + '    ' * (indentation_level - 1) + char
            elif char == ')':
                formatted_str += char + '\n' + '    ' * (indentation_level - 2)
                indentation_level -= 1
            elif char == '=' and formatted_str[-1] == ' ':
                formatted_str = formatted_str[:-1] + '\n' + '    ' * (
                    max(indentation_level - 2, 0)) + '=' + '\n' + '    ' * (max(indentation_level - 2, 0))
            else:
                formatted_str += char

        return formatted_str


def intermediate_calculation(intermediate_calculation_label):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            result.define_as_intermediate_calculation(f"{intermediate_calculation_label} in {self.name}")
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    from footprint_model.constants.units import u
    a = ExplainableQuantity(1 * u.W, "1 Watt")
    b = ExplainableQuantity(2 * u.W, "2 Watt")
    c = a + b
    c.define_as_intermediate_calculation("power")
    d = ExplainableQuantity(3 * u.W, "other power")
    e = c + d
    e.explain()
    e.explain(height_level=1)
    e.define_as_intermediate_calculation("2nd level int calc")
    f = e + a
    f.explain()
    f.explain(1)
    f.explain(2)