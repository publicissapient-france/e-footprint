# Autoscaling

## Params

### name
A human readable description of the object.

### carbon_footprint_fabrication
carbon footprint fabrication of server in kilogram.

### power
power of server in watt.

### lifespan
lifespan of server in year.

### idle_power
idle power of server in watt.

### ram
ram of server in gigabyte.

### cpu_cores
nb cpus cores of server in core.

### power_usage_effectiveness
pue of server in dimensionless.

### average_carbon_intensity
average carbon intensity of server electricity in gram / kilowatt_hour.

### server_utilization_rate
server utilization rate in dimensionless.

### base_ram_consumption
base ram consumption of server in megabyte.

### base_cpu_consumption
base cpu consumption of server in core.


## Backwards links

- [Job](Job.md)


## Calculated attributes

### hour_by_hour_cpu_need  
server hour by hour cpu need in core.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in core:  
    first 10 vals [0.4, 0.27, 0.2, 0.2, 0.13, 0.47, 0.07, 0.2, 0.47, 0.2],  
    last 10 vals [0.13, 0.53, 0.6, 0.27, 0.07, 0.4, 0.07, 0.47, 0.6, 0.2]  
  
Depends directly on:  
  
- [Hourly streaming average occurrences across usage patterns](Job.md#hourly_avg_occurrences_across_usage_patterns)
- [CPU needed on server server to process streaming](Job.md#cpu_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_hour_by_hour_cpu_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_hour_by_hour_cpu_need.html' target='_blank'>link to server hour by hour cpu need’s full calculation graph</a>.

### hour_by_hour_ram_need  
server hour by hour ram need in gigabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in GB:  
    first 10 vals [0.02, 0.01, 0.01, 0.01, 0.01, 0.02, 0.0, 0.01, 0.02, 0.01],  
    last 10 vals [0.01, 0.03, 0.03, 0.01, 0.0, 0.02, 0.0, 0.02, 0.03, 0.01]  
  
Depends directly on:  
  
- [Hourly streaming average occurrences across usage patterns](Job.md#hourly_avg_occurrences_across_usage_patterns)
- [RAM needed on server server to process streaming](Job.md#ram_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_hour_by_hour_ram_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_hour_by_hour_ram_need.html' target='_blank'>link to server hour by hour ram need’s full calculation graph</a>.

### available_ram_per_instance  
ExplainableQuantity in gigabyte, representing the available ram per server instance.  
  
Example value: 114.9 gigabyte  
  
Depends directly on:  
  
- [RAM of server](Autoscaling.md#ram)
- [server utilization rate](Autoscaling.md#server_utilization_rate)
- [Base RAM consumption of server](Autoscaling.md#base_ram_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_available_ram_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_available_ram_per_instance.html' target='_blank'>link to Available RAM per server instance’s full calculation graph</a>.

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per server instance.  
  
Example value: 19.6 core  
  
Depends directly on:  
  
- [Nb cpus cores of server](Autoscaling.md#cpu_cores)
- [server utilization rate](Autoscaling.md#server_utilization_rate)
- [Base CPU consumption of server](Autoscaling.md#base_cpu_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_available_cpu_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_available_cpu_per_instance.html' target='_blank'>link to Available CPU per server instance’s full calculation graph</a>.

### raw_nb_of_instances  
hourly raw number of server instances in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.02, 0.01, 0.01, 0.01, 0.01, 0.02, 0.0, 0.01, 0.02, 0.01],  
    last 10 vals [0.01, 0.03, 0.03, 0.01, 0.0, 0.02, 0.0, 0.02, 0.03, 0.01]  
  
Depends directly on:  
  
- [server hour by hour ram need](Autoscaling.md#hour_by_hour_ram_need)
- [Available RAM per server instance](Autoscaling.md#available_ram_per_instance)
- [server hour by hour cpu need](Autoscaling.md#hour_by_hour_cpu_need)
- [Available CPU per server instance](Autoscaling.md#available_cpu_per_instance)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_raw_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_raw_nb_of_instances.html' target='_blank'>link to Hourly raw number of server instances’s full calculation graph</a>.

### nb_of_instances  
hourly number of server instances in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  
    last 10 vals [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]  
  
Depends directly on:  
  
- [Hourly raw number of server instances](Autoscaling.md#raw_nb_of_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_nb_of_instances.html' target='_blank'>link to Hourly number of server instances’s full calculation graph</a>.

### instances_fabrication_footprint  
hourly server instances fabrication footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],  
    last 10 vals [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]  
  
Depends directly on:  
  
- [Hourly number of server instances](Autoscaling.md#nb_of_instances)
- [Carbon footprint fabrication of server](Autoscaling.md#carbon_footprint_fabrication)
- [Lifespan of server](Autoscaling.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_instances_fabrication_footprint.html' target='_blank'>link to Hourly server instances fabrication footprint’s full calculation graph</a>.

### instances_energy  
hourly energy consumed by server instances in kilowatt_hour.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kWh:  
    first 10 vals [0.07, 0.06, 0.06, 0.06, 0.06, 0.07, 0.06, 0.06, 0.07, 0.06],  
    last 10 vals [0.06, 0.07, 0.07, 0.06, 0.06, 0.07, 0.06, 0.07, 0.07, 0.06]  
  
Depends directly on:  
  
- [Hourly number of server instances](Autoscaling.md#nb_of_instances)
- [Idle power of server](Autoscaling.md#idle_power)
- [PUE of server](Autoscaling.md#power_usage_effectiveness)
- [Hourly raw number of server instances](Autoscaling.md#raw_nb_of_instances)
- [Power of server](Autoscaling.md#power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_instances_energy_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_instances_energy.html' target='_blank'>link to Hourly energy consumed by server instances’s full calculation graph</a>.

### energy_footprint  
hourly server energy footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],  
    last 10 vals [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]  
  
Depends directly on:  
  
- [Hourly energy consumed by server instances](Autoscaling.md#instances_energy)
- [Average carbon intensity of server electricity](Autoscaling.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_energy_footprint.html' target='_blank'>link to Hourly server energy footprint’s full calculation graph</a>.
