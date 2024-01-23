from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.hardware.network import Network


def default_wifi_network(name="Default wifi network", **kwargs):
    output_args = {
        "bandwidth_energy_intensity": SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY)
    }

    output_args.update(kwargs)

    return Network(name, **output_args)


def default_mobile_network(name="Default mobile network", **kwargs):
    output_args = {
        "bandwidth_energy_intensity": SourceValue(0.12 * u("kWh/GB"), Sources.TRAFICOM_STUDY)
    }

    output_args.update(kwargs)

    return Network(name, **output_args)
