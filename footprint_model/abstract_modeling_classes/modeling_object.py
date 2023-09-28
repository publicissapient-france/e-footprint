from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject

import uuid
from abc import ABCMeta, abstractmethod
from typing import List, Set
from pubsub import pub
from importlib import import_module
from footprint_model.logger import logger


def get_subclass_attributes(obj, target_class):
    return {attr_name: attr_value for attr_name, attr_value in obj.__dict__.items()
            if issubclass(type(attr_value), target_class)}


def recursively_send_pubsub_message_for_every_attribute_used_in_calculation(old_attribute_value: List):
    for obj in old_attribute_value:
        for attr_name, attr_value in get_subclass_attributes(obj, ExplainableObject).items():
            pub.sendMessage(attr_value.pubsub_topic)
        for modeling_object, modeling_object_name in get_subclass_attributes(obj, ModelingObject).items():
            recursively_send_pubsub_message_for_every_attribute_used_in_calculation([modeling_object])


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
        self.id = str(uuid.uuid4())[:6]
        self.dont_handle_pubsub_topic_messages = False

    @abstractmethod
    def compute_calculated_attributes(self):
        pass

    def after_init(self):
        self.init_has_passed = True

    def handle_explainableobject_update(self, input_value: ExplainableObject, input_attr_name: str,
                                        old_value: ExplainableObject):
        update_func = getattr(self, f"update_{input_attr_name}", None)
        if update_func is None and \
                (input_value.left_child is not None or input_value.right_child is not None):
            raise ValueError(
                f"update_{input_attr_name} function does not exist. Please create it and checkout optimization.md")
        elif update_func is not None:
            if len(input_value.pubsub_topics_to_listen_to) == 0:
                logger.warning(
                    f"Update function update_{input_attr_name} doesn’t listen to any input. "
                    f"Normal in tests but not at runtime")
            if old_value is not None:
                for pubsub_topic in old_value.pubsub_topics_to_listen_to:
                    pub.unsubscribe(update_func, pubsub_topic)
            for pubsub_topic in input_value.pubsub_topics_to_listen_to:
                pub.subscribe(update_func, pubsub_topic)
            logger.debug(f"Subscribed update_{input_attr_name} to {input_value.pubsub_topics_to_listen_to}")

    def __setattr__(self, name, input_value):
        super().__setattr__(name, input_value)
        if name not in ["init_has_passed", "name", "id", "dont_handle_pubsub_topic_messages"]:
            logger.debug(f"attribute {name} updated in {self.name}")

        if issubclass(type(input_value), ExplainableObject) and not self.dont_handle_pubsub_topic_messages:
            current_pubsub_topic = f"{name}_in_{self.name}_{self.id}"
            if input_value.pubsub_topic is not None and current_pubsub_topic != input_value.pubsub_topic:
                raise ValueError(
                    f"An ExplainableObject can’t be linked to more than one pubsub topic. Here "
                    f"{current_pubsub_topic} is trying to be set instead of preexisting {input_value.pubsub_topic}."
                    f" A classic reason why this error could happen is that a mutable object (SourceValue for"
                    f" example) has been set as default value in one of the classes.")
            else:
                if not input_value.label:
                    logger.warning(
                        f"Intermediate calculation is being set at attribute {name} in {self.name} "
                        f"(id {self.id}) but has no label attached to it.")
                input_value.pubsub_topic = current_pubsub_topic
                logger.debug(f"Sending message to {current_pubsub_topic} (from obj {self.name})")
                pub.sendMessage(current_pubsub_topic)

        if self.init_has_passed and not self.dont_handle_pubsub_topic_messages:
            old_value = self.__dict__.get(name, None)

            if issubclass(type(input_value), ExplainableObject):
                self.handle_explainableobject_update(input_value, name, old_value)
            elif type(input_value) == ModelingObject:
                self.compute_calculated_attributes()
            elif type(input_value) == list:
                values_type = check_type_homogeneity_within_list_or_set(input_value)
                # DevicePopulation class has a Hardware list attribute and UserJourney has an UserJourneyStep attribute
                Hardware = import_module("footprint_model.core.hardware.hardware_base_classes").Hardware
                UserJourneyStep = import_module("footprint_model.core.usage.user_journey").UserJourneyStep
                assert values_type in [Hardware, UserJourneyStep]
                self.compute_calculated_attributes()
            elif type(input_value) == set:
                values_type = check_type_homogeneity_within_list_or_set(input_value)
                UsagePattern = import_module("footprint_model.core.usage.usage_pattern").UsagePattern
                assert values_type == UsagePattern
                self.compute_calculated_attributes()
