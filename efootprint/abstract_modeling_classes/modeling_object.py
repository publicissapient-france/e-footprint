from efootprint.logger import logger
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.utils.graph_tools import WIDTH, HEIGHT
from efootprint.utils.object_relationships_graphs import build_object_relationships_graph, \
    USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE
from efootprint.utils.tools import convert_to_list

import uuid
from abc import ABCMeta, abstractmethod
from typing import List, Type
from copy import copy
import os


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

    # TODO: add abstractmethod self_delete

    def compute_calculated_attributes(self):
        logger.info(f"Computing calculated attributes for {type(self).__name__} {self.name}")
        for attr_name in self.calculated_attributes:
            update_func = self.retrieve_update_function_from_attribute_name(self, attr_name)
            update_func()

    def launch_attributes_computation_chain(self):
        self.compute_calculated_attributes()

        mod_objs_with_attributes_to_compute = self.modeling_objects_whose_attributes_depend_directly_on_me

        while len(mod_objs_with_attributes_to_compute) > 0:
            current_mod_obj_to_update = mod_objs_with_attributes_to_compute[0]
            current_mod_obj_to_update.compute_calculated_attributes()
            mod_objs_with_attributes_to_compute = mod_objs_with_attributes_to_compute[1:]

            for mod_obj in current_mod_obj_to_update.modeling_objects_whose_attributes_depend_directly_on_me:
                if mod_obj not in mod_objs_with_attributes_to_compute:
                    mod_objs_with_attributes_to_compute.append(mod_obj)

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
        super().__setattr__(name, input_value)
        if getattr(self, "name", None) is not None:
            logger.debug(f"attribute {name} updated in {self.name}")

        if not self.dont_handle_input_updates:
            if issubclass(type(input_value), ModelingObject):
                input_value.add_obj_to_modeling_obj_containers(self)
                if self.init_has_passed:
                    self.handle_object_link_update(input_value, old_value)

            elif issubclass(type(input_value), List) and name not in ["modeling_obj_containers"]:
                if len(input_value) > 0 and type(input_value[0]) == str and self.init_has_passed:
                    raise ValueError(f"There shouldn’t be a str list update after init")
                old_list_value_attr_name = f"{name}__previous_list_value_set"
                if not (len(input_value) > 0 and type(input_value[0]) == str):
                    for obj in input_value:
                        obj.add_obj_to_modeling_obj_containers(self)
                    # Necessary to handle syntax obj.list_attr += [new_attr_in_list] because lists are mutable objects
                    # Otherwise if using old_value, it would already be equal to input_value
                    old_list_value = getattr(self, old_list_value_attr_name, None)
                    if self.init_has_passed and old_list_value is not None:
                        self.handle_object_list_link_update(input_value, old_list_value)
                    super().__setattr__(old_list_value_attr_name, copy(input_value))

            elif issubclass(type(input_value), ExplainableObject):
                input_value.set_modeling_obj_container(self, name)
                is_a_user_attribute_update = self.init_has_passed and (
                    name not in self.calculated_attributes and old_value is not None)
                if is_a_user_attribute_update:
                    self.handle_model_input_update(old_value)

            elif issubclass(type(input_value), ExplainableObjectDict):
                if self.init_has_passed:
                    assert name in self.calculated_attributes
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
        descendants = old_value_that_gets_updated.get_all_descendants_with_id()
        has_been_recomputed_dict = {descendant.id: False for descendant in descendants}
        has_been_recomputed_dict[old_value_that_gets_updated.id] = True

        computed_parents_with_children_to_recompute = [old_value_that_gets_updated]

        while len(computed_parents_with_children_to_recompute) > 0:
            for recomputed_parent in computed_parents_with_children_to_recompute:
                drop_recomputed_parent_from_list = True
                for child in recomputed_parent.direct_children_with_id:
                    if not has_been_recomputed_dict[child.id]:
                        ancestors_that_belong_to_old_value_descendants = [
                            ancestor for ancestor in child.direct_ancestors_with_id
                            if ancestor.id in [ancestor.id for ancestor in descendants]]
                        if all([has_been_recomputed_dict[ancestor.id]
                                for ancestor in ancestors_that_belong_to_old_value_descendants]):
                            child_update_func = self.retrieve_update_function_from_attribute_name(
                                child.modeling_obj_container, child.attr_name_in_mod_obj_container)
                            child_update_func()
                            has_been_recomputed_dict[child.id] = True
                            if len(child.direct_children_with_id) > 0:
                                computed_parents_with_children_to_recompute.append(child)
                        else:
                            # Wait for next iteration
                            drop_recomputed_parent_from_list = False
                if drop_recomputed_parent_from_list:
                    computed_parents_with_children_to_recompute = [
                        child for child in computed_parents_with_children_to_recompute
                        if child.id != recomputed_parent.id]

    def handle_object_link_update(
            self, input_value: Type["ModelingObject"], old_value: Type["ModelingObject"]):
        if old_value is None:
            raise ValueError(f"A link update is trying to replace an null object")
        if (self in old_value.modeling_objects_whose_attributes_depend_directly_on_me and
            old_value in self.modeling_objects_whose_attributes_depend_directly_on_me):
            raise AssertionError(
                f"There is a circular recalculation dependency between {self.id} and {old_value.id}")

        old_value.remove_obj_from_modeling_obj_containers(self)

        if self in old_value.modeling_objects_whose_attributes_depend_directly_on_me:
            self.launch_attributes_computation_chain()
        else:
            input_value.launch_attributes_computation_chain()
            old_value.launch_attributes_computation_chain()

    def handle_object_list_link_update(self, input_value: List[Type["ModelingObject"]],
                                       old_value: List[Type["ModelingObject"]]):
        removed_objs = [obj for obj in old_value if obj not in input_value]
        added_objs = [obj for obj in input_value if obj not in old_value]

        for obj in removed_objs:
            obj.remove_obj_from_modeling_obj_containers(self)

        for obj in removed_objs + added_objs:
            if self not in obj.modeling_objects_whose_attributes_depend_directly_on_me:
                obj.launch_attributes_computation_chain()

        self.launch_attributes_computation_chain()

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

    @property
    def mod_obj_attributes(self):
        output_list = []
        for attr_name, attr_value in vars(self).items():
            values = convert_to_list(attr_value)
            for value in values:
                if isinstance(value, ModelingObject):
                    output_list.append(value)

        return output_list

    def object_relationship_graph_to_file(
            self, filename=None, classes_to_ignore=USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE, width=WIDTH, height=HEIGHT):
        object_relationships_graph = build_object_relationships_graph(
            self, classes_to_ignore=classes_to_ignore, width=width, height=height)

        if filename is None:
            filename = os.path.join(".", f"{self.name} calculus graph.html")
        object_relationships_graph.show(filename)
