from footprint_model.constants.units import u
from footprint_model.constants.physical_elements import PhysicalElements, Servers, Server, Storages
from footprint_model.core.usage_pattern import UsagePattern
from footprint_model.utils.tools import round_dict
from footprint_model.utils.plot_utils import plot_emissions
from footprint_model.constants.files import PDF_EXPORTS

from dataclasses import dataclass
from typing import Dict, List
from pint import Quantity
import math
import matplotlib.pyplot as plt
import os


@dataclass
class System:
    # TODO: a list of UsagePattern could be considered afterwards
    usage_patterns: List[UsagePattern]
    data_replication_factor: int
    data_storage_duration: Quantity
    cloud: bool

    def __post_init__(self):
        if not self.data_storage_duration.check("[time]"):
            raise ValueError("Variable 'data_storage_duration' does not have time dimensionality")
        usage_pattern_names = [usage_pattern.name for usage_pattern in self.usage_patterns]
        if len(usage_pattern_names) != len(set(usage_pattern_names)):
            raise ValueError("You can’t have 2 usage patterns with the same name within a System")

    @property
    def nb_of_servers_required__raw(self) -> Dict[UsagePattern, float]:
        nb_of_servers_required = {}
        for usage_pattern in self.usage_patterns:
            nb_of_servers_required[usage_pattern] = (
                    usage_pattern.estimated_infra_need.ram
                    / (Servers.SERVER.ram * Server.server_utilization_rate(self.cloud)))
        return nb_of_servers_required

    @property
    def nb_of_terabytes_required(self) -> Dict[UsagePattern, Quantity]:
        nb_of_terabytes_required = {}
        for usage_pattern in self.usage_patterns:
            nb_of_terabytes_required[usage_pattern] = math.ceil(
                (usage_pattern.estimated_infra_need.storage.to(u.To)
                 * self.data_replication_factor * self.data_storage_duration / u.year).magnitude) * u.To
        return nb_of_terabytes_required

    def compute_servers_consumption(self) -> Dict[UsagePattern, Quantity]:
        servers_consumption = {}
        nb_of_servers_required__raw = self.nb_of_servers_required__raw
        for usage_pattern in self.usage_patterns:
            if self.cloud:
                nb_servers = nb_of_servers_required__raw[usage_pattern]
                duration_per_year_at_100_percent = (usage_pattern.daily_usage_window / u.day) * u.year
                duration_per_year_downscaled = 1 * u.year - duration_per_year_at_100_percent
                effective_power = Servers.SERVER.power * Servers.SERVER.power_usage_effectiveness
                servers_consumption[usage_pattern] = (
                        nb_servers * effective_power
                        * (
                                duration_per_year_at_100_percent
                                + (duration_per_year_downscaled / Server.CLOUD_DOWNSCALING_FACTOR)
                        )
                ).to(u.kWh)
            else:
                nb_servers = math.ceil(nb_of_servers_required__raw[usage_pattern])
                # TODO: Take idle time into account
                servers_consumption[usage_pattern] = (
                        Servers.SERVER.power * Servers.SERVER.power_usage_effectiveness * nb_servers * u.year).to(u.kWh)
        return servers_consumption

    def compute_servers_fabrication_footprint(self) -> Dict[UsagePattern, Quantity]:
        servers_fabrication_footprint = {}
        nb_of_servers_required__raw = self.nb_of_servers_required__raw
        for usage_pattern in self.usage_patterns:
            if self.cloud:
                nb_servers = nb_of_servers_required__raw[usage_pattern]
                duration_per_year_at_100_percent = (usage_pattern.daily_usage_window / u.day) * u.year
                duration_per_year_downscaled = 1 * u.year - duration_per_year_at_100_percent
                servers_fabrication_footprint[usage_pattern] = (
                    nb_servers * Servers.SERVER.carbon_footprint_fabrication.value
                    * (
                            duration_per_year_at_100_percent
                            + (duration_per_year_downscaled / Server.CLOUD_DOWNSCALING_FACTOR)
                    )
                    / Servers.SERVER.lifespan.value
                ).to(u.kg)
            else:
                nb_servers = math.ceil(nb_of_servers_required__raw[usage_pattern])
                servers_fab_footprint = (Servers.SERVER.carbon_footprint_fabrication * nb_servers
                                         * (1 * u.year / Servers.SERVER.lifespan.value))
                servers_fabrication_footprint[usage_pattern] = servers_fab_footprint.to(u.kg)
        return servers_fabrication_footprint

    def compute_storage_consumption(self) -> Dict[UsagePattern, Quantity]:
        storage_consumption = {}
        nb_of_terabytes_required = self.nb_of_terabytes_required
        for usage_pattern in self.usage_patterns:
            storage_power_during_use = (Storages.SSD_STORAGE.power * Storages.SSD_STORAGE.power_usage_effectiveness
                                        * (nb_of_terabytes_required[usage_pattern]
                                           / Storages.SSD_STORAGE.storage_capacity.value))
            usage_time_per_year = (usage_pattern.daily_usage_window / u.day) * u.year
            storage_consumption[usage_pattern] = (storage_power_during_use * usage_time_per_year).to(u.kWh)
        return storage_consumption

    def compute_storage_fabrication_footprint(self) -> Dict[UsagePattern, Quantity]:
        storage_fabrication_footprint = {}
        nb_of_terabytes_required = self.nb_of_terabytes_required
        for usage_pattern in self.usage_patterns:
            storage_fabrication_footprint[usage_pattern] = (
                    nb_of_terabytes_required[usage_pattern]
                    * (Storages.SSD_STORAGE.carbon_footprint_fabrication / Storages.SSD_STORAGE.storage_capacity)
                    * 1 * u.year / Storages.SSD_STORAGE.lifespan.value)
        return storage_fabrication_footprint

    def compute_energy_consumption(self) -> Dict[UsagePattern, Dict[PhysicalElements, Quantity]]:
        energy_consumptions = {}
        servers_consumption = self.compute_servers_consumption()
        storage_consumption = self.compute_storage_consumption()
        for usage_pattern in self.usage_patterns:
            up_energy_consumption = usage_pattern.compute_energy_consumption()
            up_energy_consumption[PhysicalElements.SERVER] = servers_consumption[usage_pattern]
            up_energy_consumption[PhysicalElements.SSD] = storage_consumption[usage_pattern]
            energy_consumptions[usage_pattern] = round_dict(up_energy_consumption, 1)

        return energy_consumptions

    def compute_fabrication_emissions(self) -> Dict[UsagePattern, Dict[PhysicalElements, Quantity]]:
        fabrication_emissions = {}
        servers_fabrication_footprint = self.compute_servers_fabrication_footprint()
        storage_fabrication_footprint = self.compute_storage_fabrication_footprint()
        for usage_pattern in self.usage_patterns:
            up_fabrication_emissions = usage_pattern.compute_fabrication_emissions()
            up_fabrication_emissions[PhysicalElements.SERVER] = servers_fabrication_footprint[usage_pattern]
            up_fabrication_emissions[PhysicalElements.SSD] = storage_fabrication_footprint[usage_pattern]

            fabrication_emissions[usage_pattern] = round_dict(up_fabrication_emissions, 1)

        return fabrication_emissions

    def compute_energy_emissions(self) -> Dict[UsagePattern, Dict[PhysicalElements, Quantity]]:
        up_energy_consumption = self.compute_energy_consumption()
        energy_emissions = {}
        for usage_pattern in self.usage_patterns:
            output_dict = {}
            energy_consumption = up_energy_consumption[usage_pattern]
            for key in energy_consumption:
                output_dict[key] = (
                        energy_consumption[key] * usage_pattern.population.country.average_carbon_intensity).to(u.kg)
            energy_emissions[usage_pattern] = round_dict(output_dict, 1)

        return energy_emissions

    def plot_emissions(self, export_file, rounding_value=0):
        energy_emissions = self.compute_energy_emissions()
        fabrication_emissions = self.compute_fabrication_emissions()
        if len(self.usage_patterns) == 1:
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))
            usage_pattern = self.usage_patterns[0]
            plot_emissions(
                ax,
                [energy_emissions[usage_pattern], fabrication_emissions[usage_pattern]],
                ["Electricity consumption", "Fabrication"],
                usage_pattern.name,
                rounding_value)
        else:
            nb_rows = len(self.usage_patterns) + 2
            fig, axs = plt.subplots(nrows=nb_rows, ncols=1, figsize=(12, 6 * nb_rows))
            for ax, usage_pattern in zip(axs[:-2], self.usage_patterns):
                plot_emissions(
                    ax,
                    [energy_emissions[usage_pattern], fabrication_emissions[usage_pattern]
                     ],
                    ["Electricity consumption", "Fabrication"],
                    usage_pattern.name,
                    rounding_value
                )
            total_energy_emissions = {
                key: sum(d[key] for d in energy_emissions.values())
                for key in energy_emissions[self.usage_patterns[0]].keys()}
            total_fabrication_emissions = {
                key: sum(d[key] for d in fabrication_emissions.values())
                for key in fabrication_emissions[self.usage_patterns[0]].keys()}
            plot_emissions(
                axs[-2], [total_energy_emissions, total_fabrication_emissions],
                ["Electricity consumption", "Fabrication"], title="Total emissions", rounding_value=0)
            total_emissions_by_up_dict = {
                up.name: (sum(fabrication_emissions[up].values()) + sum(energy_emissions[up].values())).magnitude / 1000
                for up in fabrication_emissions.keys()}
            axs[-1].pie(
                list(total_emissions_by_up_dict.values()), labels=list(total_emissions_by_up_dict.keys()),
                autopct='%1.0f%%')
            axs[-1].set_title("Emissions distribution", fontsize=24, fontweight="bold")
        fig.tight_layout()
        plt.savefig(os.path.join(PDF_EXPORTS, export_file))
        plt.show()
