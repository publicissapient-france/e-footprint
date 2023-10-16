import unittest
from unittest import TestCase
from unittest.mock import PropertyMock, MagicMock
from copy import deepcopy

from footprint_model.constants.sources import SourceValue, Sources, u
from footprint_model.core.user_journey import UserJourneyStep, UserJourney
from footprint_model.constants.explainable_quantities import ExplainableQuantity

UJ_MODULE = "footprint_model.core.user_journey.UserJourney"


class TestUserJourney(TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.server = MagicMock()
        self.service = MagicMock()
        self.service.server = self.server
        self.service.storage = self.storage

        self.server.usage_patterns = set()
        self.storage.usage_patterns = set()

        request = MagicMock()
        request.service = self.service
        request.data_download = 200 * u.Mo
        request.data_upload = ExplainableQuantity(100 * u.Mo / u.user_journey)
        request.ram_needed = ExplainableQuantity(2 * u.Go)
        request.cpu_needed = ExplainableQuantity(2 * u.core)
        request.duration = ExplainableQuantity(2 * u.min / u.user_journey)

        self.user_journey = UserJourney("test user journey")
        self.user_journey_step = UserJourneyStep("", request, 10 * u.s)
        self.one_user_journey = ExplainableQuantity(1 * u.user_journey)
        self.user_journey.uj_steps = [self.user_journey_step]

        self.usage_pattern = MagicMock()
        self.user_journey.usage_patterns = {self.usage_pattern}

    def test_link_usage_pattern_add_new_usage_pattern(self):
        test_user_journey = deepcopy(self.user_journey)
        test_user_journey.usage_patterns = {'up'}
        test_user_journey.link_usage_pattern('up2')

        self.assertEqual({'up', 'up2'}, test_user_journey.usage_patterns)
        for server in test_user_journey.servers:
            server.link_usage_pattern.assert_called_once_with('up2')

        for storage in test_user_journey.storages:
            storage.link_usage_pattern.assert_called_once_with('up2')

    def test_unlink_usage_pattern(self):
        test_user_journey = deepcopy(self.user_journey)
        test_user_journey.usage_patterns = {'up', 'up2'}
        test_user_journey.unlink_usage_pattern('up2')
        self.assertEqual({'up'}, test_user_journey.usage_patterns)

        for server in test_user_journey.servers:
            server.unlink_usage_pattern.assert_called_once_with('up2')
        for storage in test_user_journey.storages:
            storage.unlink_usage_pattern.assert_called_once_with('up2')

    def test_add_step(self):
        self.user_journey.add_step(self.user_journey_step)
        self.assertEqual(self.user_journey.uj_steps, [self.user_journey_step, self.user_journey_step])

    def test_servers(self):
        self.assertEqual(self.user_journey.servers, {self.server})

    def test_storages(self):
        self.assertEqual(self.user_journey.storages, {self.storage})

    def test_services(self):
        self.assertEqual(self.user_journey.services, {self.service})

    def test_duration(self):
        duration1 = 10 * u.s
        duration2 = 30 * u.s
        user_journey_step1 = UserJourneyStep("", self.user_journey_step.request, duration1)
        user_journey_step2 = UserJourneyStep("", self.user_journey_step.request, duration2)
        self.assertEqual(UserJourney("uj", uj_steps=[user_journey_step1]).duration.value, duration1 / u.user_journey)
        self.assertEqual(UserJourney("uj", uj_steps=[user_journey_step2]).duration.value, duration2 / u.user_journey)
        self.assertEqual(UserJourney("uj", uj_steps=[user_journey_step1, user_journey_step2]).duration.value,
                         (duration1 + duration2) / u.user_journey)

    def test_data_download(self):
        data_download = 30 * u.Mo
        data_upload = ExplainableQuantity(40 * u.Mo)

        request_download = MagicMock()
        request_download.data_download = ExplainableQuantity(data_download / u.user_journey)
        request_download.data_upload = ExplainableQuantity(0 * u.Mo)

        request_upload = MagicMock()
        request_upload.data_download = ExplainableQuantity(0 * u.Mo)
        request_upload.data_upload = data_upload

        user_journey_step_download = UserJourneyStep("", request_download, 10 * u.s)
        user_journey_step_upload = UserJourneyStep("", request_upload, 10 * u.s)
        self.assertEqual(UserJourney("uj", uj_steps=[user_journey_step_download]).data_download.value,
                         data_download / u.user_journey)
        self.assertEqual(UserJourney("uj", uj_steps=[user_journey_step_download] * 2).data_download.value,
                         data_download * 2 / u.user_journey)
        self.assertEqual(
            UserJourney("uj", uj_steps=[user_journey_step_download, user_journey_step_upload]).data_download.value,
            data_download / u.user_journey,
        )

    def test_data_upload(self):
        data_download = 30 * u.Mo
        data_upload = 40 * u.Mo

        request_download = MagicMock()
        request_download.data_download = ExplainableQuantity(data_download / u.user_journey)
        request_download.data_upload = ExplainableQuantity(0 * u.Mo / u.user_journey)

        request_upload = MagicMock()
        request_upload.data_download = 0 * u.Mo
        request_upload.data_upload = ExplainableQuantity(data_upload / u.user_journey)

        user_journey_step_download = UserJourneyStep("", request_download, 10 * u.s)
        user_journey_step_upload = UserJourneyStep("", request_upload, 10 * u.s)
        self.assertEqual(UserJourney("uj", uj_steps=[user_journey_step_upload]).data_upload.value,
                         data_upload / u.user_journey)
        self.assertEqual(round(UserJourney("uj", uj_steps=[user_journey_step_upload] * 2).data_upload.value, 2),
                         (data_upload * 2) / u.user_journey)
        self.assertEqual(
            UserJourney("uj", uj_steps=[user_journey_step_download, user_journey_step_upload]).data_upload.value,
            # Strangely this conversion is needed for the comparison to work...
            data_upload.to(u.o) / u.user_journey
        )

    def test_compute_device_consumption(self):
        duration = ExplainableQuantity(10 * u.s / u.user_journey, "duration")
        device_power = 3 * u.W
        device_consumption = device_power * duration.value
        device = MagicMock()
        device.power = SourceValue(device_power, Sources.HYPOTHESIS)

        with unittest.mock.patch(f"{UJ_MODULE}.duration", new=duration):
            user_journey = UserJourney("test user journey")
            device_consumption_computed = user_journey.compute_device_consumption(device)
            self.assertEqual(device_consumption_computed.value, device_consumption)

    def test_compute_fabrication_footprint(self):
        duration = ExplainableQuantity(10 * u.s / u.user_journey, "duration")
        carbon_footprint_fabrication = 60 * u.kg
        average_fraction_of_usage_per_day = 3 * u.hour / u.day
        lifespan = 3 * u.year
        fabrication_footprint = (carbon_footprint_fabrication * duration.value /
                                 (lifespan * average_fraction_of_usage_per_day)).to(u.gram / u.user_journey)
        device = MagicMock()
        device.carbon_footprint_fabrication = SourceValue(carbon_footprint_fabrication, Sources.BASE_ADEME_V19)
        device.lifespan = SourceValue(lifespan, Sources.HYPOTHESIS)
        device.fraction_of_usage_time = SourceValue(average_fraction_of_usage_per_day, Sources.HYPOTHESIS)
        with unittest.mock.patch(f"{UJ_MODULE}.duration", new=duration):
            user_journey = UserJourney("test user journey")
            fabrication_footprint_computed = user_journey.compute_fabrication_footprint(device)
            self.assertEqual(fabrication_footprint_computed.value, fabrication_footprint)

    def test_compute_network_consumption(self):
        data_download = ExplainableQuantity(10 * u.Mo / u.user_journey, "data_download")
        data_upload = ExplainableQuantity(20 * u.Mo / u.user_journey, "data_upload")
        bandwidth_energy_intensity = 0.05 * u("kWh/Go")
        network_consumption = ((data_download.value + data_upload.value) * bandwidth_energy_intensity).to(
            u.Wh / u.user_journey)
        network = MagicMock()
        network.bandwidth_energy_intensity = SourceValue(bandwidth_energy_intensity, Sources.TRAFICOM_STUDY)

        with unittest.mock.patch(f"{UJ_MODULE}.data_download", new=data_download),\
                unittest.mock.patch(f"{UJ_MODULE}.data_upload", new=data_upload):
            user_journey = UserJourney("test user journey")
            network_consumption_computed = user_journey.compute_network_consumption(network)
            self.assertEqual(network_consumption_computed.value, network_consumption)

    def test_ram_needed_per_service(self):
        expected_ram_per_service = {
            self.user_journey_step.request.service: (self.user_journey_step.request.ram_needed
                                                     * self.user_journey_step.request.duration
                                                     / (self.user_journey.duration * self.one_user_journey)
                                                     ).to(u.Mo / u.user_journey)
        }
        self.assertDictEqual(
            self.user_journey.ram_needed_per_service,
            expected_ram_per_service
        )

    def test_storage_need_per_service(self):
        expected_storage_per_service = {
            self.user_journey_step.request.service: (self.user_journey_step.request.data_upload
                                                     ).to(u.Mo / u.user_journey)
        }
        self.assertDictEqual(self.user_journey.storage_need_per_service, expected_storage_per_service)

    def test_cpu_need_per_service(self):
        expected_cpu_per_service = {
            self.user_journey_step.request.service: (self.user_journey_step.request.cpu_needed *
                                                     self.user_journey_step.request.duration
                                                     / (self.user_journey.duration * self.one_user_journey)
                                                     ).to(u.core / u.user_journey)
        }
        self.assertDictEqual(self.user_journey.cpu_need_per_service, expected_cpu_per_service)


if __name__ == "__main__":
    unittest.main()
