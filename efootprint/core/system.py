from efootprint.constants.units import u
from efootprint.core.hardware.network import Network
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.hardware.storage import Storage
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity

from typing import Dict, List, Set


class System:
    def __init__(self, name: str, usage_patterns: List[UsagePattern]):
        self.name = name
        usage_pattern_names = [usage_pattern.name for usage_pattern in usage_patterns]
        if len(usage_pattern_names) != len(set(usage_pattern_names)):
            raise ValueError("You can’t have 2 usage patterns with the same name within a System")
        self.usage_patterns = usage_patterns

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

    def fabrication_footprints(self) -> Dict[str, ExplainableQuantity]:
        fab_footprints = {
            "Servers": sum(server.instances_fabrication_footprint for server in self.servers),
            "Storage": sum(storage.instances_fabrication_footprint for storage in self.storages),
            "Devices": sum(device_population.instances_fabrication_footprint
                           for device_population in self.device_populations),
            "Network": ExplainableQuantity(0 * u.kg / u.year, "No fabrication footprint for networks")
        }

        return fab_footprints

    def energy_footprints(self) -> Dict[str, ExplainableQuantity]:
        energy_footprints = {
            "Servers": sum(server.energy_footprint for server in self.servers),
            "Storage": sum(storage.energy_footprint for storage in self.storages),
            "Devices": sum(device_population.energy_footprint for device_population in self.device_populations),
            "Network": sum(network.energy_footprint for network in self.networks)
        }

        return energy_footprints

    def total_footprint(self) -> ExplainableQuantity:
        return (sum(self.fabrication_footprints().values()) + sum(self.energy_footprints().values())
                ).define_as_intermediate_calculation(f"{self.name} total carbon footprint")
