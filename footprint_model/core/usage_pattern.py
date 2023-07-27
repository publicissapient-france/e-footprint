from footprint_model.constants.units import u
from footprint_model.core.device_population import DevicePopulation
from footprint_model.core.user_journey import UserJourney
from footprint_model.core.service import Service
from footprint_model.core.infra_need import InfraNeed
from footprint_model.core.network import Network
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.constants.explainable_quantities import intermediate_calculation


from typing import Dict, List, Set
from datetime import datetime
import pytz
import math
from pint import Quantity


class UsagePattern:
    def __init__(self, name: str, user_journey: UserJourney, device_population: DevicePopulation,
                 network: Network, user_journey_freq_per_user: Quantity, time_intervals: List[List[int]]):
        self.name = name
        self._user_journey = user_journey
        self._user_journey.link_usage_pattern(self)
        self._device_population = device_population
        self._device_population.link_usage_pattern(self)
        self._network = network
        self._network.link_usage_pattern(self)
        if not user_journey_freq_per_user.check("[user_journey] / ([person] * [time])"):
            raise ValueError(f"User journey frequency defined in {self.name} should have "
                             f"[user_journey] / ([user] * [time]) dimensionality")
        self.user_journey_freq_per_user = SourceValue(
            user_journey_freq_per_user, Sources.USER_INPUT, f"user_journeys frequency per user in {self.name}")
        self._check_time_intervals_validity(time_intervals)
        self.time_intervals = time_intervals

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, UsagePattern):
            return self.name == other.name
        return False

    @property
    def usage_time_fraction(self):
        return SourceValue(
            (sum(time_interval[1] - time_interval[0] for time_interval in self.time_intervals) / 24) * u.dimensionless,
            Sources.USER_INPUT, f"usage time fraction in {self.name}")

    @staticmethod
    def _check_time_intervals_validity(time_intervals: List[List[int]]):
        sorted_time_intervals = sorted(time_intervals, key=lambda x: x[0])
        for i in range(len(sorted_time_intervals)):
            start_time, end_time = sorted_time_intervals[i]
            if start_time >= end_time:
                raise ValueError(
                    f"Invalid time interval {sorted_time_intervals[i]}, start time must be earlier than end time")
            if i < len(sorted_time_intervals) - 1:
                next_start_time = sorted_time_intervals[i + 1][0]
                if next_start_time < end_time:
                    raise ValueError(
                        f"Time interval {sorted_time_intervals[i + 1]} starts before time interval"
                        f" {sorted_time_intervals[i]} ends")

    @property
    def user_journey(self) -> UserJourney:
        return self._user_journey

    @user_journey.setter
    def user_journey(self, new_user_journey):
        self._user_journey.unlink_usage_pattern(self)
        self._user_journey = new_user_journey
        self._user_journey.link_usage_pattern(self)

    @property
    def device_population(self) -> DevicePopulation:
        return self._device_population

    @device_population.setter
    def device_population(self, new_device_population):
        self._device_population.unlink_usage_pattern(self)
        self._device_population = new_device_population
        self._device_population.link_usage_pattern(self)

    @property
    def network(self) -> Network:
        return self._network

    @network.setter
    def network(self, new_network):
        self._network.unlink_usage_pattern(self)
        self._network = new_network
        self._network.link_usage_pattern(self)

    @property
    def services(self) -> Set[Service]:
        return self.user_journey.services

    @property
    def non_usage_time_fraction(self) -> ExplainableQuantity:
        return SourceValue(
            1 - self.usage_time_fraction.value, Sources.USER_INPUT, f"fraction of non usage time in {self.name}")

    @property
    def user_journey_freq(self) -> ExplainableQuantity:
        return self.device_population.nb_devices * self.user_journey_freq_per_user

    @property
    @intermediate_calculation("Number of user journeys in parallel during usage")
    def nb_user_journeys_in_parallel_during_usage(self):
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        nb_uj_in_parallel__raw = (
            (one_user_journey * (self.user_journey_freq * self.user_journey.duration / self.usage_time_fraction)).to(
                u.user_journey))
        if nb_uj_in_parallel__raw.magnitude != int(nb_uj_in_parallel__raw.magnitude):
            nb_user_journeys_in_parallel_during_usage = (
                    nb_uj_in_parallel__raw + ExplainableQuantity(
                (math.ceil(nb_uj_in_parallel__raw.magnitude) - nb_uj_in_parallel__raw.magnitude)
                * u.user_journey, "Rounding up of user journeys in parallel to next integer"))
        else:
            nb_user_journeys_in_parallel_during_usage = nb_uj_in_parallel__raw

        return nb_user_journeys_in_parallel_during_usage

    @property
    def estimated_infra_need(self) -> Dict[Service, InfraNeed]:
        infra_needs = {}

        ram_per_service = self.user_journey.ram_needed_per_service
        storage_per_service = self.user_journey.storage_need_per_service
        cpu_per_service = self.user_journey.cpu_need_per_service

        # determine the time difference between population timezone and UTC
        utc_tz = pytz.timezone('UTC')
        current_time = datetime.now()
        time_diff = self.device_population.country.timezone.utcoffset(current_time) - utc_tz.utcoffset(current_time)
        time_diff_in_hours = int(time_diff.total_seconds() / 3600)

        nb_user_journeys_in_parallel_during_usage = self.nb_user_journeys_in_parallel_during_usage
        for service in ram_per_service.keys():
            ram_needed = [ExplainableQuantity(0 * u.Mo)] * 24
            cpu_needed = [ExplainableQuantity(0 * u.core)] * 24

            for time in self.time_intervals:
                start_time, end_time = time

                for hour in range(start_time, end_time):
                    # calculate the corresponding hour in UTC
                    utc_hour = (hour - time_diff_in_hours) % 24

                    ram_needed[utc_hour] += ram_per_service[service] * nb_user_journeys_in_parallel_during_usage
                    cpu_needed[utc_hour] += cpu_per_service[service] * nb_user_journeys_in_parallel_during_usage

            storage_needed = (storage_per_service[service] * self.user_journey_freq).to(u.To / u.year)

            infra_needs[service] = InfraNeed(ram_needed, storage_needed, cpu_needed)

        return infra_needs
