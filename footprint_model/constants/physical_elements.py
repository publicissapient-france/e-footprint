from footprint_model.constants.units import u
from footprint_model.constants.sources import SourceValue, Sources

from dataclasses import dataclass
import enum


class PhysicalElements(str, enum.Enum):
    LAPTOP = "laptop"
    SMARTPHONE = "smartphone"
    SCREEN = "screen"
    BOX = "box"
    WIFI_NETWORK = "wifi_network"
    MOBILE_NETWORK = "mobile_network"
    SERVER = "server"
    SSD = "SSD"
    HDD = "HDD"


@dataclass
class Hardware:
    name: PhysicalElements
    carbon_footprint_fabrication: SourceValue
    power: SourceValue
    lifespan: SourceValue


@dataclass
class Device(Hardware):
    fraction_of_usage_per_day: SourceValue

    def __post_init__(self):
        if not self.fraction_of_usage_per_day.value.check("[]"):
            raise ValueError("Variable 'fraction_of_usage_per_day' shouldn’t have any dimensionality")


class Devices:
    SMARTPHONE = Device(
        PhysicalElements.SMARTPHONE,
        carbon_footprint_fabrication=SourceValue(30 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(1 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(3 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_per_day=SourceValue(3 * u.hour / u.day, Sources.HYPOTHESIS),
    )
    LAPTOP = Device(
        PhysicalElements.LAPTOP,
        carbon_footprint_fabrication=SourceValue(156 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_per_day=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
    )
    BOX = Device(
        PhysicalElements.BOX,
        carbon_footprint_fabrication=SourceValue(78 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(10 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_per_day=SourceValue(24 * u.hour / u.day, Sources.HYPOTHESIS)
    )
    SCREEN = Device(
        PhysicalElements.SCREEN,
        # TODO: To update
        carbon_footprint_fabrication=SourceValue(222 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(30 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_per_day=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS)
    )
    FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN = 0.20


@dataclass
class Server(Hardware):
    idle_power: SourceValue
    ram: SourceValue
    nb_of_cpus: SourceValue
    power_usage_effectiveness: float

    # Number of Mo of RAM the server needs to generate and transfer 1 Mo of data. To improve
    SERVER_RAM_PER_DATA_TRANSFERRED = 5
    SERVER_UTILISATION_RATE = 0.7


class Servers:
    SERVER = Server(
        PhysicalElements.SERVER,
        carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        ram=SourceValue(128 * u.Go, Sources.HYPOTHESIS),
        nb_of_cpus=24,
        power_usage_effectiveness=1.2
    )


@dataclass
class Storage(Hardware):
    idle_power: SourceValue
    storage_capacity: SourceValue
    power_usage_effectiveness: float


class Storages:
    SSD_STORAGE = Storage(
        PhysicalElements.SSD,
        carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(4 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=1.2
    )
    HDD_STORAGE = Storage(
        PhysicalElements.HDD,
        carbon_footprint_fabrication=SourceValue(20 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(4.2 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(4 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=1.2
    )

@dataclass
class Network:
    name: PhysicalElements
    bandwidth_energy_intensity: SourceValue


class Networks:
    WIFI_NETWORK = Network(
        PhysicalElements.WIFI_NETWORK,
        SourceValue(0.05 * u("kWh/Go"), Sources.TRAFICOM_STUDY),
        # TODO: enable list for multiple sources
        # SourceValue(0.08 * u("kWh/Go"), Sources.ONE_BYTE_MODEL_SHIFT_2018)
    )
    MOBILE_NETWORK = Network(
        PhysicalElements.MOBILE_NETWORK,
        SourceValue(0.12 * u("kWh/Go"), Sources.TRAFICOM_STUDY),
        # SourceValue(0.06 * u("kWh/Go"), Sources.ONE_BYTE_MODEL_SHIFT_2018)
    )


if __name__ == "__main__":
    test_source = SourceValue(
        value=78 * u.kg,
        source=Sources.ADEME_STUDY,
    )
    print(test_source)
