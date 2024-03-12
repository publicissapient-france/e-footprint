# UsagePattern

## Params

### name
A human readable description of the object.

### user_journey
An instance of [UserJourney](UserJourney.md).

### device_population
An instance of [DevicePopulation](DevicePopulation.md).

### network
An instance of [Network](Network.md).

### user_journey_freq_per_user
usage frequency in usage pattern in user_journey / user / year.

### time_intervals
description to be done


## Backwards links

- [System](System.md)


## Calculated attributes

### hourly_usage  
Representation of the evolution throughout a typical day of the usage pattern local timezone hourly usage by 24 values in dimensionless.  
  
Depends directly on:  
  
- [usage pattern time intervals in local timezone from hypothesis](UsagePattern.md#time_intervals)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_hourly_usage_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_hourly_usage.html' target='_blank'>link to usage pattern local timezone hourly usage’s full calculation graph</a>.

### usage_time_fraction  
ExplainableQuantity in dimensionless, representing the usage time fraction of usage pattern.  
  
Depends directly on:  
  
- [usage pattern local timezone hourly usage](UsagePattern.md#hourly_usage)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_usage_time_fraction_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_usage_time_fraction.html' target='_blank'>link to Usage time fraction of usage pattern’s full calculation graph</a>.
