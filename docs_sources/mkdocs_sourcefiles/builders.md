# e-footprint builders

e-footprint builders are higher-level functions that allows for the creation of e-footprint objects from fewer parameters than the raw model requires.

## Default builders

### Devices


```python
from efootprint.builders.hardware.devices_defaults import default_smartphone, default_laptop, default_box, default_screen
```


```python
print(default_smartphone())
```

    Hardware Default smartphone 34ec51
     
    carbon_footprint_fabrication: 30 kilogram
    power: 1 watt
    lifespan: 3 year
    fraction_of_usage_time: 3.6 hour / day
    



```python
print(default_laptop())
```

    Hardware Default laptop 3dce43
     
    carbon_footprint_fabrication: 156 kilogram
    power: 50 watt
    lifespan: 6 year
    fraction_of_usage_time: 7.0 hour / day
    



```python
print(default_box())
```

    Hardware Default box ada3d5
     
    carbon_footprint_fabrication: 78 kilogram
    power: 10 watt
    lifespan: 6 year
    fraction_of_usage_time: 24.0 hour / day
    



```python
print(default_screen())
```

    Hardware Default screen 374e21
     
    carbon_footprint_fabrication: 222 kilogram
    power: 30 watt
    lifespan: 6 year
    fraction_of_usage_time: 7.0 hour / day
    


### Network


```python
from efootprint.builders.hardware.network_defaults import default_mobile_network, default_wifi_network
```


```python
print(default_mobile_network())
```

    Network Default mobile network 3f5ca5
     
    bandwidth_energy_intensity: 0.12 kilowatt_hour / gigabyte
     
    calculated_attributes:
      data_download: None
      data_upload: None
      energy_footprint: None
    



```python
print(default_wifi_network())
```

    Network Default wifi network fbd0fd
     
    bandwidth_energy_intensity: 0.05 kilowatt_hour / gigabyte
     
    calculated_attributes:
      data_download: None
      data_upload: None
      energy_footprint: None
    


### Servers

Different server types have same default attributes but their calculated attributes logic will be different.


```python
from efootprint.builders.hardware.servers_defaults import default_autoscaling, default_serverless, default_onpremise
```


```python
print(default_autoscaling())
```

    Autoscaling Default autoscaling d2a554
     
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
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    



```python
print(default_serverless())
```

    Serverless Default serverless 7acfe6
     
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
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    



```python
print(default_onpremise())
```

    OnPremise Default on premise ad016a
     
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
    fixed_nb_of_instances: None
     
    calculated_attributes:
      available_ram_per_instance: None
      available_cpu_per_instance: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    


### Storage


```python
from efootprint.builders.hardware.storage_defaults import default_hdd, default_ssd
```


```python
print(default_hdd())
```

    Storage Default HDD storage 57458f
     
    carbon_footprint_fabrication: 20 kilogram
    power: 4.2 watt
    lifespan: 4 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    idle_power: 0 watt
    storage_capacity: 1 terabyte
    power_usage_effectiveness: 1.2 dimensionless
    data_replication_factor: 3 dimensionless
    storage_need_from_previous_year: 0
     
    calculated_attributes:
      all_services_storage_needs: None
      active_storage_required: None
      long_term_storage_required: None
      nb_of_idle_instances: None
      nb_of_active_instances: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    



```python
print(default_ssd())
```

    Storage Default SSD storage dc7c76
     
    carbon_footprint_fabrication: 160 kilogram
    power: 1.3 watt
    lifespan: 6 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    idle_power: 0 watt
    storage_capacity: 1 terabyte
    power_usage_effectiveness: 1.2 dimensionless
    data_replication_factor: 3 dimensionless
    storage_need_from_previous_year: 0
     
    calculated_attributes:
      all_services_storage_needs: None
      active_storage_required: None
      long_term_storage_required: None
      nb_of_idle_instances: None
      nb_of_active_instances: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    


## Overwriting default builders attributes

Any default builder attribute can be overwritten, for example:


```python
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u

print(default_ssd("My custom default SSD with higher carbon intensity", average_carbon_intensity=SourceValue(300 * u.g / u.kWh)))
```

    Storage My custom default SSD with higher carbon intensity c58c06
     
    carbon_footprint_fabrication: 160 kilogram
    power: 1.3 watt
    lifespan: 6 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 300.0 gram / kilowatt_hour
    idle_power: 0 watt
    storage_capacity: 1 terabyte
    power_usage_effectiveness: 1.2 dimensionless
    data_replication_factor: 3 dimensionless
    storage_need_from_previous_year: 0
     
    calculated_attributes:
      all_services_storage_needs: None
      active_storage_required: None
      long_term_storage_required: None
      nb_of_idle_instances: None
      nb_of_active_instances: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    


## BoaviztAPI builders

These builders make use of [Boavizta’s API](https://github.com/Boavizta/boaviztapi) to create objects with their full technical characteristics from fewer information like server name and cloud provider.

### BoaviztAPI server builders

#### Cloud server from cloud provider and server name


```python
from efootprint.builders.hardware.servers_boaviztapi import get_cloud_server
```


```python
print(get_cloud_server("aws", "m5.xlarge", SourceValue(100 * u.g / u.kWh)))
```

    Autoscaling aws m5.xlarge instances c527ec
     
    carbon_footprint_fabrication: 48.0 kilogram
    power: 25.94 watt
    lifespan: 6 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    server_utilization_rate: 0.9 dimensionless
    idle_power: 0 watt
    ram: 384.0 gigabyte
    cpu_cores: 48.0 core
    power_usage_effectiveness: 1.2 dimensionless
     
    calculated_attributes:
      available_ram_per_instance: None
      available_cpu_per_instance: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    



```python
# The server type can be changed, as well as lifespan, idle_power, power_usage_effectiveness and server_utilization_rate
from efootprint.core.hardware.servers.serverless import Serverless

print(get_cloud_server(
    "aws", "m5.xlarge", SourceValue(100 * u.g / u.kWh), base_efootprint_class=Serverless, lifespan=SourceValue(7 * u.year)))
```

    Serverless aws m5.xlarge instances cede54
     
    carbon_footprint_fabrication: 48.0 kilogram
    power: 25.94 watt
    lifespan: 7 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    server_utilization_rate: 0.9 dimensionless
    idle_power: 0 watt
    ram: 384.0 gigabyte
    cpu_cores: 48.0 core
    power_usage_effectiveness: 1.2 dimensionless
     
    calculated_attributes:
      available_ram_per_instance: None
      available_cpu_per_instance: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    


#### On premise server from config


```python
from efootprint.builders.hardware.servers_boaviztapi import on_premise_server_from_config
```


```python
print(on_premise_server_from_config(
    "My server", nb_of_cpu_units=2, nb_of_cores_per_cpu_unit=24,nb_of_ram_units=6,
    ram_quantity_per_unit_in_gb=16, average_carbon_intensity=SourceValue(100 * u.g / u.kWh)))
```

    OnPremise My server 63ec5f
     
    carbon_footprint_fabrication: 670.0 kilogram
    power: 520.99 watt
    lifespan: 6 year
    fraction_of_usage_time: 1 dimensionless
    average_carbon_intensity: 100.0 gram / kilowatt_hour
    server_utilization_rate: 0.7 dimensionless
    idle_power: 0 watt
    ram: 96 gigabyte
    cpu_cores: 48 core
    power_usage_effectiveness: 1.4 dimensionless
    fixed_nb_of_instances: None
     
    calculated_attributes:
      available_ram_per_instance: None
      available_cpu_per_instance: None
      all_services_cpu_needs: None
      all_services_ram_needs: None
      fraction_of_time_in_use: None
      nb_of_instances: None
      instances_fabrication_footprint: None
      instances_power: None
      energy_footprint: None
    


## Job builder from Boavizta’s ecobenchmark data


```python
from efootprint.builders.usage.job_ecobenchmark.ecobenchmark_job_builder import ecobenchmark_job
from efootprint.core.service import Service

server = default_autoscaling()
storage = default_ssd()
service = Service("test service", server, storage, base_ram_consumption=SourceValue(1 * u.MB))
job = ecobenchmark_job(
    "test job", service, data_upload=SourceValue(1 * u.MB / u.uj), data_download=SourceValue(1 * u.MB / u.uj),
    technology='php-symfony')

print(job)
```

    2024-04-06 19:04:45,884 - INFO - File /ecobenchmark_results__raw.csv already exists, we do not overwrite it


    Job test job d125d8
     
    job_type: undefined
    service: test service 2448a7
    data_upload: 1.0 megabyte / user_journey
    data_download: 1.0 megabyte / user_journey
    request_duration: 1 second
    ram_needed: 6.15 megabyte / user_journey
    cpu_needed: 0.08 core / user_journey
    description: 
    



```python
# List of available technologies
from efootprint.builders.usage.job_ecobenchmark.ecobenchmark_job_builder import get_ecobenchmark_technologies
print(get_ecobenchmark_technologies())
```

    ['go-pgx', 'jvm-kotlin-spring', 'node-express-sequelize', 'php-symfony', 'rust-actix-sqlx']



```python

```
