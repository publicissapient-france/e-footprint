# Network

## Params

### name
A human readable description of the object.

### bandwidth_energy_intensity
bandwith energy intensity of network in kilowatt_hour / gigabyte.


## Backwards links

- [UsagePattern](UsagePattern.md)


## Calculated attributes

### energy_footprint  
hourly network energy footprint in kilogram.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in kg:  
    first 10 vals [0.0, 0.01, 0.02, 0.01, 0.02, 0.01, 0.02, 0.0, 0.02, 0.03],  
    last 10 vals [0.03, 0.0, 0.01, 0.02, 0.01, 0.01, 0.03, 0.01, 0.03, 0.0]  
  
Depends directly on:  
  
- [Hourly data upload for streaming in usage pattern](Job.md#hourly_data_upload_per_usage_pattern)
- [Hourly data download for streaming in usage pattern](Job.md#hourly_data_download_per_usage_pattern)
- [bandwith energy intensity of network](Network.md#bandwidth_energy_intensity)
- [Average carbon intensity of devices country](Country.md#average_carbon_intensity)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/network_energy_footprint_depth1.html"
  
You can also visit the <a href='../calculus_graphs/network_energy_footprint.html' target='_blank'>link to Hourly network energy footprint’s full calculation graph</a>.
