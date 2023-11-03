# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
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