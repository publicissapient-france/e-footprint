from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.utils.graph_tools import WIDTH, HEIGHT, set_string_max_width
from efootprint.utils.tools import convert_to_list

from pyvis.network import Network

COLOR_MAP = {
    "Autoscaling": "brown",
    "OnPremise": "brown",
    "Serverless": "brown",
    "Hardware": "brown",
    "Storage": "brown",
    "Service": "blue",
    "UsagePattern": "green",
    "DevicePopulation": "brown",
    "UserJourney": "green",
    "UserJourneyStep": "green",
    "TimeIntervals": "green",
}

USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE = [
    "System", "TimeIntervals", "Network", "Hardware", "Country"]
SERVICES_VIEW_CLASSES_TO_IGNORE = [
    "System", "UsagePattern", "TimeIntervals", "Network", "Server", "Storage", "Hardware", "DevicePopulation"]
SERVICES_AND_INFRA_VIEW_CLASSES_TO_IGNORE = [
    "UsagePattern", "TimeIntervals", "Network", "Hardware", "DevicePopulation", "System",
    "UserJourney", "UserJourneyStep"]


def build_object_relationships_graph(
        node, input_graph=None, visited=None, classes_to_ignore=None, width=WIDTH, height=HEIGHT):
    if classes_to_ignore is None:
        classes_to_ignore = ["System"]
    if input_graph is None:
        input_graph = Network(notebook=True, width=f"{width}px", height=f"{height}px")
    if visited is None:
        visited = set()

    if node in visited:
        return input_graph

    node_type = type(node).__name__
    if node_type not in classes_to_ignore:
        input_graph.add_node(
            id(node), label=set_string_max_width(f"{type(node).__name__} {node.name}", 20),
            color=COLOR_MAP.get(node_type, "gray"))

    for attr_name, attr_value in vars(node).items():
        values = convert_to_list(attr_value)
        for value in values:
            if isinstance(value, ModelingObject):
                value_type = type(value).__name__
                if value_type not in classes_to_ignore:
                    input_graph.add_node(
                        id(value), label=set_string_max_width(f"{type(value).__name__} {value.name}", 20),
                        color=COLOR_MAP.get(value_type, "gray"))
                    if node_type not in classes_to_ignore:
                        input_graph.add_edge(id(node), id(value), title=attr_name)

                if value not in visited:
                    visited.add(node)
                    build_object_relationships_graph(value, input_graph, visited, classes_to_ignore, width, height)

    return input_graph
