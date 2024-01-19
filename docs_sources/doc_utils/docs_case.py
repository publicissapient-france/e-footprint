from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.core.usage.job import Job
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import country_generator, tz
from efootprint.constants.units import u


server = Autoscaling(
    "server",
    carbon_footprint_fabrication=SourceValue(600 * u.kg, source=None),
    power=SourceValue(300 * u.W, source=None),
    lifespan=SourceValue(6 * u.year, source=None),
    idle_power=SourceValue(50 * u.W, source=None),
    ram=SourceValue(128 * u.GB, source=None),
    cpu_cores=SourceValue(24 * u.core, source=None),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, source=None),
    average_carbon_intensity=SourceValue(100 * u.g / u.kWh, source=None),
    server_utilization_rate=SourceValue(0.9 * u.dimensionless, source=None))

storage = Storage(
    "storage",
    carbon_footprint_fabrication=SourceValue(160 * u.kg, source=None),
    power=SourceValue(1.3 * u.W, source=None),
    lifespan=SourceValue(6 * u.years, source=None),
    idle_power=SourceValue(0 * u.W, source=None),
    storage_capacity=SourceValue(1 * u.TB, source=None),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, source=None),
    average_carbon_intensity=SourceValue(100 * u.g / u.kWh, source=None),
    data_replication_factor=SourceValue(3 * u.dimensionless, source=None))

service = Service(
    "service",
    server=server,
    storage=storage,
    base_ram_consumption=SourceValue(300 * u.MB, source=None),
    base_cpu_consumption=SourceValue(2 * u.core, source=None))

streaming_step = UserJourneyStep(
    "20 min streaming",
    user_time_spent=SourceValue(20 * u.min / u.uj, source=None),
    jobs=[
        Job(
            "streaming",
            service=service,
            data_upload=SourceValue(0.05 * u.MB / u.uj, source=None),
            data_download=SourceValue(800 * u.MB / u.uj, source=None),
            request_duration=SourceValue(4 * u.min, source=None),
            cpu_needed=SourceValue(1 * u.core / u.uj, source=None),
            ram_needed=SourceValue(50 * u.MB / u.uj, source=None)
            )
        ]
    )

user_journey = UserJourney("user journey", uj_steps=[streaming_step])

device_population = DevicePopulation(
    "device population",
    nb_devices=SourceValue(4e7 * 0.3 * u.user, source=None),
    country=country_generator(
        "devices country", "its 3 letter shortname, for example FRA", SourceValue(85 * u.g / u.kWh, source=None),
        2022, tz('Europe/Paris'))(),
    devices=[
        Hardware(name="device on which the user journey is made",
                 carbon_footprint_fabrication=SourceValue(156 * u.kg, source=None),
                 power=SourceValue(50 * u.W, source=None),
                 lifespan=SourceValue(6 * u.year, source=None),
                 fraction_of_usage_time=SourceValue(7 * u.hour / u.day, source=None))])

network = Network(
        "network",
        bandwidth_energy_intensity=SourceValue(0.05 * u("kWh/GB"), source=None))

usage_pattern = UsagePattern(
    "usage pattern",
    user_journey=user_journey,
    device_population=device_population,
    network=network,
    user_journey_freq_per_user=SourceValue(365 * u.user_journey / (u.user * u.year), source=None),
    time_intervals=SourceObject([[7, 12], [17, 23]]))

system = System("system", usage_patterns=[usage_pattern])
