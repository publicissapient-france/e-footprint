import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock

from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.usage.job import Job
from efootprint.constants.units import u


class TestJob(TestCase):
    def setUp(self):
        self.service = MagicMock()
        self.service.name = "service"

        self.job = Job(
            "test job", service=self.service, data_download=SourceValue(200 * u.MB / u.uj),
            data_upload=SourceValue(100 * u.MB / u.uj),
            ram_needed=SourceValue(400 * u.MB / u.uj), cpu_needed=SourceValue(2 * u.core / u.uj),
            request_duration=SourceValue(2 * u.min))

    def test_self_delete_should_raise_error_if_self_has_associated_uj_step(self):
        uj_step = MagicMock()
        uj_step.name = "uj_step"
        self.job.modeling_obj_containers = [uj_step]
        with self.assertRaises(PermissionError):
            self.job.self_delete()

    def test_self_delete_removes_backward_links_and_recomputes_server_and_storage(self):
        with patch.object(Job, "mod_obj_attributes", new_callable=PropertyMock) as mock_mod_obj_attributes:
            mock_mod_obj_attributes.return_value = [self.service]
            self.service.modeling_obj_containers = [self.job]
            self.job.self_delete()
            self.assertEqual([], self.service.modeling_obj_containers)
            self.service.launch_attributes_computation_chain.assert_called_once()


if __name__ == "__main__":
    unittest.main()
