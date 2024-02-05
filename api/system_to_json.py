from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from efootprint.abstract_modeling_classes.source_objects import SourceObject
from efootprint.utils.tools import time_it
from quickstart import system, streaming_step
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject, Source
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.constants.units import u
from efootprint.core.service import Service
from efootprint.core.system import System
from efootprint.core.hardware.storage import Storage
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.servers.serverless import Serverless
from efootprint.core.hardware.servers.on_premise import OnPremise
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.usage.user_journey import UserJourney, UserJourneyStep
from efootprint.core.hardware.network import Network
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.constants.countries import Country

from pint import Quantity
import pytz


def mod_obj_to_json(mod_obj: ModelingObject):
    output_dict = {}

    for key, value in mod_obj.__dict__.items():
        if issubclass(type(mod_obj), ModelingObject) and \
                (key in mod_obj.calculated_attributes or "calculated_attributes" in key):
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
            if issubclass(type(value.value), Quantity):
                output_dict[key] = {
                    "value": value.value.magnitude, "unit": str(value.value.units)}
            elif type(value.value) == list:
                if len(value.value) > 0 and type(value.value[0]) == list:
                    output_dict[key] = {"value": value.value}
                else:
                    output_dict[key] = {"values": [elt.magnitude for elt in value.value], "unit": value.value[0].units}
            elif getattr(value.value, "zone", None) is not None:
                output_dict[key] = {"zone": value.value.zone}
            if value.source is not None:
                output_dict[key]["source"] = {"name": value.source.name, "link": value.source.link}
            output_dict[key]["label"] = value.label
        elif issubclass(type(value), ExplainableObjectDict):
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


@time_it
def json_to_system(system_dict):
    class_obj_dict = {}
    flat_obj_dict = {}

    for class_key in system_dict.keys():
        if class_key not in class_obj_dict.keys():
            class_obj_dict[class_key] = {}
        current_class = globals()[class_key]
        current_class_dict = {}
        for class_instance_key in system_dict[class_key].keys():
            new_obj = current_class.__new__(current_class)
            for attr_key, attr_value in system_dict[class_key][class_instance_key].items():
                if type(attr_value) == dict:
                    source = None
                    if "source" in attr_value.keys():
                        source = Source(attr_value["source"]["name"], attr_value["source"]["link"])
                    if "value" in attr_value.keys() and "unit" in attr_value.keys():
                        value = attr_value["value"] * u(attr_value["unit"])
                        new_obj.__dict__[attr_key] = ExplainableQuantity(
                            value, label=attr_value["label"], source=source)
                    elif "value" in attr_value.keys():
                        new_obj.__dict__[attr_key] = ExplainableObject(
                            value=attr_value["value"], label=attr_value["label"], source=source)
                    elif "unit" in attr_value.keys():
                        unit = u(attr_value["unit"])
                        value = [elt * unit for elt in attr_value["values"]]
                        new_obj.__dict__[attr_key] = ExplainableHourlyUsage(
                            value, label=attr_value["label"], source=source)
                    elif "zone" in attr_value.keys():
                        new_obj.__dict__[attr_key] = SourceObject(
                            pytz.timezone(attr_value["zone"]), source, attr_value["label"])
                else:
                    new_obj.__dict__[attr_key] = attr_value

            current_class_dict[class_instance_key] = new_obj
            flat_obj_dict[class_instance_key] = new_obj

        class_obj_dict[class_key] = current_class_dict

    for class_key in class_obj_dict.keys():
        for mod_obj_key, mod_obj in class_obj_dict[class_key].items():
            for attr_key, attr_value in mod_obj.__dict__.items():
                if type(attr_value) == str and attr_key != "id" and attr_value in flat_obj_dict.keys():
                    mod_obj.__dict__[attr_key] = flat_obj_dict[attr_value]
                elif type(attr_value) == list:
                    output_val = []
                    for elt in attr_value:
                        if type(elt) == str and elt in flat_obj_dict.keys():
                            output_val.append(flat_obj_dict[elt])
                    mod_obj.__dict__[attr_key] = output_val
            mod_obj.__dict__["dont_handle_input_updates"] = False
            mod_obj.__dict__["init_has_passed"] = True

    for class_key in ["UserJourneyStep", "UserJourney"]:
        for mod_obj_key, mod_obj in class_obj_dict[class_key].items():
            mod_obj.compute_calculated_attributes()

    for mod_obj_key, mod_obj in class_obj_dict["DevicePopulation"].items():
        mod_obj.user_journey_freq_per_up = ExplainableObjectDict()
        mod_obj.nb_user_journeys_in_parallel_during_usage_per_up = ExplainableObjectDict()
        mod_obj.utc_time_intervals_per_up = ExplainableObjectDict()

    for mod_obj_key, mod_obj in class_obj_dict["DevicePopulation"].items():
        mod_obj.user_journey_freq_per_up = ExplainableObjectDict()
        mod_obj.nb_user_journeys_in_parallel_during_usage_per_up = ExplainableObjectDict()
        mod_obj.utc_time_intervals_per_up = ExplainableObjectDict()

    for mod_obj_key, mod_obj in class_obj_dict["System"].items():
        mod_obj.launch_attributes_computation_chain()

    return class_obj_dict, flat_obj_dict


def get_obj_by_key_similarity(obj_container_dict, input_key):
    for key in obj_container_dict.keys():
        if input_key in key:
            return obj_container_dict[key]


if __name__ == "__main__":
    full_dict = system_to_json(system)
    import json
    with open("./full_dict.json", "w") as file:
        file.write(json.dumps(full_dict, indent=4))

    class_obj_dict, flat_obj_dict = json_to_system(full_dict)

    streaming_step__retrieved = get_obj_by_key_similarity(flat_obj_dict, "20 min streaming on Youtube")

    system__retrieved = get_obj_by_key_similarity(flat_obj_dict, "system")
    system__retrieved.launch_attributes_computation_chain()
