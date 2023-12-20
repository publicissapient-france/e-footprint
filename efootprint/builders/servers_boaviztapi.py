from efootprint.constants.sources import SourceValue, Source, Sources
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.constants.units import u

import requests


def call_boaviztapi(url, headers=None, params=None):
    if headers is None:
        headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise ConnectionError(f"Request failed with status code {response.status_code}")


def get_archetypes_and_their_configs_and_impacts():
    output_dict = {}
    for archetype in call_boaviztapi('https://api.boavizta.org/v1/server/archetypes'):
        configuration = call_boaviztapi(
            url="https://api.boavizta.org/v1/server/archetype_config", params={"archetype": archetype})
        impact = call_boaviztapi(
            url="https://api.boavizta.org/v1/server/", params={"archetype": archetype})
        output_dict[archetype] = {}
        output_dict[archetype]["config"] = configuration
        output_dict[archetype]["impact"] = impact

    return output_dict


def print_archetypes_and_their_configs():
    archetypes_data = get_archetypes_and_their_configs_and_impacts()

    for archetype in archetypes_data.keys():
        config = archetypes_data[archetype]["config"]
        impact = archetypes_data[archetype]["impact"]
        units_with_tab_car = 'units\t'
        print(
            f"{archetype}: \n    {config['CASE']['case_type']['default']},\n"
            f"    {config['CPU']['units']['default']} cpu units with {config['CPU']['core_units']['default']} core units,\n"
            f"    {config['RAM']['units']['default']} RAM units with {config['RAM']['capacity']['default']} GB capacity,\n"
            f"    {config['SSD'][units_with_tab_car]['default']} SSD units with {config['SSD']['capacity']['default']} GB capacity,\n")
        if len(config["HDD"]["units"].keys()) > 0:
            print(f"    {config['HDD']['units']['default']} HDD units with {config['HDD']['capacity']['default']} GB capacity,\n")

        total_gwp_embedded_value = impact["impacts"]["gwp"]["embedded"]["value"]
        ssd_gwp_embedded_value = impact["verbose"]["SSD-1"]["impacts"]["gwp"]["embedded"]["value"]

        total_gwp_embedded_unit = impact["impacts"]["gwp"]["unit"]
        ssd_gwp_embedded_unit = impact["verbose"]["SSD-1"]["impacts"]["gwp"]["unit"]

        assert total_gwp_embedded_unit == ssd_gwp_embedded_unit

        average_power_value = impact["verbose"]["avg_power"]["value"]
        average_power_unit = impact["verbose"]["avg_power"]["unit"]

        print(
            f"    Impact fabrication compute: {total_gwp_embedded_value - ssd_gwp_embedded_value} {total_gwp_embedded_unit},\n"
            f"    Impact fabrication SSD: {ssd_gwp_embedded_value} {ssd_gwp_embedded_unit},\n"
            f"    Average power: {average_power_value} {average_power_unit}")


def get_cloud_server(
        provider, instance_type, average_carbon_intensity, base_efootprint_class=Autoscaling,
        lifespan=None, idle_power=None, power_usage_effectiveness=None,
        server_utilization_rate=None
        ):
    if lifespan is None:
        lifespan = SourceValue(6 * u.year, Sources.HYPOTHESIS)
    if idle_power is None:
        idle_power = SourceValue(0 * u.W, Sources.HYPOTHESIS)
    if power_usage_effectiveness is None:
        power_usage_effectiveness = SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS)
    if server_utilization_rate is None:
        server_utilization_rate = SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)

    impact_url = "https://api.boavizta.org/v1/cloud/instance"
    params = {"provider": provider, "instance_type": instance_type}
    impact_source = Source(name="Boavizta API cloud instances",
                    link=f"{impact_url}?{'&'.join([key + '=' + params[key] for key in params.keys()])}")
    impact_data = call_boaviztapi(url=impact_url, params=params)
    impacts = impact_data["impacts"]
    cpu_spec = impact_data["verbose"]["CPU-1"]
    ram_spec = impact_data["verbose"]["RAM-1"]

    return base_efootprint_class(
        f"{provider} {instance_type} instances",
        carbon_footprint_fabrication=SourceValue(impacts["gwp"]["embedded"]["value"] * u.kg, impact_source),
        # TODO: document and challenge power calculation
        power=SourceValue(cpu_spec["units"]["value"] * cpu_spec["avg_power"]["value"] * u.W, impact_source),
        lifespan=lifespan,
        idle_power=idle_power,
        ram=SourceValue(ram_spec["units"]["value"] * u.GB, impact_source),
        nb_of_cpus=SourceValue(cpu_spec["core_units"]["value"] * u.core, impact_source),
        power_usage_effectiveness=power_usage_effectiveness,
        average_carbon_intensity=average_carbon_intensity,
        server_utilization_rate=server_utilization_rate)


def on_premise_server_from_config(
        nb_of_cpus, nb_of_core_units, nb_of_ram, ram_quantity_per_ram_unit, average_power):
    impact_url = "https://api.boavizta.org/v1/server"
    params = {"archetype": "compute-medium", "criteria": "gwp"}
    data = {"model": {"type": "rack"},
            "configuration": {"cpu": {"units": nb_of_cpus, "core_units": nb_of_core_units},
                              "ram": {"units": nb_of_ram, "capacity": ram_quantity_per_ram_unit}}}

    impact_source = Source(name="Boavizta API servers",
                           link=f"{impact_url}?{'&'.join([key + '=' + params[key] for key in params.keys()])}")
    impact_data = call_boaviztapi(url=impact_url, params=params)


if __name__ == "__main__":
    print_archetypes_and_their_configs()

    aws_server = get_cloud_server("aws", "m5.xlarge", SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS))
