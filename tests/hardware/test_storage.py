from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from footprint_model.core.hardware.storage import Storage

from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock


class TestStorage(TestCase):
    def setUp(self):
        self.storage_base = Storage(
            "storage_base",
            carbon_footprint_fabrication=SourceValue(0 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power=SourceValue(0 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            lifespan=SourceValue(0 * u.years, Sources.HYPOTHESIS),
            idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
            storage_capacity=SourceValue(0 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
            power_usage_effectiveness=0,
            country=MagicMock(),
            data_replication_factor=0
        )

    def test_services(self):
        usage_pattern1 = MagicMock()
        usage_pattern2 = MagicMock()
        service1 = MagicMock()
        service1.storage = self.storage_base
        service2 = MagicMock()
        service2.storage = "other server"
        usage_pattern1.services = {service1, service2}
        service3 = MagicMock()
        service3.storage = self.storage_base
        usage_pattern2.services = {service3}
        with patch.object(self.storage_base, "usage_patterns", new={usage_pattern1, usage_pattern2}):
            self.assertEqual({service1, service3}, self.storage_base.services)

    def test_update_all_services_storage_needs_single_service(self):
        service1 = MagicMock()
        service1.storage = self.storage_base
        service1.storage_needed = ExplainableQuantity(2 * u.TB / u.year)
        service2 = MagicMock()
        service2.storage = self.storage_base
        service2.storage_needed = ExplainableQuantity(3 * u.TB / u.year)
        with patch.object(Storage, "services", new_callable=PropertyMock) as services_mock:
            services_mock.return_value = {service1, service2}
            self.storage_base.update_all_services_storage_needs()
            self.assertEqual(5 * u.TB / u.year, self.storage_base.all_services_storage_needs.value)

    def test_active_storage_required(self):
        active_storage_expected = (
                ExplainableQuantity(10.1 * u.TB / u.year)
                * SourceValue(1 * u.hour, Sources.HYPOTHESIS, "Time interval during which active storage is considered")
        ).to(u.GB)
        with patch.object(self.storage_base, "all_services_storage_needs", new=ExplainableQuantity(10.1 * u.TB / u.year)):
            self.storage_base.update_active_storage_required()
            self.assertEqual(active_storage_expected.value, self.storage_base.active_storage_required.value)

    def test_long_term_storage_required(self):
        with patch.object(self.storage_base, "all_services_storage_needs", ExplainableQuantity(10.1 * u.TB / u.year)), \
                patch.object(self.storage_base, "active_storage_required", ExplainableQuantity(1.5 * u.TB)), \
                patch.object(self.storage_base, "data_replication_factor", ExplainableQuantity(3 * u.dimensionless)), \
                patch.object(self.storage_base, "storage_need_from_previous_year", ExplainableQuantity(1 * u.TB)):
            self.storage_base.update_long_term_storage_required()

            self.assertEqual(29.8 * u.TB, round(self.storage_base.long_term_storage_required.value, 1))

    def test_nb_of_active_instances(self):
        with patch.object(self.storage_base, "active_storage_required", ExplainableQuantity(500 * u.GB)), \
                patch.object(self.storage_base, "storage_capacity", ExplainableQuantity(1 * u.TB)):
            self.storage_base.update_nb_of_active_instances()
            self.assertEqual(0.5, round(self.storage_base.nb_of_active_instances.value, 1))

    def test_nb_of_idle_instances(self):
        with patch.object(self.storage_base, "long_term_storage_required", ExplainableQuantity(5 * u.GB)), \
                patch.object(self.storage_base, "storage_capacity", ExplainableQuantity(1 * u.GB)):
            self.storage_base.update_nb_of_idle_instances()
            self.assertEqual(5, self.storage_base.nb_of_idle_instances.value)

    def test_nb_of_instances(self):
        with patch.object(self.storage_base, "nb_of_active_instances",
                          ExplainableQuantity(3 * u.dimensionless)), \
                patch.object(self.storage_base, "nb_of_idle_instances", ExplainableQuantity(2 * u.dimensionless)):
            self.storage_base.update_nb_of_instances()
            self.assertEqual(ExplainableQuantity(5 * u.dimensionless), self.storage_base.nb_of_instances)

    def test_instances_power(self):
        with patch.object(self.storage_base, "nb_of_active_instances",
                          ExplainableQuantity(10 * u.dimensionless)), \
              patch.object(self.storage_base, "nb_of_idle_instances", ExplainableQuantity(1 * u.dimensionless)), \
              patch.object(self.storage_base, "fraction_of_time_in_use", ExplainableQuantity(0.5 * u.dimensionless)), \
              patch.object(self.storage_base, "power", ExplainableQuantity(1.3 * u.W)), \
              patch.object(self.storage_base, "idle_power", ExplainableQuantity(0.3 * u.W)), \
              patch.object(self.storage_base, "power_usage_effectiveness", ExplainableQuantity(1.2 * u.dimensionless)):
            self.storage_base.update_instances_power()
            expected_power = ExplainableQuantity((15.6 / 2 + 0.36) * u.W).to(u.kWh / u.year)
            self.assertEqual(round(expected_power.value, 0), round(self.storage_base.instances_power.value, 0))
