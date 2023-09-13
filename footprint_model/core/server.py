from footprint_model.constants.physical_elements import InfraHardware, PhysicalElements
from footprint_model.constants.explainable_quantities import (ExplainableQuantity, NonQuantityUsedInCalculation,
                                                              ExplainableHourlyUsage)
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.constants.countries import Country, Countries

import math


class CloudConfig(NonQuantityUsedInCalculation):
    def __init__(self, cloud_config: str):
        super().__init__(cloud_config)

    def __eq__(self, other):
        return self.value == other


class Server(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, ram: SourceValue, nb_of_cpus: int,
                 power_usage_effectiveness: float, country: Country, cloud: str):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, country)
        self.available_cpu_per_instance = None
        self.available_ram_per_instance = None
        self.server_utilization_rate = None
        self.nb_of_instances = None
        self.idle_power = idle_power
        self.idle_power.set_name(f"idle power of {self.name}")
        self.ram = ram
        self.ram.set_name(f"ram of {self.name}")
        self.nb_of_cpus = ExplainableQuantity(nb_of_cpus * u.core, f"nb cpus of {self.name}")
        self.power_usage_effectiveness = ExplainableQuantity(
            power_usage_effectiveness * u.dimensionless, f"PUE of {self.name}")
        self.cloud = CloudConfig(cloud)
        self.usage_patterns = set()

        self.compute_calculated_attributes()

    def compute_calculated_attributes(self):
        if len(self.usage_patterns) > 0:
            self.update_server_utilization_rate()
            self.update_available_ram_per_instance()
            self.update_available_cpu_per_instance()
            self.update_functions_defined_in_infra_hardware_class()

    def update_server_utilization_rate(self):
        if self.cloud == "Serverless" or self.cloud == "Autoscaling":
            self.server_utilization_rate = ExplainableQuantity(
                0.9 * u.dimensionless, "Cloud server utilization rate").define_as_intermediate_calculation(
                "Cloud server utilization rate")
        elif self.cloud == "On premise":
            self.server_utilization_rate = ExplainableQuantity(
                0.7 * u.dimensionless, "On premise server utilization rate").define_as_intermediate_calculation(
                "On premise server utilization rate"
            )

    @property
    def services(self):
        return {service for usage_pattern in self.usage_patterns for service in usage_pattern.services
                if service.server == self}

    def update_available_ram_per_instance(self):
        services_base_ram_consumptions = [service.base_ram_consumption for service in self.services]
        available_ram_per_instance = self.ram * self.server_utilization_rate
        for service_base_resource_consumption in services_base_ram_consumptions:
            available_ram_per_instance -= service_base_resource_consumption
            if available_ram_per_instance.value < 0:
                services_resource_need = sum(services_base_ram_consumptions)
                raise ValueError(
                    f"server has available capacity of "
                    f"{(self.ram * self.server_utilization_rate).value} "
                    f" but is asked {services_resource_need.value}")

        self.available_ram_per_instance = available_ram_per_instance.define_as_intermediate_calculation(
            f"Available ram per instance of {self.name}")

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
            f"Available cpu per instance of {self.name}")

    def update_nb_of_instances(self):
        all_services_ram_needs = self.all_services_ram_needs
        all_services_cpu_needs = self.all_services_cpu_needs
        available_ram_per_instance = self.available_ram_per_instance
        available_cpu_per_instance = self.available_cpu_per_instance

        if self.cloud == "Serverless":
            one_day = ExplainableQuantity(24 * u.hour, '24 hours')
            ram_needed_per_day = (
                    all_services_ram_needs.sum() * ExplainableQuantity(1 * u.hour, "1 hour") / one_day)
            cpu_needed_per_day = (
                    all_services_cpu_needs.sum() * ExplainableQuantity(1 * u.hour, "1 hour") / one_day)

            nb_of_servers_raw = max(ram_needed_per_day / available_ram_per_instance,
                                    cpu_needed_per_day / available_cpu_per_instance)

            nb_of_instances = nb_of_servers_raw

        elif self.cloud == "Autoscaling":
            nb_of_servers_based_on_ram_alone = all_services_ram_needs / available_ram_per_instance
            nb_of_servers_based_on_cpu_alone = all_services_cpu_needs / available_cpu_per_instance

            nb_of_servers_raw = ExplainableHourlyUsage(
                [max(ram_nb_of_servers, cpu_nb_of_servers) for ram_nb_of_servers, cpu_nb_of_servers
                 in zip(nb_of_servers_based_on_ram_alone.value, nb_of_servers_based_on_cpu_alone.value)],
                "",
                left_child=nb_of_servers_based_on_ram_alone,
                right_child=nb_of_servers_based_on_cpu_alone,
                child_operator="Max nb of servers hour by hour based on cpu or ram"
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
                hour_by_hour_nb_of_instances__list, "", left_child=nb_of_servers_raw,
                child_operator="Rounding of server number of instances"
            )

            nb_of_instances = (hour_by_hour_nb_of_instances.sum()
                               / ExplainableQuantity(24 * u.dimensionless, "24 hours per day"))

        elif self.cloud == "On premise":
            ram_needed_per_day = all_services_ram_needs.max()
            cpu_needed_per_day = all_services_cpu_needs.max()

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

        self.nb_of_instances = nb_of_instances.define_as_intermediate_calculation(f"Number of instances of {self.name}")

    def update_instances_power(self):
        effective_active_power = self.power * self.power_usage_effectiveness
        effective_idle_power = self.idle_power * self.power_usage_effectiveness
        if self.cloud == "Serverless" or self.cloud == "Autoscaling":
            server_power = (effective_active_power * self.nb_of_instances).to(u.kWh / u.year)
        else:
            fraction_of_time_not_in_use = ExplainableQuantity(1 * u.dimensionless) - self.fraction_of_time_in_use
            server_power = (
                    self.nb_of_instances *
                    ((effective_active_power * self.fraction_of_time_in_use)
                     + (effective_idle_power * fraction_of_time_not_in_use))
            ).to(u.kWh / u.year)

        self.instances_power = server_power.define_as_intermediate_calculation(f"Power of {self.name}")


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
        cloud="Serverless"
    )
