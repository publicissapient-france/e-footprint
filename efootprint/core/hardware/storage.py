from efootprint.constants.countries import Countries
from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u


class Storage(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, storage_capacity: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 data_replication_factor: SourceValue, storage_need_from_previous_year: SourceValue = None):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
        self.all_services_storage_needs = None
        self.long_term_storage_required = None
        self.active_storage_required = None
        self.nb_of_idle_instances = None
        self.nb_of_active_instances = None
        self.instances_power = None
        self.idle_power = idle_power
        self.idle_power.set_name(f"Idle power of {self.name}")
        self.storage_capacity = storage_capacity
        self.storage_capacity.set_name(f"Storage capacity of {self.name}")
        self.power_usage_effectiveness = power_usage_effectiveness
        self.power_usage_effectiveness.set_name(f"PUE of {self.name}")
        self.data_replication_factor = data_replication_factor
        self.data_replication_factor.set_name(f"Data replication factor of {self.name}")
        # TODO: implement data storage duration logic
        if storage_need_from_previous_year is not None:
            if not storage_need_from_previous_year.value.check("[]"):
                raise ValueError(
                    "Value of variable 'storage_need_from_previous_year' does not have the appropriate"
                    " '[]' dimensionality")
            storage_need_from_previous_year.left_child = None
            storage_need_from_previous_year.right_child = None
            storage_need_from_previous_year.label = f"{self.name} storage need from previous year"
            self.storage_need_from_previous_year = storage_need_from_previous_year
        else:
            self.storage_need_from_previous_year = 0

        self.calculated_attributes = [
            "all_services_storage_needs", "active_storage_required", "long_term_storage_required",
            "nb_of_idle_instances", "nb_of_active_instances"
        ] + self.calculated_attributes_defined_in_infra_hardware_class

    def update_all_services_storage_needs(self):
        if len(self.services) > 0:
            all_services_storage_needs = sum(service.storage_needed for service in self.services).to(u.TB / u.year)

            self.all_services_storage_needs = all_services_storage_needs.define_as_intermediate_calculation(
                f"Storage need of {self.name}")
        else:
            self.all_services_storage_needs = ExplainableQuantity(
                0 * u.TB / u.year, f"No storage need for {self.name} because no associated services")

    def update_long_term_storage_required(self):
        # TODO: Higher level year by year analysis that adds storage from previous year with remaining storage duration
        # to current storage
        long_term_storage_required = (
                self.all_services_storage_needs * self.data_replication_factor
                * ExplainableQuantity(1 * u.year, "one year") + self.storage_need_from_previous_year
                - self.active_storage_required
        )

        self.long_term_storage_required = long_term_storage_required.define_as_intermediate_calculation(
            f"Long term storage required for {self.name}")

    def update_active_storage_required(self):
        active_storage_required = (
                self.all_services_storage_needs
                * SourceValue(1 * u.hour, Sources.HYPOTHESIS, "Time interval during which active storage is considered")
        ).to(u.GB)

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
        active_storage_power = (
                self.nb_of_active_instances * self.power * self.power_usage_effectiveness
        ).define_as_intermediate_calculation(f"Active instances power")
        idle_storage_power = (
                self.nb_of_idle_instances * self.idle_power * self.power_usage_effectiveness
        ).define_as_intermediate_calculation(f"Idle instances power")
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
        storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
        data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS),
    )
    HDD_STORAGE = Storage(
        "Default HDD storage",
        carbon_footprint_fabrication=SourceValue(20 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(4.2 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(4 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
        data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS),
    )
