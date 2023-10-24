from efootprint.constants.physical_elements import PhysicalElements
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u
from efootprint.core.hardware.servers.on_premise import OnPremise
from tests.utils import create_cpu_need, create_ram_need

from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestOnPremise(TestCase):
    def setUp(self):
        self.country = MagicMock()
        self.server_base = OnPremise(
            PhysicalElements.ON_PREMISE,
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(0 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(0 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(0 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(0 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
            server_utilization_rate=SourceValue(0 * u.dimensionless)
        )
        self.server_base.dont_handle_input_updates = True

    def test_nb_of_instances_on_premise_rounds_up_to_next_integer(self):
        hour_by_hour_ram_need = create_ram_need([[10, 20]], ram=950 * u.GB)
        hour_by_hour_cpu_need = create_cpu_need([[10, 20]])

        with patch.object(self.server_base, "all_services_ram_needs", new= hour_by_hour_ram_need), \
                patch.object(self.server_base, "all_services_cpu_needs", new=hour_by_hour_cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(100 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(25 * u.core)):
            self.server_base.update_nb_of_instances()
            self.assertEqual(10 * u.dimensionless, self.server_base.nb_of_instances.value)

    def test_compute_instances_power(self):
        with patch.object(self.server_base,
                          "fraction_of_time_in_use", SourceValue(((24 - 10) / 24) * u.dimensionless)), \
                patch.object(self.server_base, "nb_of_instances", SourceValue(10 * u.dimensionless)), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(1.2 * u.dimensionless)):
            self.server_base.update_instances_power()
            self.assertEqual(20600.1 * u.kWh / u.year,
                             round(self.server_base.instances_power.value, 2))
