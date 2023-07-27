from footprint_model.constants.countries import Country, Countries
from footprint_model.constants.physical_elements import InfraHardware
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u

from pint import Quantity


class Storage(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, storage_capacity: SourceValue,
                 power_usage_effectiveness: float, country: Country, data_replication_factor: int,
                 data_storage_duration: Quantity):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, country)
        self.all_services_storage_needs = None
        self.long_term_storage_required = None
        self.active_storage_required = None
        self.nb_of_idle_instances = None
        self.nb_of_active_instances = None
        self.instances_power = None
        self.idle_power = idle_power
        self.idle_power.set_name(f"idle power of {self.name}")
        self.storage_capacity = storage_capacity
        self.storage_capacity.set_name(f"storage capacity of {self.name}")
        self.power_usage_effectiveness = SourceValue(
            power_usage_effectiveness * u.dimensionless, Sources.USER_INPUT, f"PUE of {self.name}")
        self.data_replication_factor = SourceValue(
            data_replication_factor * u.dimensionless, Sources.USER_INPUT, f"Data replication factor of {self.name}")
        if not data_storage_duration.check("[time]"):
            raise ValueError("Variable 'data_storage_duration' does not have time dimensionality")
        self.data_storage_duration = SourceValue(
            data_storage_duration, Sources.USER_INPUT, f"Data storage duration of {self.name}")

    def compute_calculated_attributes(self):
        self.update_all_services_storage_needs()
        self.update_active_storage_required()
        self.update_long_term_storage_required()
        self.update_nb_of_idle_instances()
        self.update_nb_of_active_instances()
        self.update_functions_defined_in_infra_hardware_class()

    @property
    def services(self):
        return {service for usage_pattern in self.usage_patterns for service in usage_pattern.services
                if service.storage == self}

    def update_all_services_storage_needs(self):
        all_services_storage_needs = sum(service.storage_needed for service in self.services).to(u.To / u.year)

        self.all_services_storage_needs = all_services_storage_needs.define_as_intermediate_calculation(
            f"Storage need of {self.name}")

    def update_long_term_storage_required(self):
        long_term_storage_required = (
                self.all_services_storage_needs * self.data_replication_factor * self.data_storage_duration
                - self.active_storage_required
        )

        self.long_term_storage_required = long_term_storage_required.define_as_intermediate_calculation(
            f"Long term storage required for {self.name}")

    def update_active_storage_required(self):
        active_storage_required = (
                self.all_services_storage_needs
                * SourceValue(1 * u.hour, Sources.HYPOTHESIS, "Time interval during which active storage is considered")
        ).to(u.Go)

        self.active_storage_required = active_storage_required.define_as_intermediate_calculation(
            f"Active storage required for {self.name}")

    def update_nb_of_idle_instances(self):
        nb_of_idle_instances = (self.long_term_storage_required / self.storage_capacity).to(u.dimensionless)
        self.nb_of_idle_instances = nb_of_idle_instances.define_as_intermediate_calculation(
            f"Number of idle storage units for {self.name}")

    def update_nb_of_active_instances(self):
        active_instances = (self.active_storage_required / self.storage_capacity).to(u.dimensionless)

        self.nb_of_active_instances = active_instances.define_as_intermediate_calculation(
            f"Number of active instances for {self.name}")

    def update_nb_of_instances(self):
        nb_of_instances = self.nb_of_active_instances + self.nb_of_idle_instances

        self.nb_of_instances = nb_of_instances.define_as_intermediate_calculation(
            f"Number of total instances for {self.name}")

    def update_instances_power(self):
        active_storage_power = self.nb_of_active_instances * self.power * self.power_usage_effectiveness
        idle_storage_power = self.nb_of_idle_instances * self.idle_power * self.power_usage_effectiveness
        storage_power = (
                active_storage_power * self.fraction_of_time_in_use + idle_storage_power).to(u.kWh / u.year)

        self.instances_power = storage_power.define_as_intermediate_calculation(
            f"Storage power for {self.name}")


class Storages:
    SSD_STORAGE = Storage(
        "Default SSD storage",
        carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=1.2,
        country=Countries.GERMANY,
        data_replication_factor=3,
        data_storage_duration=5 * u.year
    )
    HDD_STORAGE = Storage(
        "Default HDD storage",
        carbon_footprint_fabrication=SourceValue(20 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(4.2 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(4 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.To, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=1.2,
        country=Countries.GERMANY,
        data_replication_factor=3,
        data_storage_duration=5 * u.year
    )
