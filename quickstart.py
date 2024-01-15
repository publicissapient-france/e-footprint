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
from efootprint.utils.calculus_graph import build_calculus_graph
from efootprint.utils.object_relationships_graphs import build_object_relationships_graph, \
    USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE
from efootprint.builders.hardware.devices_defaults import default_laptop

import os

server = Autoscaling(
    "Autoscaling server",
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
storage = Storage(
    "SSD storage",
    carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
    idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
    storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
    data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS),
)
service = Service(
    "Youtube", server, storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
    base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

streaming_step = UserJourneyStep(
    "20 min streaming on Youtube", service, SourceValue(50 * u.kB / u.uj, Sources.USER_INPUT),
    SourceValue((2.5 / 3) * u.GB / u.uj, Sources.USER_INPUT),
    user_time_spent=SourceValue(20 * u.min / u.uj, Sources.USER_INPUT),
    request_duration=SourceValue(4 * u.min, Sources.HYPOTHESIS))
upload_step = UserJourneyStep(
    "0.4s of upload", service, SourceValue(300 * u.kB / u.uj, Sources.USER_INPUT),
    SourceValue(0 * u.GB / u.uj, Sources.USER_INPUT),
    user_time_spent=SourceValue(0.4 * u.s / u.uj, Sources.USER_INPUT),
    request_duration=SourceValue(0.4 * u.s, Sources.HYPOTHESIS))

user_journey = UserJourney("Mean Youtube user journey", uj_steps=[streaming_step, upload_step])

device_population = DevicePopulation(
    "French Youtube users on laptop", SourceValue(4e7 * 0.3 * u.user, Sources.USER_INPUT),
    Countries.FRANCE, [default_laptop()])

network = Network(
        "WIFI network",
        SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY)
    )

usage_pattern = UsagePattern(
    "Daily Youtube usage", user_journey, device_population,
    network, SourceValue(365 * u.user_journey / (u.user * u.year), Sources.USER_INPUT),
    SourceObject([[7, 12], [17, 23]]))

system = System("system 1", [usage_pattern])

print(f"Server carbon footprint is {(server.energy_footprint + server.instances_fabrication_footprint).value}")
print(f"Total system carbon footprint is {system.total_footprint().value}")

current_dir = os.path.abspath(os.path.dirname(__file__))

calculus_graph = build_calculus_graph(device_population.instances_fabrication_footprint)
calculus_graph.show(os.path.join(current_dir, "device_population_fab_footprint_calculus_graph.html"))

object_relationships_graph = build_object_relationships_graph(
    usage_pattern, classes_to_ignore=USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE)
object_relationships_graph.show(os.path.join(current_dir, "object_relationships_graph.html"))
