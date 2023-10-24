from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.constants.countries import Country, Countries
from efootprint.constants.physical_elements import PhysicalElements
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u
from efootprint.core.hardware.servers.server_base_class import Server

import math


class OnPremise(Server):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 server_utilization_rate: SourceValue):
        super().__init__(
            name, carbon_footprint_fabrication, power, lifespan, idle_power, ram, nb_of_cpus, power_usage_effectiveness,
            average_carbon_intensity, server_utilization_rate)

    def update_nb_of_instances(self):
        ram_needed_per_day = self.all_services_ram_needs.max().define_as_intermediate_calculation(
            f"Max daily {self.name} RAM need")
        cpu_needed_per_day = self.all_services_cpu_needs.max().define_as_intermediate_calculation(
            f"Max daily {self.name} CPU need")

        nb_of_servers_based_on_ram_alone = (
                ram_needed_per_day / self.available_ram_per_instance).define_as_intermediate_calculation(
            f"Raw nb of {self.name} instances based on RAM alone")
        nb_of_servers_based_on_cpu_alone = (
                cpu_needed_per_day / self.available_cpu_per_instance).define_as_intermediate_calculation(
            f"Raw nb of {self.name} instances based on CPU alone")

        nb_of_servers_raw = nb_of_servers_based_on_ram_alone.compare_with_and_return_max(
            nb_of_servers_based_on_cpu_alone)

        if math.ceil(nb_of_servers_raw.magnitude) - nb_of_servers_raw.magnitude != 0:
            nb_of_instances = nb_of_servers_raw + ExplainableQuantity(
                (math.ceil(nb_of_servers_raw.magnitude) - nb_of_servers_raw.magnitude)
                * u.dimensionless, "Extra server capacity because number of servers must be an integer")
        else:
            nb_of_instances = nb_of_servers_raw

        self.nb_of_instances = nb_of_instances.define_as_intermediate_calculation(f"Nb of {self.name} instances")

    def update_instances_power(self):
        effective_active_power = self.power * self.power_usage_effectiveness
        effective_idle_power = self.idle_power * self.power_usage_effectiveness

        fraction_of_time_not_in_use = ExplainableQuantity(1 * u.dimensionless, "100%") - self.fraction_of_time_in_use
        server_power = (
                self.nb_of_instances *
                ((effective_active_power * self.fraction_of_time_in_use)
                 + (effective_idle_power * fraction_of_time_not_in_use))
        ).to(u.kWh / u.year)

        self.instances_power = server_power.define_as_intermediate_calculation(f"Power of {self.name} instances")


ON_PREMISE = OnPremise(
    PhysicalElements.ON_PREMISE,
    carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
    power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
    lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
    idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
    ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
    nb_of_cpus=SourceValue(24 * u.core, Sources.HYPOTHESIS),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
    server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
)
