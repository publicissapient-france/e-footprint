from dataclasses import dataclass, field
from typing import Dict

from pint import Quantity

from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import (Device, Network, PhysicalElements, Devices, Networks, Server)
from footprint_model.constants.units import u
from footprint_model.core.user_journey import UserJourney


@dataclass
class Population:
    name: str
    nb_users: float
    country: Country


@dataclass()
class InfraNeed:
    ram: Quantity
    storage: Quantity

    def __post_init__(self):
        # Todo: Simplify unit checking by creating a custom dataclass
        if not self.ram.check("[data]"):
            raise ValueError("Variable 'ram' does not have octet dimensionality")
        if not self.storage.check("[data]"):
            raise ValueError("Variable 'storage' does not have octet dimensionality")


@dataclass
class UsagePattern:
    name: str
    user_journey: UserJourney
    population: Population
    frac_smartphone: float
    frac_mobile_network_for_smartphones: float
    nb_visits_per_user_per_year: int
    # TODO: Raise ValueError if daily_usage_window is inferior to user_journey.duration
    daily_usage_window: Quantity
    smartphone: Device = field(default_factory=lambda: Devices.SMARTPHONE)
    laptop: Device = field(default_factory=lambda: Devices.LAPTOP)

    def __post_init__(self):
        if not self.daily_usage_window.check("[time]"):
            raise ValueError("Variable 'daily_usage_window' does not have time dimensionality")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, UsagePattern):
            return self.name == other.name
        return False

    @property
    def frac_laptop(self) -> float:
        return 1 - self.frac_smartphone

    @property
    def wifi_usage_fraction(self) -> float:
        return self.frac_laptop + self.frac_smartphone * (1 - self.frac_mobile_network_for_smartphones)

    @property
    def nb_visits_per_year(self) -> float:
        return self.population.nb_users * self.nb_visits_per_user_per_year

    def compute_device_consumption(self, device: Device, frac_visits: float) -> Quantity:
        return frac_visits * self.nb_visits_per_year * self.user_journey.compute_device_consumption(device)

    def compute_device_fabrication_footprint(self, device: Device, frac_visits: float) -> Quantity:
        return frac_visits * self.nb_visits_per_year * self.user_journey.compute_fabrication_footprint(device)

    def compute_network_consumption(self, network: Network, frac_visits: float) -> Quantity:
        return frac_visits * self.nb_visits_per_year * self.user_journey.compute_network_consumption(network)

    def compute_energy_consumption(self) -> Dict[PhysicalElements, Quantity]:
        return {
            PhysicalElements.SMARTPHONE: self.compute_device_consumption(
                self.smartphone, self.frac_smartphone).to(u.kWh),
            PhysicalElements.LAPTOP: self.compute_device_consumption(
                self.laptop, self.frac_laptop).to(u.kWh),
            PhysicalElements.BOX: self.compute_device_consumption(Devices.BOX, self.wifi_usage_fraction).to(u.kWh),
            PhysicalElements.SCREEN: self.compute_device_consumption(
                Devices.SCREEN, self.frac_laptop * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN).to(u.kWh),
            PhysicalElements.MOBILE_NETWORK: self.compute_network_consumption(
                Networks.MOBILE_NETWORK, self.frac_smartphone * self.frac_mobile_network_for_smartphones
            ).to(u.kWh),
            PhysicalElements.WIFI_NETWORK: self.compute_network_consumption(
                Networks.WIFI_NETWORK, self.wifi_usage_fraction).to(u.kWh),
        }

    def compute_fabrication_emissions(self) -> Dict[PhysicalElements, Quantity]:
        return {
            PhysicalElements.SMARTPHONE: self.compute_device_fabrication_footprint(
                self.smartphone, self.frac_smartphone).to(u.kg),
            PhysicalElements.LAPTOP: self.compute_device_fabrication_footprint(
                self.laptop, self.frac_laptop).to(u.kg),
            PhysicalElements.BOX: self.compute_device_fabrication_footprint(
                Devices.BOX, self.wifi_usage_fraction).to(u.kg),
            PhysicalElements.SCREEN: self.compute_device_fabrication_footprint(
                Devices.SCREEN, self.frac_laptop * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN).to(u.kg),
        }

    @property
    def estimated_infra_need(self) -> InfraNeed:
        # TODO: Split into estimated_ram_need and estimated_storage_need for optimization
        nb_visits_per_usage_window = self.nb_visits_per_year / 365
        nb_visitors_in_parallel_during_usage_window = max(
            1,
            (nb_visits_per_usage_window * self.user_journey.duration / self.daily_usage_window).to(u.s / u.s).magnitude)
        data_transferred_in_parallel = (nb_visitors_in_parallel_during_usage_window
                                        * (self.user_journey.data_upload + self.user_journey.data_download))
        ram_needed = Server.SERVER_RAM_PER_DATA_TRANSFERRED * data_transferred_in_parallel

        storage_needed = self.user_journey.data_upload * self.nb_visits_per_year

        return InfraNeed(ram_needed.to(u.Go), storage_needed.to(u.To))

    @property
    def data_upload(self) -> Quantity:
        return (self.user_journey.data_upload * self.nb_visits_per_year).to(u.To)

    @property
    def data_download(self) -> Quantity:
        return (self.user_journey.data_download * self.nb_visits_per_year).to(u.To)
