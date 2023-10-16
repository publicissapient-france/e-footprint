from unittest import TestCase

from footprint_model.constants.countries import Countries
from footprint_model.core.user_journey import UserJourney, UserJourneyStep, DataTransferred, DataTransferredType, u
from footprint_model.constants.physical_elements import PhysicalElements

from footprint_model.core.system import System
from footprint_model.core.usage_pattern import Population, UsagePattern
from tests.test_utils import extract_values_from_dict


class IntegrationTest(TestCase):
    def test_base_use_case(self):
        user_journey = UserJourney("test user journey")
        user_journey_step = UserJourneyStep(
            "", [DataTransferred(DataTransferredType.DOWNLOAD, 3 * u.Mo)], 5 * u.min, tracking_data=0.1 * u.Mo)
        user_journey.add_step(user_journey_step)
        population = Population("buyers_sonepar", 1e6, Countries.FRANCE)
        usage_pattern = UsagePattern(
            "usage_pattern", user_journey, population, frac_smartphone=0.5, frac_mobile_network_for_smartphones=0.5,
            user_journey_freq_per_user=20 * u.user_journey / (u.user * u.year), usage_time_fraction=8 * u.hour / u.day)
        system = System(
            "System", [usage_pattern], data_replication_factor=2, data_storage_duration=3 * u.year, cloud=True)

        energy_consumption_dict = {usage_pattern: {
            PhysicalElements.SMARTPHONE: 833.3 * u.kWh / u.year,
            PhysicalElements.LAPTOP: 41666.7 * u.kWh / u.year,
            PhysicalElements.BOX: 12500.0 * u.kWh / u.year,
            PhysicalElements.SCREEN: 5000.0 * u.kWh / u.year,
            PhysicalElements.MOBILE_NETWORK: 1860.0 * u.kWh / u.year,
            PhysicalElements.WIFI_NETWORK: 2325.0 * u.kWh / u.year,
            PhysicalElements.SERVER: 134.5 * u.kWh / u.year,
            PhysicalElements.SSD: 54.7 * u.kWh / u.year,
        }}
        self.assertDictEqual(extract_values_from_dict(system.compute_energy_consumption(), imbricated_dict=True),
                             energy_consumption_dict)
        fabrication_dict = {usage_pattern: {
            PhysicalElements.SMARTPHONE: 6337.6 * u.kg / u.year,
            PhysicalElements.LAPTOP: 8474.3 * u.kg / u.year,
            PhysicalElements.BOX: 1853.8 * u.kg / u.year,
            PhysicalElements.SCREEN: 2411.9 * u.kg / u.year,
            PhysicalElements.SERVER: 4.3 * u.kg / u.year,
            PhysicalElements.SSD: 320.0 * u.kg / u.year
        }}
        self.assertDictEqual(extract_values_from_dict(system.compute_fabrication_emissions(), imbricated_dict=True),
                             fabrication_dict)
        energy_emissions_dict = {usage_pattern: {
            PhysicalElements.SMARTPHONE: 70.8 * u.kg / u.year,
            PhysicalElements.LAPTOP: 3541.7 * u.kg / u.year,
            PhysicalElements.BOX: 1062.5 * u.kg / u.year,
            PhysicalElements.SCREEN: 425 * u.kg / u.year,
            PhysicalElements.MOBILE_NETWORK: 158.1 * u.kg / u.year,
            PhysicalElements.WIFI_NETWORK: 197.6 * u.kg / u.year,
            PhysicalElements.SERVER: 11.4 * u.kg / u.year,
            PhysicalElements.SSD: 4.6 * u.kg / u.year,
        }}
        self.assertDictEqual(extract_values_from_dict(system.compute_energy_emissions(), imbricated_dict=True),
                             energy_emissions_dict)
