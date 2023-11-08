from efootprint.constants.sources import Sources, SourceObject
from efootprint.utils.graph_tools import set_string_max_width

from pyvis.network import Network


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

    if node.left_parent:
        nodes_at_depth(node.left_parent, depth, depth_lists)
    if node.right_parent:
        nodes_at_depth(node.right_parent, depth, depth_lists)

    return depth_lists


def calculate_positions(node):
    depth_lists = nodes_at_depth(node)
    max_width = max(len(lst) for lst in depth_lists.values())
    max_depth = len(depth_lists.keys())
    pos = {}

    for depth, nodes in depth_lists.items():
        num_nodes = len(nodes)
        for i, n in enumerate(nodes):
            offset = (num_nodes - 1) / 2
            x = (i - offset) * (max_width / num_nodes)
            pos[n.label] = (x, max_depth - depth)

    return pos


def build_calculus_graph(root_node, x_multiplier=150, y_multiplier=150, width="1800px", height="900px"):
    G = Network(notebook=True, directed=True, width=width, height=height)
    G.toggle_physics(False)

    pos = calculate_positions(root_node)

    def add_nodes_edges(node, parent_id=None):
        if node.label and (issubclass(type(node), SourceObject) or node.has_parent):
            if node.left_parent is None and node.right_parent is None and issubclass(type(node), SourceObject):
                if node.source == Sources.USER_INPUT:
                    color = "gold"
                else:
                    color = "darkred"
            else:
                color = None
            G.add_node(
                node.label, label=set_string_max_width(node.label, 20),
                title=set_string_max_width(str(node.explain()), 80),
                x=pos[node.label][0]*x_multiplier, y=pos[node.label][1]*y_multiplier, color=color, size=15)
            if parent_id:
                G.add_edge(node.label, parent_id)
            current_id = node.label
        else:
            current_id = parent_id

        if node.left_parent:
            add_nodes_edges(node.left_parent, current_id)
        if node.right_parent:
            add_nodes_edges(node.right_parent, current_id)

    add_nodes_edges(root_node)

    return G
