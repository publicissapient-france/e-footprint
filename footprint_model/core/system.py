from footprint_model.constants.units import u
from footprint_model.core.network import Network
from footprint_model.core.device_population import DevicePopulation
from footprint_model.core.server import Server
from footprint_model.core.storage import Storage
from footprint_model.core.usage_pattern import UsagePattern
from footprint_model.constants.explainable_quantities import ExplainableQuantity

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

    def fabrication_footprints(self) -> Dict[str, ExplainableQuantity]:
        fab_footprints = {
            "Servers": sum(server.instances_fabrication_footprint for server in self.servers),
            "Storage": sum(storage.instances_fabrication_footprint for storage in self.storages),
            "Devices": sum(device_population.fabrication_footprint for device_population in self.device_populations),
            "Network": ExplainableQuantity(0 * u.kg / u.year)
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
