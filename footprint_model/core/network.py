from footprint_model.constants.explainable_quantities import ExplainableQuantity, ModelingObject
from footprint_model.constants.physical_elements import PhysicalElements, ObjectLinkedToUsagePatterns
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u


class Network(ObjectLinkedToUsagePatterns, ModelingObject):
    def __init__(self, name: PhysicalElements, bandwidth_energy_intensity: SourceValue):
        ModelingObject.__init__(self, name)
        super().__init__()
        self.data_upload = None
        self.data_download = None
        self.energy_footprint = None
        self.bandwidth_energy_intensity = bandwidth_energy_intensity
        self.bandwidth_energy_intensity.set_name(f"bandwith energy intensity of {self.name}")

        self.compute_calculated_attributes()

    def compute_calculated_attributes(self):
        self.update_data_download()
        self.update_data_upload()
        self.update_energy_footprint()

    def update_data_upload(self):
        data_upload = ExplainableQuantity(0 * u.Mo / u.year)
        for usage_pattern in self.usage_patterns:
            data_upload += usage_pattern.user_journey.data_upload * usage_pattern.user_journey_freq

        self.data_upload = data_upload.to(u.To / u.year).define_as_intermediate_calculation(
            f"Data upload in {self.name}")

    def update_data_download(self):
        data_download = ExplainableQuantity(0 * u.Mo / u.year)
        for usage_pattern in self.usage_patterns:
            data_download += usage_pattern.user_journey.data_download * usage_pattern.user_journey_freq

        self.data_download = data_download.to(u.To / u.year).define_as_intermediate_calculation(
            f"Data download in {self.name}")

    def update_energy_footprint(self):
        power_footprint = ExplainableQuantity(0 * u.kg / u.year)
        for usage_pattern in self.usage_patterns:
            user_journey = usage_pattern.user_journey
            uj_network_consumption = (
                        self.bandwidth_energy_intensity
                        * (user_journey.data_download + user_journey.data_upload)
            ).to(u.Wh / u.user_journey)
            uj_network_consumption.define_as_intermediate_calculation(
                f"{self.name} consumption during {user_journey.name}")
            power_footprint += (
                    usage_pattern.user_journey_freq * uj_network_consumption
                    * usage_pattern.device_population.country.average_carbon_intensity)

        self.energy_footprint = power_footprint.to(u.kg / u.year).define_as_intermediate_calculation(
            f"Energy footprint of {self.name}")


class Networks:
    WIFI_NETWORK = Network(
        PhysicalElements.WIFI_NETWORK,
        SourceValue(0.05 * u("kWh/Go"), Sources.TRAFICOM_STUDY),
        # TODO: enable list for multiple sources
        # SourceValue(0.08 * u("kWh/Go"), Sources.ONE_BYTE_MODEL_SHIFT_2018)
    )
    MOBILE_NETWORK = Network(
        PhysicalElements.MOBILE_NETWORK,
        SourceValue(0.12 * u("kWh/Go"), Sources.TRAFICOM_STUDY),
        # SourceValue(0.06 * u("kWh/Go"), Sources.ONE_BYTE_MODEL_SHIFT_2018)
    )
