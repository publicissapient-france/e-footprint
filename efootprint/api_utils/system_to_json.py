from efootprint.utils.tools import time_it
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict

import json


def mod_obj_to_json(mod_obj: ModelingObject, save_calculated_attributes=False):
    output_dict = {}

    for key, value in mod_obj.__dict__.items():
        if (key in mod_obj.calculated_attributes and not save_calculated_attributes) or "calculated_attributes" in key\
                or key == "modeling_obj_containers":
            continue
        if type(value) == str:
            output_dict[key] = value
        elif type(value) == int:
            output_dict[key] = value
        elif type(value) == list:
            if len(value) == 0:
                output_dict[key] = value
            else:
                if type(value[0]) == str:
                    output_dict[key] = value
                elif issubclass(type(value[0]), ModelingObject) and "__previous_list_value_set" not in key:
                    output_dict[key] = [elt.id for elt in value]
        elif issubclass(type(value), ExplainableObject):
            output_dict[key] = value.to_json(save_calculated_attributes)
        elif issubclass(type(value), ExplainableObjectDict):
            output_dict[key] = mod_obj_to_json(value, save_calculated_attributes)
        elif issubclass(type(value), ModelingObject):
            output_dict[key] = value.id

    return output_dict


def recursively_write_json_dict(output_dict, mod_obj, save_calculated_attributes=True):
    mod_obj_class = str(mod_obj.__class__).replace("<class '", "").replace("'>", "").split(".")[-1]
    if mod_obj_class not in output_dict.keys():
        output_dict[mod_obj_class] = {}
    if mod_obj.id not in output_dict[mod_obj_class].keys():
        output_dict[mod_obj_class][mod_obj.id] = mod_obj_to_json(mod_obj, save_calculated_attributes)
        for key, value in mod_obj.__dict__.items():
            if issubclass(type(value), ModelingObject):
                recursively_write_json_dict(output_dict, value, save_calculated_attributes)
            elif type(value) == list and len(value) > 0 and issubclass(type(value[0]), ModelingObject):
                for mod_obj_elt in value:
                    recursively_write_json_dict(output_dict, mod_obj_elt, save_calculated_attributes)

    return output_dict


@time_it
def system_to_json(input_system, save_calculated_attributes, output_filepath=None):
    output_dict = {}
    recursively_write_json_dict(output_dict, input_system, save_calculated_attributes)

    if output_filepath is not None:
        with open(output_filepath, "w") as file:
            file.write(json.dumps(output_dict, indent=4))

    return output_dict


if __name__ == "__main__":
    from quickstart import system
    full_dict = system_to_json(system, save_calculated_attributes=False, output_filepath="full_dict.json")
