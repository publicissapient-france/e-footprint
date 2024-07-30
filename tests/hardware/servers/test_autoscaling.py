from unittest import TestCase
from unittest.mock import MagicMock, patch

from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.builders.time_builders import create_hourly_usage_df_from_list


class TestAutoscaling(TestCase):
    def setUp(self):
        self.country = MagicMock()
        self.server_base = Autoscaling(
            "Autoscaling",
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(0 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(0 * u.GB, Sources.HYPOTHESIS),
            cpu_cores=SourceValue(0 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
            server_utilization_rate=SourceValue(0 * u.dimensionless)
        )

        self.server_base.dont_handle_input_updates = True

    def test_nb_of_instances_autoscaling_simple_case(self):
        ram_need = SourceHourlyValues(create_hourly_usage_df_from_list([0, 1, 2, 3, 10], pint_unit=u.GB))
        cpu_need = SourceHourlyValues(create_hourly_usage_df_from_list([1, 4, 2, 10, 3], pint_unit=u.core))

        with patch.object(self.server_base, "all_services_ram_needs", new=ram_need), \
                patch.object(self.server_base, "all_services_cpu_needs", new=cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(2 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(4 * u.core)):
            self.server_base.update_nb_of_instances()
            self.assertEqual([1, 1, 1, 3, 5], self.server_base.nb_of_instances.value_as_float_list)

    def test_nb_of_instances_autoscaling_different_timespan_cas(self):
        raise NotImplementedError

    def test_compute_instances_energy(self):
        with patch.object(self.server_base, "nb_of_instances",
                          SourceHourlyValues(create_hourly_usage_df_from_list([1, 0, 2]))), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(3 * u.dimensionless)):
            self.server_base.update_instances_energy()
            self.assertEqual(u.kWh, self.server_base.instances_energy.unit)
            self.assertEqual([0.9, 0, 1.8], self.server_base.instances_energy.value_as_float_list)
