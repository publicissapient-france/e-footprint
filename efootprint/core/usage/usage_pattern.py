from typing import List
import math

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
        self.hourly_job_occurrences_per_job = ExplainableObjectDict()
        self.hourly_avg_job_occurrences_per_job = ExplainableObjectDict()
        self.hourly_data_upload_per_job = ExplainableObjectDict()
        self.hourly_data_download_per_job = ExplainableObjectDict()
        self.hourly_user_journey_starts = hourly_user_journey_starts.set_label(f"{self.name}hourly nb of visits")
        self.user_journey = user_journey
        self.devices = devices
        self.network = network
        self.country = country

    @property
    def calculated_attributes(self):
        return ["utc_hourly_user_journey_starts", "nb_user_journeys_in_parallel", "devices_energy",
                "devices_energy_footprint", "devices_fabrication_footprint", "energy_footprint",
                "instances_fabrication_footprint", "hourly_job_occurrences_per_job",
                "hourly_avg_job_occurrences_per_job", "hourly_data_upload_per_job", "hourly_data_download_per_job"]

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return self.services + [self.network]

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
        utc_hourly_user_journey_starts = self.hourly_user_journey_starts.convert_to_utc(local_timezone=self.country.timezone)

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

    def compute_hourly_job_occurrences(self, job):
        job_occurrences = EmptyExplainableObject()
        delay_between_uj_start_and_job_evt = EmptyExplainableObject()
        delay_in_hours_between_uj_start_and_job_evt = 0
        for uj_step in self.user_journey.uj_steps:
            for uj_step_job in uj_step.jobs:
                if uj_step_job == job:
                    job_occurrences += self.utc_hourly_user_journey_starts.return_shifted_hourly_quantities(
                        delay_in_hours_between_uj_start_and_job_evt)

            delay_between_uj_start_and_job_evt += uj_step.user_time_spent
            delay_in_hours_between_uj_start_and_job_evt = math.floor(
                delay_between_uj_start_and_job_evt.to(u.hour).magnitude)

        return job_occurrences.set_label(f"Hourly {job.name} occurrences in {self.name}")

    def update_hourly_job_occurrences_per_job(self):
        for job in self.jobs:
            self.hourly_job_occurrences_per_job[job] = self.compute_hourly_job_occurrences(job)

    def update_hourly_avg_job_occurrences_per_job(self):
        for job in self.jobs:
            hourly_avg_job_occurrences = compute_nb_avg_hourly_occurrences(
                self.hourly_job_occurrences_per_job[job], job.request_duration)
            if isinstance(hourly_avg_job_occurrences, ExplainableHourlyQuantities):
                hourly_avg_job_occurrences.set_label(f"Average hourly {job.name} occurrences in {self.name}")

            self.hourly_avg_job_occurrences_per_job[job] = hourly_avg_job_occurrences

    def compute_job_hourly_data_exchange(self, job: Job, data_exchange_type: str):
        data_exchange_type_no_underscore = data_exchange_type.replace("_", " ")

        job_hourly_data_exchange = EmptyExplainableObject()
        data_exchange_per_hour = (getattr(job, data_exchange_type) / job.duration_in_full_hours).set_label(
            f"{data_exchange_type_no_underscore} per hour for job {job.name} in {self.name}")

        for hour_shift in range(0, job.duration_in_full_hours.magnitude):
            if not isinstance(self.hourly_job_occurrences_per_job[job], EmptyExplainableObject):
                job_hourly_data_exchange += (
                        self.hourly_job_occurrences_per_job[job].return_shifted_hourly_quantities(hour_shift)
                        * data_exchange_per_hour)

        return job_hourly_data_exchange.set_label(
                f"Hourly {data_exchange_type_no_underscore} for {job.name} in {self.name}")

    def update_hourly_data_upload_per_job(self):
        for job in self.jobs:
            self.hourly_data_upload_per_job[job] = self.compute_job_hourly_data_exchange(job, "data_upload")

    def update_hourly_data_download_per_job(self):
        for job in self.jobs:
            self.hourly_data_download_per_job[job] = self.compute_job_hourly_data_exchange(job, "data_download")
