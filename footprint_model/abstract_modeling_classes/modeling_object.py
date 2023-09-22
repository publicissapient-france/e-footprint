from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from footprint_model.utils.tools import convert_to_list

import uuid
from abc import ABC, abstractmethod
from typing import List
from pubsub import pub
import inspect
import logging


def get_subclass_attributes(obj, target_class):
    return {attr_name: attr_value for attr_name, attr_value in obj.__dict__.items()
            if issubclass(type(attr_value), target_class)}


def recursively_send_pubsub_message_for_every_attribute_used_in_calculation(old_attribute_value: List):
    for obj in old_attribute_value:
        for attr_name, attr_value in get_subclass_attributes(obj, ExplainableObject).items():
            pub.sendMessage(attr_value.pubsub_topic)
        for modeling_object, modeling_object_name in get_subclass_attributes(obj, ModelingObject).items():
            recursively_send_pubsub_message_for_every_attribute_used_in_calculation([modeling_object])


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
            if issubclass(type(value), ExplainableObject):
                if value.pubsub_topic is not None and current_pubsub_topic != value.pubsub_topic:
                    raise ValueError(
                        f"An AttributeUsedInCalculation object can’t be linked to more than one pubsub topic. Here "
                        f"{current_pubsub_topic} is trying to be set in addition to preexisting {value.pubsub_topic}. "
                        f"A classic reason why this error could happen is that a mutable object (SourceValue for"
                        f" example) has been set as default value in one of the classes.")
                else:
                    value.pubsub_topic = current_pubsub_topic

        # Get caller function info
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        info = inspect.getframeinfo(caller_frame)

        if info.function not in ("__init__", "__exit__"):
            type_set = [type(value) for value in value_elts]
            base_type = type(type_set[0])

            if not all(isinstance(item, base_type) for item in type_set):
                raise ValueError(
                    f"There shouldn't be objects of different types within the same list, found {type_set}")
            else:
                values_type = type_set.pop()
            if issubclass(values_type, ExplainableObject):
                pub.sendMessage(current_pubsub_topic)
                logging.debug(f"Message sent to {current_pubsub_topic} (from obj {self.name})")
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
