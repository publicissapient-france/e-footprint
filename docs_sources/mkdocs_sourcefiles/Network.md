# Network

## Params

### name
A human readable description of the object.

### bandwidth_energy_intensity
bandwith energy intensity of network in kilowatt_hour / gigabyte.


## Backwards links

- [UsagePattern](UsagePattern.md)


## Calculated attributes

### data_download  
ExplainableQuantity in terabyte / year, representing the data download in network.  
  
Depends directly on:  
  
- [Data download of user journey](UserJourney.md#data_download)
- [User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/network_data_download_depth1.html"
  
You can also visit the <a href='../calculus_graphs/network_data_download.html' target='_blank'>link to Data download in network’s full calculation graph</a>.

### data_upload  
ExplainableQuantity in terabyte / year, representing the data upload in network.  
  
Depends directly on:  
  
- [Data upload of user journey](UserJourney.md#data_upload)
- [User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/network_data_upload_depth1.html"
  
You can also visit the <a href='../calculus_graphs/network_data_upload.html' target='_blank'>link to Data upload in network’s full calculation graph</a>.

### energy_footprint  
ExplainableQuantity in kilogram / year, representing the energy footprint of network.  
  
Depends directly on:  
  
- [User journey frequency of usage pattern](DevicePopulation.md#user_journey_freq_per_up)
- [bandwith energy intensity of network](Network.md#bandwidth_energy_intensity)
- [Data download of user journey](UserJourney.md#data_download)
- [Data upload of user journey](UserJourney.md#data_upload)
- [Average carbon intensity of devices country](Country.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/network_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/network_energy_footprint.html' target='_blank'>link to Energy footprint of network’s full calculation graph</a>.
