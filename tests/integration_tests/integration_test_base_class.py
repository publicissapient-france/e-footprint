from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.hardware.network import Network
from efootprint.logger import logger

from typing import List
from unittest import TestCase


class IntegrationTestBaseClass(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.initial_energy_footprints = {}
        cls.initial_fab_footprints = {}

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
