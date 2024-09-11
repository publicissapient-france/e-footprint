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
ExplainableQuantity in hour, representing the duration of user journey.  
  
Example value: 0.33 hour  
  
Depends directly on:  
  
- [Time spent on step 20 min streaming](UserJourneyStep.md#user_time_spent)  

through the following calculations:  

--8<-- "docs_sources/mkdocs_sourcefiles/calculus_graphs_depth1/user_journey_duration_depth1.html"
  
You can also visit the <a href='../calculus_graphs/user_journey_duration.html' target='_blank'>link to Duration of user journey’s full calculation graph</a>.
