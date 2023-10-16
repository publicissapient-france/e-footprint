from unittest import TestCase

from footprint_model.constants.countries import Countries
from footprint_model.core.user_journey import UserJourney, UserJourneyStep, DataTransferred, DataTransferredType, u
from footprint_model.constants.physical_elements import PhysicalElements

from footprint_model.core.system import Population, UsagePattern, System


class IntegrationTest(TestCase):
    def test_base_use_case(self):
        user_journey = UserJourney()
        user_journey_step = UserJourneyStep(
            "", [DataTransferred(DataTransferredType.DOWNLOAD, 3 * u.Mo)], 5 * u.min, tracking_data=0.1 * u.Mo)
        user_journey.add_step(user_journey_step)
        population = Population("buyers_sonepar", 1e6, Countries.FRANCE)
        usage_pattern = UsagePattern(user_journey, population, frac_smartphone=0.5,
                                     frac_mobile_network_for_smartphones=0.5,
                                     nb_visits_per_user_per_year=20, daily_usage_window=8 * u.hour)
        system = System(usage_pattern, data_replication_factor=2, data_storage_duration=3 * u.year, cloud=True)

        energy_consumption_dict = {
            PhysicalElements.SMARTPHONE: 833.3 * u.kWh,
            PhysicalElements.LAPTOP: 41666.7 * u.kWh,
            PhysicalElements.BOX: 12500.0 * u.kWh,
            PhysicalElements.SCREEN: 5000.0 * u.kWh,
            PhysicalElements.MOBILE_NETWORK: 1860.0 * u.kWh,
            PhysicalElements.WIFI_NETWORK: 2325.0 * u.kWh,
            PhysicalElements.SERVER: 134.6 * u.kWh,
            PhysicalElements.SSD: 54.7 * u.kWh,
        }
        self.assertDictEqual(system.compute_energy_consumption(), energy_consumption_dict)
        fabrication_dict = {
            PhysicalElements.SMARTPHONE: 6337.6 * u.kg,
            PhysicalElements.LAPTOP: 8474.3 * u.kg,
            PhysicalElements.BOX: 1853.8 * u.kg,
            PhysicalElements.SCREEN: 2411.9 * u.kg,
            PhysicalElements.SERVER: 4.3 * u.kg,
            PhysicalElements.SSD: 320.0 * u.kg}
        self.assertDictEqual(system.compute_fabrication_emissions(), fabrication_dict)
        energy_emissions_dict = {
            PhysicalElements.SMARTPHONE: 50.0 * u.kg,
            PhysicalElements.LAPTOP: 2500.0 * u.kg,
            PhysicalElements.BOX: 750.0 * u.kg,
            PhysicalElements.SCREEN: 300.0 * u.kg,
            PhysicalElements.MOBILE_NETWORK: 111.6 * u.kg,
            PhysicalElements.WIFI_NETWORK: 139.5 * u.kg,
            PhysicalElements.SERVER: 8.1 * u.kg,
            PhysicalElements.SSD: 3.3 * u.kg,
        }
        self.assertDictEqual(system.compute_energy_emissions(), energy_emissions_dict)
