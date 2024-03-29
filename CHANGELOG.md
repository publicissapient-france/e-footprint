# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.3.2] - 2024-03-20

### Added
- Characterics of objects are now displayed when hovering over a node in an object relationship graph (to create such a graph use the object_relationship_graph_to_file method of the ModelingObject class).

## [1.3.1] - 2024-03-16

### Fixed
- set modeling obj container of ExplainableObjects created through json_to_system function so that accessing their id property doesn’t trigger a ValueError because of a null modeling_obj_container.
- Fixed ExplainableObject’s set_label method so that it doesn’t duplicate "from source.name" when reconstructing the object with the json_to_system function.

## [1.3.0] - 2024-03-15

### Added
- plot_emission_diffs method to System for easy analysis of System changes.
- Tutorial to documentation.
- System changes analysis in tutorial.

## [1.2.2] - 2024-03-08

### Added
- notebook parameter in object and calculus graph generation functions + set cdn_resources=in_line in pyvis Network objects to silence jupyter warning
- to_json, __repr__ and __str__ methods in ExplainableObject subclasses and ModelingObject.

### Changed
- quickstart as jupyter notebook

## [1.2.1] - 2024-02-29

### Added

### Changed

### Fixed
- Possibility to use fixed_nb_of_instances with the on_premise_server_from_config builder.

## [1.2.0] - 2024-02-29

### Added
- Possibility to specify the fixed number of on premise instances through the fixed_nb_of_instances attribute
- Doc generation logic with mkdocs. Here is the link to the [e-footprint documentation](https://publicissapient-france.github.io/e-footprint).

### Changed

### Fixed
- File paths in graphs generating functions

## [1.1.9] - 2024-02-12

### Added
- system_to_json and json_to_system functions in api_utils package in order to be able to save a system as json file and then load it and run computations. Saving of intermediate calculations will be implemented in another release.

### Changed
- calculated_attributes are now a property method instead of an attribute, to facilitate system to json and json to system flow.
- calculated attributes of System class are now properties for a more coherent syntax.
- Countries class is now made of country generator objects to avoid unwanted link between systems that would share a common country.
- System now inherits from ModelingObject

## [1.1.8] - 2024-02-02

### Added
- calculus_graph_to_file function in ExplainableObject to more easily create calculus graphs
- object_relationship_graph_to_file function in ModelingObject to more easily create object relationship graphs
- Generic self_delete method for ModelingObjects

### Changed
- System now inherits from ModelingObject

## [1.1.7] - 2024-01-29

### Added

### Changed
- Put ModelingObject list update logic in ModelingObject __setattr__ method
- Name server CPU capacity cpu_cores instead of nb_of_cpus to make it clearer

### Fixed
- Set input attribute label at attribute setting time and not after. Avoids a bug when the input attribute of a ModelingObject is the result of a calculation and hence has no label.

## [1.1.6] - 2024-01-29

### Added

### Changed
- Put all the naming logic that was in SourceValue and SourceObject classes into ExplainableObject

### Fixed
- Boaviztapi server builders to accommodate for Boaviztapi update. 

## [1.1.5] - 2024-01-18

### Added
- plot_footprints_by_category_and_object method to the System object, to display the CO2 emission breakdown by object type (server, storage, network, end user devices), emission types (from electricity and from fabrication), and by objects within object types (for example, the share of each server within the servers).
- Default object builders that return a new object each time.
- Server builders based on the [Boavizta API](https://github.com/Boavizta/boaviztapi).

### Changed
- Suppress the notion of server_ram_per_data_transferred to simply directly specify the ram_needed for UserJourneyStep objects.
- More explicity quickstart with all attributes explicitely named and set.

### Fixed


## [1.1.4] - 2023-11-13

### Added

### Changed

### Fixed
- Don’t write logs to file by default to avoid unnecessary storage usage + be compliant with Streamlit Cloud security.

## [1.1.3] - 2023-11-13

### Added

### Changed

### Fixed
- Put data folder (for logs) inside module and set default log level to INFO.

## [1.1.2] - 2023-11-10

### Added
- Missing tests.
- Optimisations that can lead to 10x+ improvements in complex systems initiation speed.

### Changed
- Clarification of vocabulary in ExplainableObject class: an ExplainableObject now links to its children, to follow a genealogical logic.
- Graph colors for more color blindness friendliness. Reach out if this is still unsatisfactory !

### Fixed
- Object link recomputation logic: the launch_attributes_computation_chain function in the [ModelingObject class](./efootprint/abstract_modeling_classes/modeling_object.py) now allows for a breadth first exploration of the object link graph to recompute object attributes in the right order. 
 
## [1.1.1] - 2023-11-03

### Added

### Changed
 
### Fixed
- Possibility to have a null service as input for user journey steps (in cases when the user simply uses the device without any service call).
- UserJourney’s add_step method didn’t trigger setattr because of the use of the self.uj_steps.append(new_step) syntax, and hence didn’t trigger the appropriate recomputation logic. Fixed by replacing it with the self.uj_steps = self.uj_steps + [new_step] syntax.
- [graph_tools](./efootprint/utils/graph_tools.py) module doesn’t depend any more on special selenium screenshot functions that are only used during development. Such functions have been moved to the [dev_utils](./efootprint/utils/dev_utils) package that only contains modules not used in the project because they are work in progress or dev helper functions.
- Fixed the [convert_to_utc_test](./tests/abstract_modeling_classes/test_explainable_objects.py) that had broken because of time change  
 
## [1.1.0] - 2023-10-26

State of project at time of open sourcing.

### Added
Full optimization of recomputation whenever an input or object relationship changes.