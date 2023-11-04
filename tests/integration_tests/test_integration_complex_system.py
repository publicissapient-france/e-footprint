from efootprint.constants.sources import SourceValue, Sources, SourceObject
from efootprint.core.usage.user_journey import UserJourney, UserJourneyStep
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.hardware.device_population import DevicePopulation, Devices
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import Countries
from efootprint.constants.units import u
from efootprint.logger import logger
from tests.integration_tests.integration_test_base_class import IntegrationTestBaseClass


class IntegrationTestComplexSystem(IntegrationTestBaseClass):
    def setUp(self):
        self.server = Autoscaling(
            "Default server",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(24 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )
        self.storage = Storage(
            "Default SSD storage",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0.1 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS)
        )
        self.service1 = Service(
            "Youtube", self.server, self.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))
        self.service2 = Service(
            "Dailymotion", self.server, self.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

        self.streaming_step = UserJourneyStep(
            "20 min streaming on Youtube", self.service1, SourceValue(50 * u.kB / u.uj),
            SourceValue((2.5 / 3) * u.GB / u.uj),
            user_time_spent=SourceValue(20 * u.min / u.uj), request_duration=SourceValue(4 * u.min))
        self.upload_step = UserJourneyStep(
            "0.4s of upload", self.service1, SourceValue(300 * u.kB / u.uj), SourceValue(0 * u.kB / u.uj),
            user_time_spent=SourceValue(1 * u.s / u.uj), request_duration=SourceValue(0.1 * u.s))
        self.dailymotion_step = UserJourneyStep(
            "Dailymotion step", self.service2, SourceValue(300 * u.kB / u.uj), SourceValue(3 * u.MB / u.uj),
            user_time_spent=SourceValue(60 * u.s / u.uj), request_duration=SourceValue(1 * u.s))

        self.uj = UserJourney(
            "Daily video usage", uj_steps=[self.streaming_step, self.upload_step, self.dailymotion_step])
        self.device_population = DevicePopulation(
            "French video watchers on laptop", SourceValue(4e7 * 0.3 * u.user), Countries.FRANCE, [Devices.LAPTOP])

        self.network = Network("Default network", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        self.usage_pattern = UsagePattern(
            "Video watching in France", self.uj, self.device_population,
            self.network, SourceValue(365 * u.user_journey / (u.user * u.year)),
            SourceObject([[7, 23]], Sources.USER_INPUT))

        self.system = System("system 1", [self.usage_pattern])

        self.initial_footprint = self.system.total_footprint()
        self.initial_fab_footprints = {
            self.storage: self.storage.instances_fabrication_footprint,
            self.server: self.server.instances_fabrication_footprint,
            self.device_population: self.device_population.instances_fabrication_footprint,
        }
        self.initial_energy_footprints = {
            self.storage: self.storage.energy_footprint,
            self.server: self.server.energy_footprint,
            self.network: self.network.energy_footprint,
            self.device_population: self.device_population.energy_footprint,
        }

    def test_remove_service2_uj_step(self):
        logger.warning("Removing service2 uj step")
        self.uj.uj_steps = [self.streaming_step, self.upload_step]

        self.footprint_has_changed([self.server, self.storage])
        self.assertNotEqual(self.initial_footprint, self.system.total_footprint())

        logger.warning("Putting service2 uj step back")
        self.uj.uj_steps = [self.streaming_step, self.upload_step, self.dailymotion_step]

        self.footprint_has_not_changed([self.server, self.storage])
        self.assertEqual(self.initial_footprint, self.system.total_footprint())
