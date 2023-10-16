from footprint_model.constants.physical_elements import InfraHardware, PhysicalElements
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.constants.countries import Country, Countries

import math


class Server(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: int,
                 power_usage_effectiveness: float, country: Country, cloud: bool):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, country)
        self.idle_power = idle_power
        self.idle_power.set_name(f"idle power of {self.name}")
        self.ram = ram
        self.ram.set_name(f"ram of {self.name}")
        self.nb_of_cpus = ExplainableQuantity(nb_of_cpus * u.core, f"nb cpus of {self.name}")
        self.power_usage_effectiveness = ExplainableQuantity(
            power_usage_effectiveness * u.dimensionless, f"PUE of {self.name}")
        self.cloud = cloud
        self.usage_patterns = set()

    @property
    def server_utilization_rate(self):
        if self.cloud:
            return ExplainableQuantity(0.9 * u.dimensionless, "Cloud server utilization rate")
        else:
            return ExplainableQuantity(0.7 * u.dimensionless, "On premise server utilization rate")

    @property
    def services(self):
        return {service for usage_pattern in self.usage_patterns for service in usage_pattern.services
                if service.server == self}

    def available_resource_per_instance(self, server_resource: ExplainableQuantity,
                                        service_base_resource_consumption: str):
        available_resource_per_instance = server_resource * self.server_utilization_rate
        for service in self.services:
            available_resource_per_instance -= getattr(service, service_base_resource_consumption)
            if available_resource_per_instance.value < 0:
                services_resource_need = sum(service.get(service_base_resource_consumption) for service in self.services)
                raise ValueError(
                    f"server {self.name} has available capacity of "
                    f"{(server_resource * self.server_utilization_rate).value} "
                    f"of {service_base_resource_consumption} but is asked {services_resource_need.value}")

        return available_resource_per_instance

    @property
    def available_ram_per_instance(self):
        return self.available_resource_per_instance(self.ram, "base_ram_consumption")

    @property
    def available_cpu_per_instance(self):
        return self.available_resource_per_instance(self.nb_of_cpus, "base_cpu_consumption")

    @property
    @intermediate_calculation("Nb of instances")
    def nb_of_instances(self) -> ExplainableQuantity:
        if self.cloud:
            one_day = ExplainableQuantity(24 * u.hour, '24 hours')
            ram_needed_per_day = (
                    sum(self.all_services_infra_needs.ram) * ExplainableQuantity(1 * u.hour, "1 hour") / one_day)
            cpu_needed_per_day = (
                    sum(self.all_services_infra_needs.cpu) * ExplainableQuantity(1 * u.hour, "1 hour") / one_day)

            nb_of_servers_raw = max(ram_needed_per_day / self.available_ram_per_instance,
                                    cpu_needed_per_day / self.available_cpu_per_instance)

            nb_of_instances = nb_of_servers_raw
        else:
            ram_needed_per_day = max(self.all_services_infra_needs.ram)
            cpu_needed_per_day = max(self.all_services_infra_needs.cpu)

            nb_of_servers_raw = max(ram_needed_per_day / self.available_ram_per_instance,
                                    cpu_needed_per_day / self.available_cpu_per_instance).to(u.dimensionless)
            if math.ceil(nb_of_servers_raw.magnitude) - nb_of_servers_raw.magnitude != 0:
                nb_of_instances = nb_of_servers_raw + ExplainableQuantity(
                    (math.ceil(nb_of_servers_raw.magnitude) - nb_of_servers_raw.magnitude)
                    * u.dimensionless, "Extra server capacity because number of servers must be an integer")
            else:
                nb_of_instances = nb_of_servers_raw

        return nb_of_instances

    @property
    @intermediate_calculation("Instances power")
    def instances_power(self) -> ExplainableQuantity:
        effective_power = self.power * self.power_usage_effectiveness
        if self.cloud:
            server_power = (effective_power * self.nb_of_instances).to(u.kWh / u.year)
        else:
            hours_per_day = ExplainableQuantity(24 * u.hour / u.day)
            usage_hours = self.fraction_of_time_in_use
            non_usage_hours = hours_per_day - usage_hours
            server_power = (
                    self.nb_of_instances * 
                    ((effective_power * usage_hours) + (self.idle_power * non_usage_hours))
            ).to(u.kWh / u.year)
        return server_power


class Servers:
    SERVER = Server(
        PhysicalElements.SERVER,
        carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        ram=SourceValue(128 * u.Go, Sources.HYPOTHESIS),
        nb_of_cpus=24,
        power_usage_effectiveness=1.2,
        country=Countries.GERMANY,
        cloud=True
    )
