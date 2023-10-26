from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.constants.sources import SourceValue, Sources, SourceObject
from efootprint.core.usage.user_journey import UserJourney, UserJourneyStep
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.hardware.device_population import DevicePopulation, Devices
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import Countries
from efootprint.constants.units import u
from efootprint.abstract_modeling_classes.modeling_object import get_subclass_attributes, ModelingObject
from efootprint.logger import logger
from efootprint.utils.calculus_graph import build_calculus_graph

from unittest import TestCase
from copy import deepcopy
from typing import List


class IntegrationTest(TestCase):
    def setUp(self):
        self.server = Autoscaling(
            "Default server",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(24 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )
        self.storage = Storage(
            "Default SSD storage",
            carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0.1 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS)
        )
        self.service = Service(
            "Youtube", self.server, self.storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
            base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))

        self.streaming_step = UserJourneyStep(
            "20 min streaming on Youtube", self.service, SourceValue(50 * u.kB / u.uj),
            SourceValue((2.5 / 3) * u.GB / u.uj),
            user_time_spent=SourceValue(20 * u.min / u.uj), request_duration=SourceValue(4 * u.min))
        self.upload_step = UserJourneyStep(
            "0.4s of upload", self.service, SourceValue(300 * u.kB / u.uj), SourceValue(0 * u.kB / u.uj),
            user_time_spent=SourceValue(1 * u.s / u.uj), request_duration=SourceValue(0.1 * u.s))

        self.uj = UserJourney("Daily Youtube usage", uj_steps=[self.streaming_step, self.upload_step])
        self.device_population = DevicePopulation(
            "French Youtube users on laptop", SourceValue(4e7 * 0.3 * u.user), Countries.FRANCE, [Devices.LAPTOP])

        self.network = Network("Default network", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        self.usage_pattern = UsagePattern(
            "Youtube usage in France", self.uj, self.device_population,
            self.network, SourceValue(365 * u.user_journey / (u.user * u.year)),
            SourceObject([[7, 23]], Sources.USER_INPUT))

        self.system = System("system 1", [self.usage_pattern])
        graph = build_calculus_graph(self.system.total_footprint())
        graph.show("test_integration.html")

        self.initial_footprint = self.system.total_footprint()
        self.initial_fab_footprints = {
            self.storage: self.storage.instances_fabrication_footprint,
            self.server: self.server.instances_fabrication_footprint,
            self.device_population: self.device_population.instances_fabrication_footprint,
        }
        self.initial_energy_footprints = {
            self.storage: self.storage.energy_footprint,
            self.server: self.server.energy_footprint,
            self.network: self.network.energy_footprint,
            self.device_population: self.device_population.energy_footprint,
        }

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
                if expl_attr.left_child is None and expl_attr.right_child is None \
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
                    new_footprint = self.system.total_footprint()
                    logger.info(f"system footprint went from {round(self.initial_footprint.value, 1)} "
                                f"to {round(new_footprint.value, 1)}")
                    assert round(self.initial_footprint.magnitude, 2) != round(new_footprint.magnitude, 2)
                    input_object.__setattr__(expl_attr_name, expl_attr)
                    assert round(self.system.total_footprint().magnitude, 2) == \
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

    def test_time_intervals_change(self):
        logger.warning("Updating time intervals in usage pattern")
        old_time_intervals = deepcopy(self.usage_pattern.time_intervals)
        self.usage_pattern.time_intervals = SourceObject([[7, 13]], Sources.USER_INPUT)
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint().magnitude, 2)
        self.usage_pattern.time_intervals = old_time_intervals
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint().magnitude, 2)

    def test_uj_step_update(self):
        logger.warning("Updating uj steps in default user journey")
        self.uj.uj_steps = [self.streaming_step]
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint().magnitude, 2)
        self.uj.uj_steps = [self.streaming_step, self.upload_step]
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint().magnitude, 2)

    def test_device_pop_update(self):
        logger.warning("Updating devices in device population")
        self.device_population.devices = [Devices.LAPTOP, Devices.SCREEN]
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint().magnitude, 2)
        self.device_population.devices = [Devices.LAPTOP]
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint().magnitude, 2)

    def test_update_server(self):
        new_server = Autoscaling(
            "New server, identical in specs to default one",
            carbon_footprint_fabrication=SourceValue(600 * u.kg, Sources.BASE_ADEME_V19),
            power=SourceValue(300 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
            idle_power=SourceValue(50 * u.W, Sources.HYPOTHESIS),
            ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
            nb_of_cpus=SourceValue(24 * u.core, Sources.HYPOTHESIS),
            power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
            average_carbon_intensity=SourceValue(100 * u.g / u.kWh, Sources.HYPOTHESIS),
            server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
        )
        
        logger.warning("Changing service server")
        self.service.server = new_server

        self.assertEqual(0, self.server.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, self.server.energy_footprint.magnitude)
        self.footprint_has_changed([self.server])
        self.assertEqual(self.system.total_footprint().value, self.initial_footprint.value)

        logger.warning("Changing back to initial service server")
        self.service.server = self.server
        self.assertEqual(0, new_server.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, new_server.energy_footprint.magnitude)
        self.footprint_has_not_changed([self.server])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)

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
        self.assertEqual(self.system.total_footprint().value, self.initial_footprint.value)

        logger.warning("Changing back to initial service storage")
        self.service.storage = self.storage
        self.assertEqual(0, new_storage.instances_fabrication_footprint.magnitude)
        self.assertEqual(0, new_storage.energy_footprint.magnitude)
        self.footprint_has_not_changed([self.storage])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)

    def test_update_uj_steps(self):
        logger.warning("Modifying uj steps")
        new_step = UserJourneyStep(
            "new_step", self.service, SourceValue(5 * u.kB / u.uj),
            SourceValue(5 * u.GB / u.uj),
            user_time_spent=SourceValue(2 * u.min / u.uj), request_duration=SourceValue(4 * u.s))
        self.uj.uj_steps = [new_step]

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_changed([self.storage, self.server, self.network, self.device_population])

        logger.warning("Changing back to previous uj steps")
        self.uj.uj_steps = [self.streaming_step, self.upload_step]

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)

    def test_update_user_journey(self):
        logger.warning("Changing user journey")
        new_uj = UserJourney("New version of daily Youtube usage", uj_steps=[self.streaming_step])
        self.usage_pattern.user_journey = new_uj

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_changed([self.storage, self.server, self.network, self.device_population])

        logger.warning("Changing back to previous uj")
        self.usage_pattern.user_journey = self.uj

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)

    def test_update_device_population(self):
        logger.warning("Changing device population")
        new_device_pop = DevicePopulation(
            "New device pop with different specs", SourceValue(10 * u.user), Countries.FRANCE, [Devices.LAPTOP])

        self.usage_pattern.device_population = new_device_pop

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_changed([self.storage, self.server, self.network, self.device_population])

        logger.warning("Changing back to initial device population")
        self.usage_pattern.device_population = self.device_population

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_not_changed([self.storage, self.server, self.network, self.device_population])

    def test_update_country_in_device_pop(self):
        logger.warning("Changing device population country")

        self.device_population.country = Countries.MALAYSIA

        self.assertNotEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_changed([self.network, self.device_population])

        logger.warning("Changing back to initial device population country")
        self.device_population.country = Countries.FRANCE

        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)
        self.footprint_has_not_changed([self.network, self.device_population])

    def test_update_network(self):
        logger.warning("Changing network")
        new_network = Network(
            "New network with same specs as default", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))
        self.usage_pattern.network = new_network

        self.assertEqual(0, self.network.energy_footprint.magnitude)
        self.footprint_has_changed([self.network])
        self.assertEqual(self.system.total_footprint().value, self.initial_footprint.value)

        logger.warning("Changing back to initial network")
        self.usage_pattern.network = self.network
        self.assertEqual(0, new_network.energy_footprint.magnitude)
        self.footprint_has_not_changed([self.network])
        self.assertEqual(self.initial_footprint.value, self.system.total_footprint().value)
