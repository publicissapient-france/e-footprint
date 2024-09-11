# Service

## Params

### name
A human readable description of the object.

### server
An instance of [Autoscaling](Autoscaling.md).

### storage
An instance of [Storage](Storage.md).

### base_ram_consumption
base ram consumption of service in megabyte.

### base_cpu_consumption
base cpu consumption of service in core.


## Backwards links

- [Job](Job.md)


## Calculated attributes

### hour_by_hour_ram_need  
service hour by hour ram need in gigabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in GB:  
    first 10 vals [0.02, 0.01, 0.0, 0.02, 0.01, 0.01, 0.03, 0.0, 0.03, 0.03],  
    last 10 vals [0.02, 0.02, 0.0, 0.03, 0.02, 0.01, 0.01, 0.02, 0.01, 0.03]  
  
Depends directly on:  
  
- [Hourly streaming average occurrences across usage patterns](Job.md#hourly_avg_occurrences_across_usage_patterns)
- [RAM needed on server server to process streaming](Job.md#ram_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/service_hour_by_hour_ram_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/service_hour_by_hour_ram_need.html' target='_blank'>link to service hour by hour ram need’s full calculation graph</a>.

### hour_by_hour_cpu_need  
service hour by hour cpu need in core.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in core:  
    first 10 vals [0.4, 0.27, 0.07, 0.33, 0.2, 0.27, 0.53, 0.07, 0.6, 0.6],  
    last 10 vals [0.33, 0.33, 0.07, 0.6, 0.33, 0.27, 0.13, 0.4, 0.27, 0.6]  
  
Depends directly on:  
  
- [Hourly streaming average occurrences across usage patterns](Job.md#hourly_avg_occurrences_across_usage_patterns)
- [CPU needed on server server to process streaming](Job.md#cpu_needed)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/service_hour_by_hour_cpu_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/service_hour_by_hour_cpu_need.html' target='_blank'>link to service hour by hour cpu need’s full calculation graph</a>.

### storage_needed  
hourly service storage need in terabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly streaming data upload across usage patterns](Job.md#hourly_data_upload_across_usage_patterns)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/service_storage_needed_depth1.html"
  
You can also visit the <a href='../calculus_graphs/service_storage_needed.html' target='_blank'>link to Hourly service storage need’s full calculation graph</a>.
