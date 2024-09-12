# Serverless

## Params

### name
A human readable description of the object.

### carbon_footprint_fabrication
carbon footprint fabrication of serverless in kilogram.

### power
power of serverless in watt.

### lifespan
lifespan of serverless in year.

### idle_power
idle power of serverless in watt.

### ram
ram of serverless in gigabyte.

### cpu_cores
nb cpus cores of serverless in core.

### power_usage_effectiveness
pue of serverless in dimensionless.

### average_carbon_intensity
average carbon intensity of serverless electricity in gram / kilowatt_hour.

### server_utilization_rate
serverless utilization rate in dimensionless.


## Backwards links

- [Service](Service.md)


## Calculated attributes

### available_ram_per_instance  
ExplainableQuantity in gigabyte, representing the available ram per serverless instance.  
  
Example value: 114.9 gigabyte  
  
Depends directly on:  
  
- [RAM of serverless](Serverless.md#ram)
- [serverless utilization rate](Serverless.md#server_utilization_rate)
- [Base RAM consumption of service](Service.md#base_ram_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_available_ram_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_available_ram_per_instance.html' target='_blank'>link to Available RAM per serverless instance’s full calculation graph</a>.

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per serverless instance.  
  
Example value: 19.6 core  
  
Depends directly on:  
  
- [Nb cpus cores of serverless](Serverless.md#cpu_cores)
- [serverless utilization rate](Serverless.md#server_utilization_rate)
- [Base CPU consumption of service](Service.md#base_cpu_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_available_cpu_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_available_cpu_per_instance.html' target='_blank'>link to Available CPU per serverless instance’s full calculation graph</a>.

### all_services_cpu_needs  
cpu needs of all services running on serverless in core.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in core:  
    first 10 vals [0.13, 0.33, 0.6, 0.07, 0.2, 0.53, 0.4, 0.27, 0.13, 0.13],  
    last 10 vals [0.27, 0.47, 0.33, 0.47, 0.07, 0.2, 0.47, 0.27, 0.2, 0.07]  
  
Depends directly on:  
  
- [service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_all_services_cpu_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_all_services_cpu_needs.html' target='_blank'>link to CPU needs of all services running on serverless’s full calculation graph</a>.

### all_services_ram_needs  
ram needs of all services running on serverless in gigabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in GB:  
    first 10 vals [0.01, 0.02, 0.03, 0.0, 0.01, 0.03, 0.02, 0.01, 0.01, 0.01],  
    last 10 vals [0.01, 0.02, 0.02, 0.02, 0.0, 0.01, 0.02, 0.01, 0.01, 0.0]  
  
Depends directly on:  
  
- [service hour by hour ram need](Service.md#hour_by_hour_ram_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_all_services_ram_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_all_services_ram_needs.html' target='_blank'>link to RAM needs of all services running on serverless’s full calculation graph</a>.

### raw_nb_of_instances  
hourly raw number of serverless instances in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.01, 0.02, 0.03, 0.0, 0.01, 0.03, 0.02, 0.01, 0.01, 0.01],  
    last 10 vals [0.01, 0.02, 0.02, 0.02, 0.0, 0.01, 0.02, 0.01, 0.01, 0.0]  
  
Depends directly on:  
  
- [RAM needs of all services running on serverless](Serverless.md#all_services_ram_needs)
- [Available RAM per serverless instance](Serverless.md#available_ram_per_instance)
- [CPU needs of all services running on serverless](Serverless.md#all_services_cpu_needs)
- [Available CPU per serverless instance](Serverless.md#available_cpu_per_instance)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_raw_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_raw_nb_of_instances.html' target='_blank'>link to Hourly raw number of serverless instances’s full calculation graph</a>.

### nb_of_instances  
hourly number of serverless instances in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.01, 0.02, 0.03, 0.0, 0.01, 0.03, 0.02, 0.01, 0.01, 0.01],  
    last 10 vals [0.01, 0.02, 0.02, 0.02, 0.0, 0.01, 0.02, 0.01, 0.01, 0.0]  
  
Depends directly on:  
  
- [Hourly raw number of serverless instances](Serverless.md#raw_nb_of_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_nb_of_instances.html' target='_blank'>link to Hourly number of serverless instances’s full calculation graph</a>.

### instances_fabrication_footprint  
hourly serverless instances fabrication footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly number of serverless instances](Serverless.md#nb_of_instances)
- [Carbon footprint fabrication of serverless](Serverless.md#carbon_footprint_fabrication)
- [Lifespan of serverless](Serverless.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_instances_fabrication_footprint.html' target='_blank'>link to Hourly serverless instances fabrication footprint’s full calculation graph</a>.

### instances_energy  
hourly energy consumed by serverless instances in kilowatt_hour.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kWh:  
    first 10 vals [0.0, 0.01, 0.01, 0.0, 0.0, 0.01, 0.01, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.01, 0.01, 0.01, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly number of serverless instances](Serverless.md#nb_of_instances)
- [Idle power of serverless](Serverless.md#idle_power)
- [PUE of serverless](Serverless.md#power_usage_effectiveness)
- [Hourly raw number of serverless instances](Serverless.md#raw_nb_of_instances)
- [Power of serverless](Serverless.md#power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_instances_energy_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_instances_energy.html' target='_blank'>link to Hourly energy consumed by serverless instances’s full calculation graph</a>.

### energy_footprint  
hourly serverless energy footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly energy consumed by serverless instances](Serverless.md#instances_energy)
- [Average carbon intensity of serverless electricity](Serverless.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_energy_footprint.html' target='_blank'>link to Hourly serverless energy footprint’s full calculation graph</a>.
