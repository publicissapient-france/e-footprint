from efootprint.logger import logger
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict

import uuid
from abc import ABCMeta, abstractmethod
from typing import List, Set, Type


def get_subclass_attributes(obj, target_class):
    return {attr_name: attr_value for attr_name, attr_value in obj.__dict__.items()
            if issubclass(type(attr_value), target_class)}


def check_type_homogeneity_within_list_or_set(input_list_or_set):
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
        self.__dict__["dont_handle_input_updates"] = False
        self.init_has_passed = False
        self.name = name
        self.id = f"{self.name} {str(uuid.uuid4())[:6]}"
        self.modeling_obj_containers = []
        self.calculated_attributes = []

    @property
    @abstractmethod
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[Type["ModelingObject"]]:
        pass

    def compute_calculated_attributes(self):
        logger.info(f"Computing calculated attributes for {type(self).__name__} {self.name}")
        for attr_name in self.calculated_attributes:
            update_func = self.retrieve_update_function_from_attribute_name(self, attr_name)
            update_func()

        for modeling_obj in self.modeling_objects_whose_attributes_depend_directly_on_me:
            modeling_obj.compute_calculated_attributes()

    def after_init(self):
        self.init_has_passed = True

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if issubclass(type(other), ModelingObject):
            return self.id == other.id
        return False

    def __setattr__(self, name, input_value):
        old_value = self.__dict__.get(name, None)
        if self.dont_handle_input_updates:
            super().__setattr__(name, input_value)
        else:
            if issubclass(type(input_value), ModelingObject):
                input_value.add_obj_to_modeling_obj_containers(self)
                if not self.init_has_passed:
                    super().__setattr__(name, input_value)
                else:
                    self.handle_object_link_update(name, input_value, old_value)
            else:
                super().__setattr__(name, input_value)
            if issubclass(type(input_value), ExplainableObject):
                logger.debug(f"attribute {name} updated in {self.name}")
                input_value.set_modeling_obj_container(self, name)
                if self.init_has_passed and (
                        input_value.left_child is None and input_value.right_child is None and old_value is not None):
                    assert(issubclass(type(old_value), ExplainableObject))
                    self.handle_model_input_update(old_value)
            if isinstance(input_value, ExplainableObjectDict):
                logger.debug(f"attribute {name} updated in {self.name}")
                input_value.set_modeling_obj_container(self, name)

    @staticmethod
    def retrieve_update_function_from_attribute_name(mod_obj, attr_name):
        update_func_name = f"update_{attr_name}"
        update_func = getattr(mod_obj, update_func_name, None)

        if update_func is None:
            raise AttributeError(f"No update function associated to {attr_name} in {mod_obj.id}. "
                                 f"Please create it and checkout optimization.md")

        return update_func

    def handle_model_input_update(self, old_value_that_gets_updated: ExplainableObject):
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
                            parent_update_func = self.retrieve_update_function_from_attribute_name(
                                parent.modeling_obj_container, parent.attr_name_in_mod_obj_container)
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

    def handle_object_link_update(
            self, name: str, input_value: Type["ModelingObject"], old_value: Type["ModelingObject"]):
        if old_value is None:
            raise ValueError(f"A link update is trying to replace an null object")
        if (self in old_value.modeling_objects_whose_attributes_depend_directly_on_me and
            old_value in self.modeling_objects_whose_attributes_depend_directly_on_me):
            raise AssertionError(
                f"There is a circular recalculation dependency between {self.id} and {old_value.id}")
        if self in old_value.modeling_objects_whose_attributes_depend_directly_on_me:
            old_value.remove_obj_from_modeling_obj_containers(self)
            super().__setattr__(name, input_value)
            self.compute_calculated_attributes()
        else:
            old_value.remove_obj_from_modeling_obj_containers(self)
            super().__setattr__(name, input_value)
            input_value.compute_calculated_attributes()
            old_value.compute_calculated_attributes()

    def add_obj_to_modeling_obj_containers(self, new_obj):
        if new_obj not in self.modeling_obj_containers:
            if (len(self.modeling_obj_containers) > 0
                    and not isinstance(new_obj, type(self.modeling_obj_containers[0]))):
                raise ValueError(
                    f"There shouldn't be objects of different types within modeling_obj_containers for {self.name},"
                    f" found {type(new_obj)} and {type(self.modeling_obj_containers[0])}")
            self.modeling_obj_containers.append(new_obj)

    def remove_obj_from_modeling_obj_containers(self, obj_to_remove):
        self.modeling_obj_containers = [
            mod_obj for mod_obj in self.modeling_obj_containers if mod_obj != obj_to_remove]
