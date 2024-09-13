from typing import List

from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.constants.countries import Country
from efootprint.constants.units import u
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.compute_nb_occurrences_in_parallel import compute_nb_avg_hourly_occurrences
from efootprint.core.service import Service
from efootprint.core.usage.job import Job
from efootprint.core.hardware.network import Network
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.explainable_objects import (
    ExplainableQuantity, ExplainableHourlyQuantities, EmptyExplainableObject)


class UsagePattern(ModelingObject):
    def __init__(self, name: str, user_journey: UserJourney, devices: List[Hardware], network: Network,
                 country: Country, hourly_user_journey_starts: ExplainableHourlyQuantities):
        super().__init__(name)
        self.utc_hourly_user_journey_starts = None
        self.nb_user_journeys_in_parallel = None
        self.devices_energy = None
        self.devices_energy_footprint = None
        self.devices_fabrication_footprint = None
        self.energy_footprint = None
        self.instances_fabrication_footprint = None
        self.hourly_user_journey_starts = hourly_user_journey_starts.set_label(f"{self.name} hourly nb of visits")
        self.user_journey = user_journey
        self.devices = devices
        self.network = network
        self.country = country

    @property
    def calculated_attributes(self):
        return ["utc_hourly_user_journey_starts", "nb_user_journeys_in_parallel", "devices_energy",
                "devices_energy_footprint", "devices_fabrication_footprint", "energy_footprint",
                "instances_fabrication_footprint"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return self.jobs

    @property
    def services(self) -> List[Service]:
        return self.user_journey.services

    @property
    def jobs(self) -> List[Job]:
        return list(set(sum([service.jobs for service in self.services], start=[])))

    @property
    def systems(self) -> List:
        return self.modeling_obj_containers

    def update_utc_hourly_user_journey_starts(self):
        utc_hourly_user_journey_starts = self.hourly_user_journey_starts.convert_to_utc(
            local_timezone=self.country.timezone)

        self.utc_hourly_user_journey_starts = utc_hourly_user_journey_starts.set_label(f"{self.name} UTC")

    def update_nb_user_journeys_in_parallel(self):
        nb_of_user_journeys_in_parallel = compute_nb_avg_hourly_occurrences(
            self.utc_hourly_user_journey_starts, self.user_journey.duration)

        self.nb_user_journeys_in_parallel = nb_of_user_journeys_in_parallel.set_label(
            f"{self.name} hourly nb of user journeys in parallel")

    def update_devices_energy(self):
        total_devices_energy_spent_over_one_full_hour = sum(
            [device.power for device in self.devices]) * ExplainableQuantity(1 * u.hour, "one full hour")

        devices_energy = (self.nb_user_journeys_in_parallel * total_devices_energy_spent_over_one_full_hour).to(u.kWh)

        self.devices_energy = devices_energy.set_label(f"Energy consumed by {self.name} devices")

    def update_devices_energy_footprint(self):
        energy_footprint = (self.devices_energy * self.country.average_carbon_intensity).to(u.kg)
        
        self.devices_energy_footprint = energy_footprint.set_label(f"Energy footprint of {self.name}")

    def update_devices_fabrication_footprint(self):
        devices_fabrication_footprint_over_one_hour = EmptyExplainableObject()
        for device in self.devices:
            device_uj_fabrication_footprint = (
                    device.carbon_footprint_fabrication * ExplainableQuantity(1 * u.hour, "one hour")
                    / (device.lifespan * device.fraction_of_usage_time)
            ).to(u.g).set_label(
                f"{device.name} fabrication footprint over one hour")
            devices_fabrication_footprint_over_one_hour += device_uj_fabrication_footprint

        devices_fabrication_footprint = (
                self.nb_user_journeys_in_parallel * devices_fabrication_footprint_over_one_hour).to(u.kg, rounding=2)

        self.devices_fabrication_footprint = devices_fabrication_footprint.set_label(
            f"Devices fabrication footprint of {self.name}")

    def update_energy_footprint(self):
        self.energy_footprint = (self.devices_energy_footprint + 0).set_label(f"{self.name} total energy footprint")

    def update_instances_fabrication_footprint(self):
        self.instances_fabrication_footprint = (self.devices_fabrication_footprint + 0).set_label(
            f"{self.name} total fabrication footprint")
