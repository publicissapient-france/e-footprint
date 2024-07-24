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
  
Depends directly on:  
  
- [RAM of serverless](Serverless.md#ram)
- [serverless utilization rate](Serverless.md#server_utilization_rate)
- [Base RAM consumption of service](Service.md#base_ram_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_available_ram_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_available_ram_per_instance.html' target='_blank'>link to Available RAM per serverless instance’s full calculation graph</a>.

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per serverless instance.  
  
Depends directly on:  
  
- [Nb cpus cores of serverless](Serverless.md#cpu_cores)
- [serverless utilization rate](Serverless.md#server_utilization_rate)
- [Base CPU consumption of service](Service.md#base_cpu_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_available_cpu_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_available_cpu_per_instance.html' target='_blank'>link to Available CPU per serverless instance’s full calculation graph</a>.

### all_services_cpu_needs  
Representation of the evolution throughout a typical day of the cpu needs of all services running on serverless by 24 values in core.  
  
Depends directly on:  
  
- [service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_all_services_cpu_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_all_services_cpu_needs.html' target='_blank'>link to CPU needs of all services running on serverless’s full calculation graph</a>.

### all_services_ram_needs  
Representation of the evolution throughout a typical day of the ram needs of all services running on serverless by 24 values in gigabyte.  
  
Depends directly on:  
  
- [service hour by hour ram need](Service.md#hour_by_hour_ram_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_all_services_ram_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_all_services_ram_needs.html' target='_blank'>link to RAM needs of all services running on serverless’s full calculation graph</a>.

### fraction_of_time_in_use  
ExplainableQuantity in dimensionless, representing the fraction of time in use of serverless.  
  
Depends directly on:  
  
- [CPU needs of all services running on serverless](Serverless.md#all_services_cpu_needs)
- [RAM needs of all services running on serverless](Serverless.md#all_services_ram_needs)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_fraction_of_time_in_use_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_fraction_of_time_in_use.html' target='_blank'>link to Fraction of time in use of serverless’s full calculation graph</a>.

### nb_of_instances  
ExplainableQuantity in dimensionless, representing the nb of serverless instances.  
  
Depends directly on:  
  
- [RAM needs of all services running on serverless](Serverless.md#all_services_ram_needs)
- [Available RAM per serverless instance](Serverless.md#available_ram_per_instance)
- [CPU needs of all services running on serverless](Serverless.md#all_services_cpu_needs)
- [Available CPU per serverless instance](Serverless.md#available_cpu_per_instance)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_nb_of_instances.html' target='_blank'>link to Nb of serverless instances’s full calculation graph</a>.

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the instances of serverless fabrication footprint.  
  
Depends directly on:  
  
- [Carbon footprint fabrication of serverless](Serverless.md#carbon_footprint_fabrication)
- [Nb of serverless instances](Serverless.md#nb_of_instances)
- [Lifespan of serverless](Serverless.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_instances_fabrication_footprint.html' target='_blank'>link to Instances of serverless fabrication footprint’s full calculation graph</a>.

### instances_power  
ExplainableQuantity in kilowatt_hour / year, representing the power of serverless instances.  
  
Depends directly on:  
  
- [Power of serverless](Serverless.md#power)
- [PUE of serverless](Serverless.md#power_usage_effectiveness)
- [Nb of serverless instances](Serverless.md#nb_of_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_instances_power_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_instances_power.html' target='_blank'>link to Power of serverless instances’s full calculation graph</a>.

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of serverless.  
  
Depends directly on:  
  
- [Power of serverless instances](Serverless.md#instances_power)
- [Average carbon intensity of serverless electricity](Serverless.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/serverless_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/serverless_energy_footprint.html' target='_blank'>link to Energy footprint of serverless’s full calculation graph</a>.
