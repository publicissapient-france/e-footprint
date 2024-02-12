from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.core.service import Service
from efootprint.core.hardware.servers.server_base_class import Server
from efootprint.core.hardware.storage import Storage
from efootprint.core.usage.job import Job

from typing import List, Set, Type


class UserJourneyStep(ModelingObject):
    def __init__(self, name: str, user_time_spent: SourceValue, jobs: List[Job]):
        super().__init__(name)

        if not user_time_spent.value.check("[time]/[user_journey]"):
            raise ValueError(
                "Variable 'user_time_spent' does not have the appropriate '[time]/[user_journey]' dimensionality")
        self.user_time_spent = user_time_spent
        self.user_time_spent.set_label(f"Time spent on step {self.name}")
        self.jobs = jobs

    @property
    def user_journeys(self) -> List[Type["UserJourney"]]:
        return self.modeling_obj_containers

    @property
    def usage_patterns(self) -> List[Type["UsagePattern"]]:
        return list(set(sum([uj.usage_patterns for uj in self.user_journeys], start=[])))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[Type["UserJourney"]]:
        return self.user_journeys


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
    def servers(self) -> Set[Server]:
        servers = set()
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                if job.service is not None:
                    servers = servers | {job.service.server}

        return servers

    @property
    def storages(self) -> Set[Storage]:
        storages = set()
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                storages = storages | {job.service.storage}

        return storages

    @property
    def services(self) -> List[Service]:
        services = set()
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                if job.service is not None:
                    services = services | {job.service}

        return list(services)

    @property
    def usage_patterns(self):
        return self.modeling_obj_containers

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[Type["UsagePattern"]]:
        return self.usage_patterns

    def after_init(self):
        self.init_has_passed = True
        self.compute_calculated_attributes()

    def add_step(self, step: UserJourneyStep) -> None:
        step.add_obj_to_modeling_obj_containers(self)
        self.uj_steps = self.uj_steps + [step]

    def update_duration(self):
        user_time_spent_sum = sum([uj_step.user_time_spent for uj_step in self.uj_steps])

        self.duration = user_time_spent_sum.set_label(f"Duration of {self.name}")

    def update_data_download(self):
        all_data_download = 0
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                all_data_download += job.data_download

        self.data_download = all_data_download.set_label(f"Data download of {self.name}")

    def update_data_upload(self):
        all_data_upload = 0
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                all_data_upload += job.data_upload

        self.data_upload = all_data_upload.set_label(f"Data upload of {self.name}")
