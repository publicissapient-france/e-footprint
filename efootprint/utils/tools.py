import time


def round_dict(my_dict, round_level):
    for key in my_dict:
        my_dict[key] = round(my_dict[key], round_level)

    return my_dict


def flatten_list(nested_list):
    flattened_list = [item for sublist in nested_list
                      for item in (flatten_list(sublist) if isinstance(sublist, list) else [sublist])]
    for elt in flattened_list:
        if type(elt) == set:
            raise ValueError("flatten_list function is not supposed to handle set elements, please refactor it.")

    return flattened_list


def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        diff = end_time - start_time
        if diff > 0.001:
            print(f"Function {func.__name__} took {diff:.5f} seconds to execute.")
        return result
    return wrapper


def convert_to_list(input_value):
    if type(input_value) == list:
        value_elts = flatten_list(input_value)
    elif type(input_value) == set:
        value_elts = flatten_list(list(input_value))
    else:
        value_elts = [input_value]

    return value_elts


def format_co2_amount(co2_amount_in_kg: int, rounding_value=1):
    if co2_amount_in_kg < 501:
        unit = "kg"
        dividing_number = 1
    else:
        unit = "ton"
        dividing_number = 1000
    rounded_total__new = round(co2_amount_in_kg / dividing_number, rounding_value)
    if rounding_value == 0:
        rounded_total__new = int(rounded_total__new)

    return rounded_total__new, unit


def display_co2_amount(num_value_and_unit_tuple):
    num_value, unit = num_value_and_unit_tuple

    return f"{num_value} {unit}s"
