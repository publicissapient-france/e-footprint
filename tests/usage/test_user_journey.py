import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from footprint_model.constants.sources import u
from footprint_model.core.usage.user_journey import UserJourneyStep, UserJourney
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity


class TestUserJourneyStep(TestCase):
    def setUp(self):
        self.service = MagicMock()

        self.user_journey_step = UserJourneyStep(
            "", service=self.service, data_download=200 * u.Mo, data_upload=(100 * u.Mo),
            server_ram_per_data_transferred=2, cpu_needed=(2 * u.core),
            user_time_spent=(2 * u.min))

    def test_update_ram_needed(self):
        self.user_journey_step.update_ram_needed()
        expected_ram_needed = ExplainableQuantity(400 * u.Mo / u.user_journey)

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
            "", service=self.service, data_download=200 * u.Mo, data_upload=(100 * u.Mo),
            server_ram_per_data_transferred=2, cpu_needed=(2 * u.core),
            user_time_spent=(2 * u.min))
        self.one_user_journey = ExplainableQuantity(1 * u.user_journey)
        self.user_journey = UserJourney("test user journey", uj_steps=[self.user_journey_step])

        self.usage_pattern = MagicMock()
        self.user_journey.usage_patterns = {self.usage_pattern}

    def test_link_usage_pattern_add_new_usage_pattern(self):
        self.user_journey.usage_patterns = {'up'}
        self.user_journey.link_usage_pattern('up2')

        self.assertEqual({'up', 'up2'}, self.user_journey.usage_patterns)
        for server in self.user_journey.servers:
            server.link_usage_pattern.assert_called_once_with('up2')

        for storage in self.user_journey.storages:
            storage.link_usage_pattern.assert_called_once_with('up2')

    def test_unlink_usage_pattern(self):
        self.user_journey.usage_patterns = {'up', 'up2'}
        self.user_journey.unlink_usage_pattern('up2')
        self.assertEqual({'up'}, self.user_journey.usage_patterns)

        for server in self.user_journey.servers:
            server.unlink_usage_pattern.assert_called_once_with('up2')
        for storage in self.user_journey.storages:
            storage.unlink_usage_pattern.assert_called_once_with('up2')

    def test_add_step(self):
        self.user_journey.add_step(self.user_journey_step)
        self.assertEqual(self.user_journey.uj_steps, [self.user_journey_step, self.user_journey_step])
        self.assertEqual(self.user_journey.duration.value, 2 * self.user_journey_step.user_time_spent.value)
        self.assertEqual(self.user_journey.data_download.value, 2 * self.user_journey_step.data_download.value)
        self.assertEqual(self.user_journey.data_upload.value, 2 * self.user_journey_step.data_upload.value)

    def test_servers(self):
        self.assertEqual(self.user_journey.servers, {self.server})

    def test_storages(self):
        self.assertEqual(self.user_journey.storages, {self.storage})

    def test_services(self):
        self.assertEqual(self.user_journey.services, {self.service})

    def test_update_duration_with_multiple_steps(self):
        self.user_journey.add_step(self.user_journey_step)
        for step in self.user_journey.uj_steps:
            step.user_time_spent = ExplainableQuantity(5 * u.min / u.user_journey)

        self.user_journey.update_duration()
        expected_duration = ExplainableQuantity(10 * u.min / u.user_journey)

        self.assertEqual(self.user_journey.duration.value, expected_duration.value)

    def test_update_data_download_with_multiple_steps(self):
        self.user_journey.add_step(self.user_journey_step)

        for step in self.user_journey.uj_steps:
            step.data_download = ExplainableQuantity(10 * u.Mo / u.user_journey)
        self.user_journey.update_data_download()

        expected_data_download = ExplainableQuantity(20 * u.Mo / u.user_journey)

        self.assertEqual(self.user_journey.data_download.value, expected_data_download.value)

    def test_update_data_upload_with_multiple_steps(self):
        self.user_journey.add_step(self.user_journey_step)
        for step in self.user_journey.uj_steps:
            step.data_upload = ExplainableQuantity(10 * u.Mo / u.user_journey)

        self.user_journey.update_data_upload()

        expected_data_upload = ExplainableQuantity(20 * u.Mo / u.user_journey)

        self.assertEqual(self.user_journey.data_upload.value, expected_data_upload.value)


if __name__ == "__main__":
    unittest.main()
