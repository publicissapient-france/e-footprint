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

    def define_as_intermediate_calculation(self, intermediate_calculation_label):
        self.height_level += 1
        self.label = intermediate_calculation_label

        return self

    @property
    def pubsub_topics_to_listen_to(self):
        return [input_attribute.pubsub_topic for input_attribute in self.input_attributes_to_listen_to]

    def explain(self):
        if self.left_child and self.right_child:  # Checks if there are child nodes
            left_explanation = self.left_child.explain()
            right_explanation = self.right_child.explain()

            return f"({left_explanation} {self.child_operator} {right_explanation})"
        else:
            return self.label
