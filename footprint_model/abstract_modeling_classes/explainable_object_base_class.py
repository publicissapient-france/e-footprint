from abc import ABC, abstractmethod
from typing import List, Type


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

    @property
    def has_child(self):
        return self.left_child is not None or self.right_child is not None

    def define_as_intermediate_calculation(self, intermediate_calculation_label):
        self.height_level += 1
        self.label = intermediate_calculation_label

        return self

    @property
    def pubsub_topics_to_listen_to(self):
        return [input_attribute.pubsub_topic for input_attribute in self.input_attributes_to_listen_to]

    def explain(self, pretty_print=True):
        element_value_to_print = self.print_tuple_element_value(self.value)

        if self.left_child is None and self.right_child is None:
            return f"{self.label} = {element_value_to_print}"
        explain_tuples = self.compute_explain_nested_tuples()

        if pretty_print:
            return self.pretty_print_calculation(
                f"{self.label} = {self.print_tuple_element(explain_tuples, values=False)}"
                f" = {self.print_tuple_element(explain_tuples, values=True)}"
                f" = {element_value_to_print}")
        else:
            return f"{self.label} = {self.print_tuple_element(explain_tuples, values=False)}" \
                f" = {self.print_tuple_element(explain_tuples, values=True)}" \
                f" = {element_value_to_print}"

    def compute_explain_nested_tuples(self, return_label_if_self_has_one=False):
        if return_label_if_self_has_one and self.label:
            return self

        left_explanation = None
        right_explanation = None

        if self.left_child:
            left_explanation = self.left_child.compute_explain_nested_tuples(return_label_if_self_has_one=True)
        if self.right_child:
            right_explanation = self.right_child.compute_explain_nested_tuples(return_label_if_self_has_one=True)

        if left_explanation is None and right_explanation is None:
            raise ValueError("Object to explain should have at least one child")

        return left_explanation, self.child_operator, right_explanation

    @staticmethod
    def print_tuple_element_value(tuple_element_value):
        if type(tuple_element_value) == list:
            if type(tuple_element_value[0]) == list:
                return f"{tuple_element_value}"
            else:
                output_values = []
                for expl_quant in tuple_element_value:
                    output_values.append(f"{round(expl_quant.value, 1):~P}")
                return f"[{', '.join(output_values)}]"
        else:
            try:
                return f"{round(tuple_element_value, 1):~P}"
            except:
                return f"{tuple_element_value}"

    def print_tuple_element(self, tuple_element, values):
        if issubclass(type(tuple_element), ExplainableObject):
            if values:
                return self.print_tuple_element_value(tuple_element.value)
            else:
                return f"{tuple_element.label}"
        elif type(tuple_element) == str:
            return tuple_element
        elif type(tuple_element) == tuple:
            if tuple_element[2] is None:
                return f"{tuple_element[1]}" \
                       f" of ({self.print_tuple_element(tuple_element[0], values)})"

            left_parenthesis = False
            right_parenthesis = False

            if tuple_element[1] == "/":
                if type(tuple_element[2]) == tuple:
                    right_parenthesis = True
                if type(tuple_element[0]) == tuple and tuple_element[0][1] != "*":
                    left_parenthesis = True
            elif tuple_element[1] == "*":
                if type(tuple_element[0]) == tuple and tuple_element[0][1] != "*":
                    left_parenthesis = True
                if type(tuple_element[2]) == tuple and tuple_element[2][1] != "*":
                    right_parenthesis = True
            elif tuple_element[1] in ["+", "-"]:
                pass

            lp_open = ""
            lp_close = ""
            rp_open = ""
            rp_close = ""

            if left_parenthesis:
                lp_open = "("
                lp_close = ")"
            if right_parenthesis:
                rp_open = "("
                rp_close = ")"

            return f"{lp_open}{self.print_tuple_element(tuple_element[0], values)}{lp_close}" \
                   f" {tuple_element[1]}" \
                   f" {rp_open}{self.print_tuple_element(tuple_element[2], values)}{rp_close}"

    @staticmethod
    def pretty_print_calculation(calc_str):
        formatted_str = ""

        for char in calc_str:
            if char == '=' and formatted_str[-1] == ' ':
                formatted_str = formatted_str[:-1] + '\n=\n'
            else:
                formatted_str += char

        return formatted_str
