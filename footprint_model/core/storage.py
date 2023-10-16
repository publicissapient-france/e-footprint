from footprint_model.constants.countries import Country, Countries
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation
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

    @property
    def services(self):
        return {service for usage_pattern in self.usage_patterns for service in usage_pattern.services
                if service.storage == self}

    @property
    @intermediate_calculation("Long term storage required")
    def long_term_storage_required(self) -> ExplainableQuantity:
        long_term_storage_required = (
                self.all_services_infra_needs.storage * self.data_replication_factor * self.data_storage_duration
                - self.active_storage_required
                )
        return long_term_storage_required

    @property
    @intermediate_calculation("Active storage required")
    def active_storage_required(self) -> ExplainableQuantity:
        active_storage_required = (
                self.all_services_infra_needs.storage
                * SourceValue(1 * u.hour, Sources.HYPOTHESIS, "Time interval during which active storage is considered")
        )
        return active_storage_required.to(u.Go)

    @property
    @intermediate_calculation("Number of idle storage units")
    def nb_of_idle_instances(self) -> ExplainableQuantity:
        return (self.long_term_storage_required / self.storage_capacity).to(u.dimensionless)

    @property
    @intermediate_calculation("Number of idle storage units")
    def nb_of_active_instances(self) -> ExplainableQuantity:
        return (self.active_storage_required / self.storage_capacity).to(u.dimensionless)

    @property
    def nb_of_instances(self):
        return self.nb_of_active_instances + self.nb_of_idle_instances

    @property
    @intermediate_calculation("Storage power")
    def instances_power(self) -> ExplainableQuantity:
        active_storage_power = self.nb_of_active_instances * self.power * self.power_usage_effectiveness
        idle_storage_power = self.nb_of_idle_instances * self.idle_power * self.power_usage_effectiveness
        storage_power = (
                active_storage_power * self.fraction_of_time_in_use + idle_storage_power).to(u.kWh / u.year)

        return storage_power


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
