# DevicePopulation

## Params

### name
A human readable description of the object.

### nb_devices
SourceValue with Quantity in user, representing the nb devices in device population.

### country
An instance of [Country](Country.md).

### devices
A list of [Hardwares](Hardware.md).


## Backwards links

- [UsagePattern](UsagePattern.md)


## Calculated attributes

### user_journey_freq_per_up
Description of ExplainableObjectDicts is not yes supported.

### nb_user_journeys_in_parallel_during_usage_per_up
Description of ExplainableObjectDicts is not yes supported.

### utc_time_intervals_per_up
Description of ExplainableObjectDicts is not yes supported.

### power  
ExplainableQuantity in kilowatt_hour / year, representing the power of device population devices.  
  
Depends directly on ['[User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)', '[Power of device on which the user journey is made](Hardware.md#power)', '[Duration of user journey](UserJourney.md#duration)'] through the following formula:

Power of device population devices=User journey frequency of usage pattern * Power of device on which the user journey is made * Duration of user journey  
  
See Power of device population devices calculation graph at <a href='../calculus_graphs/device_population_power.html' target='_blank'>this link</a>

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of device population.  
  
Depends directly on ['[Power of device population devices](DevicePopulation.md#power)', '[Average carbon intensity of devices country](Country.md#average_carbon_intensity)'] through the following formula:

Energy footprint of device population=Power of device population devices * Average carbon intensity of devices country  
  
See Energy footprint of device population calculation graph at <a href='../calculus_graphs/device_population_energy_footprint.html' target='_blank'>this link</a>

### instances_fabrication_footprint  
ExplainableQuantity in kilogram / year, representing the devices fabrication footprint of device population.  
  
Depends directly on ['[User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)', '[Carbon footprint fabrication of device on which the user journey is made](Hardware.md#carbon_footprint_fabrication)', '[Duration of user journey](UserJourney.md#duration)', '[Lifespan of device on which the user journey is made](Hardware.md#lifespan)', '[device on which the user journey is made fraction of usage time](Hardware.md#fraction_of_usage_time)'] through the following formula:

Devices fabrication footprint of device population=User journey frequency of usage pattern * device on which the user journey is made fabrication footprint over user journey  
  
See Devices fabrication footprint of device population calculation graph at <a href='../calculus_graphs/device_population_instances_fabrication_footprint.html' target='_blank'>this link</a>
