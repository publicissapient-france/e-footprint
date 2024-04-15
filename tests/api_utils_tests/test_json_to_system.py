import json
import os.path

from efootprint.api_utils.json_to_system import json_to_system
from tests.integration_tests.integration_test_base_class import IntegrationTestBaseClass
from copy import deepcopy


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

        new_uj = flat_obj_dict["New UJ + its uuid"]

        assert new_uj.duration.magnitude > 0
