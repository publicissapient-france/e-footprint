from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.service import Service
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.hardware.storage import Storage
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.core.usage.job import Job

from typing import List, Set, Type


class UserJourney(ModelingObject):
    def __init__(self, name: str, uj_steps: List[UserJourneyStep]):
        super().__init__(name)
        self.data_upload = None
        self.data_download = None
        self.duration = None
        self.uj_steps = uj_steps

    @property
    def calculated_attributes(self):
        return ["duration", "data_download", "data_upload"]

    @property
    def servers(self) -> List[Server]:
        servers = set()
        for job in self.jobs:
            servers = servers | {job.service.server}

        return list(servers)

    @property
    def storages(self) -> List[Storage]:
        storages = set()
        for job in self.jobs:
            storages = storages | {job.service.storage}

        return list(storages)

    @property
    def services(self) -> List[Service]:
        services = set()
        for job in self.jobs:
            services = services | {job.service}

        return list(services)

    @property
    def usage_patterns(self):
        return self.modeling_obj_containers

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[Type["UsagePattern"]]:
        return self.usage_patterns

    @property
    def jobs(self) -> List[Job]:
        output_list = []
        for uj_step in self.uj_steps:
            output_list += uj_step.jobs

        return output_list

    def add_step(self, step: UserJourneyStep) -> None:
        step.add_obj_to_modeling_obj_containers(self)
        self.uj_steps = self.uj_steps + [step]

    def update_duration(self):
        user_time_spent_sum = sum([uj_step.user_time_spent for uj_step in self.uj_steps])

        self.duration = user_time_spent_sum.set_label(f"Duration of {self.name}")

    def update_data_download(self):
        all_data_download = 0
        for job in self.jobs:
            all_data_download += job.data_download

        self.data_download = all_data_download.set_label(f"Data download of {self.name}")

    def update_data_upload(self):
        all_data_upload = 0
        for job in self.jobs:
            all_data_upload += job.data_upload

        self.data_upload = all_data_upload.set_label(f"Data upload of {self.name}")
