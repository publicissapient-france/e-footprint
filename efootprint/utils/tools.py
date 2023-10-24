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
        print(f"Function {func.__name__} took {end_time - start_time:.5f} seconds to execute.")
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
