from efootprint.constants.countries import Country, Countries
from efootprint.constants.physical_elements import PhysicalElements
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u
from efootprint.core.hardware.servers.server_base_class import Server


class Serverless(Server):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 server_utilization_rate: SourceValue):
        super().__init__(
            name, carbon_footprint_fabrication, power, lifespan, idle_power, ram, nb_of_cpus, power_usage_effectiveness,
            average_carbon_intensity, server_utilization_rate)

    def update_nb_of_instances(self):
        average_ram_needed_per_day = self.all_services_ram_needs.mean().define_as_intermediate_calculation(
            f"Average RAM need of {self.name}")
        average_cpu_needed_per_day = self.all_services_cpu_needs.mean().define_as_intermediate_calculation(
            f"Average CPU need of {self.name}")

        nb_of_servers_based_on_ram = (
                average_ram_needed_per_day / self.available_ram_per_instance).define_as_intermediate_calculation(
            f"Raw nb of {self.name} instances based on RAM alone")
        nb_of_servers_based_on_cpu = (
                average_cpu_needed_per_day / self.available_cpu_per_instance).define_as_intermediate_calculation(
            f"Raw nb of {self.name} instances based on CPU alone")

        nb_of_servers_raw = nb_of_servers_based_on_ram.compare_with_and_return_max(nb_of_servers_based_on_cpu)

        self.nb_of_instances = nb_of_servers_raw.define_as_intermediate_calculation(f"Nb of {self.name} instances")

    def update_instances_power(self):
        effective_active_power = self.power * self.power_usage_effectiveness
        server_power = (effective_active_power * self.nb_of_instances).to(u.kWh / u.year)

        self.instances_power = server_power.define_as_intermediate_calculation(f"Power of {self.name} instances")


SERVERLESS = Serverless(
    PhysicalElements.SERVERLESS,
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