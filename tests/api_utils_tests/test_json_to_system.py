import json
import os.path

from efootprint.api_utils.json_to_system import json_to_system
from tests.integration_tests.integration_test_base_class import IntegrationTestBaseClass


API_UTILS_TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class TestJsonToSystem(IntegrationTestBaseClass):
    def test_service_not_linked_to_user_journey(self):
        with open(os.path.join(API_UTILS_TEST_DIR, "service_not_linked_to_user_journey.json"), "rb") as file:
            full_dict = json.load(file)

        class_obj_dict, flat_obj_dict = json_to_system(full_dict)

        self.assertEqual(2, len(list(class_obj_dict["Service"].values())))

    def test_server_not_linked_to_user_journey(self):
        with open(os.path.join(API_UTILS_TEST_DIR, "server_not_linked_to_user_journey.json"), "rb") as file:
            full_dict = json.load(file)

        class_obj_dict, flat_obj_dict = json_to_system(full_dict)

        self.assertEqual(2, len(list(class_obj_dict["Autoscaling"].values())))
