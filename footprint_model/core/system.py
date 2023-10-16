from footprint_model.constants.units import u
from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import (Device, Network, PhysicalElements, Devices, Networks, Servers,
                                                         Server, Storages)
from footprint_model.core.user_journey import UserJourney

from dataclasses import dataclass
from typing import Dict
from pint import Quantity
import math


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

    def compute_device_fabrication_footprint(self, device: Device, frac_visits: float) -> Quantity:
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

    def compute_fabrication_emissions(self) -> Dict[PhysicalElements, Quantity]:
        return {
            PhysicalElements.SMARTPHONE: self.compute_device_fabrication_footprint(
                Devices.SMARTPHONE, self.frac_smartphone).to(u.kg),
            PhysicalElements.LAPTOP: self.compute_device_fabrication_footprint(
                Devices.LAPTOP, 1 - self.frac_smartphone).to(u.kg),
        }

    @property
    def estimated_infra_need(self) -> InfraNeed:
        nb_visits_per_usage_window = self.nb_visits_per_year / 365
        nb_visitors_in_parallel_during_usage_window = (
                nb_visits_per_usage_window * self.user_journey.duration / self.daily_usage_window)
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


@dataclass
class System:
    # TODO: a list of UsagePattern could be considered afterwards
    usage_pattern: UsagePattern
    data_replication_factor: int
    data_storage_duration: Quantity

    def __post_init__(self):
        if not self.data_storage_duration.check("[time]"):
            raise ValueError("Variable 'data_storage_duration' does not have time dimensionality")

    @property
    def number_of_servers_needed__raw(self) -> float:
        return self.usage_pattern.estimated_infra_need.ram / (Servers.SERVER.ram.value * Server.SERVER_UTILISATION_RATE)

    def compute_servers_consumption(self) -> Quantity:
        nb_servers = math.ceil(self.number_of_servers_needed__raw)
        # TODO: Take idle time into account
        return (nb_servers * u.year * Servers.SERVER.power.value * Servers.SERVER.power_usage_effectiveness).to(u.kWh)

    def compute_servers_fabrication_footprint(self) -> Quantity:
        nb_servers = math.ceil(self.number_of_servers_needed__raw)
        servers_fab_footprint = (nb_servers * Servers.SERVER.carbon_footprint_fabrication.value
                                 * (1 * u.year / Servers.SERVER.lifespan.value))
        return servers_fab_footprint.to(u.kg)

    def compute_storage_consumption(self) -> Quantity:
        nb_of_terabytes_required = math.ceil(
            (self.usage_pattern.estimated_infra_need.storage.to(u.To) * self.data_replication_factor
             * self.data_storage_duration / u.year).magnitude) * u.To
        storage_power_during_use = ((nb_of_terabytes_required / Storages.SSD_STORAGE.storage_capacity.value)
                                    * Storages.SSD_STORAGE.power.value * Storages.SSD_STORAGE.power_usage_effectiveness)
        usage_time_per_year = (self.usage_pattern.daily_usage_window / u.day) * u.year
        return (storage_power_during_use * usage_time_per_year).to(u.kWh)

    def compute_energy_consumption(self) -> Dict[PhysicalElements, Quantity]:
        energy_consumption = self.usage_pattern.compute_energy_consumption()
        energy_consumption[PhysicalElements.SERVER] = self.compute_servers_consumption()
        energy_consumption[PhysicalElements.SSD] = self.compute_storage_consumption()

        return energy_consumption

    def compute_fabrication_emissions(self) -> Dict[PhysicalElements, Quantity]:
        fabrication_emissions = self.usage_pattern.compute_fabrication_emissions()
        fabrication_emissions[PhysicalElements.SERVER] = self.compute_servers_fabrication_footprint()

        return fabrication_emissions
