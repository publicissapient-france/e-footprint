from footprint_model.constants.units import u
from footprint_model.core.hardware.device_population import DevicePopulation
from footprint_model.core.usage.time_intervals import TimeIntervals
from footprint_model.core.usage.user_journey import UserJourney
from footprint_model.core.service import Service
from footprint_model.core.hardware.network import Network
from footprint_model.constants.sources import SourceValue
from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity

from typing import List, Set
import math
import logging


class UsagePattern(ModelingObject):
    def __init__(self, name: str, user_journey: UserJourney, device_population: DevicePopulation,
                 network: Network, user_journey_freq_per_user: SourceValue, time_intervals: List[List[int]]):
        super().__init__(name)
        self.nb_user_journeys_in_parallel_during_usage = None
        self.user_journey_freq = None
        self.non_usage_time_fraction = None
        self.usage_time_fraction = None
        self._user_journey = user_journey
        self._device_population = device_population
        self._network = network
        if not user_journey_freq_per_user.value.check("[user_journey] / ([person] * [time])"):
            raise ValueError(f"User journey frequency defined in {self.name} should have "
                             f"[user_journey] / ([user] * [time]) dimensionality")
        self.user_journey_freq_per_user = user_journey_freq_per_user
        self.user_journey_freq_per_user.set_name(f"Usage frequency in {self.name}")
        self.time_intervals = TimeIntervals(f"{self.name} usage time intervals", time_intervals,
                                            device_population.country.timezone)

        self.compute_calculated_attributes()

        self._user_journey.link_usage_pattern(self)
        self._device_population.link_usage_pattern(self)
        self._network.link_usage_pattern(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, UsagePattern):
            return self.name == other.name
        return False

    def compute_calculated_attributes(self):
        logging.info(f"Computing calculated attributes for {self.name}")
        self.update_usage_time_fraction()
        self.update_user_journey_freq()
        self.update_nb_user_journeys_in_parallel_during_usage()

    def update_usage_time_fraction(self):
        usage_time_fraction = self.time_intervals.utc_time_intervals.compute_usage_time_fraction()
        self.usage_time_fraction = usage_time_fraction.define_as_intermediate_calculation(
            f"Usage time fraction of {self.name}")

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

    def update_user_journey_freq(self):
        self.user_journey_freq = (
                self.device_population.nb_devices * self.user_journey_freq_per_user).define_as_intermediate_calculation(
            f"User journey frequency of {self.name}")

    def update_nb_user_journeys_in_parallel_during_usage(self):
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

        self.nb_user_journeys_in_parallel_during_usage = nb_user_journeys_in_parallel_during_usage\
            .define_as_intermediate_calculation(f"Number of user journeys in parallel during {self.name}")
