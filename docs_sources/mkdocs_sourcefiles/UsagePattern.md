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

### hourly_user_journey_starts
description to be done


## Backwards links

- [System](System.md)


## Calculated attributes

### utc_hourly_user_journey_starts  
usage pattern utc in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [1, 3, 5, 2, 6, 2, 5, 1, 5, 9],  
    last 10 vals [9, 1, 2, 5, 4, 4, 9, 3, 9, 1]  
  
Depends directly on:  
  
- [usage pattern hourly nb of visits from hypothesis](UsagePattern.md#hourly_user_journey_starts)
- [devices country timezone from user data](Country.md#timezone)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_utc_hourly_user_journey_starts_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_utc_hourly_user_journey_starts.html' target='_blank'>link to usage pattern UTC’s full calculation graph</a>.

### nb_user_journeys_in_parallel  
usage pattern hourly nb of user journeys in parallel in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.33, 1.0, 1.67, 0.67, 2.0, 0.67, 1.67, 0.33, 1.67, 3.0],  
    last 10 vals [3.0, 0.33, 0.67, 1.67, 1.33, 1.33, 3.0, 1.0, 3.0, 0.33]  
  
Depends directly on:  
  
- [usage pattern UTC](UsagePattern.md#utc_hourly_user_journey_starts)
- [Duration of user journey](UserJourney.md#duration)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_nb_user_journeys_in_parallel_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_nb_user_journeys_in_parallel.html' target='_blank'>link to usage pattern hourly nb of user journeys in parallel’s full calculation graph</a>.

### devices_energy  
energy consumed by usage pattern devices in kilowatt_hour.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kWh:  
    first 10 vals [0.02, 0.05, 0.08, 0.03, 0.1, 0.03, 0.08, 0.02, 0.08, 0.15],  
    last 10 vals [0.15, 0.02, 0.03, 0.08, 0.07, 0.07, 0.15, 0.05, 0.15, 0.02]  
  
Depends directly on:  
  
- [usage pattern hourly nb of user journeys in parallel](UsagePattern.md#nb_user_journeys_in_parallel)
- [Power of device on which the user journey is made](Hardware.md#power)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_devices_energy_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_devices_energy.html' target='_blank'>link to Energy consumed by usage pattern devices’s full calculation graph</a>.

### devices_energy_footprint  
energy footprint of usage pattern in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.0, 0.01, 0.0, 0.01, 0.0, 0.01, 0.0, 0.01, 0.01],  
    last 10 vals [0.01, 0.0, 0.0, 0.01, 0.01, 0.01, 0.01, 0.0, 0.01, 0.0]  
  
Depends directly on:  
  
- [Energy consumed by usage pattern devices](UsagePattern.md#devices_energy)
- [Average carbon intensity of devices country](Country.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_devices_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_devices_energy_footprint.html' target='_blank'>link to Energy footprint of usage pattern’s full calculation graph</a>.

### devices_fabrication_footprint  
devices fabrication footprint of usage pattern in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.01, 0.02, 0.01, 0.02, 0.01, 0.02, 0.0, 0.02, 0.03],  
    last 10 vals [0.03, 0.0, 0.01, 0.02, 0.01, 0.01, 0.03, 0.01, 0.03, 0.0]  
  
Depends directly on:  
  
- [usage pattern hourly nb of user journeys in parallel](UsagePattern.md#nb_user_journeys_in_parallel)
- [Carbon footprint fabrication of device on which the user journey is made](Hardware.md#carbon_footprint_fabrication)
- [Lifespan of device on which the user journey is made](Hardware.md#lifespan)
- [device on which the user journey is made fraction of usage time](Hardware.md#fraction_of_usage_time)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_devices_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_devices_fabrication_footprint.html' target='_blank'>link to Devices fabrication footprint of usage pattern’s full calculation graph</a>.

### energy_footprint  
usage pattern total energy footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.0, 0.01, 0.0, 0.01, 0.0, 0.01, 0.0, 0.01, 0.01],  
    last 10 vals [0.01, 0.0, 0.0, 0.01, 0.01, 0.01, 0.01, 0.0, 0.01, 0.0]  
  
Depends directly on:  
  
- [Energy footprint of usage pattern](UsagePattern.md#devices_energy_footprint)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_energy_footprint.html' target='_blank'>link to usage pattern total energy footprint’s full calculation graph</a>.

### instances_fabrication_footprint  
usage pattern total fabrication footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.01, 0.02, 0.01, 0.02, 0.01, 0.02, 0.0, 0.02, 0.03],  
    last 10 vals [0.03, 0.0, 0.01, 0.02, 0.01, 0.01, 0.03, 0.01, 0.03, 0.0]  
  
Depends directly on:  
  
- [Devices fabrication footprint of usage pattern](UsagePattern.md#devices_fabrication_footprint)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/usage_pattern_instances_fabrication_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/usage_pattern_instances_fabrication_footprint.html' target='_blank'>link to usage pattern total fabrication footprint’s full calculation graph</a>.
