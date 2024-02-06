from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.api_utils.json_to_system import json_to_system
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.logger import logger

from typing import List
from unittest import TestCase
import os
import json

INTEGRATION_TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class IntegrationTestBaseClass(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.initial_energy_footprints = {}
        cls.initial_fab_footprints = {}

        cls.ref_json_filename = "default_ref_json_file.json"

    def footprint_has_changed(self, objects_to_test: List[ModelingObject]):
        for obj in objects_to_test:
            try:
                initial_energy_footprint = round(self.initial_energy_footprints[obj].value, 2)
                self.assertNotEqual(initial_energy_footprint, obj.energy_footprint.value)
                if type(obj) != Network:
                    initial_fab_footprint = round(self.initial_fab_footprints[obj].value, 2)
                    new_footprint = round(obj.instances_fabrication_footprint.value + obj.energy_footprint.value, 2)
                    self.assertNotEqual(
                        initial_fab_footprint + initial_energy_footprint, new_footprint)
                    logger.info(
                        f"{obj.name} footprint has changed from {initial_fab_footprint + initial_energy_footprint}"
                        f" to {new_footprint}")
                else:
                    logger.info(f"{obj.name} footprint has changed from "
                                f"{round(initial_energy_footprint, 2)} to {round(obj.energy_footprint.value, 2)}")
            except AssertionError:
                raise AssertionError(f"Footprint hasn’t changed for {obj.name}")

    def footprint_has_not_changed(self, objects_to_test: List[ModelingObject]):
        for obj in objects_to_test:
            try:
                initial_energy_footprint = self.initial_energy_footprints[obj].value
                if type(obj) != Network:
                    initial_fab_footprint = self.initial_fab_footprints[obj].value
                    self.assertEqual(initial_fab_footprint, obj.instances_fabrication_footprint.value)
                self.assertEqual(initial_energy_footprint, obj.energy_footprint.value)
                logger.info(f"{obj.name} footprint is the same as in setup")
            except AssertionError:
                raise AssertionError(f"Footprint has changed for {obj.name}")

    @staticmethod
    def retrieve_all_mod_obj_from_system(input_system: System):
        output_list = [input_system] + list(input_system.servers) + list(input_system.storages) \
                      + list(input_system.services) + input_system.usage_patterns \
                      + list(input_system.device_populations) + list(input_system.networks)
        user_journeys = [up.user_journey for up in input_system.usage_patterns]
        uj_steps = sum([uj.uj_steps for uj in user_journeys], start=[])
        devices = sum([dp.devices for dp in input_system.device_populations], start=[])
        countries = [dp.country for dp in input_system.device_populations]

        return output_list + user_journeys + uj_steps + devices + countries

    def run_system_to_json_test(self, input_system):
        mod_obj_list = self.retrieve_all_mod_obj_from_system(input_system)

        old_ids = {}
        for mod_obj in mod_obj_list:
            old_ids[mod_obj.name] = mod_obj.id
            mod_obj.id = f"{mod_obj.name} + its uuid"

        tmp_filepath = os.path.join(INTEGRATION_TEST_DIR, "tmp_system_file.json")
        system_to_json(input_system, save_calculated_attributes=False, output_filepath=tmp_filepath)

        for mod_obj in mod_obj_list:
            mod_obj.id = old_ids[mod_obj.name]

        with open(os.path.join(INTEGRATION_TEST_DIR, self.ref_json_filename), 'r') as ref_file, open(tmp_filepath, 'r') as tmp_file:
            ref_file_content = ref_file.read()
            tmp_file_content = tmp_file.read()

            self.assertEqual(ref_file_content, tmp_file_content)

        os.remove(tmp_filepath)

    def run_json_to_system_test(self, input_system):
        with open(os.path.join(INTEGRATION_TEST_DIR, self.ref_json_filename), "rb") as file:
            full_dict = json.load(file)

        def retrieve_obj_by_name(name, mod_obj_list):
            for obj in mod_obj_list:
                if obj.name == name:
                    return obj

        class_obj_dict, flat_obj_dict = json_to_system(full_dict)

        initial_mod_objs = self.retrieve_all_mod_obj_from_system(input_system)
        for obj_id, obj in flat_obj_dict.items():
            corresponding_obj = retrieve_obj_by_name(obj.name, initial_mod_objs)
            for attr_key, attr_value in obj.__dict__.items():
                if isinstance(attr_value, ExplainableQuantity):
                    self.assertEqual(getattr(corresponding_obj, attr_key).value, attr_value.value)
            logger.info(f"All ExplainableQuantities have right values for generated object {obj.name}")
