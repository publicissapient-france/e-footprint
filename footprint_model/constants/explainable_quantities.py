from footprint_model.utils.tools import flatten_list
from footprint_model.constants.units import u

import numbers
import uuid
from abc import ABC, abstractmethod
from pint import Quantity
from typing import Type, List
from pubsub import pub
import inspect
from datetime import datetime
import pytz
import logging


DEFAULT_ROUNDING_LEVEL = 2


class UpdateFunctionOutput(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def pubsub_topics_to_listen_to(self) -> List[str]:
        pass


class AttributeUsedInCalculation:
    def __init__(self):
        self.pubsub_topic = None


class ExplainableObject(AttributeUsedInCalculation, UpdateFunctionOutput):
    def __init__(
            self, value: object, label: str = "no label", left_child: Type["ExplainableObject"] = None, 
            right_child: Type["ExplainableObject"] = None, child_operator: str = None):
        super().__init__()
        self.value = value
        self.label = label
        left_child_height_level = left_child.height_level if left_child is not None else 0
        right_child_height_level = right_child.height_level if right_child is not None else 0
        self.height_level = max(left_child_height_level, right_child_height_level)
        self.left_child = left_child
        self.right_child = right_child
        self.child_operator = child_operator
        self.input_attributes_to_listen_to = []
        for child in (self.left_child, self.right_child):
            if child is not None:
                if child.pubsub_topic is not None:
                    self.input_attributes_to_listen_to.append(child)
                else:
                    self.input_attributes_to_listen_to += child.input_attributes_to_listen_to

    def define_as_intermediate_calculation(self, intermediate_calculation_label):
        self.height_level += 1
        self.label = intermediate_calculation_label

        return self

    @property
    def pubsub_topics_to_listen_to(self):
        return [input_attribute.pubsub_topic for input_attribute in self.input_attributes_to_listen_to]

    def explain(self):
        if self.left_child and self.right_child:  # Checks if there are child nodes
            left_explanation = self.left_child.explain()
            right_explanation = self.right_child.explain()

            return f"({left_explanation} {self.child_operator} {right_explanation})"
        else:
            return self.label


class ExplainableQuantity(ExplainableObject):
    def __init__(
            self, value: Quantity, label: str = "no label", left_child: Type["ExplainableQuantity"] = None,
            right_child: Type["ExplainableQuantity"] = None, child_operator: str = None):
        if not isinstance(value, Quantity):
            raise ValueError(
                "Variable 'value' does not correspond to the appropriate 'Quantity' type, "
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
            return ExplainableQuantity(self.value, "", left_child=self, child_operator="add 0")
        elif issubclass(type(other), ExplainableQuantity):
            return ExplainableQuantity(self.value + other.value, "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableQuantity, not with {type(other)}")

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return ExplainableQuantity(self.value, "", left_child=self, child_operator="subtract 0")
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

    def explain(self):
        if self.left_child and self.right_child:  # Checks if there are child nodes
            left_explanation = self.left_child.explain()
            right_explanation = self.right_child.explain()

            return f"({left_explanation} {self.child_operator} {right_explanation})"
        else:
            return self.label

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
            self.value[time_diff_in_hours:] + self.value[:time_diff_in_hours], "convert to utc",
            left_child=local_timezone, right_child=self, child_operator="conversion to utc time hourly usage")

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
                usage_hours.append(ExplainableQuantity(1 * u.dimensionless, f"Usage between {i} and {i+1}"))
            else:
                usage_hours.append(ExplainableQuantity(0 * u.dimensionless, f" Non usage between {i} and {i+1}"))

        return ExplainableHourlyUsage(usage_hours, "", left_child=self, child_operator="retrieving usage hours")

    def sum(self):
        result = sum(self.value)
        result.left_child = self
        result.right_child = None
        result.child_operator = "sum of values in ExplainableHourlyUsage object"

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
            return ExplainableHourlyUsage(self.value, "", left_child=self, child_operator="add 0")
        elif issubclass(type(other), ExplainableHourlyUsage):
            return ExplainableHourlyUsage(
                [elt1 + elt2 for elt1, elt2 in zip(self.value, other.value)], "", self, other, "+")
        else:
            raise ValueError(f"Can only make operation with another ExplainableHourlyUsage, not with {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if issubclass(type(other), numbers.Number) and other == 0:
            return ExplainableHourlyUsage(self.value, "", left_child=self, child_operator="subtract 0")
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


def get_subclass_attributes(obj, target_class):
    return {attr_name: attr_value for attr_name, attr_value in obj.__dict__.items()
            if issubclass(type(attr_value), target_class)}


def recursively_send_pubsub_message_for_every_attribute_used_in_calculation(old_attribute_value: List):
    for obj in old_attribute_value:
        for attr_name, attr_value in get_subclass_attributes(obj, AttributeUsedInCalculation).items():
            pub.sendMessage(attr_value.pubsub_topic)
        for modeling_object, modeling_object_name in get_subclass_attributes(obj, ModelingObject).items():
            recursively_send_pubsub_message_for_every_attribute_used_in_calculation([modeling_object])


def convert_to_list(input_value):
    if type(input_value) == list:
        value_elts = flatten_list(input_value)
    elif type(input_value) == set:
        value_elts = flatten_list(list(input_value))
    else:
        value_elts = [input_value]

    return value_elts


class ModelingObject(ABC):
    def __init__(self, name):
        self.__dict__["name"] = name
        self.__dict__["id"] = str(uuid.uuid4())[:6]

    @abstractmethod
    def compute_calculated_attributes(self):
        pass

    def __setattr__(self, name, input_value):
        old_value = self.__dict__.get(name, None)
        super().__setattr__(name, input_value)
        value_elts = convert_to_list(input_value)

        current_pubsub_topic = f"{name}_in_{self.name}_{self.id}"
        for value in value_elts:
            if issubclass(type(value), AttributeUsedInCalculation):
                value.pubsub_topic = current_pubsub_topic

        # Get caller function info
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        info = inspect.getframeinfo(caller_frame)

        if info.function != "__init__":
            type_set = [type(value) for value in value_elts]
            base_type = type(type_set[0])

            if not all(isinstance(item, base_type) for item in type_set):
                raise ValueError(
                    f"There shouldn't be objects of different types within the same list, found {type_set}")
            else:
                values_type = type_set.pop()
            if issubclass(values_type, AttributeUsedInCalculation):
                pub.sendMessage(current_pubsub_topic)
            if issubclass(values_type, UpdateFunctionOutput):
                update_func = getattr(self, f"update_{name}", None)
                if update_func is None and (input_value.left_child is not None or input_value.right_child is not None):
                    # TODO: Create doc optimization.md
                    raise ValueError(
                        f"update_{name} function does not exist. Please create it and checkout optimization.md")
                elif update_func is not None:
                    # TODO: if value is ExplainableQuantity check that left child and right child are not None (raise value error)
                    pubsub_topics_to_listen_to = set(
                        sum((value.pubsub_topics_to_listen_to for value in value_elts), start=[]))
                    for pubsub_topic in pubsub_topics_to_listen_to:
                        # TODO: Also unsubscribe from all old_value topics before subscribing
                        pub.subscribe(update_func, pubsub_topic)
                    logging.debug(f"Subscribed update_{name} to {pubsub_topics_to_listen_to}")
            elif issubclass(values_type, ModelingObject):
                if old_value is not None and old_value != input_value:
                    old_value_elts = convert_to_list(old_value)
                    disappearing_objects = [obj for obj in old_value_elts if obj not in value_elts]
                    for obj in disappearing_objects:
                        recursively_send_pubsub_message_for_every_attribute_used_in_calculation([obj])
                logging.info(f"Computing calculated attributes for {self.name}")
                self.compute_calculated_attributes()


class NonQuantityUsedInCalculation(AttributeUsedInCalculation):
    def __init__(self, value=None):
        super().__init__()
        self.value = value

    def get_calling_function(self):
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back
        calling_function_name = inspect.getframeinfo(caller_frame).function
        if calling_function_name.startswith("update_"):
            instance_in_prev_frame = caller_frame.f_locals.get("self")
            method_obj = getattr(instance_in_prev_frame, calling_function_name, None)
            pubsub_topic_to_listen_to = self.pubsub_topic
            pub.subscribe(method_obj, pubsub_topic_to_listen_to)
            print(f"CALLING FUNC - Subscribed {calling_function_name} to {pubsub_topic_to_listen_to}")

    def __get__(self, instance, owner):
        self.get_calling_function()

        return self.value

    def __set__(self, instance, value):
        self.value = value

    def __iter__(self):
        self.get_calling_function()

        return iter(self.value)

    def __len__(self):
        self.get_calling_function()

        if type(self.value) == bool:
            return int(self.value)

        return len(self.value)
