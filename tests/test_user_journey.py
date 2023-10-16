import unittest
from unittest import TestCase
from unittest.mock import PropertyMock

from footprint_model.constants.physical_elements import Network, PhysicalElements, Device
from footprint_model.constants.sources import SourceValue, Sources, u
from footprint_model.core.user_journey import DataTransferred, DataTransferredType, UserJourneyStep, UserJourney


class TestUserJourney(TestCase):
    def test_add_step(self):
        user_journey = UserJourney()
        user_journey_step = UserJourneyStep("", DataTransferred(DataTransferredType.DOWNLOAD, 30 * u.Mo), 10 * u.s)
        user_journey.add_step(user_journey_step)
        self.assertEqual(user_journey.list_actions, [user_journey_step])

    def test_duration(self):
        duration1 = 10 * u.s
        duration2 = 30 * u.s
        user_journey_step1 = UserJourneyStep("", DataTransferred(DataTransferredType.DOWNLOAD, 30 * u.Mo), duration1)
        user_journey_step2 = UserJourneyStep("", DataTransferred(DataTransferredType.UPLOAD, 30 * u.Mo), duration2)
        self.assertEqual(UserJourney(list_actions=[user_journey_step1]).duration, duration1)
        self.assertEqual(UserJourney(list_actions=[user_journey_step2]).duration, duration2)
        self.assertEqual(
            UserJourney(list_actions=[user_journey_step1, user_journey_step2]).duration, duration1 + duration2
        )

    def test_data_download(self):
        data_download = 30 * u.Mo
        data_upload = 40 * u.Mo
        user_journey_step_download = UserJourneyStep(
            "", DataTransferred(DataTransferredType.DOWNLOAD, data_download), 10 * u.s
        )
        user_journey_step_upload = UserJourneyStep(
            "", DataTransferred(DataTransferredType.UPLOAD, data_upload), 10 * u.s
        )
        self.assertEqual(UserJourney(list_actions=[user_journey_step_download]).data_download, data_download)
        self.assertEqual(UserJourney(list_actions=[user_journey_step_download] * 2).data_download, data_download * 2)
        self.assertEqual(
            UserJourney(list_actions=[user_journey_step_download, user_journey_step_upload]).data_download,
            data_download,
        )

    def test_data_upload(self):
        data_download = 30 * u.Mo
        data_upload = 40 * u.Mo
        user_journey_step_download = UserJourneyStep(
            "", DataTransferred(DataTransferredType.DOWNLOAD, data_download), 10 * u.s
        )
        user_journey_step_upload = UserJourneyStep(
            "", DataTransferred(DataTransferredType.UPLOAD, data_upload), 10 * u.s
        )
        self.assertEqual(UserJourney(list_actions=[user_journey_step_upload]).data_upload, data_upload)
        self.assertEqual(UserJourney(list_actions=[user_journey_step_upload] * 2).data_upload, data_upload * 2)
        self.assertEqual(
            UserJourney(list_actions=[user_journey_step_download, user_journey_step_upload]).data_upload, data_upload
        )

    def test_compute_device_consumption(self):
        duration = 10 * u.s
        device_power = 3 * u.W
        device_consumption = device_power * duration
        device = Device(
            PhysicalElements.SMARTPHONE,
            carbon_footprint_fabrication=SourceValue(60 * u.W, Sources.BASE_ADEME_V19),
            power=SourceValue(device_power, Sources.HYPOTHESIS),
            lifespan=SourceValue(3 * u.year, Sources.HYPOTHESIS),
            average_usage_duration_per_day=SourceValue(3 * u.year, Sources.HYPOTHESIS),
        )
        with unittest.mock.patch("footprint_model.core.user_journey.UserJourney.duration", new_callable=PropertyMock) as mock_duration:
            mock_duration.return_value = duration
            user_journey = UserJourney()
            device_consumption_computed = user_journey.compute_device_consumption(device)
            self.assertEqual(device_consumption_computed, device_consumption)

    def test_compute_fabrication_footprint(self):
        duration = 10 * u.s
        carbon_footprint_fabrication = 60 * u.kg
        average_usage_duration_per_day = 3 * u.hour
        lifespan = 3 * u.year
        fabrication_footprint = carbon_footprint_fabrication * duration / (lifespan * average_usage_duration_per_day)
        device = Device(
            PhysicalElements.SMARTPHONE,
            carbon_footprint_fabrication=SourceValue(carbon_footprint_fabrication, Sources.BASE_ADEME_V19),
            power=SourceValue(1 * u.W, Sources.HYPOTHESIS),
            lifespan=SourceValue(lifespan, Sources.HYPOTHESIS),
            average_usage_duration_per_day=SourceValue(average_usage_duration_per_day, Sources.HYPOTHESIS),
        )
        with unittest.mock.patch("footprint_model.core.user_journey.UserJourney.duration", new_callable=PropertyMock) as mock_duration:
            mock_duration.return_value = duration
            user_journey = UserJourney()
            fabrication_footprint_computed = user_journey.compute_fabrication_footprint(device)
            self.assertEqual(fabrication_footprint_computed, fabrication_footprint)

    def test_compute_network_consumption(self):
        data_download = 10 * u.Mo
        data_upload = 20 * u.Mo
        bandwidth_energy_intensity = 0.05 * u("kWh/Go")
        network_consumption = (data_download + data_upload) * bandwidth_energy_intensity
        network = Network(
            PhysicalElements.WIFI_NETWORK,
            SourceValue(bandwidth_energy_intensity, Sources.TRAFICOM_STUDY),
        )
        with unittest.mock.patch(
            "footprint_model.core.user_journey.UserJourney.data_download", new_callable=PropertyMock
        ) as mock_data_download, unittest.mock.patch(
            "footprint_model.core.user_journey.UserJourney.data_upload", new_callable=PropertyMock
        ) as mock_data_upload:
            mock_data_download.return_value = data_download
            mock_data_upload.return_value = data_upload
            user_journey = UserJourney()
            network_consumption_computed = user_journey.compute_network_consumption(network)
            self.assertEqual(network_consumption_computed, network_consumption)


if __name__ == "__main__":
    unittest.main()
