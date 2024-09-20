from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch

from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.builders.time_builders import create_hourly_usage_df_from_list


class TestInfraHardware(TestCase):
    def setUp(self):
        class InfraHardwareTestClass(InfraHardware):
            def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                         lifespan: SourceValue, average_carbon_intensity: SourceValue):
                super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
                self.dont_handle_pubsub_topic_messages = True

            def update_raw_nb_of_instances(self):
                self.raw_nb_of_instances = SourceHourlyValues(create_hourly_usage_df_from_list([1.5, 3]))

            def update_nb_of_instances(self):
                self.nb_of_instances = SourceHourlyValues(create_hourly_usage_df_from_list([2, 3]))

            def update_instances_energy(self):
                self.instances_energy = SourceHourlyValues(create_hourly_usage_df_from_list([2, 4], pint_unit=u.kWh))

        self.test_infra_hardware = InfraHardwareTestClass(
            "test_infra_hardware", carbon_footprint_fabrication=SourceValue(120 * u.kg, Sources.USER_DATA),
            power=SourceValue(2 * u.W, Sources.USER_DATA), lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh))

        self.job1 = MagicMock()
        self.job2 = MagicMock()
        self.job3 = MagicMock()

        self.job1.ram_needed = SourceHourlyValues(create_hourly_usage_df_from_list([0, 8], pint_unit=u.GB))
        self.job2.ram_needed = SourceHourlyValues(create_hourly_usage_df_from_list([6, 14], pint_unit=u.GB))
        self.job3.ram_needed = SourceHourlyValues(create_hourly_usage_df_from_list([8, 16], pint_unit=u.GB))
        self.job1.cpu_needed = SourceHourlyValues(create_hourly_usage_df_from_list([0, 8], pint_unit=u.core))
        self.job2.cpu_needed = SourceHourlyValues(create_hourly_usage_df_from_list([6, 14], pint_unit=u.core))
        self.job3.cpu_needed = SourceHourlyValues(create_hourly_usage_df_from_list([8, 16], pint_unit=u.core))

        self.test_infra_hardware_single_job = deepcopy(self.test_infra_hardware)
        self.test_infra_hardware_single_job.modeling_obj_containers = [self.job1]
        self.test_infra_hardware_multiple_jobs = deepcopy(self.test_infra_hardware)
        self.test_infra_hardware_multiple_jobs.modeling_obj_containers = [self.job1, self.job2, self.job3]

    def test_jobs(self):
        job1 = MagicMock()
        job2 = MagicMock()

        with patch.object(self.test_infra_hardware, "modeling_obj_containers", new=[job1, job2]):
            self.assertEqual([job1, job2], self.test_infra_hardware.jobs)

    def test_instances_fabrication_footprint(self):
        self.test_infra_hardware_single_job.update_nb_of_instances()
        self.test_infra_hardware_single_job.update_instances_fabrication_footprint()
        self.assertEqual(u.kg, self.test_infra_hardware_single_job.instances_fabrication_footprint.unit)
        self.assertEqual(
            [round(2 * 20 / (365.25 * 24), 3), round(3 * 20 / (365.25 * 24), 3)],
            self.test_infra_hardware_single_job.instances_fabrication_footprint.round(3).value_as_float_list)

    def test_energy_footprints(self):
        self.test_infra_hardware_single_job.update_instances_energy()
        self.test_infra_hardware_single_job.update_energy_footprint()
        self.assertEqual(u.kg, self.test_infra_hardware_single_job.energy_footprint.unit)
        self.assertEqual([0.2, 0.4],
                         self.test_infra_hardware_single_job.energy_footprint.value_as_float_list)
