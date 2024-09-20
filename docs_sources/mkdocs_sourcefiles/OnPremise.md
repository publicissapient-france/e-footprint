# OnPremise

## Params

### name
A human readable description of the object.

### carbon_footprint_fabrication
carbon footprint fabrication of on premise server in kilogram.

### power
power of on premise server in watt.

### lifespan
lifespan of on premise server in year.

### idle_power
idle power of on premise server in watt.

### ram
ram of on premise server in gigabyte.

### cpu_cores
nb cpus cores of on premise server in core.

### power_usage_effectiveness
pue of on premise server in dimensionless.

### average_carbon_intensity
average carbon intensity of on premise server electricity in gram / kilowatt_hour.

### server_utilization_rate
on premise server utilization rate in dimensionless.

### base_ram_consumption
base ram consumption of on premise server in megabyte.

### base_cpu_consumption
base cpu consumption of on premise server in core.

### fixed_nb_of_instances
user defined number of on premise server instances in dimensionless.


## Backwards links

- [Job](Job.md)


## Calculated attributes

### hour_by_hour_cpu_need  
on premise server hour by hour cpu need in core.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in core:  
    first 10 vals [0.4, 0.27, 0.2, 0.2, 0.13, 0.47, 0.07, 0.2, 0.47, 0.2],  
    last 10 vals [0.13, 0.53, 0.6, 0.27, 0.07, 0.4, 0.07, 0.47, 0.6, 0.2]  
  
Depends directly on:  
  
- [Hourly streaming average occurrences across usage patterns](Job.md#hourly_avg_occurrences_across_usage_patterns)
- [CPU needed on server server to process streaming](Job.md#cpu_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_hour_by_hour_cpu_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_hour_by_hour_cpu_need.html' target='_blank'>link to on premise server hour by hour cpu need’s full calculation graph</a>.

### hour_by_hour_ram_need  
on premise server hour by hour ram need in gigabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in GB:  
    first 10 vals [0.02, 0.01, 0.01, 0.01, 0.01, 0.02, 0.0, 0.01, 0.02, 0.01],  
    last 10 vals [0.01, 0.03, 0.03, 0.01, 0.0, 0.02, 0.0, 0.02, 0.03, 0.01]  
  
Depends directly on:  
  
- [Hourly streaming average occurrences across usage patterns](Job.md#hourly_avg_occurrences_across_usage_patterns)
- [RAM needed on server server to process streaming](Job.md#ram_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_hour_by_hour_ram_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_hour_by_hour_ram_need.html' target='_blank'>link to on premise server hour by hour ram need’s full calculation graph</a>.

### available_ram_per_instance  
ExplainableQuantity in gigabyte, representing the available ram per on premise server instance.  
  
Example value: 114.9 gigabyte  
  
Depends directly on:  
  
- [RAM of on premise server](OnPremise.md#ram)
- [on premise server utilization rate](OnPremise.md#server_utilization_rate)
- [Base RAM consumption of on premise server](OnPremise.md#base_ram_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_available_ram_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_available_ram_per_instance.html' target='_blank'>link to Available RAM per on premise server instance’s full calculation graph</a>.

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per on premise server instance.  
  
Example value: 19.6 core  
  
Depends directly on:  
  
- [Nb cpus cores of on premise server](OnPremise.md#cpu_cores)
- [on premise server utilization rate](OnPremise.md#server_utilization_rate)
- [Base CPU consumption of on premise server](OnPremise.md#base_cpu_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_available_cpu_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_available_cpu_per_instance.html' target='_blank'>link to Available CPU per on premise server instance’s full calculation graph</a>.

### raw_nb_of_instances  
hourly raw number of on premise server instances in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.02, 0.01, 0.01, 0.01, 0.01, 0.02, 0.0, 0.01, 0.02, 0.01],  
    last 10 vals [0.01, 0.03, 0.03, 0.01, 0.0, 0.02, 0.0, 0.02, 0.03, 0.01]  
  
Depends directly on:  
  
- [on premise server hour by hour ram need](OnPremise.md#hour_by_hour_ram_need)
- [Available RAM per on premise server instance](OnPremise.md#available_ram_per_instance)
- [on premise server hour by hour cpu need](OnPremise.md#hour_by_hour_cpu_need)
- [Available CPU per on premise server instance](OnPremise.md#available_cpu_per_instance)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_raw_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_raw_nb_of_instances.html' target='_blank'>link to Hourly raw number of on premise server instances’s full calculation graph</a>.

### nb_of_instances  
fixed number of on premise server instances in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000],  
    last 10 vals [4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000]  
  
Depends directly on:  
  
- [Hourly raw number of on premise server instances](OnPremise.md#raw_nb_of_instances)
- [User defined number of on premise server instances](OnPremise.md#fixed_nb_of_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_nb_of_instances.html' target='_blank'>link to Fixed number of on premise server instances’s full calculation graph</a>.

### instances_fabrication_footprint  
hourly on premise server instances fabrication footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63],  
    last 10 vals [45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63, 45.63]  
  
Depends directly on:  
  
- [Fixed number of on premise server instances](OnPremise.md#nb_of_instances)
- [Carbon footprint fabrication of on premise server](OnPremise.md#carbon_footprint_fabrication)
- [Lifespan of on premise server](OnPremise.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_instances_fabrication_footprint.html' target='_blank'>link to Hourly on premise server instances fabrication footprint’s full calculation graph</a>.

### instances_energy  
hourly energy consumed by on premise server instances in kilowatt_hour.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kWh:  
    first 10 vals [240.01, 240.0, 240.0, 240.0, 240.0, 240.01, 240.0, 240.0, 240.01, 240.0],  
    last 10 vals [240.0, 240.01, 240.01, 240.0, 240.0, 240.01, 240.0, 240.01, 240.01, 240.0]  
  
Depends directly on:  
  
- [Fixed number of on premise server instances](OnPremise.md#nb_of_instances)
- [Idle power of on premise server](OnPremise.md#idle_power)
- [PUE of on premise server](OnPremise.md#power_usage_effectiveness)
- [Hourly raw number of on premise server instances](OnPremise.md#raw_nb_of_instances)
- [Power of on premise server](OnPremise.md#power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_instances_energy_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_instances_energy.html' target='_blank'>link to Hourly energy consumed by on premise server instances’s full calculation graph</a>.

### energy_footprint  
hourly on premise server energy footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0],  
    last 10 vals [24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0]  
  
Depends directly on:  
  
- [Hourly energy consumed by on premise server instances](OnPremise.md#instances_energy)
- [Average carbon intensity of on premise server electricity](OnPremise.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_energy_footprint.html' target='_blank'>link to Hourly on premise server energy footprint’s full calculation graph</a>.
