from pyvis.network import Network

from footprint_model.constants.sources import SourceValue, Sources, SourceObject


def nodes_at_depth(node, depth=0, depth_lists=None):
    if depth_lists is None:
        depth_lists = {}

    if node.label:
        if depth not in depth_lists:
            depth_lists[depth] = []
        for i in range(0, depth):
            depth_lists[i] = [n for n in depth_lists[i] if n.label != node.label]
        if node.label not in [n.label for n in depth_lists[depth]]:
            depth_lists[depth].append(node)

        depth += 1

    if node.left_child:
        nodes_at_depth(node.left_child, depth, depth_lists)
    if node.right_child:
        nodes_at_depth(node.right_child, depth, depth_lists)

    return depth_lists


def calculate_positions(node):
    depth_lists = nodes_at_depth(node)
    max_width = max(len(lst) for lst in depth_lists.values())
    pos = {}

    for depth, nodes in depth_lists.items():
        num_nodes = len(nodes)
        for i, n in enumerate(nodes):
            offset = (num_nodes - 1) / 2
            x = (i - offset) * (max_width / num_nodes)
            pos[n.label] = (x, depth)

    return pos


def build_graph(root_node, x_multiplier=150, y_multiplier=150, width="1800px", height="900px"):
    G = Network(notebook=True, directed=True, width=width, height=height)
    G.toggle_physics(False)

    pos = calculate_positions(root_node)

    def add_nodes_edges(node, parent_id=None):
        if node.label and (issubclass(type(node), SourceObject) or node.has_child):
            if node.left_child is None and node.right_child is None and issubclass(type(node), SourceObject):
                if node.source == Sources.USER_INPUT:
                    color = "green"
                else:
                    color = "red"
            else:
                color = None
            G.add_node(
                node.label, label=set_string_max_width(node.label, 20), title=set_string_max_width(str(node.explain()), 80),
                x=pos[node.label][0]*x_multiplier, y=pos[node.label][1]*y_multiplier, color=color, size=15)
            if parent_id:
                G.add_edge(parent_id, node.label)
            current_id = node.label
        else:
            current_id = parent_id

        if node.left_child:
            add_nodes_edges(node.left_child, current_id)
        if node.right_child:
            add_nodes_edges(node.right_child, current_id)

    add_nodes_edges(root_node)

    return G


def set_string_max_width(s, max_width):
    lines = s.split('\n')
    formatted_lines = []

    for line in lines:
        words = line.split()
        current_line = []
        current_len = 0

        for word in words:
            if current_len + len(word) > max_width:
                formatted_lines.append(' '.join(current_line))
                current_line = [word]
                current_len = len(word) + 1
            else:
                current_line.append(word)
                current_len += len(word) + 1

        if current_line:
            formatted_lines.append(' '.join(current_line))

    return '\n'.join(formatted_lines)


if __name__ == "__main__":
    from footprint_model.core.usage.user_journey import UserJourney, UserJourneyStep
    from footprint_model.core.hardware.server import Servers
    from footprint_model.core.hardware.storage import Storage
    from footprint_model.core.service import Service
    from footprint_model.core.hardware.device_population import DevicePopulation, Devices
    from footprint_model.core.usage.usage_pattern import UsagePattern
    from footprint_model.core.hardware.network import Networks
    from footprint_model.core.system import System
    from footprint_model.constants.countries import Countries
    from footprint_model.constants.units import u

    default_server = Servers.SERVER
    default_server.cloud = "Autoscaling"
    default_storage = Storage(
        "Default SSD storage",
        carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        country=Countries.GERMANY,
        data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS),
    )
    default_service = Service(
        "Youtube", default_server, default_storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
        base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

    streaming_step = UserJourneyStep(
        "20 min streaming on Youtube", default_service, SourceValue(50 * u.kB / u.uj, Sources.USER_INPUT),
        SourceValue((2.5 / 3) * u.GB / u.uj, Sources.USER_INPUT),
        user_time_spent=SourceValue(20 * u.min / u.uj, Sources.USER_INPUT),
        request_duration=SourceValue(4 * u.min, Sources.HYPOTHESIS))
    upload_step = UserJourneyStep(
        "0.4s of upload", default_service, SourceValue(300 * u.kB / u.uj, Sources.USER_INPUT),
        SourceValue(0 * u.GB / u.uj, Sources.USER_INPUT),
        user_time_spent=SourceValue(0.4 * u.s / u.uj, Sources.USER_INPUT),
        request_duration=SourceValue(0.4 * u.s, Sources.HYPOTHESIS))

    default_user_journey = UserJourney("Daily Youtube usage", uj_steps=[streaming_step, upload_step])

    default_device_population = DevicePopulation(
        "French Youtube users on laptop", SourceValue(4e7 * 0.3 * u.user, Sources.USER_INPUT),
        Countries.FRANCE, [Devices.LAPTOP])

    default_network = Networks.WIFI_NETWORK

    default_usage_pattern = UsagePattern(
        "Daily Youtube usage", default_user_journey, default_device_population,
        default_network, SourceValue(365 * u.user_journey / (u.user * u.year), Sources.USER_INPUT), [[7, 23]])

    system = System("system 1", [default_usage_pattern])

    G = build_graph(system.energy_footprints()["Storage"])
    G.show("calculus_output_storage.html")
    G = build_graph(system.energy_footprints()["Servers"])
    G.show("calculus_output_server.html")
    G = build_graph(system.energy_footprints()["Storage"])
    G.show("calculus_output_storage.html")
    G = build_graph(system.total_footprint())
    G.show("calculus_output_total.html")
