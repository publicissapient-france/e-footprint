from efootprint.utils.graph_tools import WIDTH, HEIGHT, set_string_max_width

from pyvis.network import Network

COLOR_MAP = {
    "Autoscaling": "red",
    "OnPremise": "red",
    "Serverless": "red",
    "Hardware": "red",
    "Storage": "red",
    "Service": "deepskyblue",
    "UsagePattern": "blueviolet",
    "DevicePopulation": "red",
    "UserJourney": "gold",
    "UserJourneyStep": "gold",
    "TimeIntervals": "gold",
}

USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE = [
    "System", "Network", "Hardware", "Country"]
SERVICES_VIEW_CLASSES_TO_IGNORE = [
    "System", "UsagePattern", "TimeIntervals", "Network", "Server", "Storage", "Hardware", "DevicePopulation"]
SERVICES_AND_INFRA_VIEW_CLASSES_TO_IGNORE = [
    "UsagePattern", "TimeIntervals", "Network", "Hardware", "DevicePopulation", "System",
    "UserJourney", "UserJourneyStep"]


def build_object_relationships_graph(
        node, input_graph=None, visited=None, classes_to_ignore=None, width=WIDTH, height=HEIGHT, notebook=False):
    cdn_resources = "local"
    if notebook:
        cdn_resources = "in_line"
    if classes_to_ignore is None:
        classes_to_ignore = ["System"]
    if input_graph is None:
        input_graph = Network(notebook=notebook, width=width, height=height, cdn_resources=cdn_resources)
    if visited is None:
        visited = set()

    if node in visited:
        return input_graph

    node_type = type(node).__name__
    if node_type not in classes_to_ignore:
        input_graph.add_node(
            id(node), label=set_string_max_width(f"{node.name}", 20),
            title=set_string_max_width(str(node), 80),
            color=COLOR_MAP.get(node_type, "gray"))

    for mod_obj in node.mod_obj_attributes:
        mod_obj_type = type(mod_obj).__name__
        if mod_obj_type not in classes_to_ignore:
            input_graph.add_node(
                id(mod_obj), label=set_string_max_width(f"{mod_obj.name}", 20),
                title=set_string_max_width(str(mod_obj), 80),
                color=COLOR_MAP.get(mod_obj_type, "gray"))
            if node_type not in classes_to_ignore:
                input_graph.add_edge(id(node), id(mod_obj))

        if mod_obj not in visited:
            visited.add(node)
            build_object_relationships_graph(mod_obj, input_graph, visited, classes_to_ignore, width, height)

    return input_graph
