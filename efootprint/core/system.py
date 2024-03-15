from matplotlib import pyplot as plt

from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.constants.units import u
from efootprint.core.hardware.network import Network
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.utils.plot_emission_diffs import EmissionPlotter
from efootprint.utils.tools import format_co2_amount, display_co2_amount

from typing import Dict, List, Set
import plotly.express as px
import plotly
import pandas as pd
from IPython.display import HTML


class System(ModelingObject):
    def __init__(self, name: str, usage_patterns: List[UsagePattern]):
        super().__init__(name)
        self.usage_patterns = usage_patterns
        self.previous_change = None
        self.previous_total_energy_footprints = None
        self.previous_total_fabrication_footprints = None
        self.all_changes = []
        self.initial_total_energy_footprints = None
        self.initial_total_fabrication_footprints = None

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self):
        return self.usage_patterns

    @property
    def systems(self) -> List:
        return []

    def after_init(self):
        self.init_has_passed = True
        self.launch_attributes_computation_chain()
        self.initial_total_energy_footprints = self.total_energy_footprints
        self.initial_total_fabrication_footprints = self.total_fabrication_footprints

    @property
    def servers(self) -> Set[Server]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update(usage_pattern.user_journey.servers)

        return output_set

    @property
    def storages(self) -> Set[Storage]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update(usage_pattern.user_journey.storages)

        return output_set

    @property
    def services(self) -> Set[Service]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update(usage_pattern.user_journey.services)

        return output_set

    @property
    def device_populations(self) -> Set[DevicePopulation]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update({usage_pattern.device_population})

        return output_set

    @property
    def networks(self) -> Set[Network]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update({usage_pattern.network})

        return output_set

    def get_storage_by_name(self, storage_name) -> Storage:
        for storage in self.storages:
            if storage.name == storage_name:
                return storage

    def get_server_by_name(self, server_name) -> Server:
        for server in self.servers:
            if server.name == server_name:
                return server

    def get_usage_pattern_by_name(self, usage_pattern_name) -> UsagePattern:
        for usage_pattern in self.usage_patterns:
            if usage_pattern.name == usage_pattern_name:
                return usage_pattern

    @property
    def fabrication_footprints(self) -> Dict[str, Dict[str, ExplainableQuantity]]:
        fab_footprints = {
            "Servers": {server.name: server.instances_fabrication_footprint for server in self.servers},
            "Storage": {storage.name: storage.instances_fabrication_footprint for storage in self.storages},
            "Network": {"networks": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks")},
            "Devices": {device_population.name: device_population.instances_fabrication_footprint
                        for device_population in self.device_populations},
        }

        return fab_footprints

    @property
    def energy_footprints(self) -> Dict[str, Dict[str, ExplainableQuantity]]:
        energy_footprints = {
            "Servers": {server.name: server.energy_footprint for server in self.servers},
            "Storage": {storage.name: storage.energy_footprint for storage in self.storages},
            "Network": {network.name: network.energy_footprint for network in self.networks},
            "Devices": {device_population.name: device_population.energy_footprint
                        for device_population in self.device_populations},
        }

        return energy_footprints

    @property
    def total_fabrication_footprints(self) -> Dict[str, ExplainableQuantity]:
        fab_footprints = {
            "Servers": sum(server.instances_fabrication_footprint for server in self.servers),
            "Storage": sum(storage.instances_fabrication_footprint for storage in self.storages),
            "Network": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks"),
            "Devices": sum(device_population.instances_fabrication_footprint
                           for device_population in self.device_populations)
        }

        return fab_footprints

    @property
    def total_energy_footprints(self) -> Dict[str, ExplainableQuantity]:
        energy_footprints = {
            "Servers": sum(server.energy_footprint for server in self.servers),
            "Storage": sum(storage.energy_footprint for storage in self.storages),
            "Network": sum(network.energy_footprint for network in self.networks),
            "Devices": sum(device_population.energy_footprint for device_population in self.device_populations)
        }

        return energy_footprints

    @property
    def total_footprint(self):
        return (
            sum(
                sum(
                    self.fabrication_footprints[key].values()) + sum(self.energy_footprints[key].values())
                for key in self.fabrication_footprints.keys()
            )
        ).set_label(f"{self.name} total carbon footprint")

    def plot_footprints_by_category_and_object(self, filename=None):
        fab_footprints = self.fabrication_footprints
        energy_footprints = self.energy_footprints
        categories = list(fab_footprints.keys())

        rows_as_dicts = []

        value_colname = "Carbon footprints in tons CO2eq / year"
        for category in categories:
            fab_objects = sorted(fab_footprints[category].items(), key=lambda x: x[0])
            energy_objects = sorted(energy_footprints[category].items(), key=lambda x: x[0])

            for objs, color in zip([energy_objects, fab_objects], ["Electricity", "Fabrication"]):
                data_dicts = [
                    {"Type": color, "Category": category, "Object": obj[0],
                     value_colname: obj[1].value.magnitude / 1000,
                     "Amount": f"{display_co2_amount(format_co2_amount(obj[1].value.magnitude))} / year"}
                    for obj in objs]
                rows_as_dicts += data_dicts

        df = pd.DataFrame.from_records(rows_as_dicts)

        total_co2 = df[value_colname].sum()

        fig = px.bar(
            df, x="Category", y=value_colname, color='Type', barmode='group', height=400,
            hover_data={"Type": False, "Category": False, "Object": True, value_colname: False, "Amount": True},
            template="plotly_white", width=800,
            title=f"Total CO2 emissions from {self.name}: {display_co2_amount(format_co2_amount(total_co2 * 1000))} / year")

        total_co2_per_category_and_type = df.groupby(["Category", "Type"])[value_colname].sum()

        for category, source_type in total_co2_per_category_and_type.keys():
            height = total_co2_per_category_and_type.loc[category, source_type]
            x_shift_direction = 1 if source_type == 'Fabrication' else -1

            fig.add_annotation(
                x=category,
                y=height,
                text=f"{int((height / total_co2) * 100)}%",  # Format the label as a percentage
                showarrow=False,
                yshift=10,  # Shift the label slightly above the stack
                xshift=30 * x_shift_direction
            )

        if filename is None:
            filename = f"{self.name} footprints.html"

        plotly.offline.plot(fig, filename=filename, auto_open=False)

        return HTML(filename)

    def plot_emission_diffs(self, filepath=None, figsize=(10, 5), from_start=False, plt_show=False):
        if self.previous_change is None:
            raise ValueError(
                f"There has been no change to the system yet so no diff to plot.\n"
                f"Use System.plot_footprints_by_category_and_object() to visualize footprints")

        if from_start and len(self.all_changes) > 1:
            changes_list = "\n- ".join([change.replace('changed', 'changing') for change in self.all_changes])
            print(f"Plotting the impact of:\n\n- {changes_list}")
            emissions_dict__old = [self.initial_total_energy_footprints, self.initial_total_fabrication_footprints]
        else:
            print(f"Plotting the impact of {self.previous_change.replace('changed', 'changing')}")
            emissions_dict__old = [self.previous_total_energy_footprints, self.previous_total_fabrication_footprints]

        emissions_dict__new = [self.total_energy_footprints, self.total_fabrication_footprints]

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)

        EmissionPlotter(
            ax, emissions_dict__old, emissions_dict__new, title=self.name, rounding_value=1,
            timespan=ExplainableQuantity(1 * u.year, "one year")).plot_emission_diffs()

        if filepath is not None:
            plt.savefig(filepath, bbox_inches='tight')

        if plt_show:
            plt.show()
