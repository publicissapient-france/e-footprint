# e-footprint quickstart

This notebook provides an example scenario that you can use to get familiar with the Python API of efootprint: the daily video consumption of all French households on a big streaming platform.

You will get to describe:

- the infrastructure involved (servers with auto-scaling settings, storage, service and network)
- the user journey involving 2 steps (Streaming, Upload)
- the usage pattern and the device population that executes it (the laptops of all French households)

## Import the packages

⚠ If this steps fails, remember to run *ipython kernel install --user --name=efootprint-kernel* _inside_ your python virtual environement (initializable with `poetry install`) to be able to select efootprint-kernel as the jupyter kernel.


```python
import os

from efootprint.abstract_modeling_classes.source_objects import SourceValue, Sources, SourceObject
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.core.usage.job import Job
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import Countries
from efootprint.constants.units import u
from efootprint.utils.object_relationships_graphs import USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE
from efootprint.builders.hardware.devices_defaults import default_laptop
```

## Define the infrastructure

An e-footprint object has a name and attributes describing its technical and environmental characteristics:


```python
server = Autoscaling(
    "server",
    carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
    power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
    lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
    idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
    ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
    cpu_cores=SourceValue(24 * u.core, Sources.HYPOTHESIS),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
    server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS))
```

Moreover, all e-footprint objects have a *calculated_attributes* attributes that shows the list of attributes that are setup as None and then computed by e-footprint when the modeling is over. For example, for our server:


```python
print(server)
```

    Autoscaling id-7f6395-server
     
    carbon_footprint_fabrication: 600 kilogram
    power: 300 watt
    lifespan: 6 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    server_utilization_rate: 0.9 dimensionless
    idle_power: 50 watt
    ram: 128 gigabyte
    cpu_cores: 24 core
    power_usage_effectiveness: 1.2 dimensionless
     
    calculated_attributes:
      available_ram_per_instance: None
      available_cpu_per_instance: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      raw_nb_of_instances: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_energy: None
      energy_footprint: None
    


More information on e-footprint objects’ calculated_attributes can be found in the [e-footprint documentation](https://boavizta.github.io/e-footprint/).


```python
storage = Storage(
    "SSD storage",
    carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
    idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
    storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(100 * u.g / u.kWh),
    data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS),
    data_storage_duration = SourceValue(2 * u.year, Sources.HYPOTHESIS),
    base_storage_need = SourceValue(100 * u.TB, Sources.HYPOTHESIS)
    )
```

Apart from environmental and technical attributes, e-footprint objects can link to other e-footprint objects. For example, the following service runs on the server and uploads data to the storage:


```python
service = Service(
    "Streaming platform",
    server=server,
    storage=storage,
    base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
    base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))
```

## Define the user journey

This is the modeling of the average daily usage of the streaming platform in France:


```python
streaming_step = UserJourneyStep(
    "20 min streaming",
    user_time_spent=SourceValue(20 * u.min, Sources.USER_DATA),
    jobs=[
        Job(
            "streaming",
            service=service,
            data_upload=SourceValue(0.05 * u.MB, Sources.USER_DATA),
            data_download=SourceValue(800 * u.MB, Sources.USER_DATA),
            request_duration=SourceValue(4 * u.min, Sources.HYPOTHESIS),
            cpu_needed=SourceValue(1 * u.core, Sources.HYPOTHESIS),
            ram_needed=SourceValue(50 * u.MB, Sources.HYPOTHESIS)
            )
        ]
    )
upload_step = UserJourneyStep(
    "1 min video capture then upload",
    user_time_spent=SourceValue(70 * u.s, Sources.USER_DATA),
    jobs=[
        Job(
            "video upload",
            service=service,
            data_upload=SourceValue(20 * u.MB, Sources.USER_DATA),
            data_download=SourceValue(0 * u.GB, Sources.USER_DATA),
            request_duration=SourceValue(2 * u.s, Sources.HYPOTHESIS),
            cpu_needed=SourceValue(1 * u.core, Sources.HYPOTHESIS),
            ram_needed=SourceValue(50 * u.MB, Sources.HYPOTHESIS)
        )
    ]
)
```

The user journey is then simply a list of user journey steps:


```python
user_journey = UserJourney("Mean video consumption user journey", uj_steps=[streaming_step, upload_step])
```

## Describe usage

An e-footprint usage pattern links a user journey to devices that run it, a network, a country, and the number of times the user journey gets executed hour by hour. 


```python
# Let’s build synthetic usage data by summing a linear growth with a sinusoidal fluctuation components, then adding daily variation
from datetime import datetime, timedelta

from efootprint.builders.time_builders import linear_growth_hourly_values

start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
nb_of_hours = 3 * 365 * 24

linear_growth = linear_growth_hourly_values(nb_of_hours, start_value=5000, end_value=100000, start_date=start_date)
linear_growth.set_label("Hourly user journeys linear growth component")

linear_growth.plot()
```


    
![png](tutorial_images/docs_tutorial.nbconvert_19_0.png)
    



```python
from efootprint.builders.time_builders import sinusoidal_fluct_hourly_values

sinusoidal_fluct = sinusoidal_fluct_hourly_values(
    nb_of_hours, sin_fluct_amplitude=3000, sin_fluct_period_in_hours=3 * 30 * 24, start_date=start_date)

lin_growth_plus_sin_fluct = (linear_growth + sinusoidal_fluct).set_label("Hourly user journeys linear growth with sinusoidal fluctuations")

lin_growth_plus_sin_fluct.plot()
```


    
![png](tutorial_images/docs_tutorial.nbconvert_20_0.png)
    



```python
# Let’s add daily variations because people use the system less at night
from efootprint.builders.time_builders import daily_fluct_hourly_values

daily_fluct = daily_fluct_hourly_values(nb_of_hours, fluct_scale=0.8, hour_of_day_for_min_value=4, start_date=start_date)
daily_fluct.set_label("Daily volume fluctuation")

daily_fluct.plot(xlims=[start_date, start_date+timedelta(days=1)])
```


    
![png](tutorial_images/docs_tutorial.nbconvert_21_0.png)
    



```python
hourly_user_journey_starts = lin_growth_plus_sin_fluct * daily_fluct
hourly_user_journey_starts.set_label("Hourly number of user journey started")

hourly_user_journey_starts.plot(xlims=[start_date, start_date + timedelta(days=7)])
```


    
![png](tutorial_images/docs_tutorial.nbconvert_22_0.png)
    



```python
# Over 3 years the daily fluctuation color the area between daily min and max number of hourly user journeys
hourly_user_journey_starts.plot()
```


    
![png](tutorial_images/docs_tutorial.nbconvert_23_0.png)
    



```python
network = Network(
        "WIFI network",
        bandwidth_energy_intensity=SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))

usage_pattern = UsagePattern(
    "Daily video streaming consumption",
    user_journey=user_journey,
    devices=[default_laptop()],
    network=network,
    country=Countries.FRANCE(),
    hourly_user_journey_starts=hourly_user_journey_starts
)

system = System("System", usage_patterns=[usage_pattern])
```

    2024-09-12 16:35:37,349 - INFO - Computing calculated attributes for System System
    2024-09-12 16:35:37,350 - INFO - Computing calculated attributes for UserJourney Mean video consumption user journey
    2024-09-12 16:35:37,351 - INFO - Computing calculated attributes for UsagePattern Daily video streaming consumption
    2024-09-12 16:35:37,481 - INFO - Computing calculated attributes for Job streaming
    2024-09-12 16:35:37,486 - INFO - Computing calculated attributes for Job video upload
    2024-09-12 16:35:37,491 - INFO - Computing calculated attributes for Service Streaming platform
    2024-09-12 16:35:37,499 - INFO - Computing calculated attributes for Network WIFI network
    2024-09-12 16:35:37,505 - INFO - Computing calculated attributes for Autoscaling server
    2024-09-12 16:35:37,518 - INFO - Computing calculated attributes for Storage SSD storage
    2024-09-12 16:35:37,543 - INFO - Finished computing System modeling


## Results

### Computed attributes

Now all calculated_attributes have been computed:


```python
print(server)
```

    Autoscaling id-7f6395-server
     
    carbon_footprint_fabrication: 600 kilogram
    power: 300 watt
    lifespan: 6 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    server_utilization_rate: 0.9 dimensionless
    idle_power: 50 watt
    ram: 128 gigabyte
    cpu_cores: 24 core
    power_usage_effectiveness: 1.2 dimensionless
     
    calculated_attributes:
      available_ram_per_instance: 114.9 gigabyte
      available_cpu_per_instance: 19.6 core
      all_services_cpu_needs: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in core:
        first 10 vals [201.67, 146.34, 103.76, 76.95, 67.89, 77.33, 104.78, 148.5, 205.65, 272.44],
        last 10 vals [11666.37, 12218.13, 12407.0, 12220.07, 11670.08, 10794.48, 9652.94, 8323.25, 6896.04, 5468.6]
      all_services_ram_needs: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in GB:
        first 10 vals [10.08, 7.32, 5.19, 3.85, 3.39, 3.87, 5.24, 7.43, 10.28, 13.62],
        last 10 vals [583.32, 610.91, 620.35, 611.0, 583.5, 539.72, 482.65, 416.16, 344.8, 273.43]
      raw_nb_of_instances: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in dimensionless:
        first 10 vals [10.29, 7.47, 5.29, 3.93, 3.46, 3.95, 5.35, 7.58, 10.49, 13.9],
        last 10 vals [595.22, 623.37, 633.01, 623.47, 595.41, 550.74, 492.5, 424.66, 351.84, 279.01]
      nb_of_instances: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in dimensionless:
        first 10 vals [11.0, 8.0, 6.0, 4.0, 4.0, 4.0, 6.0, 8.0, 11.0, 14.0],
        last 10 vals [596.0, 624.0, 634.0, 624.0, 596.0, 551.0, 493.0, 425.0, 352.0, 280.0]
      instances_fabrication_footprint: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in kg:
        first 10 vals [0.13, 0.09, 0.07, 0.05, 0.05, 0.05, 0.07, 0.09, 0.13, 0.16],
        last 10 vals [6.8, 7.12, 7.23, 7.12, 6.8, 6.29, 5.62, 4.85, 4.02, 3.19]
      instances_energy: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in kWh:
        first 10 vals [3.75, 2.72, 1.95, 1.42, 1.28, 1.42, 1.96, 2.75, 3.81, 5.01],
        last 10 vals [214.33, 224.45, 227.94, 224.48, 214.38, 198.28, 177.33, 152.9, 126.67, 100.5]
      energy_footprint: 26280 values from 2024-12-31 22:00:00 to 2027-12-31 21:00:00 in kg:
        first 10 vals [0.37, 0.27, 0.19, 0.14, 0.13, 0.14, 0.2, 0.28, 0.38, 0.5],
        last 10 vals [21.43, 22.45, 22.79, 22.45, 21.44, 19.83, 17.73, 15.29, 12.67, 10.05]
    


### System footprint overview


```python
system.plot_footprints_by_category_and_object("System footprints.html")
```
--8<-- "docs_sources/mkdocs_sourcefiles/System footprints.html"


### Object relationships graph

Hover over a node to get the numerical values of its environmental and technical attributes. For simplifying the graph the Network and Hardware nodes are not shown.


```python
usage_pattern.object_relationship_graph_to_file("object_relationships_graph.html", width="800px", height="500px",
    classes_to_ignore=USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE, notebook=True)
```

--8<-- "docs_sources/mkdocs_sourcefiles/object_relationships_graph.html"


### Calculus graph

Any e-footprint calculation can generate its calculation graph for full auditability. Hover on a calculus node to display its formula and numeric value.


```python
usage_pattern.devices_fabrication_footprint.calculus_graph_to_file(
    "device_population_fab_footprint_calculus_graph.html", width="800px", height="500px", notebook=True)
```

--8<-- "docs_sources/mkdocs_sourcefiles/device_population_fab_footprint_calculus_graph.html"


## Analysing the impact of a change
### Numeric input change
Any input change automatically triggers the computation of calculations that depend on the input. For example, let’s say that the average data download consumption of the streaming step decreased because of a change in default video quality:


```python
streaming_step.jobs[0].data_download = SourceValue(500 * u.MB, Sources.USER_DATA)
```


```python
system.plot_emission_diffs("bandwith reduction.png")
```

    Plotting the impact of streaming’s data_download changing from 800 megabyte to 500 megabyte



    
![png](tutorial_images/docs_tutorial.nbconvert_36_1.png)
    


### System structure change
Now let’s make a more complex change, like adding a conversation with a generative AI chatbot before streaming the video.
Numerical values don’t matter so much for the sake of this tutorial, please check out <a href="https://github.com/publicissapient-france/e-footprint-modelings" target="_blank">the e-footprint-modelings github repository</a> for a more detailed modeling of the impact of LLM training and inference.


```python
llm_server = Autoscaling(
    "Inference GPU server",
    carbon_footprint_fabrication=SourceValue(4900 * u.kg, Sources.HYPOTHESIS),
    power=SourceValue(6400 * u.W, Sources.HYPOTHESIS),
    lifespan=SourceValue(5 * u.year, Sources.HYPOTHESIS),
    idle_power=SourceValue(500 * u.W, Sources.HYPOTHESIS),
    ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
    cpu_cores=SourceValue(16 * u.core, Sources.HYPOTHESIS), # Used to represent GPUs because e-footprint doesn’t natively model GPU resources yet.
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(300 * u.g / u.kWh, Sources.HYPOTHESIS),
    server_utilization_rate=SourceValue(1 * u.dimensionless, Sources.HYPOTHESIS))
```


```python
service_inference = Service(
    "LLM inference", llm_server, storage, base_ram_consumption=SourceValue(0 * u.MB, Sources.HYPOTHESIS),
    base_cpu_consumption=SourceValue(0 * u.core, Sources.HYPOTHESIS))

llm_chat_step = UserJourneyStep(
    "Chat with LLM to select video", user_time_spent=SourceValue(1 * u.min, Sources.HYPOTHESIS),
    jobs=[Job("LLM API", service_inference, SourceValue(300 * u.kB, Sources.USER_DATA),
              SourceValue(300 * u.kB, Sources.USER_DATA), request_duration=SourceValue(5 * u.s, Sources.HYPOTHESIS),
              cpu_needed=SourceValue(16 * u.core, Sources.HYPOTHESIS),
              ram_needed=SourceValue(128 * u.GB, Sources.HYPOTHESIS))])
```


```python
# Adding the new step is simply an attribute update.
# Don’t use user_journey.uj_steps.append(llm_chat_step) as e-footprint recomputation logic wouldn’t be triggered
user_journey.uj_steps += [llm_chat_step]
```

    2024-09-12 16:35:39,647 - INFO - Computing calculated attributes for UserJourney Mean video consumption user journey
    2024-09-12 16:35:39,648 - INFO - Computing calculated attributes for UsagePattern Daily video streaming consumption
    2024-09-12 16:35:39,777 - INFO - Computing calculated attributes for Job streaming
    2024-09-12 16:35:39,782 - INFO - Computing calculated attributes for Job LLM API
    2024-09-12 16:35:39,787 - INFO - Computing calculated attributes for Job video upload
    2024-09-12 16:35:39,792 - INFO - Computing calculated attributes for Service Streaming platform
    2024-09-12 16:35:39,799 - INFO - Computing calculated attributes for Network WIFI network
    2024-09-12 16:35:39,806 - INFO - Computing calculated attributes for Service LLM inference
    2024-09-12 16:35:39,811 - INFO - Computing calculated attributes for Autoscaling server
    2024-09-12 16:35:39,823 - INFO - Computing calculated attributes for Storage SSD storage
    2024-09-12 16:35:39,847 - INFO - Computing calculated attributes for Autoscaling Inference GPU server



```python
system.plot_emission_diffs("LLM chat addition.png")
```

    Plotting the impact of Mean video consumption user journey’s uj_steps changing from ['20 min streaming', '1 min video capture then upload'] to ['20 min streaming', '1 min video capture then upload', 'Chat with LLM to select video']



    
![png](tutorial_images/docs_tutorial.nbconvert_41_1.png)
    


We can see that server energy footprint has been multiplied by more than 10 and the rest of the impact is quite negligible. Good to know to make informed decisions ! Of course the impact is very much dependent on assumptions. If the LLM server ran on low-carbon electricity for example:


```python
llm_server.average_carbon_intensity=SourceValue(50 * u.g / u.kWh, Sources.HYPOTHESIS)
system.plot_emission_diffs("lower LLM inference carbon intensity.png")
```

    Plotting the impact of Inference GPU server’s average_carbon_intensity changing from 300.0 gram / kilowatt_hour to 50.0 gram / kilowatt_hour



    
![png](tutorial_images/docs_tutorial.nbconvert_43_1.png)
    


## Recap of all System changes


```python
system.plot_emission_diffs("All system diffs.png", from_start=True)
```

    Plotting the impact of:
    
    - streaming’s data_download changing from 800 megabyte to 500 megabyte
    - Mean video consumption user journey’s uj_steps changing from ['20 min streaming', '1 min video capture then upload'] to ['20 min streaming', '1 min video capture then upload', 'Chat with LLM to select video']
    - Inference GPU server’s average_carbon_intensity changing from 300.0 gram / kilowatt_hour to 50.0 gram / kilowatt_hour



    
![png](tutorial_images/docs_tutorial.nbconvert_45_1.png)
    




