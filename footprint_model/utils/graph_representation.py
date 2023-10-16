import os.path

from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.utils.tools import convert_to_list

from pyvis.network import Network
from selenium import webdriver
import json
import time


COLOR_MAP = {
    "Server": "red",
    "Hardware": "red",
    "Storage": "brown",
    "Service": "blue",
    "UsagePattern": "green",
    "DevicePopulation": "orange",
    "UserJourney": "green",
    "UserJourneyStep": "orange",
    "TimeIntervals": "green",
}

USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE = [
    "System", "UserJourney", "UserJourneyStep", "TimeIntervals", "Network", "Service", "Hardware"]
SERVICES_VIEW_CLASSES_TO_IGNORE = [
    "System", "UsagePattern", "TimeIntervals", "Network", "Server", "Storage", "Hardware", "DevicePopulation"]
SERVICES_AND_INFRA_VIEW_CLASSES_TO_IGNORE = [
    "UsagePattern", "TimeIntervals", "Network", "Hardware", "DevicePopulation", "System",
    "UserJourney", "UserJourneyStep"]

WIDTH = 1200
HEIGHT = 900


def build_graph(node, input_graph=None, visited=None, classes_to_ignore=None, width=WIDTH, height=HEIGHT):
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
        input_graph.add_node(id(node), label=f"{node.name}", color=COLOR_MAP.get(node_type, "gray"))

    for attr_name, attr_value in vars(node).items():
        values = convert_to_list(attr_value)
        for value in values:
            if isinstance(value, ModelingObject):
                value_type = type(value).__name__
                if value_type not in classes_to_ignore:
                    input_graph.add_node(id(value), label=f"{value.name}", color=COLOR_MAP.get(value_type, "gray"))
                    if node_type not in classes_to_ignore:
                        input_graph.add_edge(id(node), id(value), title=attr_name)

                if value not in visited:
                    visited.add(node)
                    build_graph(value, input_graph, visited, classes_to_ignore, width, height)

    return input_graph


def capture_screenshot(html_file_path, output_image_path, width, height):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width, height)

    driver.get(f"file://{html_file_path}")
    time.sleep(2)

    driver.save_screenshot(output_image_path)

    driver.quit()


def save_graph_as_both_html_and_png(input_graph, output_filepath, width=WIDTH, height=HEIGHT):
    input_graph.set_options(json.dumps({'physics': {"springLength": 250}}))
    input_graph.show(f"{output_filepath}")
    capture_screenshot(
        os.path.abspath(f"{output_filepath}"), f"{output_filepath.replace('html', 'png')}", width, height)


if __name__ == "__main__":
    from footprint_model.constants.sources import SourceValue, Sources
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
        data_storage_duration=10 * u.year
    )
    service = Service("Youtube", server, storage, base_ram_consumption=300 * u.MB,
                      base_cpu_consumption=2 * u.core)

    streaming_step = UserJourneyStep("20 min streaming on Youtube", service, 50 * u.kB, (2.5 / 3) * u.GB,
                                     user_time_spent=20 * u.min, request_duration=4 * u.min)
    upload_step = UserJourneyStep("0.4s of upload", service, 300 * u.kB, 0 * u.GB, user_time_spent=1 * u.s,
                                  request_duration=0.1 * u.s)

    default_uj = UserJourney("Daily Youtube usage", uj_steps=[streaming_step, upload_step])

    default_device_pop = DevicePopulation(
        "French Youtube users on laptop", 4e7 * 0.3, Countries.FRANCE, [Devices.LAPTOP])

    default_network = Networks.WIFI_NETWORK
    usage_pattern = UsagePattern(
        "Average daily Youtube usage in France on laptop", default_uj, default_device_pop,
        default_network, 365 * u.user_journey / (u.user * u.year), [[7, 23]])

    system = System("system 1", [usage_pattern])

    G = build_graph(usage_pattern)
    save_graph_as_both_html_and_png(G, "output.html")
