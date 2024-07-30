import math
from typing import List, Type

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.service import Service
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u


class JobTypes:
    AUTH = "auth"
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_LIST = "data_list"
    DATA_SIMPLE_ANALYTIC = "data_simple_analytic"
    DATA_STREAM = "data_stream" #video, musique, data 
    TRANSACTION = "transaction"
    TRANSACTION_STRONG = "transaction_strong"
    NOTIFICATION = "notification"
    ANALYTIC_DATA_LOADING = "analytic_data_loading"
    ANALYTIC_READING_PREPARED = "analytic_reading_prepared"
    ANALYTIC_READING_ON_THE_FLY = "analytic_reading_on_the_fly"
    ML_RECOMMENDATION ="ml_reco" #kvm
    ML_LLM ="ml_llm"
    ML_DEEPLEARNING ="ml_dl"
    ML_REGRESSION = "ml_regression" #linear regression, polynomial regression, svm
    ML_CLASSIFIER = "ml_classifier" #bayes, random forest
    UNDEFINED = "undefined"


class Job(ModelingObject):
    def __init__(self, name: str, service: Service, data_upload: SourceValue, data_download: SourceValue,
                 request_duration: SourceValue, cpu_needed: SourceValue, ram_needed: SourceValue,
                 job_type: JobTypes = JobTypes.UNDEFINED, description: str = ""):
        super().__init__(name)
        self.job_type = job_type
        self.service = service
        if not data_upload.value.check("[]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[]' dimensionality")
        self.data_upload = data_upload.set_label(f"Data upload of request {self.name}")
        if not data_download.value.check("[]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[]' dimensionality")
        self.data_download = data_download.set_label(f"Data download of request {self.name}")
        if not request_duration.value.check("[time]"):
            raise ValueError("Variable 'request_duration' does not have the appropriate '[time]' dimensionality")
        self.request_duration = request_duration.set_label(f"Request duration to {self.service.name} in {self.name}")
        if not ram_needed.value.check("[]"):
            raise ValueError(
                "Variable 'ram_needed' does not have the appropriate '[]' dimensionality")
        self.ram_needed = ram_needed.set_label(
            f"RAM needed on server {self.service.server.name} to process {self.name}")
        if not cpu_needed.value.check("[cpu]"):
            raise ValueError(
                "Variable 'cpu_needed' does not have the appropriate '[cpu]' dimensionality")
        self.cpu_needed = cpu_needed.set_label(
            f"CPU needed on server {self.service.server.name} to process {self.name}")

        self.description = description

    @property
    def duration_in_full_hours(self):
        return ExplainableQuantity(
                math.ceil(self.request_duration.to(u.hour).magnitude) * u.dimensionless,
                f"{self.name} duration in full hours")

    @property
    def user_journey_steps(self) -> List[Type["UserJourneyStep"]]:
        return self.modeling_obj_containers

    @property
    def user_journeys(self) -> List[Type["UserJourney"]]:
        return list(set(sum([uj_step.user_journeys for uj_step in self.user_journey_steps], start=[])))

    @property
    def usage_patterns(self) -> List[Type["UsagePattern"]]:
        return list(set(sum([uj_step.usage_patterns for uj_step in self.user_journey_steps], start=[])))

    @property
    def systems(self) -> List:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        if len(self.user_journeys) > 0:
            return self.user_journeys
        else:
            return [self.service]
