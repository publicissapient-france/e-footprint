from efootprint.constants.sources import SourceValue, Sources, SourceObject
from efootprint.core.usage.user_journey import UserJourney, UserJourneyStep
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import Countries
from efootprint.constants.units import u
from efootprint.logger import logger
from efootprint.builders.hardware.devices_defaults import default_laptop
from tests.integration_tests.integration_test_base_class import IntegrationTestBaseClass


class IntegrationTestComplexSystem(IntegrationTestBaseClass):
    @classmethod
    def setUpClass(cls):
        cls.server1 = Autoscaling(
            "Server 1",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(12 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(6 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )
        cls.storage = Storage(
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
        cls.service1 = Service(
            "Youtube", cls.server1, cls.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))
        cls.service2 = Service(
            "Dailymotion", cls.server1, cls.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

        cls.server2 = Autoscaling(
            "Server 2",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(12 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(6 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )

        cls.service3 = Service(
            "TikTok server", cls.server2, cls.storage,
            base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

        cls.streaming_step = UserJourneyStep(
            "20 min streaming on Youtube", cls.service1, SourceValue(50 * u.kB / u.uj),
            SourceValue((2.5 / 3) * u.GB / u.uj),
            user_time_spent=SourceValue(20 * u.min / u.uj), request_duration=SourceValue(4 * u.min))
        cls.upload_step = UserJourneyStep(
            "0.4s of upload", cls.service1, SourceValue(300 * u.kB / u.uj), SourceValue(0 * u.kB / u.uj),
            user_time_spent=SourceValue(1 * u.s / u.uj), request_duration=SourceValue(0.1 * u.s))
        cls.dailymotion_step = UserJourneyStep(
            "Dailymotion step", cls.service2, SourceValue(300 * u.kB / u.uj), SourceValue(3 * u.MB / u.uj),
            user_time_spent=SourceValue(60 * u.s / u.uj), request_duration=SourceValue(1 * u.s))
        cls.tiktok_step = UserJourneyStep(
            "20 min streaming on Tiktok", cls.service3, SourceValue(50 * u.kB / u.uj),
            SourceValue((2.5 / 3) * u.GB / u.uj),
            user_time_spent=SourceValue(20 * u.min / u.uj), request_duration=SourceValue(4 * u.min))

        cls.uj = UserJourney(
            "Daily video usage", uj_steps=[cls.streaming_step, cls.upload_step, cls.dailymotion_step, cls.tiktok_step])
        cls.device_population = DevicePopulation(
            "French video watchers on laptop", SourceValue(4e7 * 0.3 * u.user), Countries.FRANCE, [default_laptop()])

        cls.network = Network("Default network", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        cls.usage_pattern = UsagePattern(
            "Video watching in France", cls.uj, cls.device_population,
            cls.network, SourceValue(365 * u.user_journey / (u.user * u.year)),
            SourceObject([[7, 23]], Sources.USER_INPUT))

        cls.system = System("system 1", [cls.usage_pattern])

        cls.initial_footprint = cls.system.total_footprint()
        cls.initial_fab_footprints = {
            cls.storage: cls.storage.instances_fabrication_footprint,
            cls.server1: cls.server1.instances_fabrication_footprint,
            cls.device_population: cls.device_population.instances_fabrication_footprint,
        }
        cls.initial_energy_footprints = {
            cls.storage: cls.storage.energy_footprint,
            cls.server1: cls.server1.energy_footprint,
            cls.network: cls.network.energy_footprint,
            cls.device_population: cls.device_population.energy_footprint,
        }

    def test_remove_service2_uj_step(self):
        logger.warning("Removing service2 uj step")
        self.uj.uj_steps = [self.streaming_step, self.upload_step]

        self.footprint_has_changed([self.server1, self.storage])
        self.assertNotEqual(self.initial_footprint, self.system.total_footprint())

        logger.warning("Putting service2 uj step back")
        self.uj.uj_steps = [self.streaming_step, self.upload_step, self.dailymotion_step, self.tiktok_step]

        self.footprint_has_not_changed([self.server1, self.storage])
        self.assertEqual(self.initial_footprint, self.system.total_footprint())

    def test_add_new_service(self):
        logger.warning("Adding service")
        new_service = Service(
            "new service", self.server1, self.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(1 * u.core, Sources.HYPOTHESIS))
        new_uj = UserJourneyStep(
            "new uj step", new_service, SourceValue(300 * u.kB / u.uj), SourceValue(300 * u.kB / u.uj),
            user_time_spent=SourceValue(1 * u.s / u.uj), request_duration=SourceValue(0.1 * u.s))
        self.uj.uj_steps += [new_uj]

        self.footprint_has_changed([self.server1, self.storage])
        self.assertNotEqual(self.initial_footprint, self.system.total_footprint())

        logger.warning("Removing new service")
        self.uj.uj_steps = self.uj.uj_steps[:-1]
        new_uj.self_delete()
        new_service.self_delete()

        self.footprint_has_not_changed([self.server1, self.storage])
        self.assertEqual(self.initial_footprint, self.system.total_footprint())

    def test_plot_footprints_by_category_and_object(self):
        self.system.plot_footprints_by_category_and_object()

    def test_plot_emission_diffs(self):
        raise NotImplementedError
