from pyvis.network import Network

from footprint_model.constants.sources import SourceValue, Sources, SourceObject


def nodes_at_depth(node, depth=0, depth_lists=None, label_len_threshold=-1):
    if depth_lists is None:
        depth_lists = {}

    if len(node.label) > label_len_threshold:
        if depth not in depth_lists:
            depth_lists[depth] = []
        for i in range(0, depth):
            depth_lists[i] = [n for n in depth_lists[i] if n.label != node.label]
        if node.label not in [n.label for n in depth_lists[depth]]:
            depth_lists[depth].append(node)

        depth += 1

    if node.left_child:
        nodes_at_depth(node.left_child, depth, depth_lists, label_len_threshold)
    if node.right_child:
        nodes_at_depth(node.right_child, depth, depth_lists, label_len_threshold)

    return depth_lists


def calculate_positions(node, label_len_threshold=-1):
    depth_lists = nodes_at_depth(node, label_len_threshold=label_len_threshold)
    max_width = max(len(lst) for lst in depth_lists.values())
    pos = {}

    for depth, nodes in depth_lists.items():
        num_nodes = len(nodes)
        for i, n in enumerate(nodes):
            offset = (num_nodes - 1) / 2
            x = (i - offset) * (max_width / num_nodes)
            pos[n.label] = (x, depth)

    return pos


def build_graph(root_node, x_multiplier=180, y_multiplier=200, label_len_threshold=0, width="1800px", height="900px"):
    G = Network(notebook=True, directed=True, width=width, height=height)
    G.toggle_physics(False)

    pos = calculate_positions(root_node, label_len_threshold)

    def add_nodes_edges(node, parent_id=None):
        if len(node.label) > label_len_threshold and (issubclass(type(node), SourceObject) or node.has_child):
            if node.left_child is None and node.right_child is None and issubclass(type(node), SourceObject):
                if node.source == Sources.USER_INPUT:
                    color = "green"
                else:
                    color = "red"
            else:
                color = None
            G.add_node(
                node.label, label=set_string_max_width(node.label, 20), title=set_string_max_width(str(node.explain()), 80),
                x=pos[node.label][0]*x_multiplier, y=pos[node.label][1]*y_multiplier, color=color)
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

    server = Servers.SERVER
    storage = Storage(
        "Default SSD storage",
        carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
        idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
        storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
        power_usage_effectiveness=1.2,
        country=Countries.GERMANY,
        data_replication_factor=3,
    )
    service = Service("Youtube", server, storage, base_ram_consumption=300 * u.MB,
                      base_cpu_consumption=2 * u.core)

    streaming_step = UserJourneyStep("20 min streaming", service, 50 * u.kB, (2.5 / 3) * u.GB,
                                     user_time_spent=20 * u.min, request_duration=4 * u.min)
    upload_step = UserJourneyStep("0.4s upload", service, 300 * u.kB, 0 * u.GB, user_time_spent=1 * u.s,
                                  request_duration=0.1 * u.s)

    default_uj = UserJourney("Daily Youtube usage", uj_steps=[streaming_step, upload_step])

    default_device_pop = DevicePopulation(
        "French laptops", 4e7 * 0.3, Countries.FRANCE, [Devices.LAPTOP])

    default_network = Networks.WIFI_NETWORK
    usage_pattern = UsagePattern(
        "Daily Youtube usage", default_uj, default_device_pop,
        default_network, 365 * u.user_journey / (u.user * u.year), [[7, 23]])

    system = System("system 1", [usage_pattern])

    G = build_graph(system.energy_footprints()["Storage"], label_len_threshold=0)
    G.show("calculus_output_storage.html")
    G_raw = build_graph(system.energy_footprints()["Servers"], label_len_threshold=0)
    G_raw.show("calculus_output_server.html")
