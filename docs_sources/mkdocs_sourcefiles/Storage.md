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

### data_storage_duration
data storage duration of storage in hour.

### base_storage_need
storage initial storage need in terabyte.


## Backwards links

- [Service](Service.md)


## Calculated attributes

### all_services_storage_needs  
storage need of storage in terabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly service storage need](Service.md#storage_needed)
- [Data replication factor of storage](Storage.md#data_replication_factor)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_all_services_storage_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_all_services_storage_needs.html' target='_blank'>link to Storage need of storage’s full calculation graph</a>.

### storage_dumps  
storage dumps for storage in terabyte.  
  
Example value: 8749 values from 2027-01-01 10:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [-0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0],  
    last 10 vals [-0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0]  
  
Depends directly on:  
  
- [Storage need of storage](Storage.md#all_services_storage_needs)
- [Data storage duration of storage](Storage.md#data_storage_duration)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_storage_dumps_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_storage_dumps.html' target='_blank'>link to Storage dumps for storage’s full calculation graph</a>.

### storage_delta  
hourly storage delta for storage in terabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, -0.0, -0.0, 0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.0]  
  
Depends directly on:  
  
- [Storage need of storage](Storage.md#all_services_storage_needs)
- [Storage dumps for storage](Storage.md#storage_dumps)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_storage_delta_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_storage_delta.html' target='_blank'>link to Hourly storage delta for storage’s full calculation graph</a>.

### full_cumulative_storage_need  
full cumulative storage need for storage in terabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]  
  
Depends directly on:  
  
- [Hourly storage delta for storage](Storage.md#storage_delta)
- [storage initial storage need](Storage.md#base_storage_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_full_cumulative_storage_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_full_cumulative_storage_need.html' target='_blank'>link to Full cumulative storage need for storage’s full calculation graph</a>.

### nb_of_active_instances  
hourly number of active instances for storage in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly storage delta for storage](Storage.md#storage_delta)
- [Storage dumps for storage](Storage.md#storage_dumps)
- [Storage capacity of storage](Storage.md#storage_capacity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_nb_of_active_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_nb_of_active_instances.html' target='_blank'>link to Hourly number of active instances for storage’s full calculation graph</a>.

### all_services_cpu_needs  
cpu needs of all services running on storage in core.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in core:  
    first 10 vals [0.4, 0.27, 0.07, 0.33, 0.2, 0.27, 0.53, 0.07, 0.6, 0.6],  
    last 10 vals [0.33, 0.33, 0.07, 0.6, 0.33, 0.27, 0.13, 0.4, 0.27, 0.6]  
  
Depends directly on:  
  
- [service hour by hour cpu need](Service.md#hour_by_hour_cpu_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_all_services_cpu_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_all_services_cpu_needs.html' target='_blank'>link to CPU needs of all services running on storage’s full calculation graph</a>.

### all_services_ram_needs  
ram needs of all services running on storage in gigabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in GB:  
    first 10 vals [0.02, 0.01, 0.0, 0.02, 0.01, 0.01, 0.03, 0.0, 0.03, 0.03],  
    last 10 vals [0.02, 0.02, 0.0, 0.03, 0.02, 0.01, 0.01, 0.02, 0.01, 0.03]  
  
Depends directly on:  
  
- [service hour by hour ram need](Service.md#hour_by_hour_ram_need)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_all_services_ram_needs_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_all_services_ram_needs.html' target='_blank'>link to RAM needs of all services running on storage’s full calculation graph</a>.

### raw_nb_of_instances  
hourly raw number of instances for storage in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]  
  
Depends directly on:  
  
- [Full cumulative storage need for storage](Storage.md#full_cumulative_storage_need)
- [Storage capacity of storage](Storage.md#storage_capacity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_raw_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_raw_nb_of_instances.html' target='_blank'>link to Hourly raw number of instances for storage’s full calculation graph</a>.

### nb_of_instances  
hourly number of instances for storage in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  
    last 10 vals [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]  
  
Depends directly on:  
  
- [Hourly raw number of instances for storage](Storage.md#raw_nb_of_instances)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_nb_of_instances_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_nb_of_instances.html' target='_blank'>link to Hourly number of instances for storage’s full calculation graph</a>.

### instances_fabrication_footprint  
hourly storage instances fabrication footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly number of instances for storage](Storage.md#nb_of_instances)
- [Carbon footprint fabrication of storage](Storage.md#carbon_footprint_fabrication)
- [Lifespan of storage](Storage.md#lifespan)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_instances_fabrication_footprint.html' target='_blank'>link to Hourly storage instances fabrication footprint’s full calculation graph</a>.

### instances_energy  
storage energy for storage in hour * watt.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in W * h:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly number of active instances for storage](Storage.md#nb_of_active_instances)
- [Power of storage](Storage.md#power)
- [PUE of storage](Storage.md#power_usage_effectiveness)
- [Hourly number of instances for storage](Storage.md#nb_of_instances)
- [Idle power of storage](Storage.md#idle_power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_instances_energy_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_instances_energy.html' target='_blank'>link to Storage energy for storage’s full calculation graph</a>.

### energy_footprint  
hourly storage energy footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Storage energy for storage](Storage.md#instances_energy)
- [Average carbon intensity of storage electricity](Storage.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/storage_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/storage_energy_footprint.html' target='_blank'>link to Hourly storage energy footprint’s full calculation graph</a>.
