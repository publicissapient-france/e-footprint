from footprint_model.constants.units import u
from footprint_model.constants.physical_elements import PhysicalElements, Servers, Server, Storages
from footprint_model.core.usage_pattern import UsagePattern
from footprint_model.utils.tools import round_dict
from footprint_model.utils.plot_utils import plot_emissions
from footprint_model.constants.files import PDF_EXPORTS
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation

from typing import Dict, List
from pint import Quantity
import math
import matplotlib.pyplot as plt
import os


class System:
    def __init__(self, name: str, usage_patterns: List[UsagePattern], data_replication_factor: int,
                 data_storage_duration: Quantity, cloud: bool):
        self.name = name
        usage_pattern_names = [usage_pattern.name for usage_pattern in usage_patterns]
        if len(usage_pattern_names) != len(set(usage_pattern_names)):
            raise ValueError("You can’t have 2 usage patterns with the same name within a System")
        self.usage_patterns = usage_patterns
        self.data_replication_factor = ExplainableQuantity(
            data_replication_factor * u.dimensionless, f"Data replication factor of {self.name}")
        if not data_storage_duration.check("[time]"):
            raise ValueError("Variable 'data_storage_duration' does not have time dimensionality")
        self.data_storage_duration = ExplainableQuantity(data_storage_duration, f"Data storage duration of {self.name}")
        self.cloud = cloud

    @property
    def nb_of_servers_required(self) -> Dict[UsagePattern, float]:
        nb_of_servers_required = {}
        for usage_pattern in self.usage_patterns:
            nb_of_servers_required_up__raw = (
                    usage_pattern.estimated_infra_need.ram
                    / (Servers.SERVER.ram * Server.server_utilization_rate(self.cloud))
            )
            if not self.cloud and (
                    int(nb_of_servers_required_up__raw.magnitude) != nb_of_servers_required_up__raw.magnitude):
                nb_of_servers_required_up = nb_of_servers_required_up__raw + ExplainableQuantity(
                    (math.ceil(nb_of_servers_required_up__raw.magnitude) - nb_of_servers_required_up__raw.magnitude)
                    * u.dimensionless, "Extra server capacity because number of servers must be an integer")
            else:
                nb_of_servers_required_up = nb_of_servers_required_up__raw
            nb_of_servers_required[usage_pattern] = nb_of_servers_required_up.define_as_intermediate_calculation(
                f"Nb of servers required for {usage_pattern.name}")
        return nb_of_servers_required

    @property
    def storage_required(self) -> Dict[UsagePattern, ExplainableQuantity]:
        storage_required = {}
        for usage_pattern in self.usage_patterns:
            storage_required[usage_pattern] = (
                    usage_pattern.estimated_infra_need.storage.to(u.To / u.year)
                    * self.data_replication_factor * self.data_storage_duration
            ).define_as_intermediate_calculation(f"Storage required for {usage_pattern.name}")
        return storage_required

    def compute_servers_consumption(self) -> Dict[UsagePattern, ExplainableQuantity]:
        servers_consumption = {}
        nb_of_servers_required = self.nb_of_servers_required
        for usage_pattern in self.usage_patterns:
            effective_power = Servers.SERVER.power * Servers.SERVER.power_usage_effectiveness
            if self.cloud:
                servers_consumption_up = (
                        nb_of_servers_required[usage_pattern] * effective_power
                        * (
                                usage_pattern.usage_time_fraction
                                + (usage_pattern.non_usage_time_fraction / Server.CLOUD_DOWNSCALING_FACTOR)
                        )
                ).to(u.kWh / u.year)
            else:
                # TODO: Take idle time into account
                servers_consumption_up = (
                        effective_power * nb_of_servers_required[usage_pattern]).to(u.kWh / u.year)
            servers_consumption[usage_pattern] = servers_consumption_up.define_as_intermediate_calculation(
                    f"Server energy consumption of {usage_pattern.name}")
        return servers_consumption

    def compute_servers_fabrication_footprint(self) -> Dict[UsagePattern, ExplainableQuantity]:
        servers_fabrication_footprint = {}
        nb_of_servers_required = self.nb_of_servers_required
        for usage_pattern in self.usage_patterns:
            if self.cloud:
                servers_fab_footprint_up = (
                    nb_of_servers_required[usage_pattern] * Servers.SERVER.carbon_footprint_fabrication
                    * (
                            usage_pattern.usage_time_fraction
                            + (usage_pattern.non_usage_time_fraction / Server.CLOUD_DOWNSCALING_FACTOR)
                    )
                    / Servers.SERVER.lifespan
                ).to(u.kg / u.year)
            else:
                servers_fab_footprint_up = (
                        Servers.SERVER.carbon_footprint_fabrication * nb_of_servers_required[usage_pattern]
                        / Servers.SERVER.lifespan).to(u.kg / u.year)
            servers_fabrication_footprint[usage_pattern] = servers_fab_footprint_up.define_as_intermediate_calculation(
                f"Server fabrication emissions of {usage_pattern.name}")
        return servers_fabrication_footprint

    def compute_storage_consumption(self) -> Dict[UsagePattern, ExplainableQuantity]:
        storage_consumption = {}
        storage_required = self.storage_required
        for usage_pattern in self.usage_patterns:
            storage_power_during_use = (Storages.SSD_STORAGE.power * Storages.SSD_STORAGE.power_usage_effectiveness
                                        * (storage_required[usage_pattern]
                                           / Storages.SSD_STORAGE.storage_capacity))
            storage_consumption[usage_pattern] = (storage_power_during_use * usage_pattern.usage_time_fraction).to(
                u.kWh / u.year).define_as_intermediate_calculation(
                f"Storage energy consumption of {usage_pattern.name}")
        return storage_consumption

    def compute_storage_fabrication_footprint(self) -> Dict[UsagePattern, ExplainableQuantity]:
        storage_fabrication_footprint = {}
        storage_required = self.storage_required
        for usage_pattern in self.usage_patterns:
            storage_fabrication_footprint[usage_pattern] = (
                    storage_required[usage_pattern]
                    * (Storages.SSD_STORAGE.carbon_footprint_fabrication / Storages.SSD_STORAGE.storage_capacity)
                    / Storages.SSD_STORAGE.lifespan).define_as_intermediate_calculation(
                    f"Storage fabrication emissions of {usage_pattern.name}")
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
                        energy_consumption[key] * usage_pattern.population.country.average_carbon_intensity).to(
                    u.kg / u.year).define_as_intermediate_calculation(
                    f"CO2 emissions from electricity use of {key} in {usage_pattern.name}")
            energy_emissions[usage_pattern] = round_dict(output_dict, 1)

        return energy_emissions

    def plot_emissions(self, export_file, rounding_value=0, timespan=1 * u.year, return_fig_for_streamlit=True):
        timespan = ExplainableQuantity(timespan, "Study timespan")
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
                rounding_value,
                timespan)
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
                    rounding_value,
                    timespan
                )
            total_energy_emissions = {
                key: sum(d[key] for d in energy_emissions.values())
                for key in energy_emissions[self.usage_patterns[0]].keys()}
            total_fabrication_emissions = {
                key: sum(d[key] for d in fabrication_emissions.values())
                for key in fabrication_emissions[self.usage_patterns[0]].keys()}
            plot_emissions(
                axs[-2], [total_energy_emissions, total_fabrication_emissions],
                ["Electricity consumption", "Fabrication"], title="Total emissions", rounding_value=0,
                timespan=timespan)
            total_emissions_by_up_dict = {
                up.name: (
                        (sum(fabrication_emissions[up].values()) + sum(energy_emissions[up].values())) * timespan
                ).value.magnitude
                for up in fabrication_emissions.keys()}
            axs[-1].pie(
                list(total_emissions_by_up_dict.values()), labels=list(total_emissions_by_up_dict.keys()),
                autopct='%1.0f%%')
            axs[-1].set_title("Emissions distribution", fontsize=24, fontweight="bold")
        fig.tight_layout()

        if return_fig_for_streamlit:
            return fig
        else:
            plt.savefig(os.path.join(PDF_EXPORTS, export_file))
            plt.show()
