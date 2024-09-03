import math

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.constants.units import u


def compute_nb_avg_hourly_occurrences(
        hourly_occurrences_starts: ExplainableHourlyQuantities, event_duration: ExplainableQuantity):
    nb_avg_hourly_occurrences_in_parallel = None
    event_duration_in_nb_of_hours = event_duration.to(u.hour).magnitude
    nb_of_full_hours_in_event_duration = math.floor(event_duration_in_nb_of_hours)

    for hour_shift in range(0, nb_of_full_hours_in_event_duration):
        if nb_avg_hourly_occurrences_in_parallel is None:
            nb_avg_hourly_occurrences_in_parallel = hourly_occurrences_starts.value.shift(hour_shift, freq="h")
        else:
            nb_avg_hourly_occurrences_in_parallel = nb_avg_hourly_occurrences_in_parallel.add(
                hourly_occurrences_starts.value.shift(hour_shift, freq="h"), fill_value=0)

    nonfull_duration_rest = event_duration_in_nb_of_hours - nb_of_full_hours_in_event_duration
    if nonfull_duration_rest > 0:
        if nb_avg_hourly_occurrences_in_parallel is None:
            nb_avg_hourly_occurrences_in_parallel = hourly_occurrences_starts.value.shift(
                nb_of_full_hours_in_event_duration, freq="h") * nonfull_duration_rest
        else:
            nb_avg_hourly_occurrences_in_parallel = nb_avg_hourly_occurrences_in_parallel.add(
                hourly_occurrences_starts.value.shift(nb_of_full_hours_in_event_duration, freq="h")
                * nonfull_duration_rest,
                fill_value=0)
        
    return ExplainableHourlyQuantities(
            nb_avg_hourly_occurrences_in_parallel, left_parent=hourly_occurrences_starts, right_parent=event_duration,
            operator=f"hourly occurrences average")
