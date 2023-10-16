from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import (Device, Network, PhysicalElements, Devices, Networks, Server)
from footprint_model.constants.units import u
from footprint_model.core.user_journey import UserJourney
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.explainable_quantities import ExplainableQuantity


from dataclasses import dataclass
from typing import Dict

from pint import Quantity


class Population:
    def __init__(self, name: str, nb_users: float, country: Country):
        self.name = name
        self.nb_users = SourceValue(nb_users * u.user, Sources.USER_INPUT, f"nb users in {self.name}")
        self.country = country


@dataclass
class InfraNeed:
    ram: ExplainableQuantity
    storage: ExplainableQuantity

    def __post_init__(self):
        # Todo: Simplify unit checking by creating a custom dataclass
        if not self.ram.value.check("[data]"):
            raise ValueError("Variable 'ram' does not have octet dimensionality")
        if not self.storage.value.check("[data] / [time]"):
            raise ValueError("Variable 'storage' does not have octet over time dimensionality")


class UsagePattern:
    def __init__(self, name: str, user_journey: UserJourney, population: Population, frac_smartphone: float,
                 frac_mobile_network_for_smartphones: float, user_journey_freq_per_user: Quantity,
                 usage_time_fraction: Quantity, smartphone=Devices.SMARTPHONE, laptop=Devices.LAPTOP):
        self.name = name
        self.user_journey = user_journey
        self.population = population
        self.frac_smartphone = SourceValue(
            frac_smartphone * u.dimensionless, Sources.USER_INPUT, f"fraction of smartphones in {self.name}")
        self.frac_mobile_network_for_smartphones = SourceValue(
            frac_mobile_network_for_smartphones * u.dimensionless, Sources.USER_INPUT,
            f"fraction of mobile network use for smartphones in {self.name}")
        if not user_journey_freq_per_user.check("[user_journey] / ([person] * [time])"):
            raise ValueError(f"User journey frequency defined in {self.name} should have "
                             f"[user_journey] / ([user] * [time]) dimensionality")
        self.user_journey_freq_per_user = SourceValue(
            user_journey_freq_per_user, Sources.USER_INPUT, f"user_journeys frequency per user in {self.name}")
        if not usage_time_fraction.check("[]"):
            raise ValueError("Variable 'usage_time_fraction' shouldn’t have any dimensionality."
                             " It is the fraction of time the service is used.")
        self.usage_time_fraction = SourceValue(usage_time_fraction, Sources.USER_INPUT,
                                               f"usage time fraction in {self.name}")
        self.smartphone = smartphone
        self.laptop = laptop

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, UsagePattern):
            return self.name == other.name
        return False

    @property
    def frac_laptop(self) -> float:
        return SourceValue(
            1 - self.frac_smartphone.value, Sources.USER_INPUT, f"fraction of laptops in {self.name}")

    @property
    def non_usage_time_fraction(self):
        return SourceValue(
            1 - self.usage_time_fraction.value, Sources.USER_INPUT, f"fraction of non usage time in {self.name}")

    @property
    def frac_non_mobile_network_for_smartphones(self):
        return SourceValue(1 - self.frac_mobile_network_for_smartphones.value, Sources.USER_INPUT,
                           f"fraction of non mobile network use for smartphones in {self.name}")

    @property
    def wifi_usage_fraction(self) -> float:
        return self.frac_laptop + self.frac_smartphone * self.frac_non_mobile_network_for_smartphones

    @property
    def user_journeys_freq(self) -> float:
        return self.population.nb_users * self.user_journey_freq_per_user

    def compute_device_consumption(self, device: Device, frac_user_journeys: ExplainableQuantity) -> ExplainableQuantity:
        return frac_user_journeys * self.user_journeys_freq * self.user_journey.compute_device_consumption(device)

    def compute_device_fabrication_footprint(
            self, device: Device, frac_user_journeys: ExplainableQuantity) -> ExplainableQuantity:
        return frac_user_journeys * self.user_journeys_freq * self.user_journey.compute_fabrication_footprint(device)

    def compute_network_consumption(
            self, network: Network, frac_user_journeys: ExplainableQuantity) -> ExplainableQuantity:
        return frac_user_journeys * self.user_journeys_freq * self.user_journey.compute_network_consumption(network)

    def compute_energy_consumption(self) -> Dict[PhysicalElements, ExplainableQuantity]:
        return {
            PhysicalElements.SMARTPHONE: self.compute_device_consumption(
                self.smartphone, self.frac_smartphone).to(u.kWh / u.year),
            PhysicalElements.LAPTOP: self.compute_device_consumption(
                self.laptop, self.frac_laptop).to(u.kWh / u.year),
            PhysicalElements.BOX: self.compute_device_consumption(
                Devices.BOX, self.wifi_usage_fraction).to(u.kWh / u.year),
            PhysicalElements.SCREEN: self.compute_device_consumption(
                Devices.SCREEN, self.frac_laptop * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN).to(u.kWh / u.year),
            PhysicalElements.MOBILE_NETWORK: self.compute_network_consumption(
                Networks.MOBILE_NETWORK, self.frac_smartphone * self.frac_mobile_network_for_smartphones
            ).to(u.kWh / u.year),
            PhysicalElements.WIFI_NETWORK: self.compute_network_consumption(
                Networks.WIFI_NETWORK, self.wifi_usage_fraction).to(u.kWh / u.year),
        }

    def compute_fabrication_emissions(self) -> Dict[PhysicalElements, ExplainableQuantity]:
        return {
            PhysicalElements.SMARTPHONE: self.compute_device_fabrication_footprint(
                self.smartphone, self.frac_smartphone).to(u.kg / u.year),
            PhysicalElements.LAPTOP: self.compute_device_fabrication_footprint(
                self.laptop, self.frac_laptop).to(u.kg / u.year),
            PhysicalElements.BOX: self.compute_device_fabrication_footprint(
                Devices.BOX, self.wifi_usage_fraction).to(u.kg / u.year),
            PhysicalElements.SCREEN: self.compute_device_fabrication_footprint(
                Devices.SCREEN, self.frac_laptop * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN).to(u.kg / u.year),
        }

    @property
    def estimated_infra_need(self) -> InfraNeed:
        # TODO: Split into estimated_ram_need and estimated_storage_need for optimization
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        nb_user_journeys_in_parallel_during_usage = max(
            one_user_journey,
            (one_user_journey * (self.user_journeys_freq * self.user_journey.duration / self.usage_time_fraction)).to(
                u.user_journey)
        )
        total_data_transfered = self.user_journey.data_upload + self.user_journey.data_download
        total_data_transfered.formula = f"({total_data_transfered.formula})"
        data_transferred_in_parallel = (nb_user_journeys_in_parallel_during_usage * total_data_transfered)
        ram_needed = Server.SERVER_RAM_PER_DATA_TRANSFERRED * data_transferred_in_parallel

        storage_needed = self.user_journey.data_upload * self.user_journeys_freq

        return InfraNeed(ram_needed.to(u.Go), storage_needed.to(u.To / u.year))

    @property
    def data_upload(self) -> ExplainableQuantity:
        return (self.user_journey.data_upload * self.user_journeys_freq).to(u.To / u.year)

    @property
    def data_download(self) -> ExplainableQuantity:
        return (self.user_journey.data_download * self.user_journeys_freq).to(u.To / u.year)
