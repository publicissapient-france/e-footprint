from footprint_model.constants.explainable_quantities import ExplainableQuantity
from footprint_model.core.infra_need import InfraNeed
from footprint_model.constants.units import u


def create_ram_or_cpu_need_list(time_interval, value):
    need_list = [value - value] * 24

    for hour in range(time_interval[0][0], time_interval[0][1]):
        need_list[hour] = value

    return need_list


def create_infra_need(
        time_interval, value_ram=ExplainableQuantity(100 * u.Go), value_cpu=ExplainableQuantity(1 * u.core),
        value_storage=ExplainableQuantity(10.1 * u.To / u.year, "Storage for service1")):

    ram_list = create_ram_or_cpu_need_list(time_interval, value_ram)
    storage = value_storage
    cpu_list = create_ram_or_cpu_need_list(time_interval, value_cpu)

    return InfraNeed(ram=ram_list, storage=storage, cpu=cpu_list)


def extract_values_from_dict(input_dict, nested_dict=False):
    if not nested_dict:
        return {key: input_dict[key].value for key in input_dict.keys()}
    else:
        return {key: {inside_dict_key: input_dict[key][inside_dict_key].value
                      for inside_dict_key in input_dict[key].keys()}
                for key in input_dict.keys()}
