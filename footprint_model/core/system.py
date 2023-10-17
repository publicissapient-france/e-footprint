from footprint_model.constants.units import u
from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import Device, Network, PhysicalElements, Devices, Networks
from footprint_model.core.user_journey import UserJourney
from footprint_model.constants.abstract_constants import SERVER_RAM_PER_DATA_TRANSFERED

from dataclasses import dataclass
from typing import Dict
from pint import Quantity


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
    user_journey: UserJourney
    population: Population
    # TODO: attach fraction of use to device type
    frac_smartphone: float
    frac_mobile_network_for_smartphones: float
    nb_visits_per_user_per_year: int
    daily_usage_window: Quantity

    def __post_init__(self):
        if not self.daily_usage_window.check("[time]"):
            raise ValueError("Variable 'daily_usage_window' does not have time dimensionality")

    @property
    def nb_visits_per_year(self) -> float:
        return self.population.nb_users * self.nb_visits_per_user_per_year

    def compute_device_consumption(self, device: Device, frac_visits: float) -> Quantity:
        return frac_visits * self.nb_visits_per_year * self.user_journey.compute_device_consumption(device)

    def compute_fabrication_footprint(self, device: Device, frac_visits: float) -> Quantity:
        return frac_visits * self.nb_visits_per_year * self.user_journey.compute_fabrication_footprint(device)

    def compute_network_consumption(self, network: Network, frac_visits: float) -> Quantity:
        return frac_visits * self.nb_visits_per_year * self.user_journey.compute_network_consumption(network)

    def compute_energy_consumption(self) -> Dict[PhysicalElements, Quantity]:
        return {
            PhysicalElements.SMARTPHONE: self.compute_device_consumption(Devices.SMARTPHONE, self.frac_smartphone).to(
                u.kWh
            ),
            PhysicalElements.LAPTOP: self.compute_device_consumption(Devices.LAPTOP, 1 - self.frac_smartphone).to(
                u.kWh
            ),
            PhysicalElements.MOBILE_NETWORK: self.compute_network_consumption(
                Networks.MOBILE_NETWORK, self.frac_smartphone * self.frac_mobile_network_for_smartphones
            ).to(u.kWh),
            PhysicalElements.WIFI_NETWORK: self.compute_network_consumption(
                Networks.WIFI_NETWORK,
                (1 - self.frac_smartphone) + self.frac_smartphone * (1 - self.frac_mobile_network_for_smartphones),
            ).to(u.kWh),
        }

    @property
    def estimated_server_need(self):
        nb_visits_per_usage_window = self.nb_visits_per_year / 365
        nb_visitors_in_parallel_during_usage_window = (
                nb_visits_per_usage_window * self.user_journey.duration / self.daily_usage_window)
        data_transfered_in_parallel = (nb_visitors_in_parallel_during_usage_window
                                       * (self.user_journey.data_upload + self.user_journey.data_download))
        ram_needed = SERVER_RAM_PER_DATA_TRANSFERED * data_transfered_in_parallel

        storage_needed = self.user_journey.data_upload

        return InfraNeed(ram_needed.to(u.Go), storage_needed.to(u.To))


@dataclass
class System:
    # TODO: a list of UsagePattern could be considered afterwards
    usage_pattern: UsagePattern
    data_replication_factor: int
    data_storage_duration: int
