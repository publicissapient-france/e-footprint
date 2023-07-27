from unittest import TestCase

from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.core.user_journey import UserJourney, UserJourneyStep
from footprint_model.core.server import Servers
from footprint_model.core.storage import Storage
from footprint_model.core.service import Service
from footprint_model.core.device_population import DevicePopulation, Devices
from footprint_model.core.usage_pattern import UsagePattern
from footprint_model.core.network import Networks
from footprint_model.core.system import System
from footprint_model.constants.countries import Countries
from footprint_model.constants.units import u


class IntegrationTest(TestCase):
    def test_init_use_case(self):
        server = Servers.SERVER
        default_device_pop = DevicePopulation(
            "French Youtube users on laptop", 4e7 * 0.3, Countries.FRANCE, [Devices.LAPTOP])

    def test_base_use_case(self):
        server = Servers.SERVER
        storage = Storage(
            "Default SSD storage",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=1.2,
            country=Countries.GERMANY,
            data_replication_factor=3,
            data_storage_duration=10 * u.year
        )
        service = Service("Youtube", server, storage, base_ram_consumption=300 * u.Mo,
                          base_cpu_consumption=2 * u.core)

        streaming_step = UserJourneyStep("20 min streaming on Youtube", service, 50 * u.ko, (2.5 / 3) * u.Go,
                                         user_time_spent=20 * u.min, request_duration=4 * u.min)
        upload_step = UserJourneyStep("0.4s of upload", service, 300 * u.ko, 0 * u.Go, user_time_spent=1 * u.s,
                                      request_duration=0.1 * u.s)

        default_uj = UserJourney("Daily Youtube usage", uj_steps=[streaming_step, upload_step])
        print(default_uj.duration.value)
        #upload_step.user_time_spent = ExplainableQuantity(1 * u.hour / u.user_journey, "one hour")
        print(default_uj.duration.value)
        print(default_uj.duration.explain())
        default_device_pop = DevicePopulation(
            "French Youtube users on laptop", 4e7 * 0.3, Countries.FRANCE, [Devices.LAPTOP])

        default_network = Networks.WIFI_NETWORK
        usage_pattern = UsagePattern(
            "Average daily Youtube usage in France on laptop", default_uj, default_device_pop,
            default_network, 365 * u.user_journey / (u.user * u.year), [[7, 23]])

        system = System("system 1", [usage_pattern])

        fabrication_dict = {
            "Servers": 170023 * u.kg / u.year,
            "Storage": 1226400 * u.kg / u.year,
            "Devices": 14859346 * u.kg / u.year,
            "Network": 0 * u.kg / u.year
        }

        print(system.fabrication_footprints())

        energy_footprints_dict = {
            "Servers": 2071091 * u.kg / u.year,
            "Storage": 1 * u.kg / u.year,
            "Devices": 6210171 * u.kg / u.year,
            "Network": 15519015 * u.kg / u.year
        }

        print(system.energy_footprints())