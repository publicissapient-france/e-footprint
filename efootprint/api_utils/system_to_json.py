from efootprint.utils.tools import time_it
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject

import json


def recursively_write_json_dict(output_dict, mod_obj, save_calculated_attributes=True):
    mod_obj_class = mod_obj.class_as_simple_str
    if mod_obj_class not in output_dict.keys():
        output_dict[mod_obj_class] = {}
    if mod_obj.id not in output_dict[mod_obj_class].keys():
        output_dict[mod_obj_class][mod_obj.id] = mod_obj.to_json(save_calculated_attributes)
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
