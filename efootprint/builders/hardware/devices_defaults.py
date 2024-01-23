from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.hardware.hardware_base_classes import Hardware


def default_smartphone(name="Default smartphone", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(30 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(1 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(3 * u.year, Sources.HYPOTHESIS),
        "fraction_of_usage_time": SourceValue(3.6 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)
    }

    output_args.update(kwargs)

    return Hardware(name, **output_args)


def default_laptop(name="Default laptop", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(156 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(50 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(6 * u.year, Sources.HYPOTHESIS),
        "fraction_of_usage_time": SourceValue(7 * u.hour / u.day, Sources.STATE_OF_MOBILE_2022)
    }

    output_args.update(kwargs)

    return Hardware(name, **output_args)


def default_box(name="Default box", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(78 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(10 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(6 * u.year, Sources.HYPOTHESIS),
        "fraction_of_usage_time": SourceValue(24 * u.hour / u.day, Sources.HYPOTHESIS)
    }

    output_args.update(kwargs)

    return Hardware(name, **output_args)


def default_screen(name="Default screen", **kwargs):
    output_args = {
        "carbon_footprint_fabrication": SourceValue(222 * u.kg, Sources.BASE_ADEME_V19),
        "power": SourceValue(30 * u.W, Sources.HYPOTHESIS),
        "lifespan": SourceValue(6 * u.year, Sources.HYPOTHESIS),
        "fraction_of_usage_time": SourceValue(7 * u.hour / u.day, Sources.HYPOTHESIS)
    }

    output_args.update(kwargs)

    return Hardware(name, **output_args)
