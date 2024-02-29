# Storage

## Params

### name
A human readable description of the object.

### carbon_footprint_fabrication
SourceValue with Quantity in kilogram, representing the carbon footprint fabrication of storage.

### power
SourceValue with Quantity in watt, representing the power of storage.

### lifespan
SourceValue with Quantity in year, representing the lifespan of storage.

### idle_power
SourceValue with Quantity in watt, representing the idle power of storage.

### storage_capacity
SourceValue with Quantity in terabyte, representing the storage capacity of storage.

### power_usage_effectiveness
SourceValue with Quantity in dimensionless, representing the pue of storage.

### average_carbon_intensity
SourceValue with Quantity in gram / kilowatt_hour, representing the average carbon intensity of storage electricity.

### data_replication_factor
SourceValue with Quantity in dimensionless, representing the data replication factor of storage.

### storage_need_from_previous_year
description to be done


## Backwards links

- [Service](Service.md)


## Calculated attributes

### all_services_storage_needs  
ExplainableQuantity in terabyte / year, representing the storage need of storage.  
  
Depends directly on ['[Storage needed for service](Service.md#storage_needed)'] through the following formula:

Storage need of storage=Storage needed for service  
  
See Storage need of storage calculation graph at <a href='../calculus_graphs/storage_all_services_storage_needs.html' target='_blank'>this link</a>

### active_storage_required  
ExplainableQuantity in gigabyte, representing the active storage required for storage.  
  
Depends directly on ['[Storage need of storage](Storage.md#all_services_storage_needs)'] through the following formula:

Active storage required for storage=Storage need of storage * Time interval during which active storage is considered from hypothesis  
  
See Active storage required for storage calculation graph at <a href='../calculus_graphs/storage_active_storage_required.html' target='_blank'>this link</a>

### long_term_storage_required  
ExplainableQuantity in terabyte, representing the long term storage required for storage.  
  
Depends directly on ['[Storage need of storage](Storage.md#all_services_storage_needs)', '[Data replication factor of storage](Storage.md#data_replication_factor)', '[Active storage required for storage](Storage.md#active_storage_required)'] through the following formula:

Long term storage required for storage=Storage need of storage * Data replication factor of storage * one year - Active storage required for storage  
  
See Long term storage required for storage calculation graph at <a href='../calculus_graphs/storage_long_term_storage_required.html' target='_blank'>this link</a>

### nb_of_idle_instances  
ExplainableQuantity in dimensionless, representing the number of idle storage units for storage.  
  
Depends directly on ['[Long term storage required for storage](Storage.md#long_term_storage_required)', '[Storage capacity of storage](Storage.md#storage_capacity)'] through the following formula:

Number of idle storage units for storage=Long term storage required for storage / Storage capacity of storage  
  
See Number of idle storage units for storage calculation graph at <a href='../calculus_graphs/storage_nb_of_idle_instances.html' target='_blank'>this link</a>

### nb_of_active_instances  
ExplainableQuantity in dimensionless, representing the number of active instances for storage.  
  
Depends directly on ['[Active storage required for storage](Storage.md#active_storage_required)', '[Storage capacity of storage](Storage.md#storage_capacity)'] through the following formula:

Number of active instances for storage=Active storage required for storage / Storage capacity of storage  
  
See Number of active instances for storage calculation graph at <a href='../calculus_graphs/storage_nb_of_active_instances.html' target='_blank'>this link</a>

### all_services_cpu_needs  
Representation of the evolution throughout a typical day of the cpu needs of all services running on storage by 24 values in core.  
  
Depends directly on ['[service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)'] through the following formula:

CPU needs of all services running on storage=service hour by hour cpu need  
  
See CPU needs of all services running on storage calculation graph at <a href='../calculus_graphs/storage_all_services_cpu_needs.html' target='_blank'>this link</a>

### all_services_ram_needs  
Representation of the evolution throughout a typical day of the ram needs of all services running on storage by 24 values in gigabyte.  
  
Depends directly on ['[service hour by hour ram need](Service.md#hour_by_hour_ram_need)'] through the following formula:

RAM needs of all services running on storage=service hour by hour ram need  
  
See RAM needs of all services running on storage calculation graph at <a href='../calculus_graphs/storage_all_services_ram_needs.html' target='_blank'>this link</a>

### fraction_of_time_in_use  
ExplainableQuantity in dimensionless, representing the fraction of time in use of storage.  
  
Depends directly on ['[CPU needs of all services running on storage](Storage.md#all_services_cpu_needs)', '[RAM needs of all services running on storage](Storage.md#all_services_ram_needs)'] through the following formula:

Fraction of time in use of storage=usage time fraction computation of (retrieving usage hours of (CPU needs of all services running on storage) + retrieving usage hours of (RAM needs of all services running on storage))  
  
See Fraction of time in use of storage calculation graph at <a href='../calculus_graphs/storage_fraction_of_time_in_use.html' target='_blank'>this link</a>

### nb_of_instances  
ExplainableQuantity in dimensionless, representing the number of total instances for storage.  
  
Depends directly on ['[Number of active instances for storage](Storage.md#nb_of_active_instances)', '[Number of idle storage units for storage](Storage.md#nb_of_idle_instances)'] through the following formula:

Number of total instances for storage=Number of active instances for storage + Number of idle storage units for storage  
  
See Number of total instances for storage calculation graph at <a href='../calculus_graphs/storage_nb_of_instances.html' target='_blank'>this link</a>

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the instances of storage fabrication footprint.  
  
Depends directly on ['[Carbon footprint fabrication of storage](Storage.md#carbon_footprint_fabrication)', '[Number of total instances for storage](Storage.md#nb_of_instances)', '[Lifespan of storage](Storage.md#lifespan)'] through the following formula:

Instances of storage fabrication footprint=Carbon footprint fabrication of storage * Number of total instances for storage / Lifespan of storage  
  
See Instances of storage fabrication footprint calculation graph at <a href='../calculus_graphs/storage_instances_fabrication_footprint.html' target='_blank'>this link</a>

### instances_power  
ExplainableQuantity in kilowatt_hour / year, representing the storage power for storage.  
  
Depends directly on ['[Number of active instances for storage](Storage.md#nb_of_active_instances)', '[Power of storage](Storage.md#power)', '[PUE of storage](Storage.md#power_usage_effectiveness)', '[Fraction of time in use of storage](Storage.md#fraction_of_time_in_use)', '[Number of idle storage units for storage](Storage.md#nb_of_idle_instances)', '[Idle power of storage](Storage.md#idle_power)'] through the following formula:

Storage power for storage=Active instances power * Fraction of time in use of storage + Idle instances power  
  
See Storage power for storage calculation graph at <a href='../calculus_graphs/storage_instances_power.html' target='_blank'>this link</a>

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of storage.  
  
Depends directly on ['[Storage power for storage](Storage.md#instances_power)', '[Average carbon intensity of storage electricity](Storage.md#average_carbon_intensity)'] through the following formula:

Energy footprint of storage=Storage power for storage * Average carbon intensity of storage electricity  
  
See Energy footprint of storage calculation graph at <a href='../calculus_graphs/storage_energy_footprint.html' target='_blank'>this link</a>
