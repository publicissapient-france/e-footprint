from pint import Quantity

from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyUsage
from footprint_model.constants.units import u


def create_ram_or_cpu_need_list(time_interval, value):
    need_list = [value - value] * 24

    for hour in range(time_interval[0][0], time_interval[0][1]):
        need_list[hour] = value

    return need_list


def create_ram_need(hours_in_use, ram: Quantity = 100 * u.GB):
    hour_by_hour_ram_need = [ExplainableQuantity(0 * u.GB)] * 24
    for time_interval in hours_in_use:
        start, end = time_interval
        for i in range(start, end):
            hour_by_hour_ram_need[i] = ExplainableQuantity(ram)
    return ExplainableHourlyUsage(hour_by_hour_ram_need)


def create_cpu_need(hours_in_use, cpu: Quantity = 1 * u.core):
    hour_by_hour_cpu_need = [ExplainableQuantity(0 * u.core)] * 24
    for time_interval in hours_in_use:
        start, end = time_interval
        for i in range(start, end):
            hour_by_hour_cpu_need[i] = ExplainableQuantity(cpu)
    return ExplainableHourlyUsage(hour_by_hour_cpu_need)


