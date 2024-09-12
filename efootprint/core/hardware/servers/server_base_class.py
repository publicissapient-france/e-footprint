from abc import abstractmethod

import numpy as np
import pandas as pd
import pint_pandas

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyQuantities, ExplainableQuantity, \
    EmptyExplainableObject
from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u


class Server(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, cpu_cores: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 server_utilization_rate: SourceValue):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
        self.available_cpu_per_instance = None
        self.available_ram_per_instance = None
        self.server_utilization_rate = None
        self.raw_nb_of_instances = None
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

    def update_raw_nb_of_instances(self):
        if isinstance(self.all_services_ram_needs, EmptyExplainableObject) \
                and isinstance(self.all_services_cpu_needs, EmptyExplainableObject):
            self.raw_nb_of_instances = EmptyExplainableObject()
        else:
            nb_of_servers_based_on_ram_alone = (
                    self.all_services_ram_needs / self.available_ram_per_instance).to(u.dimensionless).set_label(
                f"Raw nb of {self.name} instances based on RAM alone")
            nb_of_servers_based_on_cpu_alone = (
                    self.all_services_cpu_needs / self.available_cpu_per_instance).to(u.dimensionless).set_label(
                f"Raw nb of {self.name} instances based on CPU alone")

            nb_of_servers_raw_np = np.maximum(
                nb_of_servers_based_on_ram_alone.value["value"].values.data,
                nb_of_servers_based_on_cpu_alone.value["value"].values.data
            )
            nb_of_servers_raw_df = pd.DataFrame(
                {"value": pint_pandas.PintArray(nb_of_servers_raw_np, dtype=u.dimensionless)},
                index=nb_of_servers_based_on_ram_alone.value.index)

            nb_of_servers_raw = ExplainableHourlyQuantities(
                nb_of_servers_raw_df,
                f"Raw nb of instances",
                left_parent=nb_of_servers_based_on_ram_alone,
                right_parent=nb_of_servers_based_on_cpu_alone,
                operator="max compared with"
            )
            hour_by_hour_raw_nb_of_instances = nb_of_servers_raw.set_label(
                f"Hourly raw number of {self.name} instances")

            self.raw_nb_of_instances = hour_by_hour_raw_nb_of_instances

    def update_instances_energy(self):
        energy_spent_by_one_idle_instance_over_one_hour = (
                self.idle_power * self.power_usage_effectiveness * ExplainableQuantity(1 * u.hour, "one hour"))
        extra_energy_spent_by_one_fully_active_instance_over_one_hour = (
                (self.power - self.idle_power) * self.power_usage_effectiveness
                * ExplainableQuantity(1 * u.hour, "one hour"))

        server_power = (
                energy_spent_by_one_idle_instance_over_one_hour * self.nb_of_instances
                + extra_energy_spent_by_one_fully_active_instance_over_one_hour * self.raw_nb_of_instances)

        self.instances_energy = server_power.to(u.kWh).set_label(
            f"Hourly energy consumed by {self.name} instances")

    @abstractmethod
    def update_nb_of_instances(self):
        pass
