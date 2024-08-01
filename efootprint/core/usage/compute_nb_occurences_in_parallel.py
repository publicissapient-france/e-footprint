import math

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.constants.units import u


def compute_nb_occurences_in_parallel(
        hourly_occurences_starts: ExplainableHourlyQuantities, event_duration: ExplainableQuantity):
    nb_occurences_in_parallel = hourly_occurences_starts. \
        create_empty_hourly_dimensionless_quantities_with_same_index()
    event_duration_in_nb_of_hours = event_duration.to(u.hour).magnitude
    nb_of_full_hours_in_event_duration = math.floor(event_duration_in_nb_of_hours)
    for hour in range(0, nb_of_full_hours_in_event_duration):
        nb_occurences_in_parallel += hourly_occurences_starts.return_shifted_hourly_quantities(
            hour)

    nonfull_duration_rest = event_duration_in_nb_of_hours - nb_of_full_hours_in_event_duration
    if nonfull_duration_rest > 0:
        nb_occurences_in_parallel += hourly_occurences_starts.return_shifted_hourly_quantities(
            nb_of_full_hours_in_event_duration
        ) * ExplainableQuantity(nonfull_duration_rest * u.dimensionless, "non full duration rest")
        
    return nb_occurences_in_parallel
