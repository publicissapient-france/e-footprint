import unittest

from efootprint.builders.usage.job_ecobenchmark.ecobenchmark_job_builder import ecobenchmark_job
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.builders.hardware.servers_defaults import default_autoscaling
from efootprint.builders.hardware.storage_defaults import default_ssd


class TestJobEcobenchmarkBuilder(unittest.TestCase):
    def test_ecobenchmark_job(self):
        server = default_autoscaling()
        storage = default_ssd()
        server.base_ram_consumption = SourceValue(1 * u.MB)
        ecobenchmark_job(
            "test job", server, storage, data_upload=SourceValue(1 * u.MB), data_download=SourceValue(1 * u.MB),
            technology='php-symfony')

    def test_ecobenchmark_job_raises_valueerror_if_technology_is_not_in_list(self):
        server = default_autoscaling()
        storage = default_ssd()
        server.base_ram_consumption = SourceValue(1 * u.MB)

        with self.assertRaises(ValueError):
            ecobenchmark_job(
                "test job", server, storage, data_upload=SourceValue(1 * u.MB), data_download=SourceValue(1 * u.MB),
                technology='unexisting-tech')
