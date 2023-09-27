from footprint_model.logger import logger
from typing import Type
from copy import deepcopy


class ExplainableObject:
    def __init__(
            self, value: object, label: str = None, left_child: Type["ExplainableObject"] = None,
            right_child: Type["ExplainableObject"] = None, child_operator: str = None):
        self.value = value
        if not label and left_child is None and right_child is None:
            raise ValueError(f"ExplainableObject label shouldn’t be None if it doesn’t have any child")
        self.label = label
        self._pubsub_topic = None
        self.left_child = left_child
        self.right_child = right_child
        self.child_operator = child_operator
        self.input_attributes_to_listen_to = []
        self.attributes_that_depend_on_self = []

        for child in (self.left_child, self.right_child):
            if child is not None:
                self.input_attributes_to_listen_to += [
                    input_attribute for input_attribute in child.return_objects_to_listen_to_to_parent()
                    if input_attribute.pubsub_topic not in self.pubsub_topics_to_listen_to]

    def __deepcopy__(self, memo):
        cls = self.__class__
        new_instance = cls.__new__(cls, "dummy_value", "dummy_label")
        memo[id(self)] = new_instance

        for k, v in self.__dict__.items():
            if k not in ["_pubsub_topic", "input_attributes_to_listen_to", "attributes_that_depend_on_self"]:
                setattr(new_instance, k, deepcopy(v, memo))

        new_instance._pubsub_topic = None
        new_instance.input_attributes_to_listen_to = []
        new_instance.attributes_that_depend_on_self = []

        return new_instance

    @property
    def has_child(self):
        return self.left_child is not None or self.right_child is not None

    @property
    def pubsub_topic(self) -> str:
        return self._pubsub_topic

    @pubsub_topic.setter
    def pubsub_topic(self, new_pubsub_topic):
        self._pubsub_topic = new_pubsub_topic
        for input_attribute in self.input_attributes_to_listen_to:
            input_attribute.update_attributes_that_depend_on_self(depending_attribute=self)
        self.purge_input_attributes_to_listen_to()

    @property
    def pubsub_topics_to_listen_to(self):
        return [input_attribute.pubsub_topic for input_attribute in self.input_attributes_to_listen_to]

    @property
    def pubsub_topics_that_depend_on_self(self):
        return [attribute.pubsub_topic for attribute in self.attributes_that_depend_on_self]

    def return_objects_to_listen_to_to_parent(self):
        if self.pubsub_topic is not None:
            return [self]
        else:
            return self.input_attributes_to_listen_to

    def purge_input_attributes_to_listen_to(self):
        input_attrs_to_keep = []
        for i in range(len(self.input_attributes_to_listen_to)):
            current_input_attr = self.input_attributes_to_listen_to[i]
            untreated_input_attrs = self.input_attributes_to_listen_to[
                               min(len(self.input_attributes_to_listen_to) - 1, i + 1):]
            keep_input_attr = True
            for input_attr in untreated_input_attrs + input_attrs_to_keep:
                if input_attr.pubsub_topic in current_input_attr.pubsub_topics_that_depend_on_self:
                    keep_input_attr = False
                    logger.debug(
                        f"Not keeping {current_input_attr.pubsub_topic} for {self.label} to listen to because "
                        f"{input_attr.pubsub_topic} already depends on it")
            if keep_input_attr:
                input_attrs_to_keep.append(current_input_attr)

        self.input_attributes_to_listen_to = input_attrs_to_keep

    def update_attributes_that_depend_on_self(self, depending_attribute):
        if depending_attribute.pubsub_topic not in self.pubsub_topics_that_depend_on_self:
            self.attributes_that_depend_on_self.append(depending_attribute)
        for input_attribute in self.input_attributes_to_listen_to:
            input_attribute.update_attributes_that_depend_on_self(depending_attribute=depending_attribute)

    def define_as_intermediate_calculation(self, intermediate_calculation_label):
        self.label = intermediate_calculation_label

        return self

    def explain(self, pretty_print=True):
        element_value_to_print = self.print_tuple_element_value(self.value)

        if self.left_child is None and self.right_child is None:
            return f"{self.label} = {element_value_to_print}"
        explain_tuples = self.compute_explain_nested_tuples()

        if pretty_print:
            return self.pretty_print_calculation(
                f"{self.label} = {self.print_tuple_element(explain_tuples, print_values_instead_of_labels=False)}"
                f" = {self.print_tuple_element(explain_tuples, print_values_instead_of_labels=True)}"
                f" = {element_value_to_print}")
        else:
            return f"{self.label} = {self.print_tuple_element(explain_tuples, print_values_instead_of_labels=False)}" \
                f" = {self.print_tuple_element(explain_tuples, print_values_instead_of_labels=True)}" \
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

    def print_tuple_element(self, tuple_element: object, print_values_instead_of_labels: bool):
        if issubclass(type(tuple_element), ExplainableObject):
            if print_values_instead_of_labels:
                return self.print_tuple_element_value(tuple_element.value)
            else:
                return f"{tuple_element.label}"
        elif type(tuple_element) == str:
            return tuple_element
        elif type(tuple_element) == tuple:
            if tuple_element[1] is None:
                return f"{self.print_tuple_element(tuple_element[0], print_values_instead_of_labels)}"
            if tuple_element[2] is None:
                return f"{tuple_element[1]}" \
                       f" of ({self.print_tuple_element(tuple_element[0], print_values_instead_of_labels)})"

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
            elif tuple_element[1] == "-":
                if type(tuple_element[2]) == tuple and tuple_element[2][1] in ["+", "-"]:
                    right_parenthesis = True
            elif tuple_element[1] == "+":
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

            return f"{lp_open}{self.print_tuple_element(tuple_element[0], print_values_instead_of_labels)}{lp_close}" \
                   f" {tuple_element[1]}" \
                   f" {rp_open}{self.print_tuple_element(tuple_element[2], print_values_instead_of_labels)}{rp_close}"

    @staticmethod
    def pretty_print_calculation(calc_str):
        return calc_str.replace(" = ", "\n=\n")
