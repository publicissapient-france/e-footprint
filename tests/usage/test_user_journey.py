import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.core.usage.job import Job
from efootprint.constants.units import u


class TestUserJourney(TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.server = MagicMock()
        self.service = MagicMock()
        self.service.server = self.server
        self.service.storage = self.storage

        self.job = Job("Job", data_download=MagicMock(), data_upload=MagicMock(),
                       service=self.service, request_duration=MagicMock(), cpu_needed=MagicMock(),
                       ram_needed=MagicMock())
        self.step1 = UserJourneyStep(
            "test_uj_step1",
            jobs=[self.job],
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.job2 = MagicMock(
            spec={"data_download": SourceValue(200 * u.MB / u.uj), "data_upload": SourceValue(100 * u.MB / u.uj)})
        self.step2 = UserJourneyStep(
            "test_uj_step2", jobs=[self.job],
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.step3 = UserJourneyStep(
            "test_uj_step3", jobs=[self.job],
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.user_journey = UserJourney("test user journey", uj_steps=[self.step1])
        self.user_journey.dont_handle_input_updates = True
        self.usage_pattern = MagicMock()
        self.user_journey.modeling_obj_containers = [self.usage_pattern]

        for step in [self.step1, self.step2, self.step3]:
            step.remove_obj_from_modeling_obj_containers = MagicMock()
            step.add_obj_to_modeling_obj_containers = MagicMock()
            step.launch_attributes_computation_chain = MagicMock()

    def test_servers(self):
        self.assertEqual(self.user_journey.servers, [self.server])

    def test_storages(self):
        self.assertEqual(self.user_journey.storages, [self.storage])

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

        with patch.object(self.job, "data_download", new=SourceValue(10 * u.MB / u.user_journey)):
            self.user_journey.update_data_download()

        expected_data_download = SourceValue(20 * u.MB / u.user_journey)

        self.assertEqual(self.user_journey.data_download.value, expected_data_download.value)

    def test_update_data_upload_with_multiple_steps(self):
        self.user_journey.add_step(self.step1)

        with patch.object(self.job, "data_upload", new=SourceValue(10 * u.MB / u.user_journey)):
            self.user_journey.update_data_upload()

        expected_data_upload = SourceValue(20 * u.MB / u.user_journey)

        self.assertEqual(self.user_journey.data_upload.value, expected_data_upload.value)


if __name__ == "__main__":
    unittest.main()
