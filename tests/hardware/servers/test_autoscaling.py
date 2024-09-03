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
        raw_data = [0.5, 1, 1.5, 1.5, 5]
        expected_data = [1, 1, 2, 2, 5]

        hourly_raw_data = SourceHourlyValues(create_hourly_usage_df_from_list(raw_data, pint_unit=u.dimensionless))
        with patch.object(self.server_base, "raw_nb_of_instances", new=hourly_raw_data):
            self.server_base.update_nb_of_instances()

            self.assertEqual(expected_data, self.server_base.nb_of_instances.value_as_float_list)
