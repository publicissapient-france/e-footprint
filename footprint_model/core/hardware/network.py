from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.core.hardware.hardware_base_classes import ObjectLinkedToUsagePatterns
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u

from footprint_model.logger import logger


class Network(ObjectLinkedToUsagePatterns, ModelingObject):
    def __init__(self, name: str, bandwidth_energy_intensity: SourceValue):
        ModelingObject.__init__(self, name)
        super().__init__()
        self.data_upload = None
        self.data_download = None
        self.energy_footprint = None
        self.bandwidth_energy_intensity = bandwidth_energy_intensity
        self.bandwidth_energy_intensity.set_name(f"bandwith energy intensity of {self.name}")

    def compute_calculated_attributes(self):
        logger.info(f"Computing calculated attributes for network {self.name}")
        self.update_data_download()
        self.update_data_upload()
        self.update_energy_footprint()

    def update_data_upload(self):
        if len(self.usage_patterns) > 0:
            data_upload = 0
            for usage_pattern in self.usage_patterns:
                data_upload += usage_pattern.user_journey.data_upload * usage_pattern.user_journey_freq

            self.data_upload = data_upload.to(u.TB / u.year).define_as_intermediate_calculation(
                f"Data upload in {self.name}")
        else:
            self.data_download = ExplainableQuantity(
                0 * u.MB / u.year, f"No data upload for {self.name} because no associated usage pattern")

    def update_data_download(self):
        if len(self.usage_patterns) > 0:
            data_download = 0
            for usage_pattern in self.usage_patterns:
                data_download += usage_pattern.user_journey.data_download * usage_pattern.user_journey_freq

            self.data_download = data_download.to(u.TB / u.year).define_as_intermediate_calculation(
                f"Data download in {self.name}")
        else:
            self.data_download = ExplainableQuantity(
                0 * u.MB / u.year, f"No data download for {self.name} because no associated usage pattern")

    def update_energy_footprint(self):
        if len(self.usage_patterns) > 0:
            power_footprint = 0
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

        else:
            self.energy_footprint = ExplainableQuantity(
                0 * u.kg / u.year, f"No energy footprint for {self.name} because no associated usage pattern")


class Networks:
    WIFI_NETWORK = Network(
        PhysicalElements.WIFI_NETWORK,
        SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY),
        # TODO: enable list for multiple sources
        # SourceValue(0.08 * u("kWh/GB"), Sources.ONE_BYTE_MODEL_SHIFT_2018)
    )
    MOBILE_NETWORK = Network(
        PhysicalElements.MOBILE_NETWORK,
        SourceValue(0.12 * u("kWh/GB"), Sources.TRAFICOM_STUDY),
        # SourceValue(0.06 * u("kWh/GB"), Sources.ONE_BYTE_MODEL_SHIFT_2018)
    )
