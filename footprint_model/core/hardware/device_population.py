from footprint_model.constants.countries import Country
from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.core.hardware.hardware_base_classes import Hardware, ObjectLinkedToUsagePatterns
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u

from typing import List


class DevicePopulation(ModelingObject, ObjectLinkedToUsagePatterns):
    def __init__(self, name: str, nb_devices: SourceValue, country: Country, devices: List[Hardware]):
        super().__init__(name)
        ObjectLinkedToUsagePatterns.__init__(self)
        self.fabrication_footprint = None
        self.energy_footprint = None
        self.power = None
        self.nb_devices = nb_devices
        self.nb_devices.set_name(f"Nb devices in {self.name}")
        self.country = country
        self.devices = devices

        self.compute_calculated_attributes()

    def compute_calculated_attributes(self):
        if len(self.usage_patterns) > 0:
            self.update_power()
            self.update_energy_footprint()
            self.update_fabrication_footprint()

    def update_power(self):
        devices_powers = [device.power for device in self.devices]
        user_journey_freqs = [usage_pattern.user_journey_freq for usage_pattern in self.usage_patterns]
        user_journey_durations = [usage_pattern.user_journey.duration for usage_pattern in self.usage_patterns]

        power = 0
        for device_power in devices_powers:
            for user_journey_freq, user_journey_duration in zip(user_journey_freqs, user_journey_durations):
                power += (user_journey_freq * (device_power * user_journey_duration)).to(u.kWh / u.year)

        self.power = power.define_as_intermediate_calculation(f"Power of {self.name} devices")

    def update_energy_footprint(self):
        energy_footprint = (self.power * self.country.average_carbon_intensity).to(u.kg / u.year)
        self.energy_footprint = energy_footprint.define_as_intermediate_calculation(f"Energy footprint of {self.name}")

    def update_fabrication_footprint(self):
        device_fabrication_carbon_footprints = [device.carbon_footprint_fabrication for device in self.devices]
        device_lifespans = [device.lifespan for device in self.devices]
        device_fractions_of_usage_time = [device.fraction_of_usage_time for device in self.devices]
        user_journey_durations = [usage_pattern.user_journey.duration for usage_pattern in self.usage_patterns]
        user_journey_freqs = [usage_pattern.user_journey_freq for usage_pattern in self.usage_patterns]

        devices_fabrication_footprint = 0
        for device_fabrication_carbon_footprint, device_lifespan, device_fraction_of_usage_time \
                in zip(device_fabrication_carbon_footprints, device_lifespans, device_fractions_of_usage_time):
            for user_journey_duration, user_journey_freq in zip(user_journey_durations, user_journey_freqs):
                device_uj_fabrication_footprint = (
                        device_fabrication_carbon_footprint * user_journey_duration
                        / (device_lifespan * device_fraction_of_usage_time)).to(u.g / u.user_journey)
                devices_fabrication_footprint += (
                        user_journey_freq * device_uj_fabrication_footprint).to(u.kg / u.year)

        self.fabrication_footprint = devices_fabrication_footprint.define_as_intermediate_calculation(
            f"Devices fabrication footprint of {self.name}")


class Devices:
    SMARTPHONE = Hardware(
        PhysicalElements.SMARTPHONE,
        carbon_footprint_fabrication=SourceValue(30 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(1 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(3 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(3.6 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022),
    )
    LAPTOP = Hardware(
        PhysicalElements.LAPTOP,
        carbon_footprint_fabrication=SourceValue(156 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
        # TODO: get data
    )

    BOX = Hardware(
        PhysicalElements.BOX,
        carbon_footprint_fabrication=SourceValue(78 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(10 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(24 * u.hour / u.day, Sources.HYPOTHESIS),
        # TODO: get data
    )
    SCREEN = Hardware(
        PhysicalElements.SCREEN,
        # TODO: To update
        carbon_footprint_fabrication=SourceValue(222 * u.kg, Sources.BASE_ADEME_V19),
        power=SourceValue(30 * u.W, Sources.HYPOTHESIS),
        lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
        fraction_of_usage_time=SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS),
    )