from footprint_model.constants.units import u
from footprint_model.constants.physical_elements import Device, Network

from dataclasses import dataclass, field
from typing import List, Optional
from pint import Quantity
import enum


class DataTransferredType(str, enum.Enum):
    UPLOAD = "upload"
    DOWNLOAD = "download"


@dataclass
class DataTransferred:
    type: DataTransferredType
    size: Quantity = 10 * u.Mo  # MB
    is_stored: bool = False

    def __post_init__(self):
        if not self.size.check("[data]"):
            raise ValueError("Variable 'size' does not have the appropriate '[data]' dimensionality")


@dataclass
class UserJourneyStep:
    name: str
    data_transferred: DataTransferred
    duration: Quantity
    url_pattern: Optional[str] = None

    def __post_init__(self):
        if not self.duration.check("[time]"):
            raise ValueError("Variable 'duration' does not have the appropriate '[time]' dimensionality")


@dataclass
class UserJourney:
    # TODO : add device attribute
    list_actions: List[UserJourneyStep] = field(default_factory=list)

    @property
    def duration(self) -> Quantity:
        return sum(elt.duration for elt in self.list_actions)

    def _compute_bandwidth(self, transferred_type: DataTransferredType) -> Quantity:
        # TODO: write tests for this function
        return sum(
            elt.data_transferred.size for elt in self.list_actions if elt.data_transferred.type == transferred_type
        )

    @property
    def data_download(self) -> Quantity:
        return self._compute_bandwidth(DataTransferredType.DOWNLOAD)

    @property
    def data_upload(self) -> Quantity:
        return self._compute_bandwidth(DataTransferredType.UPLOAD)

    def add_step(self, step: UserJourneyStep) -> None:
        self.list_actions.append(step)

    def compute_device_consumption(self, device: Device) -> Quantity:
        return device.power.value * self.duration

    def compute_fabrication_footprint(self, device: Device) -> Quantity:
        return (
            device.carbon_footprint_fabrication.value
            * self.duration
            / (device.lifespan.value * device.average_usage_duration_per_day.value)
        )

    def compute_network_consumption(self, network: Network) -> Quantity:
        return (self.data_download + self.data_upload) * network.bandwidth_energy_intensity.value
