from footprint_model.constants.countries import Country
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation
from footprint_model.constants.sources import SourceValue
from footprint_model.core.infra_need import InfraNeed
from footprint_model.constants.units import u

from abc import ABC, abstractmethod


class PhysicalElements:
    LAPTOP = "laptop"
    SMARTPHONE = "smartphone"
    SCREEN = "screen"
    BOX = "box"
    WIFI_NETWORK = "wifi_network"
    MOBILE_NETWORK = "mobile_network"
    SERVER = "server"
    WEB_SERVER = "web_server"
    STORAGE = "storage"


class Hardware:
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue):
        self.name = name
        self.carbon_footprint_fabrication = carbon_footprint_fabrication
        self.carbon_footprint_fabrication.set_name(f"carbon footprint fabrication of {self.name}")
        self.power = power
        self.power.set_name(f"power of {self.name}")
        self.lifespan = lifespan
        self.lifespan.set_name(f"lifespan of {self.name}")


class ObjectLinkedToUsagePatterns(ABC):
    def __init__(self):
        self.usage_patterns = set()

    def link_usage_pattern(self, usage_pattern):
        self.usage_patterns = self.usage_patterns | {usage_pattern}

    def unlink_usage_pattern(self, usage_pattern):
        self.usage_patterns.discard(usage_pattern)


class InfraHardware(Hardware, ObjectLinkedToUsagePatterns):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue, lifespan: SourceValue,
                 country: Country):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan)
        ObjectLinkedToUsagePatterns.__init__(self)
        self.country = country

    @property
    @abstractmethod
    def services(self):
        pass

    @property
    @abstractmethod
    def nb_of_instances(self):
        pass

    @property
    @abstractmethod
    def instances_power(self):
        pass

    @property
    def all_services_infra_needs(self):
        infra_hardware_resource_needs = InfraNeed(
            ram=[ExplainableQuantity(0 * u.Mo)] * 24, storage=ExplainableQuantity(0 * u.To / u.year),
            cpu=[ExplainableQuantity(0 * u.core)] * 24)

        services_using_infra_hardware = self.services
        for usage_pattern in self.usage_patterns:
            for service, service_infra_need in usage_pattern.estimated_infra_need.items():
                if service in services_using_infra_hardware:
                    infra_hardware_resource_needs += service_infra_need

        return infra_hardware_resource_needs

    @property
    def fraction_of_time_in_use(self) -> ExplainableQuantity:
        hours = 0
        for ram, cpu in zip(self.all_services_infra_needs.ram, self.all_services_infra_needs.cpu):
            if ram.magnitude > 0 or cpu.magnitude > 0:
                hours += 1

        return ExplainableQuantity(hours * u.hour / u.day, f"Fraction of time of daily use for {self.name}")

    @property
    @intermediate_calculation("Instances fabrication emissions")
    def instances_fabrication_footprint(self) -> ExplainableQuantity:
        instances_fab_footprint = (
                self.carbon_footprint_fabrication * self.nb_of_instances / self.lifespan).to(u.kg / u.year)

        return instances_fab_footprint

    @property
    @intermediate_calculation("Electricity use footprint")
    def energy_footprint(self) -> ExplainableQuantity:
        energy_footprints = (self.instances_power * self.country.average_carbon_intensity).to(u.kg / u.year)
        return energy_footprints
