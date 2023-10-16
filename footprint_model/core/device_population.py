from footprint_model.constants.countries import Country
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation
from footprint_model.constants.physical_elements import PhysicalElements, Hardware, ObjectLinkedToUsagePatterns
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u

from typing import List


class Device(Hardware):
    def __init__(self, name: str, carbon_footprint_fabrication: SourceValue, power: SourceValue,
                 lifespan: SourceValue, fraction_of_usage_time: SourceValue, data_usage: SourceValue):
        super().__init__(name, carbon_footprint_fabrication, power, lifespan)
        self.fraction_of_usage_time = fraction_of_usage_time
        self.fraction_of_usage_time.set_name(f"fraction of usage of {self.name}")
        self.data_usage = data_usage
        self.data_usage.set_name(f"data usage of {self.name}")

    def __str__(self):
        return self.name

    def __post_init__(self):
        if not self.fraction_of_usage_time.value.check("[]"):
            raise ValueError("Variable 'fraction_of_usage_per_day' shouldn’t have any dimensionality")
        if not self.data_usage.value.check("[data] / [time]"):
            raise ValueError("Variable 'data_usage' should have data / time dimensionality")


class DevicePopulation(ObjectLinkedToUsagePatterns):
    def __init__(self, name: str, nb_users: float, country: Country, devices: List[Device]):
        super().__init__()
        self.name = name
        self.nb_devices = SourceValue(nb_users * u.user, Sources.USER_INPUT, f"nb devices in {self.name}")
        self.country = country
        self.devices = devices

    @property
    @intermediate_calculation("Devices power")
    def power(self) -> ExplainableQuantity:
        power = ExplainableQuantity(0 * u.W)
        for usage_pattern in self.usage_patterns:
            for device in self.devices:
                power += (
                         usage_pattern.user_journey_freq
                         * usage_pattern.user_journey.compute_device_consumption(device)
                ).to(u.kWh / u.year)

        return power

    @property
    @intermediate_calculation("Energy footprint")
    def energy_footprint(self):
        return (self.power * self.country.average_carbon_intensity).to(u.kg / u.year)

    @property
    @intermediate_calculation("Devices fabrication footprint")
    def fabrication_footprint(self) -> ExplainableQuantity:
        devices_fabrication_footprint = ExplainableQuantity(0 * u.kg / u.year)
        for usage_pattern in self.usage_patterns:
            for device in self.devices:
                devices_fabrication_footprint += (
                        usage_pattern.user_journey_freq
                        * usage_pattern.user_journey.compute_fabrication_footprint(device)
                ).to(u.kg / u.year)

        return devices_fabrication_footprint


class Devices:
    SMARTPHONE = Device(
        PhysicalElements.SMARTPHONE,
        carbon_footprint_fabrication=SourceValue(30 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(1 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(3 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(3.6 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022),
        data_usage=SourceValue(12.7 * u.Go / u.month, Sources.ARCEP_2022_MOBILE_NETWORK_STUDY)
    )
    LAPTOP = Device(
        PhysicalElements.LAPTOP,
        carbon_footprint_fabrication=SourceValue(156 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
        # TODO: get data
        data_usage=SourceValue(0 * u.Go / u.month, Sources.HYPOTHESIS)
    )

    BOX = Device(
        PhysicalElements.BOX,
        carbon_footprint_fabrication=SourceValue(78 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(10 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(24 * u.hour / u.day, Sources.HYPOTHESIS),
        # TODO: get data
        data_usage=SourceValue(0 * u.Go / u.month, Sources.HYPOTHESIS)
    )
    SCREEN = Device(
        PhysicalElements.SCREEN,
        # TODO: To update
        carbon_footprint_fabrication=SourceValue(222 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(30 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
        data_usage=SourceValue(0 * u.Go / u.month, Sources.HYPOTHESIS)
    )