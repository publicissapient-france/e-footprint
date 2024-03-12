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


## Backwards links

- [Service](Service.md)


## Calculated attributes

### available_ram_per_instance  
ExplainableQuantity in gigabyte, representing the available ram per server instance.  
  
Depends directly on:  
  
- [RAM of server](Autoscaling.md#ram)
- [server utilization rate](Autoscaling.md#server_utilization_rate)
- [Base RAM consumption of service](Service.md#base_ram_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_available_ram_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_available_ram_per_instance.html' target='_blank'>link to Available RAM per server instance’s full calculation graph</a>.

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per server instance.  
  
Depends directly on:  
  
- [Nb cpus cores of server](Autoscaling.md#cpu_cores)
- [server utilization rate](Autoscaling.md#server_utilization_rate)
- [Base CPU consumption of service](Service.md#base_cpu_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_available_cpu_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_available_cpu_per_instance.html' target='_blank'>link to Available CPU per server instance’s full calculation graph</a>.

### all_services_cpu_needs  
Representation of the evolution throughout a typical day of the cpu needs of all services running on server by 24 values in core.  
  
Depends directly on:  
  
- [service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_all_services_cpu_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_all_services_cpu_needs.html' target='_blank'>link to CPU needs of all services running on server’s full calculation graph</a>.

### all_services_ram_needs  
Representation of the evolution throughout a typical day of the ram needs of all services running on server by 24 values in gigabyte.  
  
Depends directly on:  
  
- [service hour by hour ram need](Service.md#hour_by_hour_ram_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_all_services_ram_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_all_services_ram_needs.html' target='_blank'>link to RAM needs of all services running on server’s full calculation graph</a>.

### fraction_of_time_in_use  
ExplainableQuantity in dimensionless, representing the fraction of time in use of server.  
  
Depends directly on:  
  
- [CPU needs of all services running on server](Autoscaling.md#all_services_cpu_needs)
- [RAM needs of all services running on server](Autoscaling.md#all_services_ram_needs)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_fraction_of_time_in_use_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_fraction_of_time_in_use.html' target='_blank'>link to Fraction of time in use of server’s full calculation graph</a>.

### nb_of_instances  
ExplainableQuantity in dimensionless, representing the nb of server instances.  
  
Depends directly on:  
  
- [RAM needs of all services running on server](Autoscaling.md#all_services_ram_needs)
- [Available RAM per server instance](Autoscaling.md#available_ram_per_instance)
- [CPU needs of all services running on server](Autoscaling.md#all_services_cpu_needs)
- [Available CPU per server instance](Autoscaling.md#available_cpu_per_instance)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_nb_of_instances.html' target='_blank'>link to Nb of server instances’s full calculation graph</a>.

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the instances of server fabrication footprint.  
  
Depends directly on:  
  
- [Carbon footprint fabrication of server](Autoscaling.md#carbon_footprint_fabrication)
- [Nb of server instances](Autoscaling.md#nb_of_instances)
- [Lifespan of server](Autoscaling.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_instances_fabrication_footprint.html' target='_blank'>link to Instances of server fabrication footprint’s full calculation graph</a>.

### instances_power  
ExplainableQuantity in kilowatt_hour / year, representing the power of server instances.  
  
Depends directly on:  
  
- [Power of server](Autoscaling.md#power)
- [PUE of server](Autoscaling.md#power_usage_effectiveness)
- [Nb of server instances](Autoscaling.md#nb_of_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_instances_power_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_instances_power.html' target='_blank'>link to Power of server instances’s full calculation graph</a>.

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of server.  
  
Depends directly on:  
  
- [Power of server instances](Autoscaling.md#instances_power)
- [Average carbon intensity of server electricity](Autoscaling.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/server_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/server_energy_footprint.html' target='_blank'>link to Energy footprint of server’s full calculation graph</a>.
