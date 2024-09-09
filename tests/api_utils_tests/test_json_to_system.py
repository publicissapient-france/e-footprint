import json
import os.path
from copy import deepcopy

from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.api_utils.json_to_system import json_to_system
from efootprint.constants.units import u
from tests.integration_tests.integration_test_base_class import IntegrationTestBaseClass


API_UTILS_TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class TestJsonToSystem(IntegrationTestBaseClass):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(API_UTILS_TEST_DIR, "base_system.json"), "rb") as file:
            cls.base_system_dict = json.load(file)

    def test_create_unlinked_service(self):
        full_dict = deepcopy(self.base_system_dict)
        with open(os.path.join(API_UTILS_TEST_DIR, "service_not_linked_to_user_journey.json"), "rb") as file:
            full_dict["Service"].update(json.load(file))

        class_obj_dict, flat_obj_dict = json_to_system(full_dict)

        self.assertEqual(2, len(list(class_obj_dict["Service"].values())))

    def test_create_unlinked_server(self):
        full_dict = deepcopy(self.base_system_dict)
        with open(os.path.join(API_UTILS_TEST_DIR, "server_not_linked_to_user_journey.json"), "rb") as file:
            full_dict["Autoscaling"].update(json.load(file))

        class_obj_dict, flat_obj_dict = json_to_system(full_dict)

        self.assertEqual(2, len(list(class_obj_dict["Autoscaling"].values())))

    def test_create_unlinked_uj(self):
        full_dict = deepcopy(self.base_system_dict)
        with open(os.path.join(API_UTILS_TEST_DIR, "uj_not_linked_to_usage_pattern.json"), "rb") as file:
            full_dict["UserJourney"].update(json.load(file))

        class_obj_dict, flat_obj_dict = json_to_system(full_dict)

        new_uj = flat_obj_dict["uuid-New-UJ"]

        assert new_uj.duration.magnitude > 0

    def test_update_value_after_system_creation(self):
        class_obj_dict, flat_obj_dict = json_to_system(self.base_system_dict)

        list(class_obj_dict["Job"].values())[0].data_download = SourceValue(100 * u.GB, label="new value")

    def test_system_id_doesnt_change(self):
        class_obj_dict, flat_obj_dict = json_to_system(self.base_system_dict)

        self.assertEqual(
            list(class_obj_dict["System"].values())[0].id, list(self.base_system_dict["System"].values())[0]["id"])
