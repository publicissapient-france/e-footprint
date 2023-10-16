from footprint_model.constants.units import u
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.explainable_quantities import ExplainableQuantity


class PhysicalElements:
    LAPTOP = "laptop"
    SMARTPHONE = "smartphone"
    SCREEN = "screen"
    BOX = "box"
    WIFI_NETWORK = "wifi_network"
    MOBILE_NETWORK = "mobile_network"
    SERVER = "server"
    SSD = "SSD"
    HDD = "HDD"


class Hardware:
    def __init__(self, name: PhysicalElements, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue):
        self.name = name
        self.carbon_footprint_fabrication = carbon_footprint_fabrication
        self.carbon_footprint_fabrication.set_name(f"carbon footprint fabrication of {self.name}")
        self.power = power
        self.power.set_name(f"power of {self.name}")
        self.lifespan = lifespan
        self.lifespan.set_name(f"lifespan of {self.name}")


class Device(Hardware):
    def __init__(self, name: PhysicalElements, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, fraction_of_usage_time: SourceValue, data_usage: SourceValue):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan)
        self.fraction_of_usage_time = fraction_of_usage_time
        self.fraction_of_usage_time.set_name(f"fraction of usage of {self.name}")
        self.data_usage = data_usage
        self.data_usage.set_name(f"data usage of {self.name}")

    def __post_init__(self):
        if not self.fraction_of_usage_time.value.check("[]"):
            raise ValueError("Variable 'fraction_of_usage_per_day' shouldn’t have any dimensionality")
        if not self.data_usage.value.check("[data] / [time]"):
            raise ValueError("Variable 'data_usage' should have data / time dimensionality")


class Devices:
    SMARTPHONE = Device(
        PhysicalElements.SMARTPHONE,
        carbon_footprint_fabrication=SourceValue(30 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(1 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(3 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(3.6 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022),
        data_usage=SourceValue(12.7 * u.Go / u.month, Sources.ARCEP_2022_MOBILE_NETWORK_STUDY)
    )
    LAPTOP = Device(
        PhysicalElements.LAPTOP,
        carbon_footprint_fabrication=SourceValue(156 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
        # TODO: get data
        data_usage=SourceValue(0 * u.Go / u.month, Sources.HYPOTHESIS)
    )
    BOX = Device(
        PhysicalElements.BOX,
        carbon_footprint_fabrication=SourceValue(78 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(10 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(24 * u.hour / u.day, Sources.HYPOTHESIS),
        # TODO: get data
        data_usage=SourceValue(0 * u.Go / u.month, Sources.HYPOTHESIS)
    )
    SCREEN = Device(
        PhysicalElements.SCREEN,
        # TODO: To update
        carbon_footprint_fabrication=SourceValue(222 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(30 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
        data_usage=SourceValue(0 * u.Go / u.month, Sources.HYPOTHESIS)
    )
    FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN = SourceValue(
        0.20 * u.dimensionless, Sources.HYPOTHESIS, "Fraction of laptops equiped with screen")


class Server(Hardware):
    SERVER_RAM_PER_DATA_TRANSFERRED = ExplainableQuantity(
        5 * u.dimensionless, "Ratio of server RAM needed per quantity of data transfered for one user journey")
    CLOUD_DOWNSCALING_FACTOR = ExplainableQuantity(
        3 * u.dimensionless, "Cloud downscaling factor when service is not in use")

    def __init__(self, name: PhysicalElements, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: SourceValue,
                 power_usage_effectiveness: float):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan)
        self.idle_power = idle_power
        self.idle_power.set_name(f"idle power of {self.name}")
        self.ram = ram
        self.ram.set_name(f"ram of {self.name}")
        self.nb_of_cpus = ExplainableQuantity(nb_of_cpus * u.dimensionless, f"nb cpus of {self.name}")
        self.power_usage_effectiveness = ExplainableQuantity(
            power_usage_effectiveness * u.dimensionless, f"PUE of {self.name}")

    @staticmethod
    def server_utilization_rate(cloud):
        if cloud:
            return ExplainableQuantity(0.9 * u.dimensionless, "Cloud server utilization rate")
        else:
            return ExplainableQuantity(0.7 * u.dimensionless, "On premise server utilization rate")


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


class Storage(Hardware):
    def __init__(self, name: PhysicalElements, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, storage_capacity: SourceValue,
                 power_usage_effectiveness: float):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan)
        self.idle_power = idle_power
        self.idle_power.set_name(f"idle power of {self.name}")
        self.storage_capacity = storage_capacity
        self.storage_capacity.set_name(f"storage capacity of {self.name}")
        self.power_usage_effectiveness = ExplainableQuantity(
            power_usage_effectiveness * u.dimensionless, f"PUE of {self.name}")


class Storages:
    SSD_STORAGE = Storage(
        PhysicalElements.SSD,
        carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
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


class Network:
    def __init__(self, name: PhysicalElements, bandwidth_energy_intensity: SourceValue):
        self.name = name
        self.bandwidth_energy_intensity = bandwidth_energy_intensity
        self.bandwidth_energy_intensity.set_name(f"bandwith energy intensity of {self.name}")


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
