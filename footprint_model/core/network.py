from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation
from footprint_model.constants.physical_elements import PhysicalElements, ObjectLinkedToUsagePatterns
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u


class Network(ObjectLinkedToUsagePatterns):
    def __init__(self, name: PhysicalElements, bandwidth_energy_intensity: SourceValue):
        super().__init__()
        self.name = name
        self.bandwidth_energy_intensity = bandwidth_energy_intensity
        self.bandwidth_energy_intensity.set_name(f"bandwith energy intensity of {self.name}")

    @property
    @intermediate_calculation("Data upload")
    def data_upload(self) -> ExplainableQuantity:
        data_upload = ExplainableQuantity(0 * u.Mo)
        for usage_pattern in self.usage_patterns:
            data_upload += usage_pattern.user_journey.data_upload * usage_pattern.user_journey_freq

        return data_upload.to(u.To / u.year)

    @property
    @intermediate_calculation("Data download")
    def data_download(self) -> ExplainableQuantity:
        data_download = ExplainableQuantity(0 * u.Mo)
        for usage_pattern in self.usage_patterns:
            data_download += usage_pattern.user_journey.data_download * usage_pattern.user_journey_freq

        return data_download.to(u.To / u.year)

    @property
    @intermediate_calculation("Energy footprint")
    def energy_footprint(self) -> ExplainableQuantity:
        power_footprint = ExplainableQuantity(0 * u.kg / u.year)
        for usage_pattern in self.usage_patterns:
            power_footprint += (
                    usage_pattern.user_journey_freq * usage_pattern.user_journey.compute_network_consumption(self)
                    * usage_pattern.device_population.country.average_carbon_intensity)

        return power_footprint.to(u.kg / u.year)


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
