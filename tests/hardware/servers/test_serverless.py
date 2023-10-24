from efootprint.constants.physical_elements import PhysicalElements
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u
from efootprint.core.hardware.servers.serverless import Serverless
from tests.utils import create_cpu_need, create_ram_need

from unittest import TestCase
from unittest.mock import MagicMock, patch

SERVER_MODULE = "footprint_model.core.server.Server"


class TestServerless(TestCase):
    def setUp(self):
        self.country = MagicMock()
        self.server_base = Serverless(
            PhysicalElements.SERVERLESS,
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

    def test_nb_of_instances_serverless(self):
        ram_need = (create_ram_need([[0, 12]], 100 * u.GB) + create_ram_need([[12, 24]], 150 * u.GB))
        cpu_need = create_cpu_need([[0, 24]], 1 * u.core)

        with patch.object(self.server_base, "all_services_ram_needs", new=ram_need), \
                patch.object(self.server_base, "all_services_cpu_needs", new=cpu_need), \
                patch.object(self.server_base, "available_ram_per_instance", new=SourceValue(100 * u.GB)), \
                patch.object(self.server_base, "available_cpu_per_instance", new=SourceValue(25 * u.core)):
            self.server_base.update_nb_of_instances()
            self.assertEqual(1.25 * u.dimensionless, round(self.server_base.nb_of_instances.value, 2))

    def test_compute_instances_power_serverless(self):
        with patch.object(self.server_base,
                          "fraction_of_time_in_use", SourceValue(((24 - 10) / 24) * u.dimensionless)), \
                patch.object(self.server_base, "nb_of_instances", SourceValue(10 * u.dimensionless)), \
                patch.object(self.server_base, "power", SourceValue(300 * u.W)), \
                patch.object(self.server_base, "idle_power", SourceValue(50 * u.W)), \
                patch.object(self.server_base, "power_usage_effectiveness", SourceValue(1.2 * u.dimensionless)):
            self.server_base.update_instances_power()
            self.assertEqual(round((3600 * u.W).to(u.kWh / u.year), 2),
                             round(self.server_base.instances_power.value, 2))
