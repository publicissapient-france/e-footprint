import uuid
from abc import ABCMeta, abstractmethod
from typing import List, Set
from importlib import import_module
from footprint_model.logger import logger
from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject


def get_subclass_attributes(obj, target_class):
    return {attr_name: attr_value for attr_name, attr_value in obj.__dict__.items()
            if issubclass(type(attr_value), target_class)}


def check_type_homogeneity_within_list_or_set(input_list_or_set: List | Set):
    type_set = [type(value) for value in input_list_or_set]
    base_type = type(type_set[0])

    if not all(isinstance(item, base_type) for item in type_set):
        raise ValueError(
            f"There shouldn't be objects of different types within the same list, found {type_set}")
    else:
        return type_set.pop()


class AfterInitMeta(type):
    def __call__(cls, *args, **kwargs):
        instance = super(AfterInitMeta, cls).__call__(*args, **kwargs)
        instance.after_init()
        return instance


class ABCAfterInitMeta(ABCMeta, AfterInitMeta):
    pass


class ModelingObject(metaclass=ABCAfterInitMeta):
    def __init__(self, name):
        self.init_has_passed = False
        self.name = name
        self.id = f"{self.name} {str(uuid.uuid4())[:6]}"
        self.dont_handle_input_updates = False

    @abstractmethod
    def compute_calculated_attributes(self):
        pass

    def after_init(self):
        self.init_has_passed = True

    @staticmethod
    def handle_model_input_update(old_value_that_gets_updated: ExplainableObject):
        ancestors = old_value_that_gets_updated.get_all_ancestors_with_id()
        has_been_recomputed_dict = {ancestor.id: False for ancestor in ancestors}
        has_been_recomputed_dict[old_value_that_gets_updated.id] = True

        computed_children_with_parents_to_recompute = [old_value_that_gets_updated]

        while len(computed_children_with_parents_to_recompute) > 0:
            for recomputed_child in computed_children_with_parents_to_recompute:
                drop_recomputed_child_from_list = True
                for parent in recomputed_child.direct_parents_with_id:
                    if not has_been_recomputed_dict[parent.id]:
                        children_that_belong_to_ancestors = [
                            child for child in parent.direct_children_with_id
                            if child.id in [ancestor.id for ancestor in ancestors]]
                        if all([has_been_recomputed_dict[child.id] for child in children_that_belong_to_ancestors]):
                            parent_update_func_name = f"update_{parent.attr_name_in_mod_obj_container}"
                            parent_update_func = getattr(
                                parent.modeling_obj_container, parent_update_func_name, None)
                            if parent_update_func is None:
                                ValueError(
                                    f"{parent_update_func_name} function does not exist. Please create it and checkout "
                                    f"optimization.md")
                            else:
                                parent_update_func()
                                has_been_recomputed_dict[parent.id] = True
                                if len(parent.direct_parents_with_id) > 0:
                                    computed_children_with_parents_to_recompute.append(parent)
                        else:
                            # Wait for next iteration
                            drop_recomputed_child_from_list = False
                if drop_recomputed_child_from_list:
                    computed_children_with_parents_to_recompute = [
                        child for child in computed_children_with_parents_to_recompute
                        if child.id != recomputed_child.id]

    def __setattr__(self, name, input_value):
        old_value = self.__dict__.get(name, None)
        super().__setattr__(name, input_value)
        if name not in ["init_has_passed", "name", "id", "dont_handle_input_updates", "usage_patterns"]:
            logger.debug(f"attribute {name} updated in {self.name}")

        if issubclass(type(input_value), ExplainableObject) and not self.dont_handle_input_updates:
            if input_value.modeling_obj_container is not None and self.id != input_value.modeling_obj_container.id:
                raise ValueError(
                    f"An ExplainableObject can’t be linked attributed to more than one ModelingObject. Here "
                    f"{input_value.label} is trying to be linked to {self.name} but is already linked to "
                    f"{input_value.modeling_obj_container.name}."
                    f" A classic reason why this error could happen is that a mutable object (SourceValue for"
                    f" example) has been set as default value in one of the classes.")
            else:
                input_value.set_modeling_obj_container(self, name)

        if self.init_has_passed and not self.dont_handle_input_updates:
            if issubclass(type(input_value), ExplainableObject) and \
                    input_value.left_child is None and input_value.right_child is None and old_value is not None: # TODO: remove last condition after server update
                self.handle_model_input_update(old_value)
