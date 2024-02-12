from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.constants.sources import Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.core.usage.job import Job
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import Countries
from efootprint.constants.units import u
from efootprint.abstract_modeling_classes.modeling_object import get_subclass_attributes, ModelingObject
from efootprint.logger import logger
from efootprint.utils.calculus_graph import build_calculus_graph
from efootprint.utils.object_relationships_graphs import build_object_relationships_graph, \
    USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE
from efootprint.builders.hardware.devices_defaults import default_laptop, default_screen
from tests.integration_tests.integration_test_base_class import IntegrationTestBaseClass

from copy import deepcopy
from typing import List
import os


class IntegrationTest(IntegrationTestBaseClass):
    @classmethod
    def setUpClass(cls):
        cls.server = Autoscaling(
            "Default server",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(128 * u.GB, Sources.USER_DATA),
            cpu_cores=SourceValue(24 * u.core, Sources.USER_DATA),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.USER_DATA),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.USER_DATA),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )
        cls.storage = Storage(
            "Default SSD storage",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0.1 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            data_replication_factor=SourceValue(3 * u.dimensionless)
        )
        cls.service = Service(
            "Youtube", cls.server, cls.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

        cls.streaming_job = Job("streaming", cls.service, data_upload=SourceValue(50 * u.kB / u.uj),
                      data_download=SourceValue((2.5 / 3) * u.GB / u.uj), request_duration=SourceValue(4 * u.min),
                      ram_needed=SourceValue(100 * u.MB / u.uj), cpu_needed=SourceValue(1 * u.core / u.uj))
        cls.streaming_step = UserJourneyStep(
            "20 min streaming on Youtube", user_time_spent=SourceValue(20 * u.min / u.uj), jobs=[cls.streaming_job])

        cls.upload_job = Job("upload", cls.service, data_upload=SourceValue(300 * u.kB / u.uj),
                      data_download=SourceValue(0 * u.GB / u.uj), request_duration=SourceValue(0.4 * u.s),
                      ram_needed=SourceValue(100 * u.MB / u.uj), cpu_needed=SourceValue(1 * u.core / u.uj))
        cls.upload_step = UserJourneyStep(
            "0.4s of upload", user_time_spent=SourceValue(1 * u.s / u.uj), jobs=[cls.upload_job])

        cls.uj = UserJourney("Daily Youtube usage", uj_steps=[cls.streaming_step, cls.upload_step])
        cls.device_population = DevicePopulation(
            "French Youtube users on laptop", SourceValue(4e7 * 0.3 * u.user), Countries.FRANCE(),
            [default_laptop()])

        cls.network = Network("Default network", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        cls.usage_pattern = UsagePattern(
            "Youtube usage in France", cls.uj, cls.device_population,
            cls.network, SourceValue(365 * u.user_journey / (u.user * u.year)),
            SourceObject([[7, 23]], Sources.USER_DATA))

        cls.system = System("system 1", [cls.usage_pattern])

        cls.initial_footprint = cls.system.total_footprint
        cls.initial_fab_footprints = {
            cls.storage: cls.storage.instances_fabrication_footprint,
            cls.server: cls.server.instances_fabrication_footprint,
            cls.device_population: cls.device_population.instances_fabrication_footprint,
        }
        cls.initial_energy_footprints = {
            cls.storage: cls.storage.energy_footprint,
            cls.server: cls.server.energy_footprint,
            cls.network: cls.network.energy_footprint,
            cls.device_population: cls.device_population.energy_footprint,
        }

        cls.ref_json_filename = "simple_system.json"

    def test_calculation_graph(self):
        graph = build_calculus_graph(self.system.total_footprint)
        graph.show(os.path.join(os.path.abspath(os.path.dirname(__file__)), "full_calculation_graph.html"))

    def test_object_relationship_graph(self):
        object_relationships_graph = build_object_relationships_graph(
            self.system, classes_to_ignore=USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE)
        object_relationships_graph.show(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "object_relationships_graph.html"))

    def footprint_has_changed(self, objects_to_test: List[ModelingObject]):
        for obj in objects_to_test:
            try:
                initial_energy_footprint = round(self.initial_energy_footprints[obj].value, 2)
                self.assertNotEqual(initial_energy_footprint, obj.energy_footprint.value)
                if type(obj) != Network:
                    initial_fab_footprint = round(self.initial_fab_footprints[obj].value, 2)
                    new_footprint = round(obj.instances_fabrication_footprint.value + obj.energy_footprint.value, 2)
                    self.assertNotEqual(
                        initial_fab_footprint + initial_energy_footprint, new_footprint)
                    logger.info(
                        f"{obj.name} footprint has changed from {initial_fab_footprint + initial_energy_footprint}"
                        f" to {new_footprint}")
                else:
                    logger.info(f"{obj.name} footprint has changed from "
                                f"{round(initial_energy_footprint, 2)} to {round(obj.energy_footprint.value, 2)}")
            except AssertionError:
                raise AssertionError(f"Footprint hasn’t changed for {obj.name}")

    def footprint_has_not_changed(self, objects_to_test: List[ModelingObject]):
        for obj in objects_to_test:
            try:
                initial_energy_footprint = self.initial_energy_footprints[obj].value
                if type(obj) != Network:
                    initial_fab_footprint = self.initial_fab_footprints[obj].value
                    self.assertEqual(initial_fab_footprint, obj.instances_fabrication_footprint.value)
                self.assertEqual(initial_energy_footprint, obj.energy_footprint.value)
                logger.info(f"{obj.name} footprint is the same as in setup")
            except AssertionError:
                raise AssertionError(f"Footprint has changed for {obj.name}")

    def test_variations_on_inputs(self):
        def test_variations_on_obj_inputs(input_object: ModelingObject, attrs_to_skip=None, special_mult=None):
            if attrs_to_skip is None:
                attrs_to_skip = []
            logger.warning(f"Testing input variations on {input_object.name}")
            for expl_attr_name, expl_attr in get_subclass_attributes(input_object, ExplainableObject).items():
                if expl_attr.left_parent is None and expl_attr.right_parent is None \
                        and expl_attr_name not in attrs_to_skip:
                    old_value = expl_attr.value
                    expl_attr_new_value = deepcopy(expl_attr)
                    if special_mult and expl_attr_name in special_mult.keys():
                        expl_attr_new_value.value *= special_mult[expl_attr_name] * u.dimensionless
                    else:
                        expl_attr_new_value.value *= 100 * u.dimensionless
                    expl_attr_new_value.label = expl_attr.label
                    logger.info(f"{expl_attr_new_value.label} changing from {round(old_value, 1)} to"
                                f" {round(expl_attr_new_value.value, 1)}")
                    input_object.__setattr__(expl_attr_name, expl_attr_new_value)
                    new_footprint = self.system.total_footprint
                    logger.info(f"system footprint went from {round(self.initial_footprint.value, 1)} "
                                f"to {round(new_footprint.value, 1)}")
                    assert round(self.initial_footprint.magnitude, 2) != round(new_footprint.magnitude, 2)
                    input_object.__setattr__(expl_attr_name, expl_attr)
                    assert round(self.system.total_footprint.magnitude, 2) == \
                           round(self.initial_footprint.magnitude, 2)

        test_variations_on_obj_inputs(self.streaming_step)
        test_variations_on_obj_inputs(
            self.server, attrs_to_skip=["fraction_of_usage_time", "idle_power"],
            special_mult={"ram": 0.01})
        test_variations_on_obj_inputs(
            self.storage, attrs_to_skip=["fraction_of_usage_time"])
        test_variations_on_obj_inputs(
            self.service,
            special_mult={"base_ram_consumption": 380, "base_cpu_consumption": 10})
        test_variations_on_obj_inputs(self.uj)
        test_variations_on_obj_inputs(self.device_population)
        test_variations_on_obj_inputs(self.network)
        test_variations_on_obj_inputs(
            self.usage_pattern, attrs_to_skip=["time_intervals"])
        test_variations_on_obj_inputs(self.streaming_job)

    def test_time_intervals_change(self):
        logger.warning("Updating time intervals in usage pattern")
        old_time_intervals = deepcopy(self.usage_pattern.time_intervals)
        calculus_graph = build_calculus_graph(self.server.energy_footprint)
        calculus_graph.show(os.path.join(".", "debug_calculus_graph.html"))
        self.usage_pattern.time_intervals = SourceObject([[7, 13]], Sources.USER_DATA)
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint.magnitude, 2)
        logger.warning("Setting time intervals back to initial value in usage pattern")
        self.usage_pattern.time_intervals = old_time_intervals
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint.magnitude, 2)

    def test_uj_step_update(self):
        logger.warning("Updating uj steps in default user journey")
        self.uj.uj_steps = [self.streaming_step]
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint.magnitude, 2)
        self.uj.uj_steps = [self.streaming_step, self.upload_step]
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint.magnitude, 2)

    def test_device_pop_update(self):
        logger.warning("Updating devices in device population")
        self.device_population.devices = [default_laptop(), default_screen()]
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint.magnitude, 2)
        self.device_population.devices = [default_laptop()]
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint.magnitude, 2)

    def test_update_server(self):
        new_server = Autoscaling(
            "New server, identical in specs to default one",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
            cpu_cores=SourceValue(24 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )

        logger.warning("Changing service server")
        self.service.server = new_server

        self.assertEqual(0, self.server.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, self.server.energy_footprint.magnitude)
        self.footprint_has_changed([self.server])
        self.assertEqual(self.system.total_footprint.value, self.initial_footprint.value)

        logger.warning("Changing back to initial service server")
        self.service.server = self.server
        self.assertEqual(0, new_server.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, new_server.energy_footprint.magnitude)
        self.footprint_has_not_changed([self.server])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)

    def test_update_storage(self):
        new_storage = Storage(
            "New storage, identical in specs to Default SSD storage",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0.1 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS)
        )
        logger.warning("Changing service storage")
        self.service.storage = new_storage

        self.assertEqual(0, self.storage.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, self.storage.energy_footprint.magnitude)
        self.footprint_has_changed([self.storage])
        self.assertEqual(self.system.total_footprint.value, self.initial_footprint.value)

        logger.warning("Changing back to initial service storage")
        self.service.storage = self.storage
        self.assertEqual(0, new_storage.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, new_storage.energy_footprint.magnitude)
        self.footprint_has_not_changed([self.storage])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)

    def test_update_jobs(self):
        logger.warning("Modifying streaming jobs")
        new_job = Job("new job", self.service, data_upload=SourceValue(5 * u.kB / u.uj),
                      data_download=SourceValue(5 * u.GB / u.uj), request_duration=SourceValue(4 * u.s),
                      ram_needed=SourceValue(100 * u.MB / u.uj), cpu_needed=SourceValue(1 * u.core / u.uj))

        self.streaming_step.jobs += [new_job]

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_not_changed([self.device_population])
        self.footprint_has_changed([self.storage, self.server, self.network])

        logger.warning("Changing back to previous jobs")
        self.streaming_step.jobs = [self.streaming_job]

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)

    def test_update_uj_steps(self):
        logger.warning("Modifying uj steps")
        new_step = UserJourneyStep(
            "new_step", user_time_spent=SourceValue(2 * u.min / u.uj),
            jobs=[Job("new job", self.service, data_upload=SourceValue(5 * u.kB / u.uj),
                      data_download=SourceValue(5 * u.GB / u.uj), request_duration=SourceValue(4 * u.s),
                      ram_needed=SourceValue(100 * u.MB / u.uj), cpu_needed=SourceValue(1 * u.core / u.uj))]
        )
        self.uj.uj_steps = [new_step]

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_changed([self.storage, self.server, self.network])

        logger.warning("Changing back to previous uj steps")
        self.uj.uj_steps = [self.streaming_step, self.upload_step]

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)

    def test_update_user_journey(self):
        logger.warning("Changing user journey")
        new_uj = UserJourney("New version of daily Youtube usage", uj_steps=[self.streaming_step])
        self.usage_pattern.user_journey = new_uj

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_changed([self.storage, self.server, self.network, self.device_population])

        logger.warning("Changing back to previous uj")
        self.usage_pattern.user_journey = self.uj

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)

    def test_update_device_population(self):
        logger.warning("Changing device population")
        new_device_pop = DevicePopulation(
            "New device pop with different specs", SourceValue(10 * u.user), Countries.FRANCE(), [default_laptop()])

        self.usage_pattern.device_population = new_device_pop

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_changed([self.storage, self.server, self.network, self.device_population])

        logger.warning("Changing back to initial device population")
        self.usage_pattern.device_population = self.device_population

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])

    def test_update_country_in_device_pop(self):
        logger.warning("Changing device population country")

        self.device_population.country = Countries.MALAYSIA()

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_changed([self.network, self.device_population])

        logger.warning("Changing back to initial device population country")
        self.device_population.country = Countries.FRANCE()

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)
        self.footprint_has_not_changed([self.network, self.device_population])

    def test_update_network(self):
        logger.warning("Changing network")
        new_network = Network(
            "New network with same specs as default", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        self.usage_pattern.network = new_network

        self.assertEqual(0, self.network.energy_footprint.magnitude)
        self.footprint_has_changed([self.network])
        self.assertEqual(self.system.total_footprint.value, self.initial_footprint.value)

        logger.warning("Changing back to initial network")
        self.usage_pattern.network = self.network
        self.assertEqual(0, new_network.energy_footprint.magnitude)
        self.footprint_has_not_changed([self.network])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint.value)

    def test_add_uj_step_without_job(self):
        logger.warning("Add uj step without service")

        step_without_job = UserJourneyStep(
            "User checks her phone", user_time_spent=SourceValue(20 * u.min / u.uj), jobs=[])

        self.uj.add_step(step_without_job)

        self.footprint_has_not_changed([self.server, self.storage])
        self.footprint_has_changed([self.device_population])
        self.assertNotEqual(self.system.total_footprint.value, self.initial_footprint.value)

        logger.warning("Setting user time spent of the new step to 0s")
        step_without_job.user_time_spent = SourceValue(0 * u.min / u.uj)
        self.footprint_has_not_changed([self.server, self.storage])
        self.assertEqual(self.system.total_footprint.value, self.initial_footprint.value)

        logger.warning("Deleting the new uj step")
        self.uj.uj_steps = self.uj.uj_steps[:-1]
        step_without_job.self_delete()
        self.footprint_has_not_changed([self.server, self.storage])
        self.assertEqual(self.system.total_footprint.value, self.initial_footprint.value)

    def test_system_to_json(self):
        self.run_system_to_json_test(self.system)

    def test_json_to_system(self):
        self.run_json_to_system_test(self.system)
