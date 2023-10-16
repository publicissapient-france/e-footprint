from footprint_model.constants.units import u
from footprint_model.constants.explainable_quantities import ExplainableQuantity, intermediate_calculation
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.core.service import Request, Service
from footprint_model.core.device_population import Device
from footprint_model.core.server import Server
from footprint_model.core.network import Network

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from pint import Quantity
from copy import deepcopy

from footprint_model.core.storage import Storage


class DataTransferredType:
    UPLOAD = "upload"
    DOWNLOAD = "download"


class UserJourneyStep:
    def __init__(self, name: str, request: Request, duration: Quantity, url_pattern: Optional[str] = None):
        self.name = name
        self.request = request
        if not duration.check("[time]"):
            raise ValueError("Variable 'duration' does not have the appropriate '[time]' dimensionality")
        self.duration = SourceValue(duration / u.user_journey, Sources.USER_INPUT, f"uj step {name} duration")
        self.url_pattern = url_pattern

    def __mul__(self, other):
        if type(other) not in [int, float]:
            raise ValueError(f"Can only multiply UserJourneyStep with int or float, not {type(other)}")
        raise NotImplementedError


@dataclass
class UserJourney:
    name: str
    uj_steps: List[UserJourneyStep] = field(default_factory=list)
    usage_patterns = set()

    def link_usage_pattern(self, usage_pattern):
        self.usage_patterns = self.usage_patterns | {usage_pattern}
        for server in self.servers:
            server.link_usage_pattern(usage_pattern)
        for storage in self.storages:
            storage.link_usage_pattern(usage_pattern)

    def unlink_usage_pattern(self, usage_pattern):
        self.usage_patterns.discard(usage_pattern)
        for server in self.servers:
            server.unlink_usage_pattern(usage_pattern)
        for storage in self.storages:
            storage.unlink_usage_pattern(usage_pattern)

    @property
    def servers(self) -> Set[Server]:
        servers = set()
        for uj_step in self.uj_steps:
            servers = servers | {uj_step.request.service.server}

        return servers

    @property
    def storages(self) -> Set[Storage]:
        storages = set()
        for uj_step in self.uj_steps:
            storages = storages | {uj_step.request.service.storage}

        return storages

    @property
    def services(self) -> Set[Service]:
        services = set()
        for uj_step in self.uj_steps:
            services = services | {uj_step.request.service}

        return services

    @property
    @intermediate_calculation("duration")
    def duration(self) -> ExplainableQuantity:
        uj_step_duration_sum = deepcopy(sum(elt.duration for elt in self.uj_steps))
        uj_step_duration_sum.formulas[0] = f"({uj_step_duration_sum.formulas[0]})"
        return uj_step_duration_sum

    @property
    @intermediate_calculation("data_download")
    def data_download(self) -> Quantity:
        all_data_download = 0
        for uj_step in self.uj_steps:
            all_data_download += uj_step.request.data_download
        return all_data_download

    @property
    @intermediate_calculation("data_upload")
    def data_upload(self) -> Quantity:
        all_data_upload = 0
        for uj_step in self.uj_steps:
            all_data_upload += uj_step.request.data_upload
        return all_data_upload

    def add_step(self, step: UserJourneyStep) -> None:
        self.uj_steps.append(step)

    @intermediate_calculation("Device energy consumption")
    def compute_device_consumption(self, device: Device) -> ExplainableQuantity:
        device_consumption = (device.power * self.duration).to(u.Wh / u.user_journey)
        return device_consumption

    def compute_fabrication_footprint(self, device: Device) -> ExplainableQuantity:
        uj_fabrication_footprint = (device.carbon_footprint_fabrication * self.duration
                                    / (device.lifespan * device.fraction_of_usage_time)).to(u.g / u.user_journey)
        uj_fabrication_footprint.define_as_intermediate_calculation(
            f"{device.name} fabrication footprint during {self.name}")
        return uj_fabrication_footprint

    def compute_network_consumption(self, network: Network) -> ExplainableQuantity:
        network_consumption = (network.bandwidth_energy_intensity * (self.data_download + self.data_upload)).to(
            u.Wh / u.user_journey)
        network_consumption.define_as_intermediate_calculation(f"{network.name} consumption during {self.name}")
        return network_consumption

    @property
    def ram_needed_per_service(self) -> Dict[Service, ExplainableQuantity]:
        ram_per_service = {}
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        for uj_step in self.uj_steps:
            service = uj_step.request.service
            ram_per_service[service] = ram_per_service.get(service, 0) + (
                    uj_step.request.ram_needed * uj_step.request.duration / (self.duration * one_user_journey)
            ).to(u.Mo / u.user_journey)
        for service in ram_per_service.keys():
            ram_per_service[service].define_as_intermediate_calculation(
                f"Ram need averaged over duration of {self.name} for service {service.name}")
        return ram_per_service

    @property
    def storage_need_per_service(self) -> Dict[Service, ExplainableQuantity]:
        storage_per_service = {}
        for uj_step in self.uj_steps:
            service = uj_step.request.service
            storage_per_service[service] = (
                    storage_per_service.get(service, 0) + uj_step.request.data_upload).to(u.Mo / u.user_journey)
        for service in storage_per_service.keys():
            storage_per_service[service].define_as_intermediate_calculation(
                f"Storage need of {self.name} for service {service.name}")
        return storage_per_service

    @property
    def cpu_need_per_service(self) -> Dict[Service, ExplainableQuantity]:
        cpu_per_service = {}
        one_user_journey = ExplainableQuantity(1 * u.user_journey, "One user journey")
        for uj_step in self.uj_steps:
            service = uj_step.request.service
            cpu_per_service[service] = cpu_per_service.get(service, 0) + (
                    uj_step.request.cpu_needed * uj_step.request.duration
                    / (self.duration * one_user_journey)).to(u.core / u.user_journey)
        for service in cpu_per_service.keys():
            cpu_per_service[service].define_as_intermediate_calculation(
                f"CPU need averaged over duration of {self.name} for service {service.name}")
        return cpu_per_service
