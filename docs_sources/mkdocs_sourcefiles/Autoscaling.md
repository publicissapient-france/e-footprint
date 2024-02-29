# Autoscaling

## Params

### name
A human readable description of the object.

### carbon_footprint_fabrication
SourceValue with Quantity in kilogram, representing the carbon footprint fabrication of server.

### power
SourceValue with Quantity in watt, representing the power of server.

### lifespan
SourceValue with Quantity in year, representing the lifespan of server.

### idle_power
SourceValue with Quantity in watt, representing the idle power of server.

### ram
SourceValue with Quantity in gigabyte, representing the ram of server.

### cpu_cores
SourceValue with Quantity in core, representing the nb cpus cores of server.

### power_usage_effectiveness
SourceValue with Quantity in dimensionless, representing the pue of server.

### average_carbon_intensity
SourceValue with Quantity in gram / kilowatt_hour, representing the average carbon intensity of server electricity.

### server_utilization_rate
SourceValue with Quantity in dimensionless, representing the server utilization rate.


## Backwards links

- [Service](Service.md)


## Calculated attributes

### available_ram_per_instance  
ExplainableQuantity in gigabyte, representing the available ram per server instance.  
  
Depends directly on ['[RAM of server](Autoscaling.md#ram)', '[server utilization rate](Autoscaling.md#server_utilization_rate)', '[Base RAM consumption of service](Service.md#base_ram_consumption)'] through the following formula:

Available RAM per server instance=RAM of server * server utilization rate - Base RAM consumption of service  
  
See Available RAM per server instance calculation graph at <a href='../calculus_graphs/server_available_ram_per_instance.html' target='_blank'>this link</a>

### available_cpu_per_instance  
ExplainableQuantity in core, representing the available cpu per server instance.  
  
Depends directly on ['[Nb cpus cores of server](Autoscaling.md#cpu_cores)', '[server utilization rate](Autoscaling.md#server_utilization_rate)', '[Base CPU consumption of service](Service.md#base_cpu_consumption)'] through the following formula:

Available CPU per server instance=Nb cpus cores of server * server utilization rate - Base CPU consumption of service  
  
See Available CPU per server instance calculation graph at <a href='../calculus_graphs/server_available_cpu_per_instance.html' target='_blank'>this link</a>

### all_services_cpu_needs  
Representation of the evolution throughout a typical day of the cpu needs of all services running on server by 24 values in core.  
  
Depends directly on ['[service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)'] through the following formula:

CPU needs of all services running on server=service hour by hour cpu need  
  
See CPU needs of all services running on server calculation graph at <a href='../calculus_graphs/server_all_services_cpu_needs.html' target='_blank'>this link</a>

### all_services_ram_needs  
Representation of the evolution throughout a typical day of the ram needs of all services running on server by 24 values in gigabyte.  
  
Depends directly on ['[service hour by hour ram need](Service.md#hour_by_hour_ram_need)'] through the following formula:

RAM needs of all services running on server=service hour by hour ram need  
  
See RAM needs of all services running on server calculation graph at <a href='../calculus_graphs/server_all_services_ram_needs.html' target='_blank'>this link</a>

### fraction_of_time_in_use  
ExplainableQuantity in dimensionless, representing the fraction of time in use of server.  
  
Depends directly on ['[CPU needs of all services running on server](Autoscaling.md#all_services_cpu_needs)', '[RAM needs of all services running on server](Autoscaling.md#all_services_ram_needs)'] through the following formula:

Fraction of time in use of server=usage time fraction computation of (retrieving usage hours of (CPU needs of all services running on server) + retrieving usage hours of (RAM needs of all services running on server))  
  
See Fraction of time in use of server calculation graph at <a href='../calculus_graphs/server_fraction_of_time_in_use.html' target='_blank'>this link</a>

### nb_of_instances  
ExplainableQuantity in dimensionless, representing the nb of server instances.  
  
Depends directly on ['[RAM needs of all services running on server](Autoscaling.md#all_services_ram_needs)', '[Available RAM per server instance](Autoscaling.md#available_ram_per_instance)', '[CPU needs of all services running on server](Autoscaling.md#all_services_cpu_needs)', '[Available CPU per server instance](Autoscaling.md#available_cpu_per_instance)'] through the following formula:

Nb of server instances=mean of (Hour by hour nb of instances)  
  
See Nb of server instances calculation graph at <a href='../calculus_graphs/server_nb_of_instances.html' target='_blank'>this link</a>

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the instances of server fabrication footprint.  
  
Depends directly on ['[Carbon footprint fabrication of server](Autoscaling.md#carbon_footprint_fabrication)', '[Nb of server instances](Autoscaling.md#nb_of_instances)', '[Lifespan of server](Autoscaling.md#lifespan)'] through the following formula:

Instances of server fabrication footprint=Carbon footprint fabrication of server * Nb of server instances / Lifespan of server  
  
See Instances of server fabrication footprint calculation graph at <a href='../calculus_graphs/server_instances_fabrication_footprint.html' target='_blank'>this link</a>

### instances_power  
ExplainableQuantity in kilowatt_hour / year, representing the power of server instances.  
  
Depends directly on ['[Power of server](Autoscaling.md#power)', '[PUE of server](Autoscaling.md#power_usage_effectiveness)', '[Nb of server instances](Autoscaling.md#nb_of_instances)'] through the following formula:

Power of server instances=Power of server * PUE of server * Nb of server instances  
  
See Power of server instances calculation graph at <a href='../calculus_graphs/server_instances_power.html' target='_blank'>this link</a>

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of server.  
  
Depends directly on ['[Power of server instances](Autoscaling.md#instances_power)', '[Average carbon intensity of server electricity](Autoscaling.md#average_carbon_intensity)'] through the following formula:

Energy footprint of server=Power of server instances * Average carbon intensity of server electricity  
  
See Energy footprint of server calculation graph at <a href='../calculus_graphs/server_energy_footprint.html' target='_blank'>this link</a>
