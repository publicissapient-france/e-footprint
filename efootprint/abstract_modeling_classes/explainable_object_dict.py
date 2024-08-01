from efootprint.abstract_modeling_classes.explainable_object_base_class import (
    ObjectLinkedToModelingObj, ExplainableObject)

from typing import Type
import json


class ExplainableObjectDict(ObjectLinkedToModelingObj, dict):
    # TODO: optimization opportunity: as such in the case of several values of an ExplainableObjectDict
    # depending on the same SourceValue if the SourceValue is updated the ExplainableObjectDict will be recomputed as
    # many times as it has values depending on the SourceValue.
    def __init__(self):
        super().__init__()
        self.modeling_obj_container = None
        self.attr_name_in_mod_obj_container = None

    def set_modeling_obj_container(self, new_parent_modeling_object: Type["ModelingObject"], attr_name: str):
        if self.modeling_obj_container is not None and new_parent_modeling_object.id != self.modeling_obj_container.id:
            raise ValueError(
                f"An ExplainableObjectDict can’t be attributed to more than one ModelingObject. Here "
                f"{self.label} is trying to be linked to {new_parent_modeling_object.name} but is already linked to "
                f"{self.modeling_obj_container.name}.")
        self.modeling_obj_container = new_parent_modeling_object
        self.attr_name_in_mod_obj_container = attr_name

    def __setitem__(self, key, value: ExplainableObject):
        if not issubclass(type(value), ExplainableObject):
            raise ValueError(f"ExplainableObjectDicts only accept ExplainableObjects as values, received {type(value)}")
        super().__setitem__(key, value)
        value.set_modeling_obj_container(
            new_modeling_obj_container=self.modeling_obj_container, attr_name=self.attr_name_in_mod_obj_container)

    def to_json(self, with_calculated_attributes_data=False):
        output_dict = {}

        for key, value in self.items():
            output_dict[key.id] = value.to_json(with_calculated_attributes_data)

        return output_dict

    def __repr__(self):
        return json.dumps(self.to_json())

    def __str__(self):
        values_dict = {}

        for key, value in self.items():
            values_dict[key.id] = str(value)

        return json.dumps(values_dict)
