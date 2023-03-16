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
    average_usage_duration_per_day: SourceValue


class Devices:
    SMARTPHONE = Device(
        PhysicalElements.SMARTPHONE,
        carbon_footprint_fabrication=SourceValue(60 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(1 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(3 * u.year, Sources.HYPOTHESIS),
        average_usage_duration_per_day=SourceValue(3 * u.hour, Sources.HYPOTHESIS),
    )
    LAPTOP = Device(
        PhysicalElements.LAPTOP,
        carbon_footprint_fabrication=SourceValue(156 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        average_usage_duration_per_day=SourceValue(7 * u.hour, Sources.HYPOTHESIS),
    )


@dataclass
class Server(Hardware):
    idle_power: SourceValue
    ram: SourceValue
    nb_of_cpus: SourceValue


class Servers:
    SERVER = Server(
        PhysicalElements.SERVER,
        carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        ram=SourceValue(128 * u.Go, Sources.HYPOTHESIS),
    )


@dataclass
class Storage(Hardware):
    idle_power: SourceValue
    storage_capacity: SourceValue


class Storages:
    SSD_STORAGE = Storage(
        PhysicalElements.SSD,
        carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(4 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY)
    )
    HDD_STORAGE = Storage(
        PhysicalElements.HDD,
        carbon_footprint_fabrication=SourceValue(20 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(4.2 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(4 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY)
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
