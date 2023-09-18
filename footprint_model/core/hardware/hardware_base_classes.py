from abc import ABC, abstractmethod

from footprint_model.constants.countries import Country
from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u


class Hardware(ModelingObject):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, fraction_of_usage_time: SourceValue):
        super().__init__(name)
        self.carbon_footprint_fabrication = carbon_footprint_fabrication
        self.carbon_footprint_fabrication.set_name(f"carbon footprint fabrication of {self.name}")
        self.power = power
        self.power.set_name(f"power of {self.name}")
        self.lifespan = lifespan
        self.lifespan.set_name(f"lifespan of {self.name}")
        if not fraction_of_usage_time.value.check("[]"):
            raise ValueError("Variable 'fraction_of_usage_per_day' shouldn’t have any dimensionality")
        self.fraction_of_usage_time = fraction_of_usage_time
        self.fraction_of_usage_time.set_name(f"{self.name} fraction of usage time")

    def compute_calculated_attributes(self):
        pass


class ObjectLinkedToUsagePatterns(ABC):
    def __init__(self):
        self.usage_patterns = set()

    def link_usage_pattern(self, usage_pattern):
        self.usage_patterns = self.usage_patterns | {usage_pattern}

    def unlink_usage_pattern(self, usage_pattern):
        self.usage_patterns.discard(usage_pattern)


class InfraHardware(Hardware, ObjectLinkedToUsagePatterns):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue, lifespan: SourceValue,
                 country: Country):
        super().__init__(
            name, carbon_footprint_fabrication, power, lifespan, SourceValue(1 * u.dimensionless, Sources.HYPOTHESIS))
        ObjectLinkedToUsagePatterns.__init__(self)
        self.all_services_cpu_needs = None
        self.all_services_ram_needs = None
        self.nb_of_instances = None
        self.instances_power = None
        self.fraction_of_time_in_use = None
        self.energy_footprint = None
        self.instances_fabrication_footprint = None
        self.country = country

    def update_functions_defined_in_infra_hardware_class(self):
        self.update_all_services_cpu_needs()
        self.update_all_services_ram_needs()
        self.update_fraction_of_time_in_use()
        self.update_nb_of_instances()
        self.update_instances_fabrication_footprint()
        self.update_instances_power()
        self.update_energy_footprint()

    @abstractmethod
    def update_nb_of_instances(self):
        pass

    @abstractmethod
    def update_instances_power(self):
        pass

    @property
    @abstractmethod
    def services(self):
        pass

    def update_all_services_ram_needs(self):
        service_ram_needs_list = [service.hour_by_hour_ram_need for service in self.services]
        all_service_ram_needs = sum(service_ram_needs_list)

        self.all_services_ram_needs = all_service_ram_needs

    def update_all_services_cpu_needs(self):
        service_cpu_needs_list = [service.hour_by_hour_cpu_need for service in self.services]
        all_services_cpu_needs = sum(service_cpu_needs_list)

        self.all_services_cpu_needs = all_services_cpu_needs

    def update_fraction_of_time_in_use(self):
        usage_from_ram = self.all_services_ram_needs.to_usage().define_as_intermediate_calculation(
            f"{self.name} usage pattern from RAM need")
        usage_from_cpu = self.all_services_cpu_needs.to_usage().define_as_intermediate_calculation(
            f"{self.name} usage pattern from CPU need")

        fraction_of_time_in_use = (usage_from_ram + usage_from_cpu).compute_usage_time_fraction()

        self.fraction_of_time_in_use = fraction_of_time_in_use.define_as_intermediate_calculation(
            f"Fraction of time in use of {self.name}")

    def update_instances_fabrication_footprint(self):
        self.instances_fabrication_footprint = (
                self.carbon_footprint_fabrication * self.nb_of_instances / self.lifespan).to(
            u.kg / u.year).define_as_intermediate_calculation(f"Instances of {self.name} fabrication footprint")

    def update_energy_footprint(self):
        self.energy_footprint = (self.instances_power * self.country.average_carbon_intensity).to(
            u.kg / u.year).define_as_intermediate_calculation(f"Energy footprint of {self.name}")
