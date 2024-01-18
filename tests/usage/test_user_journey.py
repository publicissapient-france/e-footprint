from efootprint.constants.sources import u, SourceValue
from efootprint.core.usage.user_journey import UserJourneyStep, UserJourney

import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock


class TestUserJourneyStep(TestCase):
    def setUp(self):
        self.service = MagicMock()

        self.user_journey_step = UserJourneyStep(
            "test uj step", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            ram_needed=SourceValue(400 * u.MB / u.uj), cpu_needed=SourceValue(2 * u.core / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))

    def test_user_journey_step_with_null_service_doesnt_break(self):
        uj_step_without_service = UserJourneyStep(
            "", service=None, data_download=SourceValue(0 * u.MB / u.uj),
            data_upload=SourceValue(0 * u.MB / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))

    def test_user_journey_step_with_null_service_breaks_if_non_null_data_transfer(self):
        with self.assertRaises(ValueError):
            uj_step_without_service = UserJourneyStep(
                "", service=None, data_download=SourceValue(10 * u.MB / u.uj),
                data_upload=SourceValue(0 * u.MB / u.uj),
                user_time_spent=SourceValue(2 * u.min / u.uj))

    def test_self_delete_should_raise_error_if_self_has_associated_uj(self):
        self.user_journey_step.modeling_obj_containers = ["uj"]
        with self.assertRaises(PermissionError):
            self.user_journey_step.self_delete()

    def test_self_delete_removes_backward_links_and_recomputes_server_and_storage(self):
        self.service.modeling_obj_containers = [self.user_journey_step]
        self.user_journey_step.self_delete()
        self.assertEqual([], self.service.modeling_obj_containers)
        self.service.launch_attributes_computation_chain.assert_called_once()


class TestUserJourney(TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.server = MagicMock()
        self.service = MagicMock()
        self.service.server = self.server
        self.service.storage = self.storage

        self.step1 = UserJourneyStep(
            "test_uj_step1", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            ram_needed=SourceValue(400 * u.MB / u.uj), cpu_needed=SourceValue(2 * u.core / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.step2 = UserJourneyStep(
            "test_uj_step2", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            ram_needed=SourceValue(400 * u.MB / u.uj), cpu_needed=SourceValue(2 * u.core / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.step3 = UserJourneyStep(
            "test_uj_step3", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            ram_needed=SourceValue(400 * u.MB / u.uj), cpu_needed=SourceValue(2 * u.core / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.one_user_journey = SourceValue(1 * u.user_journey)
        self.user_journey = UserJourney("test user journey", uj_steps=[self.step1])
        self.user_journey.dont_handle_input_updates = True
        self.usage_pattern = MagicMock()
        self.user_journey.modeling_obj_containers = [self.usage_pattern]

        for step in [self.step1, self.step2, self.step3]:
            step.remove_obj_from_modeling_obj_containers = MagicMock()
            step.add_obj_to_modeling_obj_containers = MagicMock()
            step.launch_attributes_computation_chain = MagicMock()

    def test_uj_steps_setter(self):
        with patch.object(self.user_journey, "launch_attributes_computation_chain", new_callable=PropertyMock) \
                as mock_computation_chain_launcher:
            self.user_journey.uj_steps = [self.step2, self.step3]
            self.assertEqual(self.user_journey.uj_steps, [self.step2, self.step3])

            self.step1.remove_obj_from_modeling_obj_containers.assert_called_once_with(self.user_journey)
            self.step1.add_obj_to_modeling_obj_containers.assert_not_called()
            self.step3.remove_obj_from_modeling_obj_containers.assert_not_called()
            self.step3.add_obj_to_modeling_obj_containers.assert_called_once_with(self.user_journey)
            mock_computation_chain_launcher.assert_called()

    def test_uj_steps_setter_triggers_computation_chain_for_removed_steps_without_uj(self):
        self.step1.modeling_obj_containers = []
        self.user_journey.uj_steps = [self.step2]
        self.step1.launch_attributes_computation_chain.assert_called_once()

    def test_add_step(self):
        self.user_journey.add_step(self.step1)
        self.assertEqual(self.user_journey.uj_steps, [self.step1, self.step1])

    def test_servers(self):
        self.assertEqual(self.user_journey.servers, {self.server})

    def test_storages(self):
        self.assertEqual(self.user_journey.storages, {self.storage})

    def test_services(self):
        self.assertEqual(self.user_journey.services, [self.service])

    def test_update_duration_with_multiple_steps(self):
        self.user_journey.add_step(self.step1)
        for step in self.user_journey.uj_steps:
            step.user_time_spent = SourceValue(5 * u.min / u.user_journey)

        self.user_journey.update_duration()
        expected_duration = SourceValue(10 * u.min / u.user_journey)

        self.assertEqual(self.user_journey.duration.value, expected_duration.value)

    def test_update_data_download_with_multiple_steps(self):
        self.user_journey.add_step(self.step1)

        for step in self.user_journey.uj_steps:
            step.data_download = SourceValue(10 * u.MB / u.user_journey)
        self.user_journey.update_data_download()

        expected_data_download = SourceValue(20 * u.MB / u.user_journey)

        self.assertEqual(self.user_journey.data_download.value, expected_data_download.value)

    def test_update_data_upload_with_multiple_steps(self):
        self.user_journey.add_step(self.step1)
        for step in self.user_journey.uj_steps:
            step.data_upload = SourceValue(10 * u.MB / u.user_journey)

        self.user_journey.update_data_upload()

        expected_data_upload = SourceValue(20 * u.MB / u.user_journey)

        self.assertEqual(self.user_journey.data_upload.value, expected_data_upload.value)


if __name__ == "__main__":
    unittest.main()
