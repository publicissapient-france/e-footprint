# Service

## Params

### name
A human readable description of the object.

### server
An instance of [Autoscaling](Autoscaling.md).

### storage
An instance of [Storage](Storage.md).

### base_ram_consumption
SourceValue with Quantity in megabyte, representing the base ram consumption of service.

### base_cpu_consumption
SourceValue with Quantity in core, representing the base cpu consumption of service.


## Backwards links

- [UserJourneyStep](UserJourneyStep.md)


## Calculated attributes

### hour_by_hour_ram_need  
Representation of the evolution throughout a typical day of the service hour by hour ram need by 24 values in gigabyte.  
  
Depends directly on ['[usage pattern UTC](DevicePopulation.md#utc_time_intervals_per_up)', '[RAM needed on server server to process user journey step](UserJourneyStep.md#ram_needed)', '[Request duration to service in user journey step](UserJourneyStep.md#request_duration)', '[Duration of user journey](UserJourney.md#duration)', '[Number of user journeys in parallel during usage pattern](DevicePopulation.md#nb_user_journeys_in_parallel_during_usage_per_up)'] through the following formula:

service hour by hour ram need=usage pattern UTC * Average ram needed over usage pattern to process user journey step * Number of user journeys in parallel during usage pattern  
  
See service hour by hour ram need calculation graph at <a href='../calculus_graphs/service_hour_by_hour_ram_need.html' target='_blank'>this link</a>

### hour_by_hour_cpu_need  
Representation of the evolution throughout a typical day of the service hour by hour cpu need by 24 values in core.  
  
Depends directly on ['[usage pattern UTC](DevicePopulation.md#utc_time_intervals_per_up)', '[CPU needed on server server to process user journey step](UserJourneyStep.md#cpu_needed)', '[Request duration to service in user journey step](UserJourneyStep.md#request_duration)', '[Duration of user journey](UserJourney.md#duration)', '[Number of user journeys in parallel during usage pattern](DevicePopulation.md#nb_user_journeys_in_parallel_during_usage_per_up)'] through the following formula:

service hour by hour cpu need=usage pattern UTC * Average cpu needed over usage pattern to process user journey step * Number of user journeys in parallel during usage pattern  
  
See service hour by hour cpu need calculation graph at <a href='../calculus_graphs/service_hour_by_hour_cpu_need.html' target='_blank'>this link</a>

### storage_needed  
ExplainableQuantity in terabyte / year, representing the storage needed for service.  
  
Depends directly on ['[Data upload of request user journey step](UserJourneyStep.md#data_upload)', '[User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)'] through the following formula:

Storage needed for service=Data upload of request user journey step * (User journey frequency of usage pattern)  
  
See Storage needed for service calculation graph at <a href='../calculus_graphs/service_storage_needed.html' target='_blank'>this link</a>
