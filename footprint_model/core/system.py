from footprint_model.constants.units import u
from footprint_model.constants.countries import Country
from footprint_model.constants.physical_elements import Device, Network, PhysicalElements, Devices, Networks
from footprint_model.core.user_journey import UserJourney

from dataclasses import dataclass
from typing import Dict
from pint import Quantity


@dataclass
class Population:
    name: str
    nb_users: float
    country: Country


@dataclass
class UsagePattern:
    user_journey: UserJourney
    population: Population
    # TODO: attach fraction of use to device type
    frac_smartphone: float
    frac_mobile_network_for_smartphones: float
    nb_visits_per_user_per_year: int

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


@dataclass
class System:
    # TODO: a list of UsagePattern could be considered afterwards
    usage_pattern: UsagePattern
    data_replication_factor: int
    data_storage_duration: int
