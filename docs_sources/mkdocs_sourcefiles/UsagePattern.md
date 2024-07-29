# UsagePattern

## Params

### name
A human readable description of the object.

### user_journey
An instance of [UserJourney](UserJourney.md).

### devices
A list of [Hardwares](Hardware.md).

### network
An instance of [Network](Network.md).

### country
An instance of [Country](Country.md).

### user_journey_freq
usage frequency in usage pattern in user_journey / year.

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

### utc_time_intervals  
Representation of the evolution throughout a typical day of the usage pattern utc by 24 values in dimensionless.  
  
Depends directly on:  
  
- [usage pattern local timezone hourly usage](UsagePattern.md#hourly_usage)
- [devices country timezone from user data](Country.md#timezone)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_utc_time_intervals_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_utc_time_intervals.html' target='_blank'>link to usage pattern UTC’s full calculation graph</a>.

### nb_user_journeys_in_parallel_during_usage  
ExplainableQuantity in user_journey, representing the number of user journeys in parallel during usage pattern.  
  
Depends directly on:  
  
- [Usage frequency in usage pattern](UsagePattern.md#user_journey_freq)
- [Duration of user journey](UserJourney.md#duration)
- [Usage time fraction of usage pattern](UsagePattern.md#usage_time_fraction)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_nb_user_journeys_in_parallel_during_usage_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_nb_user_journeys_in_parallel_during_usage.html' target='_blank'>link to Number of user journeys in parallel during usage pattern’s full calculation graph</a>.

### devices_power  
ExplainableQuantity in kilowatt_hour / year, representing the power of usage pattern devices.  
  
Depends directly on:  
  
- [Usage frequency in usage pattern](UsagePattern.md#user_journey_freq)
- [Power of device on which the user journey is made](Hardware.md#power)
- [Duration of user journey](UserJourney.md#duration)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_devices_power_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_devices_power.html' target='_blank'>link to Power of usage pattern devices’s full calculation graph</a>.

### devices_energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of usage pattern.  
  
Depends directly on:  
  
- [Power of usage pattern devices](UsagePattern.md#devices_power)
- [Average carbon intensity of devices country](Country.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_devices_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_devices_energy_footprint.html' target='_blank'>link to Energy footprint of usage pattern’s full calculation graph</a>.

### devices_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the devices fabrication footprint of usage pattern.  
  
Depends directly on:  
  
- [Usage frequency in usage pattern](UsagePattern.md#user_journey_freq)
- [Carbon footprint fabrication of device on which the user journey is made](Hardware.md#carbon_footprint_fabrication)
- [Duration of user journey](UserJourney.md#duration)
- [Lifespan of device on which the user journey is made](Hardware.md#lifespan)
- [device on which the user journey is made fraction of usage time](Hardware.md#fraction_of_usage_time)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_devices_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_devices_fabrication_footprint.html' target='_blank'>link to Devices fabrication footprint of usage pattern’s full calculation graph</a>.

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the usage pattern total energy footprint.  
  
Depends directly on:  
  
- [Energy footprint of usage pattern](UsagePattern.md#devices_energy_footprint)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_energy_footprint.html' target='_blank'>link to usage pattern total energy footprint’s full calculation graph</a>.

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the usage pattern total fabrication footprint.  
  
Depends directly on:  
  
- [Devices fabrication footprint of usage pattern](UsagePattern.md#devices_fabrication_footprint)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_instances_fabrication_footprint.html' target='_blank'>link to usage pattern total fabrication footprint’s full calculation graph</a>.
