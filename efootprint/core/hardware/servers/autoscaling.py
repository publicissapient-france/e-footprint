import math

import pandas as pd
import pint_pandas

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyQuantities, ExplainableQuantity
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.hardware.servers.server_base_class import Server


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

        nb_of_servers_raw_df = pd.DataFrame(
            {"value": pd.merge(nb_of_servers_based_on_cpu_alone.value, nb_of_servers_based_on_ram_alone.value,
                               left_index=True, right_index=True).max(axis=1)})
        nb_of_servers_raw = ExplainableHourlyQuantities(
            nb_of_servers_raw_df,
            f"Raw nb of instances",
            left_parent=nb_of_servers_based_on_ram_alone,
            right_parent=nb_of_servers_based_on_cpu_alone,
            operator="max compared with"
        )

        hour_by_hour_nb_of_instances_df = nb_of_servers_raw_df.copy()
        hour_by_hour_nb_of_instances_df["value"] = pint_pandas.PintArray(hour_by_hour_nb_of_instances_df["value"].apply(
            lambda x: math.ceil(x)).values, dtype=u.dimensionless)
        hour_by_hour_nb_of_instances = ExplainableHourlyQuantities(
            hour_by_hour_nb_of_instances_df, f"Hour by hour nb of instances", left_parent=nb_of_servers_raw,
            operator="Rounding up of instances nb"
        )

        self.nb_of_instances = hour_by_hour_nb_of_instances.set_label(f"Hour by hour of {self.name} instances")

    def update_instances_energy(self):
        energy_spent_by_one_instance_over_one_hour = self.power * self.power_usage_effectiveness * ExplainableQuantity(
            1 * u.hour, "one hour")
        server_power = (energy_spent_by_one_instance_over_one_hour * self.nb_of_instances).to(u.kWh)

        self.instances_energy = server_power.set_label(f"Hour by hour energy consumed by {self.name} instances")
