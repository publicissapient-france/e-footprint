from efootprint.constants.units import u
from efootprint.core.hardware.network import Network
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity

from typing import Dict, List, Set
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd


class System:
    def __init__(self, name: str, usage_patterns: List[UsagePattern]):
        self.name = name
        usage_pattern_names = [usage_pattern.name for usage_pattern in usage_patterns]
        if len(usage_pattern_names) != len(set(usage_pattern_names)):
            raise ValueError("You can’t have 2 usage patterns with the same name within a System")
        self._usage_patterns = usage_patterns

        self.launch_computations()

    @property
    def usage_patterns(self):
        return self._usage_patterns

    @usage_patterns.setter
    def usage_patterns(self, new_usage_patterns):
        self._usage_patterns = new_usage_patterns

        self.launch_computations()

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

    def launch_computations(self):
        for usage_pattern in self.usage_patterns:
            usage_pattern.compute_calculated_attributes()
        for device_population in self.device_populations:
            device_population.compute_calculated_attributes()
        for service in self.services:
            service.compute_calculated_attributes()
        for network in self.networks:
            network.compute_calculated_attributes()
        for server in self.servers:
            server.compute_calculated_attributes()
        for storage in self.storages:
            storage.compute_calculated_attributes()

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

    def fabrication_footprints(self) -> Dict[str, Dict[str, ExplainableQuantity]]:
        fab_footprints = {
            "Servers": {server.name: server.instances_fabrication_footprint for server in self.servers},
            "Storage": {storage.name: storage.instances_fabrication_footprint for storage in self.storages},
            "Devices": {device_population.name: device_population.instances_fabrication_footprint
                        for device_population in self.device_populations},
            "Network": {"networks": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks")}
        }

        return fab_footprints

    def energy_footprints(self) -> Dict[str, Dict[str, ExplainableQuantity]]:
        energy_footprints = {
            "Servers": {server.name: server.energy_footprint for server in self.servers},
            "Storage": {storage.name: storage.energy_footprint for storage in self.storages},
            "Devices": {device_population.name: device_population.energy_footprint
                        for device_population in self.device_populations},
            "Network": {network.name: network.energy_footprint for network in self.networks},
        }

        return energy_footprints

    def total_fabrication_footprints(self) -> Dict[str, ExplainableQuantity]:
        fab_footprints = {
            "Servers": sum(server.instances_fabrication_footprint for server in self.servers),
            "Storage": sum(storage.instances_fabrication_footprint for storage in self.storages),
            "Devices": sum(device_population.instances_fabrication_footprint
                           for device_population in self.device_populations),
            "Network": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks")
        }

        return fab_footprints

    def total_energy_footprints(self) -> Dict[str, ExplainableQuantity]:
        energy_footprints = {
            "Servers": sum(server.energy_footprint for server in self.servers),
            "Storage": sum(storage.energy_footprint for storage in self.storages),
            "Devices": sum(device_population.energy_footprint for device_population in self.device_populations),
            "Network": sum(network.energy_footprint for network in self.networks)
        }

        return energy_footprints

    def total_footprint(self) -> ExplainableQuantity:
        return (
            sum(
                sum(
                    self.fabrication_footprints()[key].values()) + sum(self.energy_footprints()[key].values())
                for key in self.fabrication_footprints().keys()
            )
        ).define_as_intermediate_calculation(f"{self.name} total carbon footprint")

    def plot_footprints(self):
        import matplotlib.pyplot as plt
        import numpy as np
        # Get the footprints
        fab_footprints = self.fabrication_footprints()
        energy_footprints = self.energy_footprints()
        categories = list(fab_footprints.keys())

        # Setup the figure and axes
        fig, ax = plt.subplots(figsize=(10, 8))
        width = 0.35  # the width of the bars
        ind = np.arange(len(categories))  # the x locations for the groups

        # Stacked bars for fabrication and energy
        for idx, category in enumerate(categories):
            fab_bottom = 0
            energy_bottom = 0

            # Sort the objects by name to maintain consistent order
            fab_objects = sorted(fab_footprints[category].items(), key=lambda x: x[0])
            energy_objects = sorted(energy_footprints[category].items(), key=lambda x: x[0])

            for (fab_name, fab_value), (energy_name, energy_value) in zip(fab_objects, energy_objects):
                # Fabrication
                fab_val = fab_value.value.magnitude
                fab_rect = ax.bar(ind[idx], fab_val, width, bottom=fab_bottom, color='blue', edgecolor='white')
                fab_bottom += fab_val

                # Label for fabrication
                height = fab_rect[0].get_height()
                ax.text(fab_rect[0].get_x() + fab_rect[0].get_width() / 2, fab_bottom - (height / 2), fab_name,
                        ha='center', va='center', color='black', fontsize=8)

                # Energy
                energy_val = energy_value.value.magnitude
                energy_rect = ax.bar(
                    ind[idx] + width, energy_val, width, bottom=energy_bottom, color='orange', edgecolor='white')
                energy_bottom += energy_val

                # Label for energy
                height = energy_rect[0].get_height()
                ax.text(energy_rect[0].get_x() + energy_rect[0].get_width() / 2, energy_bottom - (height / 2),
                        energy_name, ha='center', va='center', color='black', fontsize=8)

        # Add the legend
        ax.legend(['Fabrication', 'Electricity Consumption'], loc='upper left')

        # Set labels and titles
        ax.set_ylabel('kg CO2 emissions / Year')
        ax.set_title('Footprints by object and type')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(categories)

        # Display the plot
        plt.show()

    def plotly_express_footprints_plot(self):
        import plotly.express as px

        fab_footprints = self.fabrication_footprints()
        energy_footprints = self.energy_footprints()
        categories = list(fab_footprints.keys())

        rows_as_dicts = []

        for category in categories:
            fab_objects = sorted(fab_footprints[category].items(), key=lambda x: x[0])
            energy_objects = sorted(energy_footprints[category].items(), key=lambda x: x[0])

            for objs, color in zip([fab_objects, energy_objects], ["Fabrication", "Electricity"]):
                data_dicts = [
                    {"Type": color, "Category": category, "Object name": obj[0], "Value": obj[1].value.magnitude} for obj in objs]
                rows_as_dicts += data_dicts

        df = pd.DataFrame.from_records(rows_as_dicts)

        fig = px.bar(df, x="Category", y="Value",
                     color='Type', barmode='group',
                     height=400
                     )
        # Update hovertemplate for each trace
        for trace in fig.data:
            trace.hovertemplate = '%{customdata} <extra></extra>'

        # Add the custom hover data
        fig.update_traces(customdata=df['Object name'] + " (" + df["Value"].astype(str) + ")")

        fig.show()

    def plotly_footprints_plot(self):
        # Get the footprints
        fab_footprints = self.fabrication_footprints()
        energy_footprints = self.energy_footprints()
        categories = list(fab_footprints.keys())

        # Create an empty list to hold all the bar objects
        bars = []

        # Loop through each category to create the stacked bar chart
        for idx, category in enumerate(categories):
            fab_bottom = 0
            energy_bottom = 0

            # Sort the objects by name to maintain consistent order
            fab_objects = sorted(fab_footprints[category].items(), key=lambda x: x[0])
            energy_objects = sorted(energy_footprints[category].items(), key=lambda x: x[0])

            for (fab_name, fab_value), (energy_name, energy_value) in zip(fab_objects, energy_objects):
                # Fabrication footprint
                fab_val = fab_value.value.magnitude
                bars.append(go.Bar(
                    x=[category],
                    y=[fab_val],
                    name=f'{fab_name} Fabrication',
                    hovertext=f'{fab_name}: {fab_val:.0f} kg CO2/year',
                    marker=dict(color='blue'),
                    base=fab_bottom
                ))
                fab_bottom += fab_val

                # Energy footprint
                energy_val = energy_value.value.magnitude
                bars.append(go.Bar(
                    x=[category],
                    y=[energy_val],
                    name=f'{energy_name} Energy',
                    hovertext=f'{energy_name}: {energy_val:.2f} kg CO2/year',
                    marker=dict(color='orange'),
                    base=energy_bottom
                ))
                energy_bottom += energy_val

        # Update the layout
        layout = go.Layout(
            barmode='group',
            title='Footprints by object and type',
            xaxis=dict(title='Categories'),
            yaxis=dict(title='kg CO2 emissions / Year'),
            legend=dict(x=0.8, y=1.2, orientation="h"),
            hovermode='x'
        )

        fig = go.Figure(data=bars, layout=layout)
        plot(fig, filename='footprints.html')


if __name__ == "__main__":
    import plotly.graph_objects as go
    import pandas as pd

    import plotly.express as px

    df = px.data.tips()

    # Create a new column for custom hover text
    df['hover_text'] = df['day'] + ', ' + df['time'] + ' (' + df['sex'] + ')'

    # Create the bar graph
    fig = px.bar(df, x="sex", y="total_bill",
                 color='smoker', barmode='group',
                 height=400)

    # Update hovertemplate for each trace
    for trace in fig.data:
        trace.hovertemplate = '%{customdata} <extra></extra>'

    # Add the custom hover data
    fig.update_traces(customdata=df['hover_text'])

    fig.show()
