from efootprint.constants.sources import Source, Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.constants.units import u
from efootprint.core.hardware.servers.on_premise import OnPremise

import requests


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
        print(f"{method} request to {url} with params {kwargs} failed with status code {response.status_code}")


def get_archetypes_and_their_configs_and_impacts():
    output_dict = {}
    for archetype in call_boaviztapi('https://api.boavizta.org/v1/server/archetypes'):
        configuration = call_boaviztapi(
            url="https://api.boavizta.org/v1/server/archetype_config", params={"archetype": archetype})
        impact = call_boaviztapi(
            url="https://api.boavizta.org/v1/server/", params={"archetype": archetype})
        if impact is None:
            print(f"No impact for archetype {archetype}")
        else:
            output_dict[archetype] = {}
            output_dict[archetype]["config"] = configuration
            output_dict[archetype]["impact"] = impact

    return output_dict


def print_archetypes_and_their_configs():
    archetypes_data = get_archetypes_and_their_configs_and_impacts()

    for archetype in archetypes_data.keys():
        config = archetypes_data[archetype]["config"]
        impact = archetypes_data[archetype]["impact"]
        if "default" in config['CPU']['core_units'].keys():
            nb_cpu_core_units = config['CPU']['core_units']['default']
        else:
            nb_cpu_core_units = impact["verbose"]['CPU-1']['core_units']['value']

        nb_ssd_units = config['SSD']["units"]['default']
        nb_hdd_units = config['HDD']["units"]['default']

        if nb_hdd_units > 0 and nb_ssd_units > 0:
            raise ValueError(
                f"Archetype {archetype} has both SSD and HDD, please check and delete this exception raising if ok")
        storage_type = "SSD"
        if nb_hdd_units > 0:
            storage_type = "HDD"
        nb_storage_units = config[storage_type]["units"]['default']

        print(
            f"{archetype}: type {config['CASE']['case_type']['default']},\n"
            f"    {config['CPU']['units']['default']} cpu units with {nb_cpu_core_units} core units,\n"
            f"    {config['RAM']['units']['default']} RAM units with {config['RAM']['capacity']['default']} GB capacity,\n"
            f"    {nb_storage_units} {storage_type} units with {config[storage_type]['capacity']['default']} GB capacity,")

        total_gwp_embedded_value = impact["impacts"]["gwp"]["embedded"]["value"]
        total_gwp_embedded_unit = impact["impacts"]["gwp"]["unit"]

        if nb_storage_units > 0:
            storage_gwp_embedded_value = impact["verbose"][f"{storage_type}-1"]["impacts"]["gwp"]["embedded"]["value"]
            storage_gwp_embedded_unit = impact["verbose"][f"{storage_type}-1"]["impacts"]["gwp"]["unit"]

            assert total_gwp_embedded_unit == storage_gwp_embedded_unit
        else:
            storage_gwp_embedded_value = 0
            storage_gwp_embedded_unit = "kg"

        average_power_value = impact["verbose"]["avg_power"]["value"]
        average_power_unit = impact["verbose"]["avg_power"]["unit"]

        print(
            f"    Impact fabrication compute: {total_gwp_embedded_value - storage_gwp_embedded_value} {total_gwp_embedded_unit},\n"
            f"    Impact fabrication storage: {storage_gwp_embedded_value} {storage_gwp_embedded_unit},\n"
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
        cpu_cores=SourceValue(cpu_spec["units"]["value"] * cpu_spec["core_units"]["value"] * u.core, impact_source),
        power_usage_effectiveness=power_usage_effectiveness,
        average_carbon_intensity=average_carbon_intensity,
        server_utilization_rate=server_utilization_rate)


def on_premise_server_from_config(
        name: str, nb_of_cpu_units: int, nb_of_cores_per_cpu_unit: int, nb_of_ram_units: int,
        ram_quantity_per_unit_in_gb: int, average_carbon_intensity, lifespan=None, idle_power=None,
        power_usage_effectiveness=None, server_utilization_rate=None, fixed_nb_of_instances=None):
    impact_url = "https://api.boavizta.org/v1/server/"
    params = {"verbose": "true", "archetype": "platform_compute_medium", "criteria": ["gwp"]}
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
        cpu_cores=SourceValue(cpu_spec["units"]["value"] * cpu_spec["core_units"]["value"] * u.core, impact_source),
        power_usage_effectiveness=power_usage_effectiveness,
        average_carbon_intensity=average_carbon_intensity,
        server_utilization_rate=server_utilization_rate,
        fixed_nb_of_instances=fixed_nb_of_instances)


if __name__ == "__main__":
    print_archetypes_and_their_configs()
