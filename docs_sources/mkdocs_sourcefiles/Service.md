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
Representation of the evolution throughout a typical day of the service hour by hour ram need by 24 values in gigabyte.  
  
Depends directly on:  
  
- [usage pattern UTC](DevicePopulation.md#utc_time_intervals_per_up)
- [RAM needed on server server to process streaming](Job.md#ram_needed)
- [Request duration to service in streaming](Job.md#request_duration)
- [Duration of user journey](UserJourney.md#duration)
- [Number of user journeys in parallel during usage pattern](DevicePopulation.md#nb_user_journeys_in_parallel_during_usage_per_up)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/service_hour_by_hour_ram_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/service_hour_by_hour_ram_need.html' target='_blank'>link to service hour by hour ram need’s full calculation graph</a>.

### hour_by_hour_cpu_need  
Representation of the evolution throughout a typical day of the service hour by hour cpu need by 24 values in core.  
  
Depends directly on:  
  
- [usage pattern UTC](DevicePopulation.md#utc_time_intervals_per_up)
- [CPU needed on server server to process streaming](Job.md#cpu_needed)
- [Request duration to service in streaming](Job.md#request_duration)
- [Duration of user journey](UserJourney.md#duration)
- [Number of user journeys in parallel during usage pattern](DevicePopulation.md#nb_user_journeys_in_parallel_during_usage_per_up)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/service_hour_by_hour_cpu_need_depth1.html"
  
You can also visit the <a href='../calculus_graphs/service_hour_by_hour_cpu_need.html' target='_blank'>link to service hour by hour cpu need’s full calculation graph</a>.

### storage_needed  
ExplainableQuantity in terabyte / year, representing the storage needed for service.  
  
Depends directly on:  
  
- [Data upload of request streaming](Job.md#data_upload)
- [User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/service_storage_needed_depth1.html"
  
You can also visit the <a href='../calculus_graphs/service_storage_needed.html' target='_blank'>link to Storage needed for service’s full calculation graph</a>.
