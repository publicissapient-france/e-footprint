import inspect
import logging

from pubsub import pub

from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject


class NonQuantityUsedInCalculation(ExplainableObject):
    def __init__(self, value=None):
        super().__init__(value, "non attribute used in calculation")

    def get_calling_function(self):
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back
        calling_function_name = inspect.getframeinfo(caller_frame).function
        if calling_function_name.startswith("update_"):
            instance_in_prev_frame = caller_frame.f_locals.get("self")
            method_obj = getattr(instance_in_prev_frame, calling_function_name, None)
            pubsub_topic_to_listen_to = self.pubsub_topic
            pub.subscribe(method_obj, pubsub_topic_to_listen_to)
            logging.debug(f"CALLING FUNC - Subscribed {calling_function_name} to {pubsub_topic_to_listen_to}")

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
