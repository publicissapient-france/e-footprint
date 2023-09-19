from footprint_model.constants.units import u
from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from footprint_model.constants.sources import SourceValue
from footprint_model.core.service import Service
from footprint_model.core.hardware.server import Server

from typing import List, Set
from copy import deepcopy

from footprint_model.core.hardware.storage import Storage


class DataTransferredType:
    UPLOAD = "upload"
    DOWNLOAD = "download"


class UserJourneyStep(ModelingObject):
    def __init__(self, name: str, service: Service, data_upload: SourceValue, data_download: SourceValue,
                 user_time_spent: SourceValue, request_duration: SourceValue = SourceValue(1 * u.s),
                 cpu_needed: SourceValue = SourceValue(1 * u.core / u.uj),
                 server_ram_per_data_transferred: SourceValue = SourceValue(2 * u.dimensionless)):
        super().__init__(name)
        self.ram_needed = None
        self.service = service
        if not data_upload.value.check("[]/[user_journey]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[]/[user_journey]' dimensionality")
        if not data_download.value.check("[]/[user_journey]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[]/[user_journey]' dimensionality")
        self.data_upload = data_upload
        self.data_upload.set_name(f"Data upload of request {self.name}")
        self.data_download = data_download
        self.data_download.set_name(f"Data download of request {self.name}")

        if not user_time_spent.value.check("[time]/[user_journey]"):
            raise ValueError(
                "Variable 'user_time_spent' does not have the appropriate '[time]/[user_journey]' dimensionality")
        self.user_time_spent = user_time_spent
        self.user_time_spent.set_name(f"Time spent on step {self.name}")
        if not request_duration.value.check("[time]"):
            raise ValueError("Variable 'request_duration' does not have the appropriate '[time]' dimensionality")
        self.request_duration = request_duration
        self.request_duration.set_name(f"Request duration to {self.service.name} in {self.name}")
        if request_duration.value > user_time_spent.value * u.uj:
            raise ValueError("Variable 'request_duration' can not be greater than variable 'user_time_spent'")

        self.server_ram_per_data_transferred = server_ram_per_data_transferred
        self.server_ram_per_data_transferred.set_name(
            f"Ratio of RAM server used over quantity of data sent to user during {self.name}")

        if not cpu_needed.value.check("[cpu] / [user_journey]"):
            raise ValueError(
                "Variable 'cpu_needed' does not have the appropriate '[cpu] / [user_journey]' dimensionality")
        self.cpu_needed = cpu_needed
        self.cpu_needed.set_name(f"CPU needed on server {self.service.server.name} to process request {self.name}")

        self.compute_calculated_attributes()

    def __mul__(self, other):
        if type(other) not in [int, float]:
            raise ValueError(f"Can only multiply UserJourneyStep with int or float, not {type(other)}")
        raise NotImplementedError

    def compute_calculated_attributes(self):
        self.update_ram_needed()

    def update_ram_needed(self):
        ram_needed = (self.server_ram_per_data_transferred * self.data_download)

        self.ram_needed = ram_needed.define_as_intermediate_calculation(f"Ram needed for {self.name}")


class UserJourney(ModelingObject):
    def __init__(self, name: str, uj_steps: List[UserJourneyStep]):
        super().__init__(name)
        self.data_upload = None
        self.data_download = None
        self.duration = None
        self.uj_steps = uj_steps
        self.usage_patterns = set()
        self.compute_calculated_attributes()

    def compute_calculated_attributes(self):
        self.update_duration()
        self.update_data_upload()
        self.update_data_download()

    def link_usage_pattern(self, usage_pattern):
        self.usage_patterns = self.usage_patterns | {usage_pattern}
        for service in self.services:
            service.link_usage_pattern(usage_pattern)
        for server in self.servers:
            server.link_usage_pattern(usage_pattern)
        for storage in self.storages:
            storage.link_usage_pattern(usage_pattern)

    def unlink_usage_pattern(self, usage_pattern):
        self.usage_patterns.discard(usage_pattern)
        for service in self.services:
            service.unlink_usage_pattern(usage_pattern)
        for server in self.servers:
            server.unlink_usage_pattern(usage_pattern)
        for storage in self.storages:
            storage.unlink_usage_pattern(usage_pattern)

    def add_step(self, step: UserJourneyStep) -> None:
        self.uj_steps.append(step)
        self.compute_calculated_attributes()

    @property
    def servers(self) -> Set[Server]:
        servers = set()
        for uj_step in self.uj_steps:
            servers = servers | {uj_step.service.server}

        return servers

    @property
    def storages(self) -> Set[Storage]:
        storages = set()
        for uj_step in self.uj_steps:
            storages = storages | {uj_step.service.storage}

        return storages

    @property
    def services(self) -> Set[Service]:
        services = set()
        for uj_step in self.uj_steps:
            services = services | {uj_step.service}

        return services

    def update_duration(self):
        user_time_spents = [uj_step.user_time_spent for uj_step in self.uj_steps]
        user_time_spent_sum = deepcopy(sum(user_time_spents))

        self.duration = user_time_spent_sum.define_as_intermediate_calculation(f"Duration of {self.name}")

    def update_data_download(self):
        uj_steps_data_downloads = [uj_step.data_download for uj_step in self.uj_steps]
        all_data_download = ExplainableQuantity(0 * u.MB / u.user_journey)
        for data_download in uj_steps_data_downloads:
            all_data_download += data_download

        self.data_download = all_data_download.define_as_intermediate_calculation(f"Data download of {self.name}")

    def update_data_upload(self):
        uj_steps_data_uploads = [uj_step.data_upload for uj_step in self.uj_steps]
        all_data_upload = ExplainableQuantity(0 * u.MB / u.user_journey)
        for data_upload in uj_steps_data_uploads:
            all_data_upload += data_upload

        self.data_upload = all_data_upload.define_as_intermediate_calculation(f"Data upload of {self.name}")