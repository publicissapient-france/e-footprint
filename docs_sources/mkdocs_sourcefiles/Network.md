# Network

## Params

### name
A human readable description of the object.

### bandwidth_energy_intensity
SourceValue with Quantity in kilowatt_hour / gigabyte, representing the bandwith energy intensity of network.


## Backwards links

- [UsagePattern](UsagePattern.md)


## Calculated attributes

### data_download  
ExplainableQuantity in terabyte / year, representing the data download in network.  
  
Depends directly on ['[Data download of user journey](UserJourney.md#data_download)', '[User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)'] through the following formula:

Data download in network=Data download of user journey * User journey frequency of usage pattern  
  
See Data download in network calculation graph at <a href='../calculus_graphs/network_data_download.html' target='_blank'>this link</a>

### data_upload  
ExplainableQuantity in terabyte / year, representing the data upload in network.  
  
Depends directly on ['[Data upload of user journey](UserJourney.md#data_upload)', '[User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)'] through the following formula:

Data upload in network=Data upload of user journey * User journey frequency of usage pattern  
  
See Data upload in network calculation graph at <a href='../calculus_graphs/network_data_upload.html' target='_blank'>this link</a>

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of network.  
  
Depends directly on ['[User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)', '[bandwith energy intensity of network](Network.md#bandwidth_energy_intensity)', '[Data download of user journey](UserJourney.md#data_download)', '[Data upload of user journey](UserJourney.md#data_upload)', '[Average carbon intensity of devices country](Country.md#average_carbon_intensity)'] through the following formula:

Energy footprint of network=User journey frequency of usage pattern * network consumption during user journey * Average carbon intensity of devices country  
  
See Energy footprint of network calculation graph at <a href='../calculus_graphs/network_energy_footprint.html' target='_blank'>this link</a>
