from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from footprint_model.constants.sources import SourceValue, Sources, SourceObject
from footprint_model.core.usage.user_journey import UserJourney, UserJourneyStep
from footprint_model.core.hardware.servers.autoscaling import Autoscaling
from footprint_model.core.hardware.storage import Storage
from footprint_model.core.service import Service
from footprint_model.core.hardware.device_population import DevicePopulation, Devices
from footprint_model.core.usage.usage_pattern import UsagePattern
from footprint_model.core.hardware.network import Networks
from footprint_model.core.system import System
from footprint_model.constants.countries import Countries
from footprint_model.constants.units import u
from footprint_model.abstract_modeling_classes.modeling_object import get_subclass_attributes, ModelingObject

from unittest import TestCase
from copy import deepcopy
from footprint_model.logger import logger
from footprint_model.utils.calculus_representation import build_graph


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
            country=Countries.GERMANY,
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
            country=Countries.GERMANY,
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

        self.default_uj = UserJourney("Daily Youtube usage", uj_steps=[self.streaming_step, self.upload_step])
        self.default_device_pop = DevicePopulation(
            "French Youtube users on laptop", SourceValue(4e7 * 0.3 * u.user), Countries.FRANCE, [Devices.LAPTOP])

        self.default_network = Networks.WIFI_NETWORK
        self.usage_pattern = UsagePattern(
            "Youtube usage in France", self.default_uj, self.default_device_pop,
            self.default_network, SourceValue(365 * u.user_journey / (u.user * u.year)),
            SourceObject([[7, 23]], Sources.USER_INPUT))

        self.system = System("system 1", [self.usage_pattern])
        graph = build_graph(self.system.total_footprint())
        graph.show("test_integration.html")

        self.initial_footprint = self.system.total_footprint()

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
        test_variations_on_obj_inputs(self.default_uj)
        test_variations_on_obj_inputs(self.default_device_pop)
        test_variations_on_obj_inputs(self.default_network)
        test_variations_on_obj_inputs(
            self.usage_pattern, attrs_to_skip=["time_intervals"])

    def test_time_intervals_change(self):
        old_time_intervals = deepcopy(self.usage_pattern.time_intervals)
        self.usage_pattern.time_intervals = SourceObject([[7, 13]], Sources.USER_INPUT)
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint().magnitude, 2)
        self.usage_pattern.time_intervals = old_time_intervals
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint().magnitude, 2)

    def test_uj_step_update(self):
        logger.warning("Updating uj steps in default user journey")
        self.default_uj.uj_steps = [self.streaming_step]
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint().magnitude, 2)
        self.default_uj.uj_steps = [self.streaming_step, self.upload_step]
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint().magnitude, 2)

    def test_device_pop_update(self):
        logger.warning("Updating devices in device population")
        self.default_device_pop.devices = [Devices.LAPTOP, Devices.SCREEN]
        assert round(self.initial_footprint.magnitude, 2) != round(self.system.total_footprint().magnitude, 2)
        self.default_device_pop.devices = [Devices.LAPTOP]
        assert round(self.initial_footprint.magnitude, 2) == round(self.system.total_footprint().magnitude, 2)
