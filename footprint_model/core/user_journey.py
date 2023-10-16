from footprint_model.constants.units import u
from footprint_model.constants.physical_elements import Device, Network
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation

from dataclasses import dataclass, field
from typing import List, Optional
from pint import Quantity


class DataTransferredType:
    UPLOAD = "upload"
    DOWNLOAD = "download"


class DataTransferred:
    def __init__(
            self, data_transfer_type: DataTransferredType, size: Quantity, is_stored: bool = False,
            description: str = ""):
        self.type = data_transfer_type
        if not size.check("[data]"):
            raise ValueError("Variable 'size' does not have the appropriate '[data]' dimensionality")
        self.size = size / u.user_journey
        self.is_stored = is_stored
        self.description = description

    def __truediv__(self, other):
        if other.isinstance(Quantity):
            self.size = self.size / other
            return self
        else:
            raise ValueError(f"Can only divide DataTransferred with Quantities, not with {type(other)}")


class UserJourneyStep:
    def __init__(self, name: str, data_transferred: List[DataTransferred], duration: Quantity,
                 tracking_data: Quantity = 0 * u.o, url_pattern: Optional[str] = None):
        self.name = name
        if not type(data_transferred) == list:
            raise ValueError("data_transferred should be a list")
        self.data_transferred = data_transferred
        if not duration.check("[time]"):
            raise ValueError("Variable 'duration' does not have the appropriate '[time]' dimensionality")
        self.duration = ExplainableQuantity(duration / u.user_journey, f"uj step {name} duration")
        if not tracking_data.check("[data]"):
            raise ValueError("Variable 'tracking_data' does not have the appropriate '[data]' dimensionality")
        if tracking_data > 0 * u.o:
            self.data_transferred.append(DataTransferred(DataTransferredType.UPLOAD, tracking_data))
        elif tracking_data < 0 * u.o:
            raise ValueError("Variable 'tracking data' should be positive")
        self.url_pattern = url_pattern

    def __mul__(self, other):
        if type(other) not in [int, float]:
            raise ValueError(f"Can only multiply UserJourneyStep with int or float, not {type(other)}")
        data_transfers_copy = self.data_transferred.copy()
        for data_transfer in data_transfers_copy:
            data_transfer.size = data_transfer.size * other

        return UserJourneyStep(
            self.name, data_transfers_copy, self.duration * other, 0 * u.Mo, self.url_pattern)


@dataclass
class UserJourney:
    name: str
    # TODO : add device attribute
    name: str
    uj_steps: List[UserJourneyStep] = field(default_factory=list)

    @property
    @intermediate_calculation("duration")
    def duration(self) -> ExplainableQuantity:
        uj_step_duration_sum = sum(elt.duration for elt in self.uj_steps)
        uj_step_duration_sum.formulas[0] = f"({uj_step_duration_sum.formulas[0]})"
        return uj_step_duration_sum

    def _compute_bandwidth(self, transferred_type: DataTransferredType) -> Quantity:
        # TODO: write tests for this function
        all_data_transferred = []
        for uj_step in self.uj_steps:
            all_data_transferred += uj_step.data_transferred
        uj_bandwidth = (sum([data_transfer.size for data_transfer in all_data_transferred
                             if data_transfer.type == transferred_type]))
        return uj_bandwidth

    @property
    def data_download(self) -> Quantity:
        return ExplainableQuantity(
            self._compute_bandwidth(DataTransferredType.DOWNLOAD), f"Data download of step {self.name}")

    @property
    def data_upload(self) -> Quantity:
        return ExplainableQuantity(
            self._compute_bandwidth(DataTransferredType.UPLOAD), f"Data upload of step {self.name}")

    def add_step(self, step: UserJourneyStep) -> None:
        self.uj_steps.append(step)

    @intermediate_calculation("Device energy consumption")
    def compute_device_consumption(self, device: Device) -> Quantity:
        device_consumption = device.power * self.duration
        return device_consumption

    def compute_fabrication_footprint(self, device: Device) -> Quantity:
        uj_fabrication_footprint = (device.carbon_footprint_fabrication * self.duration
                                    / (device.lifespan * device.fraction_of_usage_time))
        uj_fabrication_footprint.define_as_intermediate_calculation(
            f"{device.name} fabrication footprint during {self.name}")
        return uj_fabrication_footprint

    def compute_network_consumption(self, network: Network) -> Quantity:
        network_consumption = network.bandwidth_energy_intensity * (self.data_download + self.data_upload)
        network_consumption.define_as_intermediate_calculation(f"{network.name} consumption during {self.name}")
        return network_consumption
