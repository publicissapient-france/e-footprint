# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd


# %%
def count_character(string, char):
    count = 0
    for c in string:         
        if c == char:             
            count += 1
    return count


# %%
with open("lefigaro.log") as file:
    lines = file.readlines()
first_hits = []
subsequent_hits = []

for i in range(100):
    if count_character(lines[i], "|") == 18:
        value_list = lines[i].split("|")
        value_dict = {'fullDate': value_list[0], 'ip': value_list[2], 'domain': value_list[3], 
                      'url': value_list[6], 'Ismobile': value_list[8]}
        first_hits.append(value_dict)
        
    elif count_character(lines[i], "|") == 9:
        value_list = lines[i].split("|")
        value_dict = {'fullDate': value_list[0], 'ip': value_list[2], 'domain': value_list[3], 
                      'url': value_list[6]}
        subsequent_hits.append(value_dict)
  

# %%
first_hits_df = pd.DataFrame.from_records(first_hits)
first_hits_df

# %%
subsequent_hits_df = pd.DataFrame.from_records(subsequent_hits)
subsequent_hits_df

# %%
