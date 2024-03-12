# UserJourney

## Params

### name
A human readable description of the object.

### uj_steps
A list of [UserJourneySteps](UserJourneyStep.md).


## Backwards links

- [UsagePattern](UsagePattern.md)


## Calculated attributes

### duration  
ExplainableQuantity in minute / user_journey, representing the duration of user journey.  
  
Depends directly on:  
  
- [Time spent on step user journey step](UserJourneyStep.md#user_time_spent)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/user_journey_duration_depth1.html"
  
You can also visit the <a href='../calculus_graphs/user_journey_duration.html' target='_blank'>link to Duration of user journey’s full calculation graph</a>.

### data_download  
ExplainableQuantity in gigabyte / user_journey, representing the data download of user journey.  
  
Depends directly on:  
  
- [Data download of request user journey step](UserJourneyStep.md#data_download)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/user_journey_data_download_depth1.html"
  
You can also visit the <a href='../calculus_graphs/user_journey_data_download.html' target='_blank'>link to Data download of user journey’s full calculation graph</a>.

### data_upload  
ExplainableQuantity in kilobyte / user_journey, representing the data upload of user journey.  
  
Depends directly on:  
  
- [Data upload of request user journey step](UserJourneyStep.md#data_upload)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/user_journey_data_upload_depth1.html"
  
You can also visit the <a href='../calculus_graphs/user_journey_data_upload.html' target='_blank'>link to Data upload of user journey’s full calculation graph</a>.
