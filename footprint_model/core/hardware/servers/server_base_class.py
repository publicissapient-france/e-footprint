from abc import abstractmethod

from footprint_model.core.hardware.hardware_base_classes import InfraHardware
from footprint_model.constants.sources import SourceValue
from footprint_model.constants.units import u
from footprint_model.constants.countries import Country

from footprint_model.logger import logger


class Server(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: SourceValue,
                 power_usage_effectiveness: SourceValue, country: Country, server_utilization_rate: SourceValue):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, country)
        self.available_cpu_per_instance = None
        self.available_ram_per_instance = None
        self.server_utilization_rate = None
        self.nb_of_instances = None
        self.idle_power = idle_power
        self.idle_power.set_name(f"Idle power of {self.name}")
        self.ram = ram
        self.ram.set_name(f"RAM of {self.name}")
        self.nb_of_cpus = nb_of_cpus
        self.nb_of_cpus.set_name(f"Nb cpus of {self.name}")
        self.power_usage_effectiveness = power_usage_effectiveness
        self.power_usage_effectiveness.set_name(f"PUE of {self.name}")
        self.server_utilization_rate = server_utilization_rate
        self.server_utilization_rate.set_name(f"{self.name} utilization rate")

    def compute_calculated_attributes(self):
        logger.info(f"Computing calculated attributes for server {self.name}")
        self.update_available_ram_per_instance()
        self.update_available_cpu_per_instance()
        self.update_functions_defined_in_infra_hardware_class()

    @property
    def services(self):
        return {service for usage_pattern in self.usage_patterns for service in usage_pattern.services
                if service.server == self}

    def update_available_ram_per_instance(self):
        services_base_ram_consumptions = [service.base_ram_consumption for service in self.services]
        available_ram_per_instance = self.ram * self.server_utilization_rate
        for service_base_resource_consumption in services_base_ram_consumptions:
            available_ram_per_instance -= service_base_resource_consumption
            if available_ram_per_instance.value < 0 * u.B:
                services_resource_need = sum(services_base_ram_consumptions)
                raise ValueError(
                    f"server has available capacity of "
                    f"{(self.ram * self.server_utilization_rate).value} "
                    f" but is asked {services_resource_need.value}")

        self.available_ram_per_instance = available_ram_per_instance.define_as_intermediate_calculation(
            f"Available RAM per {self.name} instance")

    def update_available_cpu_per_instance(self):
        services_base_cpu_consumptions = [service.base_cpu_consumption for service in self.services]
        available_cpu_per_instance = self.nb_of_cpus * self.server_utilization_rate
        for service_base_resource_consumption in services_base_cpu_consumptions:
            available_cpu_per_instance -= service_base_resource_consumption
            if available_cpu_per_instance.value < 0:
                services_resource_need = sum(services_base_cpu_consumptions)
                raise ValueError(
                    f"server has available capacity of "
                    f"{(self.nb_of_cpus * self.server_utilization_rate).value} "
                    f" but is asked {services_resource_need.value}")

        self.available_cpu_per_instance = available_cpu_per_instance.define_as_intermediate_calculation(
            f"Available CPU per {self.name} instance")

    @abstractmethod
    def update_nb_of_instances(self):
        pass

    @abstractmethod
    def update_instances_power(self):
        pass
