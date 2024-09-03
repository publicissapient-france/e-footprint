import math

from efootprint.core.hardware.hardware_base_classes import InfraHardware
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u


class Storage(InfraHardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, idle_power: SourceValue, storage_capacity: SourceValue,
                 power_usage_effectiveness: SourceValue, average_carbon_intensity: SourceValue,
                 data_replication_factor: SourceValue, data_storage_duration: SourceValue,
                 initial_storage_need: SourceValue):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan, average_carbon_intensity)
        self.all_services_storage_needs = None
        self.storage_dumps = None
        self.storage_delta = None
        self.full_cumulative_storage_need = None
        self.long_term_storage_required = None
        self.nb_of_active_instances = None
        self.instances_power = None
        if not idle_power.value.check("[power]"):
            raise ValueError("Value of variable 'idle_power' does not have appropriate power dimensionality")
        self.idle_power = idle_power.set_label(f"Idle power of {self.name}")
        if not storage_capacity.value.check("[]"):
            raise ValueError("Value of variable 'storage_capacity' does not have appropriate [] dimensionality")
        self.storage_capacity = storage_capacity.set_label(f"Storage capacity of {self.name}")
        if not power_usage_effectiveness.value.check("[]"):
            raise ValueError(
                "Value of variable 'power_usage_effectiveness' does not have appropriate [] dimensionality")
        self.power_usage_effectiveness = power_usage_effectiveness.set_label(f"PUE of {self.name}")
        if not data_replication_factor.value.check("[]"):
            raise ValueError("Value of variable 'data_replication_factor' does not have appropriate [] dimensionality")
        self.data_replication_factor = data_replication_factor.set_label(f"Data replication factor of {self.name}")
        if not data_storage_duration.value.check("[time]"):
            raise ValueError("Value of variable 'data_storage_duration' does not have appropriate time dimensionality")
        self.data_storage_duration = data_storage_duration.set_label(f"Data storage duration of {self.name}")
        if not initial_storage_need.value.check("[]"):
            raise ValueError(
                "Value of variable 'storage_need_from_previous_year' does not have the appropriate"
                " '[]' dimensionality")
        self.initial_storage_need = initial_storage_need.set_label(f"{self.name} storage need from previous year")

    @property
    def calculated_attributes(self):
        return [
            "all_services_storage_needs", "storage_dumps", "storage_delta", "full_cumulative_storage_need",
            "nb_of_active_instances"] + self.calculated_attributes_defined_in_infra_hardware_class

    def update_all_services_storage_needs(self):
        if len(self.services) > 0:
            all_services_storage_needs = (sum(service.storage_needed for service in self.services).to(u.TB)
                                          * self.data_replication_factor)

            self.all_services_storage_needs = all_services_storage_needs.set_label(
                f"Storage need of {self.name}")

    def update_storage_dumps(self):
        storage_duration_in_hours = math.ceil(self.data_storage_duration.to(u.hour).magnitude)
        storage_dumps_df = - self.all_services_storage_needs.value.copy().shift(
            periods=storage_duration_in_hours, freq='h')
        storage_dumps_df = storage_dumps_df[storage_dumps_df.index <= self.all_services_storage_needs.value.index.max()]

        self.storage_dumps = ExplainableHourlyQuantities(
            storage_dumps_df, label=f"Storage dumps for {self.name}", left_parent=self.all_services_storage_needs,
            right_parent=self.data_storage_duration, operator="shift by storage duration and negate")

    def update_storage_delta(self):
        storage_delta = self.all_services_storage_needs + self.storage_dumps
        
        self.storage_delta = storage_delta.set_label(f"Hourly storage delta for {self.name}")

    def update_full_cumulative_storage_need(self):
        storage_delta_df = self.storage_delta.value.copy()
        storage_delta_df.iat[0, 0] += self.initial_storage_need.value
        full_cumulative_storage_need = storage_delta_df.cumsum()

        self.full_cumulative_storage_need = ExplainableHourlyQuantities(
            full_cumulative_storage_need, label=f"Full cumulative storage need for {self.name}",
            left_parent=self.storage_delta, right_parent=self.initial_storage_need,
            operator="cumulative sum of storage delta with initial storage need")

    def update_raw_nb_of_instances(self):
        raw_nb_of_instances = (self.full_cumulative_storage_need / self.storage_capacity).to(u.dimensionless)

        self.raw_nb_of_instances = raw_nb_of_instances.set_label(f"Hourly raw number of instances for {self.name}")

    def update_nb_of_instances(self):
        nb_of_instances = self.raw_nb_of_instances.ceil()

        self.nb_of_instances = nb_of_instances.set_label(f"Hourly number of instances for {self.name}")

    def update_nb_of_active_instances(self):
        nb_of_active_instances = (
                (self.storage_delta.abs() + self.storage_dumps.abs()) / self.storage_capacity
        ).to(u.dimensionless)

        self.nb_of_active_instances = nb_of_active_instances.set_label(
            f"Hourly number of active instances for {self.name}")

    def update_instances_energy(self):
        nb_of_idle_instances = (self.nb_of_instances - self.nb_of_active_instances).set_label(
            f"Hourly number of idle instances for {self.name}")
        active_storage_energy = (
                self.nb_of_active_instances * self.power * ExplainableQuantity(
            1 * u.hour, "one hour") * self.power_usage_effectiveness
        ).set_label(f"Hourly active instances energy for {self.name}")
        idle_storage_energy = (
                nb_of_idle_instances * self.idle_power * ExplainableQuantity(
            1 * u.hour, "one hour") * self.power_usage_effectiveness
        ).set_label(f"Hourly idle instances energy for {self.name}")

        storage_energy = (active_storage_energy + idle_storage_energy)

        self.instances_energy = storage_energy.set_label(f"Storage energy for {self.name}")