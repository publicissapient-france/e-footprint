from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.constants.countries import Country
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.constants.physical_elements import PhysicalElements
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.constants.sources import SourceValue, Sources
from efootprint.constants.units import u

from typing import List
import math


class DevicePopulation(ModelingObject):
    def __init__(self, name: str, nb_devices: SourceValue, country: Country, devices: List[Hardware]):
        super().__init__(name)
        self.instances_fabrication_footprint = None
        self.energy_footprint = None
        self.power = None
        self.user_journey_freq_per_up = ExplainableObjectDict()
        self.nb_user_journeys_in_parallel_during_usage_per_up = ExplainableObjectDict()
        self.utc_time_intervals_per_up = ExplainableObjectDict()
        self.nb_devices = nb_devices
        self.nb_devices.set_name(f"Nb devices in {self.name}")
        self.country = country

        self.calculated_attributes = [
            "user_journey_freq_per_up", "nb_user_journeys_in_parallel_during_usage_per_up",
            "utc_time_intervals_per_up", "power", "energy_footprint", "instances_fabrication_footprint"]

        self._devices = []
        # Triggers computation of calculated attributes
        self.devices = devices

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, new_devices):
        # Here the observer pattern is implemented manually because devices is a list and hence not handled by 
        # ModelingObject’s __setattr__ logic
        for device in self._devices:
            device.remove_obj_from_modeling_obj_containers(self)
        self._devices = new_devices
        for device in self._devices:
            device.add_obj_to_modeling_obj_containers(self)
        self.compute_calculated_attributes()

    @property
    def usage_patterns(self):
        return self.modeling_obj_containers

    @property
    def services(self):
        return list(set(sum([up.services for up in self.usage_patterns], [])))

    @property
    def networks(self):
        return list(set([up.network for up in self.usage_patterns]))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List:
        return self.services + self.networks

    def update_utc_time_intervals_per_up(self):
        for usage_pattern in self.usage_patterns:
            utc_time_intervals = usage_pattern.hourly_usage.convert_to_utc(local_timezone=self.country.timezone)
            self.utc_time_intervals_per_up[usage_pattern] = utc_time_intervals.define_as_intermediate_calculation(
                f"{usage_pattern.name} UTC")

    def update_user_journey_freq_per_up(self):
        for usage_pattern in self.usage_patterns:
            self.user_journey_freq_per_up[usage_pattern] = (
                    self.nb_devices * usage_pattern.user_journey_freq_per_user).define_as_intermediate_calculation(
                    f"User journey frequency of {usage_pattern.name}")

    def update_nb_user_journeys_in_parallel_during_usage_per_up(self):
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        for usage_pattern in self.usage_patterns:
            nb_uj_in_parallel__raw = (
                (one_user_journey *
                 (usage_pattern.user_journey_freq * usage_pattern.user_journey.duration
                  / usage_pattern.usage_time_fraction)
                 ).to(u.user_journey))
            if nb_uj_in_parallel__raw.magnitude != int(nb_uj_in_parallel__raw.magnitude):
                nb_user_journeys_in_parallel_during_usage = (
                        nb_uj_in_parallel__raw +
                        ExplainableQuantity(
                            (math.ceil(nb_uj_in_parallel__raw.magnitude) - nb_uj_in_parallel__raw.magnitude)
                            * u.user_journey, "Rounding up of user journeys in parallel to next integer"))
            else:
                nb_user_journeys_in_parallel_during_usage = nb_uj_in_parallel__raw

            self.nb_user_journeys_in_parallel_during_usage_per_up[usage_pattern] = \
                nb_user_journeys_in_parallel_during_usage.define_as_intermediate_calculation(
                    f"Number of user journeys in parallel during {usage_pattern.name}")

    def update_power(self):
        if len(self.usage_patterns) > 0:
            power = 0
            for device in self.devices:
                for usage_pattern in self.usage_patterns:
                    power += (
                            self.user_journey_freq_per_up[usage_pattern]
                            * (device.power * usage_pattern.user_journey.duration)
                    ).to(u.kWh / u.year)

            self.power = power.define_as_intermediate_calculation(f"Power of {self.name} devices")
        else:
            self.power = ExplainableQuantity(0 * u.W, f"No power for {self.name} because no associated usage pattern")

    def update_energy_footprint(self):
        energy_footprint = (self.power * self.country.average_carbon_intensity).to(u.kg / u.year)
        self.energy_footprint = energy_footprint.define_as_intermediate_calculation(f"Energy footprint of {self.name}")

    def update_instances_fabrication_footprint(self):
        if len(self.usage_patterns) > 0:
            devices_fabrication_footprint = 0
            for device in self.devices:
                for usage_pattern in self.usage_patterns:
                    device_uj_fabrication_footprint = (
                            device.carbon_footprint_fabrication * usage_pattern.user_journey.duration
                            / (device.lifespan * device.fraction_of_usage_time)
                    ).to(u.g / u.user_journey).define_as_intermediate_calculation(
                        f"{device.name} fabrication footprint over {usage_pattern.user_journey.name}")
                    devices_fabrication_footprint += (
                            self.user_journey_freq_per_up[usage_pattern] * device_uj_fabrication_footprint
                    ).to(u.kg / u.year)

            self.instances_fabrication_footprint = devices_fabrication_footprint.define_as_intermediate_calculation(
                f"Devices fabrication footprint of {self.name}")
        else:
            self.instances_fabrication_footprint = ExplainableQuantity(
                0 * u.kg / u.year, f"No fabrication footprint for {self.name} because no associated usage pattern")


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