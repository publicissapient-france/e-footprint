from efootprint.constants.sources import SourceValue, Source, Sources
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.constants.units import u

import requests

from efootprint.core.hardware.servers.on_premise import OnPremise


def call_boaviztapi(url, method="GET", **kwargs):
    headers = {'accept': 'application/json'}
    if method == "GET":
        response = requests.get(url, headers=headers, **kwargs)
    elif method == "POST":
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, **kwargs)

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
        # Correction for https://github.com/Boavizta/boaviztapi/issues/257
        nb_of_ssd_units = config['SSD'][units_with_tab_car]['default']
        if "," in str(nb_of_ssd_units):
            nb_of_ssd_units = int(nb_of_ssd_units.split(",")[0])
        print(
            f"{archetype}: type {config['CASE']['case_type']['default']},\n"
            f"    {config['CPU']['units']['default']} cpu units with {config['CPU']['core_units']['default']} core units,\n"
            f"    {config['RAM']['units']['default']} RAM units with {config['RAM']['capacity']['default']} GB capacity,\n"
            f"    {nb_of_ssd_units} SSD units with {config['SSD']['capacity']['default']} GB capacity,")
        if len(config["HDD"]["units"].keys()) > 0:
            print(f"    {config['HDD']['units']['default']} HDD units with {config['HDD']['capacity']['default']} GB capacity,")

        total_gwp_embedded_value = impact["impacts"]["gwp"]["embedded"]["value"]
        # Correction for https://github.com/Boavizta/boaviztapi/issues/256 by multiplying by nb of SSD units
        ssd_gwp_embedded_value__raw = impact["verbose"]["SSD-1"]["impacts"]["gwp"]["embedded"]["value"]
        ssd_gwp_embedded_value__corrected = ssd_gwp_embedded_value__raw * nb_of_ssd_units

        total_gwp_embedded_unit = impact["impacts"]["gwp"]["unit"]
        ssd_gwp_embedded_unit = impact["verbose"]["SSD-1"]["impacts"]["gwp"]["unit"]

        assert total_gwp_embedded_unit == ssd_gwp_embedded_unit

        average_power_value = impact["verbose"]["avg_power"]["value"]
        average_power_unit = impact["verbose"]["avg_power"]["unit"]

        print(
            f"    Impact fabrication compute: {total_gwp_embedded_value - ssd_gwp_embedded_value__raw} {total_gwp_embedded_unit},\n"
            f"    Impact fabrication SSD: {ssd_gwp_embedded_value__corrected} {ssd_gwp_embedded_unit},\n"
            f"    Average power: {round(average_power_value, 1)} {average_power_unit}\n")


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

    average_power_value = impact_data["verbose"]["avg_power"]["value"]
    average_power_unit = impact_data["verbose"]["avg_power"]["unit"]
    use_time_ratio = impact_data["verbose"]["use_time_ratio"]["value"]

    assert average_power_unit == "W"
    assert float(use_time_ratio) == 1

    return base_efootprint_class(
        f"{provider} {instance_type} instances",
        carbon_footprint_fabrication=SourceValue(impacts["gwp"]["embedded"]["value"] * u.kg, impact_source),
        # TODO: document and challenge power calculation
        power=SourceValue(average_power_value * u.W, impact_source),
        lifespan=lifespan,
        idle_power=idle_power,
        ram=SourceValue(ram_spec["units"]["value"] * ram_spec["capacity"]["value"] * u.GB, impact_source),
        nb_of_cpus=SourceValue(cpu_spec["units"]["value"] * cpu_spec["core_units"]["value"] * u.core, impact_source),
        power_usage_effectiveness=power_usage_effectiveness,
        average_carbon_intensity=average_carbon_intensity,
        server_utilization_rate=server_utilization_rate)


def on_premise_server_from_config(
        name: str, nb_of_cpu_units: int, nb_of_cores_per_cpu_unit: int, nb_of_ram_units: int,
        ram_quantity_per_unit_in_gb: int, average_carbon_intensity, lifespan=None, idle_power=None,
        power_usage_effectiveness=None, server_utilization_rate=None):
    impact_url = "https://api.boavizta.org/v1/server/"
    params = {"verbose": "true", "archetype": "compute_medium", "criteria": ["gwp"]}
    data = {"model": {"type": "rack"},
            "configuration": {"cpu": {"units": nb_of_cpu_units, "core_units": nb_of_cores_per_cpu_unit},
                              "ram": [{"units": nb_of_ram_units, "capacity": ram_quantity_per_unit_in_gb}]}}

    impact_source = Source(name="Boavizta API servers",
                           link=f"{impact_url}?{'&'.join([key + '=' + str(params[key]) for key in params.keys()])}")
    impact_data = call_boaviztapi(url=impact_url, params=params, json=data, method="POST")

    impacts = impact_data["impacts"]
    cpu_spec = impact_data["verbose"]["CPU-1"]
    ram_spec = impact_data["verbose"]["RAM-1"]

    if lifespan is None:
        lifespan = SourceValue(6 * u.year, Sources.HYPOTHESIS)
    if idle_power is None:
        idle_power = SourceValue(0 * u.W, Sources.HYPOTHESIS)
    if power_usage_effectiveness is None:
        power_usage_effectiveness = SourceValue(1.4 * u.dimensionless, Sources.HYPOTHESIS)
    if server_utilization_rate is None:
        server_utilization_rate = SourceValue(0.7 * u.dimensionless, Sources.HYPOTHESIS)

    average_power_value = impact_data["verbose"]["avg_power"]["value"]
    average_power_unit = impact_data["verbose"]["avg_power"]["unit"]
    use_time_ratio = impact_data["verbose"]["use_time_ratio"]["value"]

    assert average_power_unit == "W"
    assert float(use_time_ratio) == 1

    return OnPremise(
        name,
        carbon_footprint_fabrication=SourceValue(impacts["gwp"]["embedded"]["value"] * u.kg, impact_source),
        # TODO: document and challenge power calculation
        power=SourceValue(average_power_value * u.W, impact_source),
        lifespan=lifespan,
        idle_power=idle_power,
        ram=SourceValue(ram_spec["units"]["value"] * ram_spec["capacity"]["value"] * u.GB, impact_source),
        nb_of_cpus=SourceValue(cpu_spec["units"]["value"] * cpu_spec["core_units"]["value"] * u.core, impact_source),
        power_usage_effectiveness=power_usage_effectiveness,
        average_carbon_intensity=average_carbon_intensity,
        server_utilization_rate=server_utilization_rate)
