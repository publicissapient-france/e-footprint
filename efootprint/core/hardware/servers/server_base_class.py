from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u

from abc import abstractmethod


class Server(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, cpu_cores: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 server_utilization_rate: SourceValue):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
        self.available_cpu_per_instance = None
        self.available_ram_per_instance = None
        self.server_utilization_rate = None
        self.nb_of_instances = None
        self.idle_power = idle_power.set_label(f"Idle power of {self.name}")
        self.ram = ram.set_label(f"RAM of {self.name}")
        self.cpu_cores = cpu_cores.set_label(f"Nb cpus cores of {self.name}")
        self.power_usage_effectiveness = power_usage_effectiveness.set_label(f"PUE of {self.name}")
        self.server_utilization_rate = server_utilization_rate.set_label(f"{self.name} utilization rate")

    @property
    def calculated_attributes(self):
        return ["available_ram_per_instance", "available_cpu_per_instance"
                                      ] + self.calculated_attributes_defined_in_infra_hardware_class

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

        self.available_ram_per_instance = available_ram_per_instance.set_label(
            f"Available RAM per {self.name} instance")

    def update_available_cpu_per_instance(self):
        services_base_cpu_consumptions = [service.base_cpu_consumption for service in self.services]
        available_cpu_per_instance = self.cpu_cores * self.server_utilization_rate
        for service_base_resource_consumption in services_base_cpu_consumptions:
            available_cpu_per_instance -= service_base_resource_consumption
            if available_cpu_per_instance.value < 0:
                services_resource_need = sum(services_base_cpu_consumptions)
                raise ValueError(
                    f"server has available capacity of "
                    f"{(self.cpu_cores * self.server_utilization_rate).value} "
                    f" but is asked {services_resource_need.value}")

        self.available_cpu_per_instance = available_cpu_per_instance.set_label(
            f"Available CPU per {self.name} instance")

    @abstractmethod
    def update_nb_of_instances(self):
        pass

    @abstractmethod
    def update_instances_power(self):
        pass
