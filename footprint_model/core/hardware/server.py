from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.core.hardware.hardware_base_classes import InfraHardware
from footprint_model.abstract_modeling_classes.non_quantity_used_in_calculation import NonQuantityUsedInCalculation
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.constants.countries import Country, Countries

import math
import logging


class CloudConfig(NonQuantityUsedInCalculation):
    def __init__(self, cloud_config: str):
        super().__init__(cloud_config)

    def __eq__(self, other):
        return self.value == other


class Server(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: SourceValue,
                 power_usage_effectiveness: SourceValue, country: Country, cloud: str):
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
        self.cloud = CloudConfig(cloud)
        self.usage_patterns = set()

    def compute_calculated_attributes(self):
        logging.info(f"Computing calculated attributes for {self.name}")
        self.update_server_utilization_rate()
        self.update_available_ram_per_instance()
        self.update_available_cpu_per_instance()
        self.update_functions_defined_in_infra_hardware_class()

    def update_server_utilization_rate(self):
        if self.cloud == "Serverless" or self.cloud == "Autoscaling":
            self.server_utilization_rate = SourceValue(
                0.9 * u.dimensionless, Sources.HYPOTHESIS, "Cloud server utilization rate")
        elif self.cloud == "On premise":
            self.server_utilization_rate = SourceValue(
                0.7 * u.dimensionless, Sources.HYPOTHESIS, "On premise server utilization rate")

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

    def update_nb_of_instances(self):
        all_services_ram_needs = self.all_services_ram_needs
        all_services_cpu_needs = self.all_services_cpu_needs
        available_ram_per_instance = self.available_ram_per_instance
        available_cpu_per_instance = self.available_cpu_per_instance

        if self.cloud == "Serverless":
            average_ram_needed_per_day = all_services_ram_needs.mean().define_as_intermediate_calculation(
                f"Average RAM need of {self.name}")
            average_cpu_needed_per_day = all_services_cpu_needs.mean().define_as_intermediate_calculation(
                f"Average CPU need of {self.name}")

            nb_of_servers_raw = max(average_ram_needed_per_day / available_ram_per_instance,
                                    average_cpu_needed_per_day / available_cpu_per_instance)

            nb_of_instances = nb_of_servers_raw

        elif self.cloud == "Autoscaling":
            nb_of_servers_based_on_ram_alone = (
                    all_services_ram_needs / available_ram_per_instance).define_as_intermediate_calculation(
                f"Raw nb of {self.name} instances based on RAM alone")
            nb_of_servers_based_on_cpu_alone = (
                    all_services_cpu_needs / available_cpu_per_instance).define_as_intermediate_calculation(
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
                    nb_of_instances_per_hour = nb_of_servers_raw_that_hour + ExplainableQuantity(
                        (math.ceil(nb_of_servers_raw_that_hour.magnitude) - nb_of_servers_raw_that_hour.magnitude)
                        * u.dimensionless, "Extra server capacity because number of servers must be an integer")
                else:
                    nb_of_instances_per_hour = nb_of_servers_raw_that_hour

                hour_by_hour_nb_of_instances__list.append(nb_of_instances_per_hour)

            hour_by_hour_nb_of_instances = ExplainableHourlyUsage(
                hour_by_hour_nb_of_instances__list, f"Hour by hour nb of instances", left_child=nb_of_servers_raw,
                child_operator="Rounding up of instances nb"
            )

            nb_of_instances = hour_by_hour_nb_of_instances.mean()

        elif self.cloud == "On premise":
            ram_needed_per_day = all_services_ram_needs.max().define_as_intermediate_calculation(
                f"Max daily {self.name } RAM need")
            cpu_needed_per_day = all_services_cpu_needs.max().define_as_intermediate_calculation(
                f"Max daily {self.name } CPU need")

            nb_of_servers_raw = max(ram_needed_per_day / available_ram_per_instance,
                                    cpu_needed_per_day / available_cpu_per_instance).to(u.dimensionless)
            if math.ceil(nb_of_servers_raw.magnitude) - nb_of_servers_raw.magnitude != 0:
                nb_of_instances = nb_of_servers_raw + ExplainableQuantity(
                    (math.ceil(nb_of_servers_raw.magnitude) - nb_of_servers_raw.magnitude)
                    * u.dimensionless, "Extra server capacity because number of servers must be an integer")
            else:
                nb_of_instances = nb_of_servers_raw

        else:
            raise ValueError(f"CloudConfig should be Autoscaling, Serverless or On premise, not {self.cloud.value}")

        self.nb_of_instances = nb_of_instances.define_as_intermediate_calculation(f"Nb of {self.name} instances")

    def update_instances_power(self):
        effective_active_power = self.power * self.power_usage_effectiveness
        effective_idle_power = self.idle_power * self.power_usage_effectiveness
        if self.cloud == "Serverless" or self.cloud == "Autoscaling":
            server_power = (effective_active_power * self.nb_of_instances).to(u.kWh / u.year)
        elif self.cloud == "On premise":
            fraction_of_time_not_in_use = ExplainableQuantity(1 * u.dimensionless, "100%") - self.fraction_of_time_in_use
            server_power = (
                    self.nb_of_instances *
                    ((effective_active_power * self.fraction_of_time_in_use)
                     + (effective_idle_power * fraction_of_time_not_in_use))
            ).to(u.kWh / u.year)
        else:
            raise ValueError(f"CloudConfig should be Autoscaling, Serverless or On premise, not {self.cloud.value}")

        self.instances_power = server_power.define_as_intermediate_calculation(f"Power of {self.name} instances")


class Servers:
    SERVER = Server(
        PhysicalElements.SERVER,
        carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
        nb_of_cpus=SourceValue(24 * u.core, Sources.HYPOTHESIS),
        power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        country=Countries.GERMANY,
        cloud="Serverless"
    )
