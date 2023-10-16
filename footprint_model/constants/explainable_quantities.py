from pint import Quantity
from typing import Dict


class ExplainableQuantity:
    def __init__(self, value: Quantity, formula: str, name_values_dict: Dict = None):
        if not isinstance(value, Quantity):
            raise ValueError(
                "Variable 'value' does not correspond to the appropriate 'Quantity' type, "
                "it is indeed mandatory to define a unit"
            )

        self.value = value
        self.formula = formula
        if name_values_dict is None:
            self.name_values_dict = {formula: value}
        else:
            self.name_values_dict = name_values_dict

    def __gt__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.value > other.value
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {other.type}")

    def __lt__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.value < other.value
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {other.type}")

    def __eq__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            return self.value == other.value
        else:
            raise ValueError(f"Can only compare with another ExplainableQuantity, not {type(other)}")

    def __add__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            new_values = self.name_values_dict.copy()
            new_values.update(other.name_values_dict)
            return ExplainableQuantity(self.value + other.value, f"{self.formula} + {other.formula}", new_values)
        elif other == 0:
            # summing with sum() adds an implicit 0 as starting value
            return self
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __sub__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            new_values = self.name_values_dict.copy()
            new_values.update(other.name_values_dict)
            return ExplainableQuantity(self.value - other.value, f"{self.formula} - {other.formula}", new_values)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __mul__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            new_values = self.name_values_dict.copy()
            new_values.update(other.name_values_dict)
            return ExplainableQuantity(self.value * other.value, f"{self.formula} * {other.formula}", new_values)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __truediv__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            new_values = self.name_values_dict.copy()
            new_values.update(other.name_values_dict)
            return ExplainableQuantity(self.value / other.value, f"(({self.formula}) / ({other.formula}))", new_values)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            new_values = self.name_values_dict.copy()
            new_values.update(other.name_values_dict)
            return ExplainableQuantity(other.value - self.value, f"{other.formula} - {self.formula}", new_values)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        if issubclass(type(other), ExplainableQuantity):
            new_values = self.name_values_dict.copy()
            new_values.update(other.name_values_dict)
            return ExplainableQuantity(other.value / self.value, f"(({other.formula}) / ({self.formula}))", new_values)
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __round__(self, round_level):
        self.value = round(self.value, round_level)
        return self

    def explain(self, pretty_print=False):
        formula_with_values = self.formula
        for var, val in self.name_values_dict.items():
            formula_with_values = formula_with_values.replace(var, str(val))
        calc_str = f"{self.formula} = {formula_with_values} = {self.value}"
        if pretty_print:
            self.pretty_print_calculation(calc_str)
        else:
            print(calc_str)

    def to(self, unit_to_convert_to):
        self.value = self.value.to(unit_to_convert_to)
        self.name_values_dict[self.formula] = self.value
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

        print(formatted_str)

