# Job

## Params

### name
A human readable description of the object.

### service
An instance of [Service](Service.md).

### data_upload
data upload of request streaming in megabyte.

### data_download
data download of request streaming in megabyte.

### request_duration
request duration to service in streaming in hour.

### cpu_needed
cpu needed on server server to process streaming in core.

### ram_needed
ram needed on server server to process streaming in megabyte.

### job_type
description to be done

### description
description to be done


## Backwards links

- [UserJourneyStep](UserJourneyStep.md)


## Calculated attributes

### hourly_occurrences_per_usage_pattern  
Dictionary with UsagePattern as keys and 
                        hourly streaming occurrences in usage pattern as values, in dimensionless.  
  
Example value: {  
id-ccd50d-usage-pattern: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [2, 5, 9, 1, 3, 8, 6, 4, 2, 2],  
    last 10 vals [4, 7, 5, 7, 1, 3, 7, 4, 3, 1],   
}  
  
Depends directly on:  
  
- [usage pattern UTC](UsagePattern.md#utc_hourly_user_journey_starts)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_occurrences_per_usage_pattern_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_occurrences_per_usage_pattern.html' target='_blank'>link to Hourly streaming occurrences in usage pattern’s full calculation graph</a>.

### hourly_avg_occurrences_per_usage_pattern  
Dictionary with UsagePattern as keys and 
                        average hourly streaming occurrences in usage pattern as values, in dimensionless.  
  
Example value: {  
id-ccd50d-usage-pattern: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.13, 0.33, 0.6, 0.07, 0.2, 0.53, 0.4, 0.27, 0.13, 0.13],  
    last 10 vals [0.27, 0.47, 0.33, 0.47, 0.07, 0.2, 0.47, 0.27, 0.2, 0.07],   
}  
  
Depends directly on:  
  
- [Hourly streaming occurrences in usage pattern](Job.md#hourly_occurrences_per_usage_pattern)
- [Request duration to service in streaming](Job.md#request_duration)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_avg_occurrences_per_usage_pattern_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_avg_occurrences_per_usage_pattern.html' target='_blank'>link to Average hourly streaming occurrences in usage pattern’s full calculation graph</a>.

### hourly_data_upload_per_usage_pattern  
Dictionary with UsagePattern as keys and 
                        hourly data upload for streaming in usage pattern as values, in terabyte.  
  
Example value: {  
id-ccd50d-usage-pattern: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   
}  
  
Depends directly on:  
  
- [Hourly streaming occurrences in usage pattern](Job.md#hourly_occurrences_per_usage_pattern)
- [Data upload of request streaming](Job.md#data_upload)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_data_upload_per_usage_pattern_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_data_upload_per_usage_pattern.html' target='_blank'>link to Hourly data upload for streaming in usage pattern’s full calculation graph</a>.

### hourly_data_download_per_usage_pattern  
Dictionary with UsagePattern as keys and 
                        hourly data download for streaming in usage pattern as values, in megabyte.  
  
Example value: {  
id-ccd50d-usage-pattern: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in MB:  
    first 10 vals [1600.0, 4000.0, 7200.0, 800.0, 2400.0, 6400.0, 4800.0, 3200.0, 1600.0, 1600.0],  
    last 10 vals [3200.0, 5600.0, 4000.0, 5600.0, 800.0, 2400.0, 5600.0, 3200.0, 2400.0, 800.0],   
}  
  
Depends directly on:  
  
- [Hourly streaming occurrences in usage pattern](Job.md#hourly_occurrences_per_usage_pattern)
- [Data download of request streaming](Job.md#data_download)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_data_download_per_usage_pattern_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_data_download_per_usage_pattern.html' target='_blank'>link to Hourly data download for streaming in usage pattern’s full calculation graph</a>.

### hourly_occurrences_across_usage_patterns  
hourly streaming occurrences across usage patterns in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [2, 5, 9, 1, 3, 8, 6, 4, 2, 2],  
    last 10 vals [4, 7, 5, 7, 1, 3, 7, 4, 3, 1]  
  
Depends directly on:  
  
- [Hourly streaming occurrences in usage pattern](Job.md#hourly_occurrences_per_usage_pattern)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_occurrences_across_usage_patterns_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_occurrences_across_usage_patterns.html' target='_blank'>link to Hourly streaming occurrences across usage patterns’s full calculation graph</a>.

### hourly_avg_occurrences_across_usage_patterns  
hourly streaming average occurrences across usage patterns in dimensionless.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in dimensionless:  
    first 10 vals [0.13, 0.33, 0.6, 0.07, 0.2, 0.53, 0.4, 0.27, 0.13, 0.13],  
    last 10 vals [0.27, 0.47, 0.33, 0.47, 0.07, 0.2, 0.47, 0.27, 0.2, 0.07]  
  
Depends directly on:  
  
- [Average hourly streaming occurrences in usage pattern](Job.md#hourly_avg_occurrences_per_usage_pattern)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_avg_occurrences_across_usage_patterns_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_avg_occurrences_across_usage_patterns.html' target='_blank'>link to Hourly streaming average occurrences across usage patterns’s full calculation graph</a>.

### hourly_data_upload_across_usage_patterns  
hourly streaming data upload across usage patterns in terabyte.  
  
Example value: 26281 values from 2024-12-31 22:00:00 to 2027-12-31 22:00:00 in TB:  
    first 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  
    last 10 vals [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  
  
Depends directly on:  
  
- [Hourly data upload for streaming in usage pattern](Job.md#hourly_data_upload_per_usage_pattern)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/streaming_hourly_data_upload_across_usage_patterns_depth1.html"
  
You can also visit the <a href='../calculus_graphs/streaming_hourly_data_upload_across_usage_patterns.html' target='_blank'>link to Hourly streaming data upload across usage patterns’s full calculation graph</a>.
