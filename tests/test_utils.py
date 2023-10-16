def extract_values_from_dict(input_dict, imbricated_dict=False):
    if not imbricated_dict:
        return {key: input_dict[key].value for key in input_dict.keys()}
    else:
        return {key: {inside_dict_key: input_dict[key][inside_dict_key].value
                      for inside_dict_key in input_dict[key].keys()}
                for key in input_dict.keys()}
