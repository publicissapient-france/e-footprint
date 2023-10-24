import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from efootprint.constants.sources import u, SourceValue
from efootprint.core.usage.user_journey import UserJourneyStep, UserJourney


class TestUserJourneyStep(TestCase):
    def setUp(self):
        self.service = MagicMock()

        self.user_journey_step = UserJourneyStep(
            "", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            server_ram_per_data_transferred=SourceValue(2 * u.dimensionless), cpu_needed=SourceValue(2 * u.core / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))

    def test_update_ram_needed(self):
        self.user_journey_step.update_ram_needed()
        expected_ram_needed = SourceValue(400 * u.MB / u.user_journey)

        self.assertEqual(expected_ram_needed.value, self.user_journey_step.ram_needed.value)


class TestUserJourney(TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.server = MagicMock()
        self.service = MagicMock()
        self.service.server = self.server
        self.service.storage = self.storage

        self.server.usage_patterns = set()
        self.storage.usage_patterns = set()

        self.user_journey_step = UserJourneyStep(
            "test_uj_step", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            server_ram_per_data_transferred=SourceValue(2 * u.dimensionless), cpu_needed=SourceValue(2 * u.core / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj))
        self.one_user_journey = SourceValue(1 * u.user_journey)
        self.user_journey = UserJourney("test user journey", uj_steps=[self.user_journey_step])
        self.user_journey.dont_handle_input_updates = True
        self.usage_pattern = MagicMock()
        self.user_journey.modeling_obj_containers = [self.usage_pattern]

    def test_uj_step_setter(self):
        # TODO: implement
        pass

    def test_add_step(self):
        self.user_journey.add_step(self.user_journey_step)
        self.assertEqual(self.user_journey.uj_steps, [self.user_journey_step, self.user_journey_step])

    def test_servers(self):
        self.assertEqual(self.user_journey.servers, {self.server})

    def test_storages(self):
        self.assertEqual(self.user_journey.storages, {self.storage})

    def test_services(self):
        self.assertEqual(self.user_journey.services, [self.service])

    def test_update_duration_with_multiple_steps(self):
        self.user_journey.add_step(self.user_journey_step)
        for step in self.user_journey.uj_steps:
            step.user_time_spent = SourceValue(5 * u.min / u.user_journey)

        self.user_journey.update_duration()
        expected_duration = SourceValue(10 * u.min / u.user_journey)

        self.assertEqual(self.user_journey.duration.value, expected_duration.value)

    def test_update_data_download_with_multiple_steps(self):
        self.user_journey.add_step(self.user_journey_step)

        for step in self.user_journey.uj_steps:
            step.data_download = SourceValue(10 * u.MB / u.user_journey)
        self.user_journey.update_data_download()

        expected_data_download = SourceValue(20 * u.MB / u.user_journey)

        self.assertEqual(self.user_journey.data_download.value, expected_data_download.value)

    def test_update_data_upload_with_multiple_steps(self):
        self.user_journey.add_step(self.user_journey_step)
        for step in self.user_journey.uj_steps:
            step.data_upload = SourceValue(10 * u.MB / u.user_journey)

        self.user_journey.update_data_upload()

        expected_data_upload = SourceValue(20 * u.MB / u.user_journey)

        self.assertEqual(self.user_journey.data_upload.value, expected_data_upload.value)


if __name__ == "__main__":
    unittest.main()
