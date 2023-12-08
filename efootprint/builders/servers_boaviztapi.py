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


def get_archetypes():
    return call_boaviztapi('https://api.boavizta.org/v1/server/archetypes')


def get_archetype_configuration(archetype):
    assert archetype in get_archetypes()

    return call_boaviztapi(url="https://api.boavizta.org/v1/server/archetype_config", params={"archetype": archetype})


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
        nb_of_cpus=SourceValue(cpu_spec["units"]["value"] * u.core, impact_source),
        power_usage_effectiveness=power_usage_effectiveness,
        average_carbon_intensity=average_carbon_intensity,
        server_utilization_rate=server_utilization_rate)


if __name__ == "__main__":
    archetypes = get_archetypes()

    print(get_archetype_configuration('compute_low'))

    aws_server = get_cloud_server("aws", "m5d.24xlarge", SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS))
