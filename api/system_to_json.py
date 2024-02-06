from pint import Quantity

from efootprint.utils.tools import time_it
from quickstart import system
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict


def mod_obj_to_json(mod_obj: ModelingObject):
    output_dict = {}

    for key, value in mod_obj.__dict__.items():
        if issubclass(type(mod_obj), ModelingObject) and \
                (key in mod_obj.calculated_attributes or "calculated_attributes" in key):
            continue
        if type(value) == str:
            output_dict[key] = value
        elif type(value) == list:
            if len(value) == 0:
                output_dict[key] = value
            else:
                if type(value[0]) == str:
                    output_dict[key] = value
                elif issubclass(type(value), ModelingObject):
                    output_dict[key] = [elt.uuid for elt in value]
        elif issubclass(type(value), ExplainableObject):
            if issubclass(type(value.value), Quantity):
                output_dict[key] = {
                    "value": value.value.magnitude, "unit": str(value.value.units), "label": value.label}
            elif type(value.value) == list:
                if len(value.value) > 0 and type(value.value[0]) == list:
                    output_dict[key] = {"value": value.value}
                else:
                    output_dict[key] = {"values": [elt.magnitude for elt in value.value], "unit": value.value[0].units}
            elif getattr(value.value, "zone", None) is not None:
                output_dict[key] = {"zone": value.value.zone}
            if value.source is not None:
                output_dict[key]["source"] = {"name": value.source.name, "link": value.source.link}
        elif issubclass(type(value), ExplainableObjectDict):
            print(value.__dict__)
            output_dict[key] = mod_obj_to_json(value)
        elif issubclass(type(value), ModelingObject):
            output_dict[key] = value.id

    return output_dict


def recursively_write_json_dict(full_dict, mod_obj):
    mod_obj_class = str(mod_obj.__class__).replace("<class '", "").replace("'>", "").split(".")[-1]
    if mod_obj_class not in full_dict.keys():
        full_dict[mod_obj_class] = {}
    if mod_obj.id not in full_dict[mod_obj_class].keys():
        full_dict[mod_obj_class][mod_obj.id] = mod_obj_to_json(mod_obj)
        for key, value in mod_obj.__dict__.items():
            if issubclass(type(value), ModelingObject):
                recursively_write_json_dict(full_dict, value)
            elif type(value) == list and len(value) > 0 and issubclass(type(value[0]), ModelingObject):
                for mod_obj_elt in value:
                    recursively_write_json_dict(full_dict, mod_obj_elt)

    return full_dict


@time_it
def system_to_json(system):
    full_dict = {}
    recursively_write_json_dict(full_dict, system)

    return full_dict


full_dict = system_to_json(system)
from pprint import pprint
pprint(full_dict)

import json
with open("./full_dict.json", "w") as file:
    file.write(json.dumps(full_dict, indent=4))
