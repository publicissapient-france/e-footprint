from unittest import TestCase

from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.core.usage.user_journey import UserJourney, UserJourneyStep
from footprint_model.core.hardware.server import Servers
from footprint_model.core.hardware.storage import Storage
from footprint_model.core.service import Service
from footprint_model.core.hardware.device_population import DevicePopulation, Devices
from footprint_model.core.usage.usage_pattern import UsagePattern
from footprint_model.core.hardware.network import Networks
from footprint_model.core.system import System
from footprint_model.constants.countries import Countries
from footprint_model.constants.units import u


class IntegrationTest(TestCase):
    def test_base_use_case(self):
        server = Servers.SERVER
        server.cloud = "Serverless"
        storage = Storage(
            "Default SSD storage",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            country=Countries.GERMANY,
            data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS)
        )
        service = Service("Youtube", server, storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
                          base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

        streaming_step = UserJourneyStep(
            "20 min streaming on Youtube", service, SourceValue(50 * u.kB / u.uj), SourceValue((2.5 / 3) * u.GB / u.uj),
            user_time_spent=SourceValue(20 * u.min / u.uj), request_duration=SourceValue(4 * u.min))
        upload_step = UserJourneyStep(
            "0.4s of upload", service, SourceValue(300 * u.kB / u.uj), SourceValue(0 * u.GB / u.uj),
            user_time_spent=SourceValue(1 * u.s / u.uj), request_duration=SourceValue(0.1 * u.s))

        default_uj = UserJourney("Daily Youtube usage", uj_steps=[streaming_step, upload_step])
        default_device_pop = DevicePopulation(
            "French Youtube users on laptop", SourceValue(4e7 * 0.3 * u.user), Countries.FRANCE, [Devices.LAPTOP])

        default_network = Networks.WIFI_NETWORK
        usage_pattern = UsagePattern(
            "Average daily Youtube usage in France on laptop", default_uj, default_device_pop,
            default_network, SourceValue(365 * u.user_journey / (u.user * u.year)), [[7, 23]])

        system = System("system 1", [usage_pattern])

        system.fabrication_footprints()
        system.energy_footprints()
