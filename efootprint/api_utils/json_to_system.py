from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from efootprint.abstract_modeling_classes.source_objects import SourceObject
from efootprint.utils.tools import time_it
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

import pytz
import json


def json_to_explainable_quantity(input_dict):
    output = None
    source = None
    if "source" in input_dict.keys():
        source = Source(input_dict["source"]["name"], input_dict["source"]["link"])
    if "value" in input_dict.keys() and "unit" in input_dict.keys():
        value = input_dict["value"] * u(input_dict["unit"])
        output = ExplainableQuantity(
            value, label=input_dict["label"], source=source)
    elif "value" in input_dict.keys():
        output = ExplainableObject(
            value=input_dict["value"], label=input_dict["label"], source=source)
    elif "unit" in input_dict.keys():
        unit = u(input_dict["unit"])
        value = [elt * unit for elt in input_dict["values"]]
        output = ExplainableHourlyUsage(
            value, label=input_dict["label"], source=source)
    elif "zone" in input_dict.keys():
        output = SourceObject(
            pytz.timezone(input_dict["zone"]), source, input_dict["label"])

    return output


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
            new_obj.__dict__["modeling_obj_containers"] = []
            for attr_key, attr_value in system_dict[class_key][class_instance_key].items():
                if type(attr_value) == dict:
                    new_obj.__dict__[attr_key] = json_to_explainable_quantity(attr_value)
                    new_obj.__dict__[attr_key].set_modeling_obj_container(new_obj, attr_key)
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
                    flat_obj_dict[attr_value].add_obj_to_modeling_obj_containers(mod_obj)
                elif type(attr_value) == list and attr_key != "modeling_obj_containers":
                    output_val = []
                    for elt in attr_value:
                        if type(elt) == str and elt in flat_obj_dict.keys():
                            output_val.append(flat_obj_dict[elt])
                            flat_obj_dict[elt].add_obj_to_modeling_obj_containers(mod_obj)
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

    for mod_obj_key, mod_obj in class_obj_dict["System"].items():
        mod_obj.launch_attributes_computation_chain()

    return class_obj_dict, flat_obj_dict


def get_obj_by_key_similarity(obj_container_dict, input_key):
    for key in obj_container_dict.keys():
        if input_key in key:
            return obj_container_dict[key]


if __name__ == "__main__":
    with open("full_dict.json", "rb") as file:
        full_dict = json.load(file)

    class_obj_dict, flat_obj_dict = json_to_system(full_dict)

    streaming_step__retrieved = get_obj_by_key_similarity(flat_obj_dict, "20 min streaming on Youtube")

    system__retrieved = get_obj_by_key_similarity(flat_obj_dict, "system")

    from quickstart import system
    assert round(system__retrieved.total_footprint.magnitude, 2) == round(system.total_footprint.magnitude, 2)
