from footprint_model.constants.units import u
from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import (Device, Network, PhysicalElements, Devices, Networks, Servers,
                                                         Server, Storages)
from footprint_model.core.user_journey import UserJourney
from footprint_model.utils.tools import round_dict
from footprint_model.utils.plot_utils import plot_emissions

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
                Devices.SMARTPHONE, self.frac_smartphone).to(u.kWh),
            PhysicalElements.LAPTOP: self.compute_device_consumption(
                Devices.LAPTOP, self.frac_laptop).to(u.kWh),
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
                Devices.SMARTPHONE, self.frac_smartphone).to(u.kg),
            PhysicalElements.LAPTOP: self.compute_device_fabrication_footprint(
                Devices.LAPTOP, self.frac_laptop).to(u.kg),
            PhysicalElements.BOX: self.compute_device_fabrication_footprint(
                Devices.BOX, self.wifi_usage_fraction).to(u.kg),
            PhysicalElements.SCREEN: self.compute_device_fabrication_footprint(
                Devices.SCREEN, self.frac_laptop * Devices.FRACTION_OF_LAPTOPS_EQUIPED_WITH_SCREEN).to(u.kg),
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
    cloud: bool

    def __post_init__(self):
        if not self.data_storage_duration.check("[time]"):
            raise ValueError("Variable 'data_storage_duration' does not have time dimensionality")

    @property
    def nb_of_servers_required__raw(self) -> float:
        return (self.usage_pattern.estimated_infra_need.ram
                / (Servers.SERVER.ram * Server.server_utilization_rate(self.cloud)))

    @property
    def nb_of_terabytes_required(self) -> Quantity:
        return math.ceil(
            (self.usage_pattern.estimated_infra_need.storage.to(u.To)
             * self.data_replication_factor * self.data_storage_duration / u.year).magnitude
        ) * u.To

    def compute_servers_consumption(self) -> Quantity:
        if self.cloud:
            nb_servers = self.nb_of_servers_required__raw
            duration_per_year_at_100_percent = (self.usage_pattern.daily_usage_window / u.day) * u.year
            duration_per_year_downscaled = 1 * u.year - duration_per_year_at_100_percent
            effective_power = Servers.SERVER.power * Servers.SERVER.power_usage_effectiveness
            return (
                    nb_servers * effective_power
                    * (
                            duration_per_year_at_100_percent
                            + (duration_per_year_downscaled / Server.CLOUD_DOWNSCALING_FACTOR)
                    )
            ).to(u.kWh)
        else:
            nb_servers = math.ceil(self.nb_of_servers_required__raw)
            # TODO: Take idle time into account
            return (Servers.SERVER.power * Servers.SERVER.power_usage_effectiveness * nb_servers * u.year).to(u.kWh)

    def compute_servers_fabrication_footprint(self) -> Quantity:
        if self.cloud:
            nb_servers = self.nb_of_servers_required__raw
            duration_per_year_at_100_percent = (self.usage_pattern.daily_usage_window / u.day) * u.year
            duration_per_year_downscaled = 1 * u.year - duration_per_year_at_100_percent
            return (
                nb_servers * Servers.SERVER.carbon_footprint_fabrication.value
                * (
                        duration_per_year_at_100_percent
                        + (duration_per_year_downscaled / Server.CLOUD_DOWNSCALING_FACTOR)
                )
                / Servers.SERVER.lifespan.value
            ).to(u.kg)
        else:
            nb_servers = math.ceil(self.nb_of_servers_required__raw)
            servers_fab_footprint = (Servers.SERVER.carbon_footprint_fabrication * nb_servers
                                     * (1 * u.year / Servers.SERVER.lifespan.value))
            return servers_fab_footprint.to(u.kg)

    def compute_storage_consumption(self) -> Quantity:
        storage_power_during_use = (Storages.SSD_STORAGE.power * Storages.SSD_STORAGE.power_usage_effectiveness
                                    * (self.nb_of_terabytes_required / Storages.SSD_STORAGE.storage_capacity.value))
        usage_time_per_year = (self.usage_pattern.daily_usage_window / u.day) * u.year
        return (storage_power_during_use * usage_time_per_year).to(u.kWh)

    def compute_storage_fabrication_footprint(self) -> Quantity:
        return (self.nb_of_terabytes_required
                * (Storages.SSD_STORAGE.carbon_footprint_fabrication / Storages.SSD_STORAGE.storage_capacity)
                * 1 * u.year / Storages.SSD_STORAGE.lifespan.value)

    def compute_energy_consumption(self) -> Dict[PhysicalElements, Quantity]:
        energy_consumption = self.usage_pattern.compute_energy_consumption()
        energy_consumption[PhysicalElements.SERVER] = self.compute_servers_consumption()
        energy_consumption[PhysicalElements.SSD] = self.compute_storage_consumption()

        return round_dict(energy_consumption, 1)

    def compute_fabrication_emissions(self) -> Dict[PhysicalElements, Quantity]:
        fabrication_emissions = self.usage_pattern.compute_fabrication_emissions()
        fabrication_emissions[PhysicalElements.SERVER] = self.compute_servers_fabrication_footprint()
        fabrication_emissions[PhysicalElements.SSD] = self.compute_storage_fabrication_footprint()

        return round_dict(fabrication_emissions, 1)

    def compute_energy_emissions(self):
        output_dict = {}
        energy_consumption = self.compute_energy_consumption()
        for key in energy_consumption:
            output_dict[key] = (
                    energy_consumption[key] * self.usage_pattern.population.country.average_carbon_intensity).to(u.kg)
        return round_dict(output_dict, 1)

    def plot_emissions(self):
        plot_emissions([self.compute_energy_emissions(), self.compute_fabrication_emissions()],
                       ["Electricity consumption", "Fabrication"])
