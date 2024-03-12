# Storage

## Params

### name
A human readable description of the object.

### carbon_footprint_fabrication
carbon footprint fabrication of storage in kilogram.

### power
power of storage in watt.

### lifespan
lifespan of storage in year.

### idle_power
idle power of storage in watt.

### storage_capacity
storage capacity of storage in terabyte.

### power_usage_effectiveness
pue of storage in dimensionless.

### average_carbon_intensity
average carbon intensity of storage electricity in gram / kilowatt_hour.

### data_replication_factor
data replication factor of storage in dimensionless.

### storage_need_from_previous_year
description to be done


## Backwards links

- [Service](Service.md)


## Calculated attributes

### all_services_storage_needs  
ExplainableQuantity in terabyte / year, representing the storage need of storage.  
  
Depends directly on:  
  
- [Storage needed for service](Service.md#storage_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_all_services_storage_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_all_services_storage_needs.html' target='_blank'>link to Storage need of storage’s full calculation graph</a>.

### active_storage_required  
ExplainableQuantity in gigabyte, representing the active storage required for storage.  
  
Depends directly on:  
  
- [Storage need of storage](Storage.md#all_services_storage_needs)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_active_storage_required_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_active_storage_required.html' target='_blank'>link to Active storage required for storage’s full calculation graph</a>.

### long_term_storage_required  
ExplainableQuantity in terabyte, representing the long term storage required for storage.  
  
Depends directly on:  
  
- [Storage need of storage](Storage.md#all_services_storage_needs)
- [Data replication factor of storage](Storage.md#data_replication_factor)
- [Active storage required for storage](Storage.md#active_storage_required)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_long_term_storage_required_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_long_term_storage_required.html' target='_blank'>link to Long term storage required for storage’s full calculation graph</a>.

### nb_of_idle_instances  
ExplainableQuantity in dimensionless, representing the number of idle storage units for storage.  
  
Depends directly on:  
  
- [Long term storage required for storage](Storage.md#long_term_storage_required)
- [Storage capacity of storage](Storage.md#storage_capacity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_nb_of_idle_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_nb_of_idle_instances.html' target='_blank'>link to Number of idle storage units for storage’s full calculation graph</a>.

### nb_of_active_instances  
ExplainableQuantity in dimensionless, representing the number of active instances for storage.  
  
Depends directly on:  
  
- [Active storage required for storage](Storage.md#active_storage_required)
- [Storage capacity of storage](Storage.md#storage_capacity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_nb_of_active_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_nb_of_active_instances.html' target='_blank'>link to Number of active instances for storage’s full calculation graph</a>.

### all_services_cpu_needs  
Representation of the evolution throughout a typical day of the cpu needs of all services running on storage by 24 values in core.  
  
Depends directly on:  
  
- [service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_all_services_cpu_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_all_services_cpu_needs.html' target='_blank'>link to CPU needs of all services running on storage’s full calculation graph</a>.

### all_services_ram_needs  
Representation of the evolution throughout a typical day of the ram needs of all services running on storage by 24 values in gigabyte.  
  
Depends directly on:  
  
- [service hour by hour ram need](Service.md#hour_by_hour_ram_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_all_services_ram_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_all_services_ram_needs.html' target='_blank'>link to RAM needs of all services running on storage’s full calculation graph</a>.

### fraction_of_time_in_use  
ExplainableQuantity in dimensionless, representing the fraction of time in use of storage.  
  
Depends directly on:  
  
- [CPU needs of all services running on storage](Storage.md#all_services_cpu_needs)
- [RAM needs of all services running on storage](Storage.md#all_services_ram_needs)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_fraction_of_time_in_use_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_fraction_of_time_in_use.html' target='_blank'>link to Fraction of time in use of storage’s full calculation graph</a>.

### nb_of_instances  
ExplainableQuantity in dimensionless, representing the number of total instances for storage.  
  
Depends directly on:  
  
- [Number of active instances for storage](Storage.md#nb_of_active_instances)
- [Number of idle storage units for storage](Storage.md#nb_of_idle_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_nb_of_instances.html' target='_blank'>link to Number of total instances for storage’s full calculation graph</a>.

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the instances of storage fabrication footprint.  
  
Depends directly on:  
  
- [Carbon footprint fabrication of storage](Storage.md#carbon_footprint_fabrication)
- [Number of total instances for storage](Storage.md#nb_of_instances)
- [Lifespan of storage](Storage.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_instances_fabrication_footprint.html' target='_blank'>link to Instances of storage fabrication footprint’s full calculation graph</a>.

### instances_power  
ExplainableQuantity in kilowatt_hour / year, representing the storage power for storage.  
  
Depends directly on:  
  
- [Number of active instances for storage](Storage.md#nb_of_active_instances)
- [Power of storage](Storage.md#power)
- [PUE of storage](Storage.md#power_usage_effectiveness)
- [Fraction of time in use of storage](Storage.md#fraction_of_time_in_use)
- [Number of idle storage units for storage](Storage.md#nb_of_idle_instances)
- [Idle power of storage](Storage.md#idle_power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_instances_power_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_instances_power.html' target='_blank'>link to Storage power for storage’s full calculation graph</a>.

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of storage.  
  
Depends directly on:  
  
- [Storage power for storage](Storage.md#instances_power)
- [Average carbon intensity of storage electricity](Storage.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_energy_footprint.html' target='_blank'>link to Energy footprint of storage’s full calculation graph</a>.
