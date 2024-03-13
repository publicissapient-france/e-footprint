from efootprint.abstract_modeling_classes.explainable_objects import ExplainableHourlyUsage, ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.constants.sources import Sources, SOURCE_VALUE_DEFAULT_NAME
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u

from abc import abstractmethod
from typing import List


class Hardware(ModelingObject):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, fraction_of_usage_time: SourceValue):
        super().__init__(name)
        self.carbon_footprint_fabrication = carbon_footprint_fabrication.set_label(f"Carbon footprint fabrication of {self.name}")
        self.power = power.set_label(f"Power of {self.name}")
        self.lifespan = lifespan.set_label(f"Lifespan of {self.name}")
        if not fraction_of_usage_time.value.check("[]"):
            raise ValueError("Variable 'fraction_of_usage_per_day' shouldn’t have any dimensionality")
        self.fraction_of_usage_time = fraction_of_usage_time.set_label(f"{self.name} fraction of usage time")

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return self.modeling_obj_containers

    @property
    def systems(self) -> List:
        return list(set(sum([mod_obj.systems for mod_obj in self.modeling_obj_containers], start=[])))


class InfraHardware(Hardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue, lifespan: SourceValue,
                 average_carbon_intensity: SourceValue):
        super().__init__(
            name, carbon_footprint_fabrication, power, lifespan, SourceValue(1 * u.dimensionless, Sources.HYPOTHESIS))
        self.all_services_cpu_needs = None
        self.all_services_ram_needs = None
        self.nb_of_instances = None
        self.instances_power = None
        self.fraction_of_time_in_use = None
        self.energy_footprint = None
        self.instances_fabrication_footprint = None
        if not average_carbon_intensity.value.check("[time]**2 / [length]**2"):
            raise ValueError(
                "Variable 'average_carbon_intensity' does not have mass over energy "
                "('[time]**2 / [length]**2') dimensionality"
            )
        self.average_carbon_intensity = average_carbon_intensity
        if self.average_carbon_intensity.label == SOURCE_VALUE_DEFAULT_NAME:
            self.average_carbon_intensity.set_label(f"Average carbon intensity of {self.name} electricity")

    @property
    def calculated_attributes_defined_in_infra_hardware_class(self):
        return [
            "all_services_cpu_needs", "all_services_ram_needs", "fraction_of_time_in_use",
            "nb_of_instances", "instances_fabrication_footprint", "instances_power", "energy_footprint"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List:
        return []

    @abstractmethod
    def update_nb_of_instances(self):
        pass

    @abstractmethod
    def update_instances_power(self):
        pass

    @property
    def services(self):
        return self.modeling_obj_containers

    @property
    def systems(self) -> List:
        return list(set(sum([service.systems for service in self.services], start=[])))

    def update_all_services_ram_needs(self):
        if len(self.services) > 0:
            service_ram_needs_list = [service.hour_by_hour_ram_need for service in self.services]
            all_service_ram_needs = sum(service_ram_needs_list)

            self.all_services_ram_needs = all_service_ram_needs.set_label(
                f"RAM needs of all services running on {self.name}")
        else:
            self.all_services_ram_needs = ExplainableHourlyUsage(
                [0 * u.GB] * 24,
                f"No RAM need for {self.name} because no associated service")

    def update_all_services_cpu_needs(self):
        if len(self.services) > 0:
            service_cpu_needs_list = [service.hour_by_hour_cpu_need for service in self.services]
            all_services_cpu_needs = sum(service_cpu_needs_list)

            self.all_services_cpu_needs = all_services_cpu_needs.set_label(
                f"CPU needs of all services running on {self.name}")
        else:
            self.all_services_cpu_needs = ExplainableHourlyUsage(
                [0 * u.core] * 24,
                f"No CPU need for {self.name} because no associated service")

    def update_fraction_of_time_in_use(self):
        if len(self.services) > 0:
            hourly_usage_sum = self.all_services_cpu_needs.to_usage() + self.all_services_ram_needs.to_usage()

        else:
            hourly_usage_sum = ExplainableHourlyUsage(
                [0 * u.dimensionless] * 24,
                f"No activity for {self.name} because no associated service")

        fraction_of_time_in_use = hourly_usage_sum.compute_usage_time_fraction()

        self.fraction_of_time_in_use = fraction_of_time_in_use.set_label(
            f"Fraction of time in use of {self.name}")

    def update_instances_fabrication_footprint(self):
        self.instances_fabrication_footprint = (
                self.carbon_footprint_fabrication * self.nb_of_instances / self.lifespan).to(
            u.kg / u.year).set_label(f"Instances of {self.name} fabrication footprint")

    def update_energy_footprint(self):
        self.energy_footprint = (self.instances_power * self.average_carbon_intensity).to(
            u.kg / u.year).set_label(f"Energy footprint of {self.name}")
