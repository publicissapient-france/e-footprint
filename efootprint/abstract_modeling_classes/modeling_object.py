from efootprint.logger import logger
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.utils.graph_tools import WIDTH, HEIGHT, add_unique_id_to_mynetwork
from efootprint.utils.object_relationships_graphs import build_object_relationships_graph, \
    USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE
from efootprint.utils.tools import convert_to_list

import uuid
from abc import ABCMeta, abstractmethod
from typing import List, Type
from copy import copy
import os
import json
from IPython.display import HTML


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
        self.dont_handle_input_updates = False
        self.init_has_passed = False
        self.name = name
        self.id = f"{self.name} {str(uuid.uuid4())[:6]}"
        self.modeling_obj_containers = []

    @property
    @abstractmethod
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[Type["ModelingObject"]]:
        pass

    @property
    def calculated_attributes(self) -> List[str]:
        return []

    @property
    @abstractmethod
    def systems(self) -> List:
        pass

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

    def register_footprint_values_in_systems_before_change(self, change: str):
        logger.debug(change)
        for system in self.systems:
            system.previous_total_energy_footprints = system.total_energy_footprints
            system.previous_total_fabrication_footprints = system.total_fabrication_footprints
            system.previous_change = change
            system.all_changes.append(change)

    def __setattr__(self, name, input_value):
        old_value = self.__dict__.get(name, None)

        if name not in ["dont_handle_input_updates", "init_has_passed"] and not self.dont_handle_input_updates:
            if issubclass(type(input_value), ModelingObject):
                input_value.add_obj_to_modeling_obj_containers(self)
                if self.init_has_passed:
                    self.register_footprint_values_in_systems_before_change(
                        f"{self.name}’s {name} changed from {old_value.name} to {input_value.name}")
                    super().__setattr__(name, input_value)
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
                        oldlist_ids = [mod_obj.name for mod_obj in old_list_value]
                        newlist_ids = [mod_obj.name for mod_obj in input_value]
                        # Reset list to old value before registering footprints
                        super().__setattr__(name, old_list_value)
                        self.register_footprint_values_in_systems_before_change(
                            f"{self.name}’s {name} changed from {oldlist_ids} to {newlist_ids}")
                        super().__setattr__(name, input_value)
                        self.handle_object_list_link_update(input_value, old_list_value)
                    super().__setattr__(old_list_value_attr_name, copy(input_value))

            elif issubclass(type(input_value), ExplainableObject):
                input_value.set_modeling_obj_container(self, name)
                is_a_user_attribute_update = self.init_has_passed and (
                    name not in self.calculated_attributes and old_value is not None)
                if is_a_user_attribute_update:
                    self.register_footprint_values_in_systems_before_change(
                        f"{self.name}’s {name} changed from {str(old_value)} to {str(input_value)}")
                    super().__setattr__(name, input_value)
                    self.handle_model_input_update(old_value)

            elif issubclass(type(input_value), ExplainableObjectDict):
                if self.init_has_passed:
                    assert name in self.calculated_attributes
                input_value.set_modeling_obj_container(self, name)

        super().__setattr__(name, input_value)

        if getattr(self, "name", None) is not None:
            logger.debug(f"attribute {name} updated in {self.name}")

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
            self, filename=None, classes_to_ignore=USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE, width=WIDTH, height=HEIGHT,
            notebook=False):
        object_relationships_graph = build_object_relationships_graph(
            self, classes_to_ignore=classes_to_ignore, width=width, height=height, notebook=notebook)

        if filename is None:
            filename = os.path.join(".", f"{self.name} object relationship graph.html")
        object_relationships_graph.show(filename, notebook=notebook)

        add_unique_id_to_mynetwork(filename)

        if notebook:
            return HTML(filename)

    def self_delete(self):
        logger.warning(
            f"Deleting {self.name}, removing backward links pointing to it in "
            f"{','.join([mod_obj.name for mod_obj in self.mod_obj_attributes])}")
        if self.modeling_obj_containers:
            raise PermissionError(
                f"You can’t delete {self.name} because "
                f"{','.join([mod_obj.name for mod_obj in self.modeling_obj_containers])} have it as attribute.")
        for attr in self.mod_obj_attributes:
            attr.modeling_obj_containers = [elt for elt in attr.modeling_obj_containers if elt != self]
            attr.launch_attributes_computation_chain()

        del self

    def to_json(self, save_calculated_attributes=False):
        output_dict = {}

        for key, value in self.__dict__.items():
            if (
                    (key in self.calculated_attributes and not save_calculated_attributes)
                    or key in ["calculated_attributes", "all_changes"]
                    or key.startswith("previous")
                    or key.startswith("initial")
                    or key == "modeling_obj_containers"):
                continue
            if type(value) == str:
                output_dict[key] = value
            elif type(value) == int:
                output_dict[key] = value
            elif type(value) == list and "__previous_list_value_set" not in key:
                if len(value) == 0:
                    output_dict[key] = value
                else:
                    if type(value[0]) == str:
                        output_dict[key] = value
                    elif issubclass(type(value[0]), ModelingObject):
                        output_dict[key] = [elt.id for elt in value]
            elif issubclass(type(value), ExplainableObject):
                output_dict[key] = value.to_json(save_calculated_attributes)
            elif issubclass(type(value), ExplainableObjectDict):
                output_dict[key] = value.to_json(save_calculated_attributes)
            elif issubclass(type(value), ModelingObject):
                output_dict[key] = value.id

        return output_dict

    @property
    def class_as_simple_str(self):
        return str(self.__class__).replace("<class '", "").replace("'>", "").split(".")[-1]

    def __repr__(self):
        return json.dumps(self.to_json(save_calculated_attributes=True), indent=4)

    def __str__(self):
        output_str = ""

        def key_value_to_str(input_key, input_value):
            key_value_str = ""

            if type(input_value) in (str, int) or input_value is None:
                key_value_str = f"{input_key}: {input_value}\n"
            elif type(input_value) == list:
                if len(input_value) == 0:
                    key_value_str = f"{input_key}: {input_value}\n"
                else:
                    if type(input_value[0]) == str:
                        key_value_str = f"{input_key}: {input_value}"
                    elif issubclass(type(input_value[0]), ModelingObject) and "__previous_list_value_set" not in key:
                        str_value = "[" + ", ".join([elt.id for elt in input_value]) + "]"
                        key_value_str = f"{input_key}: {str_value}\n"
            elif issubclass(type(input_value), ExplainableObject):
                key_value_str = f"{input_key}: {input_value}\n"
            elif issubclass(type(input_value), ExplainableObjectDict):
                key_value_str = f"{input_key}: {input_value}\n"
            elif issubclass(type(input_value), ModelingObject):
                key_value_str = f"{input_key}: {input_value.id}\n"

            return key_value_str

        output_str += f"{self.class_as_simple_str} {self.id}\n \n"

        for key, attr_value in self.__dict__.items():
            if key == "modeling_obj_containers" or key in self.calculated_attributes or key.startswith("previous")\
                    or key in ["name", "id"]:
                continue
            output_str += key_value_to_str(key, attr_value)

        if len(self.calculated_attributes) > 0:
            output_str += " \ncalculated_attributes:\n"
            for key in self.calculated_attributes:
                output_str += "  " + key_value_to_str(key, getattr(self, key))

        return output_str
