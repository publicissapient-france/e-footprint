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
  
Depends directly on ['[Time spent on step user journey step](UserJourneyStep.md#user_time_spent)'] through the following formula:

Duration of user journey=Time spent on step user journey step  
  
See Duration of user journey calculation graph at <a href='../calculus_graphs/user_journey_duration.html' target='_blank'>this link</a>

### data_download  
ExplainableQuantity in gigabyte / user_journey, representing the data download of user journey.  
  
Depends directly on ['[Data download of request user journey step](UserJourneyStep.md#data_download)'] through the following formula:

Data download of user journey=Data download of request user journey step  
  
See Data download of user journey calculation graph at <a href='../calculus_graphs/user_journey_data_download.html' target='_blank'>this link</a>

### data_upload  
ExplainableQuantity in kilobyte / user_journey, representing the data upload of user journey.  
  
Depends directly on ['[Data upload of request user journey step](UserJourneyStep.md#data_upload)'] through the following formula:

Data upload of user journey=Data upload of request user journey step  
  
See Data upload of user journey calculation graph at <a href='../calculus_graphs/user_journey_data_upload.html' target='_blank'>this link</a>
