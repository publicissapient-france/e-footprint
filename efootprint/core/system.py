from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.constants.units import u
from efootprint.core.hardware.network import Network
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.usage.user_journey import UserJourney
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.utils.tools import format_co2_amount, display_co2_amount

from typing import Dict, List, Set
import plotly.express as px
import plotly
import pandas as pd


class System(ModelingObject):
    def __init__(self, name: str, usage_patterns: List[UsagePattern]):
        super().__init__(name)
        self.usage_patterns = usage_patterns

    @property
    def user_journeys(self) -> List[UserJourney]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update({usage_pattern.user_journey})

        return list(output_set)

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self):
        return self.user_journeys

    def after_init(self):
        self.init_has_passed = True
        self.launch_attributes_computation_chain()

    @property
    def servers(self) -> List[Server]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update(usage_pattern.user_journey.servers)

        return list(output_set)

    @property
    def storages(self) -> List[Storage]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update(usage_pattern.user_journey.storages)

        return list(output_set)

    @property
    def services(self) -> List[Service]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update(usage_pattern.user_journey.services)

        return list(output_set)

    @property
    def device_populations(self) -> List[DevicePopulation]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update({usage_pattern.device_population})

        return list(output_set)

    @property
    def networks(self) -> List[Network]:
        output_set = set()
        for usage_pattern in self.usage_patterns:
            output_set.update({usage_pattern.network})

        return list(output_set)

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
            "Devices": {device_population.name: device_population.instances_fabrication_footprint
                        for device_population in self.device_populations},
            "Network": {"networks": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks")}
        }

        return fab_footprints

    @property
    def energy_footprints(self) -> Dict[str, Dict[str, ExplainableQuantity]]:
        energy_footprints = {
            "Servers": {server.name: server.energy_footprint for server in self.servers},
            "Storage": {storage.name: storage.energy_footprint for storage in self.storages},
            "Devices": {device_population.name: device_population.energy_footprint
                        for device_population in self.device_populations},
            "Network": {network.name: network.energy_footprint for network in self.networks},
        }

        return energy_footprints

    @property
    def total_fabrication_footprints(self) -> Dict[str, ExplainableQuantity]:
        fab_footprints = {
            "Servers": sum(server.instances_fabrication_footprint for server in self.servers),
            "Storage": sum(storage.instances_fabrication_footprint for storage in self.storages),
            "Devices": sum(device_population.instances_fabrication_footprint
                           for device_population in self.device_populations),
            "Network": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks")
        }

        return fab_footprints

    @property
    def total_energy_footprints(self) -> Dict[str, ExplainableQuantity]:
        energy_footprints = {
            "Servers": sum(server.energy_footprint for server in self.servers),
            "Storage": sum(storage.energy_footprint for storage in self.storages),
            "Devices": sum(device_population.energy_footprint for device_population in self.device_populations),
            "Network": sum(network.energy_footprint for network in self.networks)
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
            filename = f"{self.name} footprints"

        plotly.offline.plot(fig, filename=filename, auto_open=False)
