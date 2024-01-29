from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.servers.on_premise import OnPremise
from efootprint.core.hardware.servers.serverless import Serverless


def default_serverless(name="Default serverless", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(300 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(6 * u.year, Sources.HYPOTHESIS),
        "idle_power": SourceValue(50 * u.W, Sources.HYPOTHESIS),
        "ram": SourceValue(128 * u.GB, Sources.HYPOTHESIS),
        "cpu_cores": SourceValue(24 * u.core, Sources.HYPOTHESIS),
        "power_usage_effectiveness": SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        "average_carbon_intensity": SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
        "server_utilization_rate": SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
    }

    output_args.update(kwargs)

    return Serverless(name, **output_args)


def default_autoscaling(name="Default autoscaling", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(300 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(6 * u.year, Sources.HYPOTHESIS),
        "idle_power": SourceValue(50 * u.W, Sources.HYPOTHESIS),
        "ram": SourceValue(128 * u.GB, Sources.HYPOTHESIS),
        "cpu_cores": SourceValue(24 * u.core, Sources.HYPOTHESIS),
        "power_usage_effectiveness": SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        "average_carbon_intensity": SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
        "server_utilization_rate": SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
    }

    output_args.update(kwargs)

    return Autoscaling(name, **output_args)


def default_onpremise(name="Default on premise", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(300 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(6 * u.year, Sources.HYPOTHESIS),
        "idle_power": SourceValue(50 * u.W, Sources.HYPOTHESIS),
        "ram": SourceValue(128 * u.GB, Sources.HYPOTHESIS),
        "cpu_cores": SourceValue(24 * u.core, Sources.HYPOTHESIS),
        "power_usage_effectiveness": SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
        "average_carbon_intensity": SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
        "server_utilization_rate": SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
    }

    output_args.update(kwargs)

    return OnPremise(name, **output_args)
