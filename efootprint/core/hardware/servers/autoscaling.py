from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.hardware.servers.server_base_class import Server

import math


class Autoscaling(Server):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, cpu_cores: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 server_utilization_rate: SourceValue):
        super().__init__(
            name, carbon_footprint_fabrication, power, lifespan, idle_power, ram, cpu_cores, power_usage_effectiveness,
            average_carbon_intensity, server_utilization_rate)

    def update_nb_of_instances(self):
        nb_of_servers_based_on_ram_alone = (
                self.all_services_ram_needs / self.available_ram_per_instance).set_label(
            f"Raw nb of {self.name} instances based on RAM alone")
        nb_of_servers_based_on_cpu_alone = (
                self.all_services_cpu_needs / self.available_cpu_per_instance).set_label(
            f"Raw nb of {self.name} instances based on CPU alone")

        nb_of_servers_raw = ExplainableHourlyUsage(
            [max(ram_nb_of_servers, cpu_nb_of_servers) for ram_nb_of_servers, cpu_nb_of_servers
             in zip(nb_of_servers_based_on_ram_alone.value, nb_of_servers_based_on_cpu_alone.value)],
            f"Raw nb of instances",
            left_child=nb_of_servers_based_on_ram_alone,
            right_child=nb_of_servers_based_on_cpu_alone,
            child_operator="max compared with"
        )

        hour_by_hour_nb_of_instances__list = []
        for hour in range(24):
            nb_of_servers_raw_that_hour = nb_of_servers_raw.value[hour]
            if math.ceil(nb_of_servers_raw_that_hour.magnitude) - nb_of_servers_raw_that_hour.magnitude != 0:
                nb_of_instances_per_hour = nb_of_servers_raw_that_hour + (
                        math.ceil(nb_of_servers_raw_that_hour.magnitude) - nb_of_servers_raw_that_hour.magnitude
                ) * u.dimensionless
            else:
                nb_of_instances_per_hour = nb_of_servers_raw_that_hour

            hour_by_hour_nb_of_instances__list.append(nb_of_instances_per_hour)

        hour_by_hour_nb_of_instances = ExplainableHourlyUsage(
            hour_by_hour_nb_of_instances__list, f"Hour by hour nb of instances", left_child=nb_of_servers_raw,
            child_operator="Rounding up of instances nb"
        )

        nb_of_instances = hour_by_hour_nb_of_instances.mean()

        self.nb_of_instances = nb_of_instances.set_label(f"Nb of {self.name} instances")

    def update_instances_power(self):
        effective_active_power = self.power * self.power_usage_effectiveness
        server_power = (effective_active_power * self.nb_of_instances).to(u.kWh / u.year)

        self.instances_power = server_power.set_label(f"Power of {self.name} instances")
