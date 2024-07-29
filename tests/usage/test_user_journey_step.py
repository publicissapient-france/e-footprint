import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.usage.job import Job
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.constants.units import u


class TestUserJourneyStep(TestCase):
    def setUp(self):
        self.service = MagicMock()
        self.service.name = "service"

        self.job = Job("Job", data_download=MagicMock(), data_upload=MagicMock(),
                       service=self.service, request_duration=MagicMock(), cpu_needed=MagicMock(),
                       ram_needed=MagicMock())

        self.user_journey_step = UserJourneyStep(
            "test uj step",
            user_time_spent=SourceValue(2 * u.min / u.uj),
            jobs=[self.job])

    def test_user_journey_step_without_job_doesnt_break(self):
        uj_step_without_job = UserJourneyStep(
            "", user_time_spent=SourceValue(2 * u.min / u.uj), jobs=[])

    def test_self_delete_should_raise_error_if_self_has_associated_uj(self):
        uj = MagicMock()
        uj.name = "uj"
        self.user_journey_step.modeling_obj_containers = [uj]
        with self.assertRaises(PermissionError):
            self.user_journey_step.self_delete()


if __name__ == "__main__":
    unittest.main()
