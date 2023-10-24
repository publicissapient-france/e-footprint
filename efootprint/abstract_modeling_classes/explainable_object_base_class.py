from efootprint.logger import logger

from typing import Type
from abc import ABC, abstractmethod


class ObjectLinkedToModelingObj(ABC):
    def __init__(self):
        self.modeling_obj_container = None
        self.attr_name_in_mod_obj_container = None

    @abstractmethod
    def set_modeling_obj_container(self, new_parent_modeling_object: Type["ModelingObject"], attr_name: str):
        pass


class ExplainableObject(ObjectLinkedToModelingObj):
    def __init__(
            self, value: object, label: str = None, left_child: Type["ExplainableObject"] = None,
            right_child: Type["ExplainableObject"] = None, child_operator: str = None):
        super().__init__()
        self.value = value
        if not label and left_child is None and right_child is None:
            raise ValueError(f"ExplainableObject label shouldn’t be None if it doesn’t have any child")
        self.label = label
        self.left_child = left_child
        self.right_child = right_child
        self.child_operator = child_operator
        self.direct_children_with_id = []
        self.direct_parents_with_id = []

        for child in (self.left_child, self.right_child):
            if child is not None:
                self.direct_children_with_id += [
                    child_with_id for child_with_id in child.return_direct_children_with_id_to_parent()
                    if child_with_id.id not in self.direct_children_ids]

    def __deepcopy__(self, memo):
        cls = self.__class__
        new_instance = cls.__new__(cls, "dummy_value", "dummy_label")
        new_instance.__init__(self.value, self.label)

        if getattr(self, "source", None) is not None:
            new_instance.source = self.source

        return new_instance

    @property
    def id(self):
        if self.modeling_obj_container is None:
            raise ValueError(
                f"{self.label} doesn’t have a modeling_obj_container, hence it makes no sense "
                f"to look for its ancestors")
        return f"{self.attr_name_in_mod_obj_container} in {self.modeling_obj_container.name}" \
               f" ({self.modeling_obj_container.id})"

    @property
    def has_child(self):
        return self.left_child is not None or self.right_child is not None

    @property
    def direct_children_ids(self):
        return [attr.id for attr in self.direct_children_with_id]

    @property
    def direct_parents_ids(self):
        return [attr.id for attr in self.direct_parents_with_id]

    def set_modeling_obj_container(self, new_parent_modeling_object: Type["ModelingObject"], attr_name: str):
        if not self.label:
            raise ValueError(f"ExplainableObjects that are attributes of a ModelingObject should always have a label.")
        if self.modeling_obj_container is not None and new_parent_modeling_object.id != self.modeling_obj_container.id:
            logger.warning(
                f"Linking {self.label} to {new_parent_modeling_object.name}, erasing its existing link to "
                f"{self.modeling_obj_container.name}.")
            if self.left_child is not None or self.right_child is not None:
                raise ValueError(
                    f"An ExplainableObject with child can’t be attributed to more than one ModelingObject. Here "
                    f"{self.label} is trying to be linked to {new_parent_modeling_object.name} but is already linked to"
                    f" {self.modeling_obj_container.name}."
                    f" A classic reason why this error could happen is that a mutable object (SourceValue for"
                    f" example) has been set as default value in one of the classes.")
        self.modeling_obj_container = new_parent_modeling_object
        self.attr_name_in_mod_obj_container = attr_name
        for direct_child_with_id in self.direct_children_with_id:
            direct_child_with_id.update_direct_parents_with_id(direct_parent=self)

    def return_direct_children_with_id_to_parent(self):
        if self.modeling_obj_container is not None:
            return [self]
        else:
            return self.direct_children_with_id

    def update_direct_parents_with_id(self, direct_parent):
        if direct_parent.id not in self.direct_parents_ids:
            self.direct_parents_with_id.append(direct_parent)

    def define_as_intermediate_calculation(self, intermediate_calculation_label):
        self.label = intermediate_calculation_label

        return self

    def get_all_ancestors_with_id(self):
        all_ancestors = []

        def retrieve_ancestors(expl_obj: ExplainableObject, ancestors_list):
            for parent in expl_obj.direct_parents_with_id:
                if parent.id not in [elt.id for elt in ancestors_list]:
                    ancestors_list.append(parent)
                retrieve_ancestors(parent, ancestors_list)

        retrieve_ancestors(self, all_ancestors)

        return all_ancestors

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
