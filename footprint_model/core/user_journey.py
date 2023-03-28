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
    size: Quantity
    is_stored: bool = False

    def __post_init__(self):
        if not self.size.check("[data]"):
            raise ValueError("Variable 'size' does not have the appropriate '[data]' dimensionality")


@dataclass
class UserJourneyStep:
    name: str
    data_transferred: List[DataTransferred]
    duration: Quantity
    tracking_data: Quantity
    url_pattern: Optional[str] = None

    def __post_init__(self):
        if not self.duration.check("[time]"):
            raise ValueError("Variable 'duration' does not have the appropriate '[time]' dimensionality")

        if not self.tracking_data.check("[data]"):
            raise ValueError("Variable 'tracking_data' does not have the appropriate '[data]' dimensionality")

        if not type(self.data_transferred) == list:
            raise ValueError("data_transferred should be a list")

        if self.tracking_data > 0 * u.o:
            self.data_transferred.append(DataTransferred(DataTransferredType.UPLOAD, self.tracking_data))


@dataclass
class UserJourney:
    # TODO : add device attribute
    uj_steps: List[UserJourneyStep] = field(default_factory=list)

    @property
    def duration(self) -> Quantity:
        return sum(elt.duration for elt in self.uj_steps)

    def _compute_bandwidth(self, transferred_type: DataTransferredType) -> Quantity:
        # TODO: write tests for this function
        all_data_transferred = []
        for uj_step in self.uj_steps:
            all_data_transferred += uj_step.data_transferred
        return sum(
            [data_transfer.size for data_transfer in all_data_transferred if data_transfer.type == transferred_type],
            # Specify starting value of sum to keep the unit
            0 * u.o
        )

    @property
    def data_download(self) -> Quantity:
        return self._compute_bandwidth(DataTransferredType.DOWNLOAD)

    @property
    def data_upload(self) -> Quantity:
        return self._compute_bandwidth(DataTransferredType.UPLOAD)

    def add_step(self, step: UserJourneyStep) -> None:
        self.uj_steps.append(step)

    def compute_device_consumption(self, device: Device) -> Quantity:
        return device.power * self.duration

    def compute_fabrication_footprint(self, device: Device) -> Quantity:
        return (
            device.carbon_footprint_fabrication
            * self.duration
            / (device.lifespan * device.fraction_of_usage_per_day)
        ).to(u.kg)

    def compute_network_consumption(self, network: Network) -> Quantity:
        return network.bandwidth_energy_intensity * (self.data_download + self.data_upload)
