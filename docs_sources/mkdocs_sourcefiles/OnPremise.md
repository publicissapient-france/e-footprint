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

### fixed_nb_of_instances
user defined number of on premise server instances in dimensionless.


## Backwards links

- [Service](Service.md)


## Calculated attributes

### available_ram_per_instance  
ExplainableQuantity in gigabyte, representing the available ram per on premise server instance.  
  
Depends directly on:  
  
- [RAM of on premise server](OnPremise.md#ram)
- [on premise server utilization rate](OnPremise.md#server_utilization_rate)
- [Base RAM consumption of service](Service.md#base_ram_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_available_ram_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_available_ram_per_instance.html' target='_blank'>link to Available RAM per on premise server instance’s full calculation graph</a>.

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per on premise server instance.  
  
Depends directly on:  
  
- [Nb cpus cores of on premise server](OnPremise.md#cpu_cores)
- [on premise server utilization rate](OnPremise.md#server_utilization_rate)
- [Base CPU consumption of service](Service.md#base_cpu_consumption)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_available_cpu_per_instance_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_available_cpu_per_instance.html' target='_blank'>link to Available CPU per on premise server instance’s full calculation graph</a>.

### all_services_cpu_needs  
Representation of the evolution throughout a typical day of the cpu needs of all services running on on premise server by 24 values in core.  
  
Depends directly on:  
  
- [service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_all_services_cpu_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_all_services_cpu_needs.html' target='_blank'>link to CPU needs of all services running on on premise server’s full calculation graph</a>.

### all_services_ram_needs  
Representation of the evolution throughout a typical day of the ram needs of all services running on on premise server by 24 values in gigabyte.  
  
Depends directly on:  
  
- [service hour by hour ram need](Service.md#hour_by_hour_ram_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_all_services_ram_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_all_services_ram_needs.html' target='_blank'>link to RAM needs of all services running on on premise server’s full calculation graph</a>.

### fraction_of_time_in_use  
ExplainableQuantity in dimensionless, representing the fraction of time in use of on premise server.  
  
Depends directly on:  
  
- [CPU needs of all services running on on premise server](OnPremise.md#all_services_cpu_needs)
- [RAM needs of all services running on on premise server](OnPremise.md#all_services_ram_needs)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_fraction_of_time_in_use_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_fraction_of_time_in_use.html' target='_blank'>link to Fraction of time in use of on premise server’s full calculation graph</a>.

### nb_of_instances  
ExplainableQuantity in dimensionless, representing the user defined number of on premise server instances.  
  
Depends directly on:  
  
-   

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_nb_of_instances.html' target='_blank'>link to User defined number of on premise server instances’s full calculation graph</a>.

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the instances of on premise server fabrication footprint.  
  
Depends directly on:  
  
- [Carbon footprint fabrication of on premise server](OnPremise.md#carbon_footprint_fabrication)
- [User defined number of on premise server instances](OnPremise.md#nb_of_instances)
- [Lifespan of on premise server](OnPremise.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_instances_fabrication_footprint.html' target='_blank'>link to Instances of on premise server fabrication footprint’s full calculation graph</a>.

### instances_power  
ExplainableQuantity in kilowatt_hour / year, representing the power of on premise server instances.  
  
Depends directly on:  
  
- [User defined number of on premise server instances](OnPremise.md#nb_of_instances)
- [Power of on premise server](OnPremise.md#power)
- [PUE of on premise server](OnPremise.md#power_usage_effectiveness)
- [Fraction of time in use of on premise server](OnPremise.md#fraction_of_time_in_use)
- [Idle power of on premise server](OnPremise.md#idle_power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_instances_power_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_instances_power.html' target='_blank'>link to Power of on premise server instances’s full calculation graph</a>.

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of on premise server.  
  
Depends directly on:  
  
- [Power of on premise server instances](OnPremise.md#instances_power)
- [Average carbon intensity of on premise server electricity](OnPremise.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/on_premise_server_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/on_premise_server_energy_footprint.html' target='_blank'>link to Energy footprint of on premise server’s full calculation graph</a>.
