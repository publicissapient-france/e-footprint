import math
from typing import List, Type

from efootprint.abstract_modeling_classes.explainable_object_dict import ExplainableObjectDict
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, EmptyExplainableObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.service import Service
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.usage.compute_nb_occurrences_in_parallel import compute_nb_avg_hourly_occurrences


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
        self.hourly_occurrences_per_usage_pattern = ExplainableObjectDict()
        self.hourly_avg_occurrences_per_usage_pattern = ExplainableObjectDict()
        self.hourly_data_upload_per_usage_pattern = ExplainableObjectDict()
        self.hourly_data_download_per_usage_pattern = ExplainableObjectDict()
        self.hourly_occurrences_across_usage_patterns = None
        self.hourly_avg_occurrences_across_usage_patterns = None
        self.hourly_data_upload_across_usage_patterns = None
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
    def calculated_attributes(self) -> List[str]:
        return ["hourly_occurrences_per_usage_pattern", "hourly_avg_occurrences_per_usage_pattern",
                "hourly_data_upload_per_usage_pattern", "hourly_data_download_per_usage_pattern",
                "hourly_occurrences_across_usage_patterns", "hourly_avg_occurrences_across_usage_patterns",
                "hourly_data_upload_across_usage_patterns"]

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
    def systems(self) -> List[Type["System"]]:
        return list(set(sum([up.systems for up in self.usage_patterns], start=[])))

    @property
    def networks(self) -> List[Type["Network"]]:
        return list(set(up.network for up in self.usage_patterns))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self) -> List[ModelingObject]:
        return [self.service] + self.networks

    def compute_hourly_occurrences_for_usage_pattern(self, usage_pattern: Type["UsagePattern"]):
        job_occurrences = EmptyExplainableObject()
        delay_between_uj_start_and_job_evt = EmptyExplainableObject()
        delay_in_hours_between_uj_start_and_job_evt = 0
        for uj_step in usage_pattern.user_journey.uj_steps:
            for uj_step_job in uj_step.jobs:
                if uj_step_job == self:
                    job_occurrences += usage_pattern.utc_hourly_user_journey_starts.return_shifted_hourly_quantities(
                        delay_in_hours_between_uj_start_and_job_evt)

            delay_between_uj_start_and_job_evt += uj_step.user_time_spent
            delay_in_hours_between_uj_start_and_job_evt = math.floor(
                delay_between_uj_start_and_job_evt.to(u.hour).magnitude)

        return job_occurrences.set_label(f"Hourly {self.name} occurrences in {usage_pattern.name}")

    def update_hourly_occurrences_per_usage_pattern(self):
        self.hourly_occurrences_per_usage_pattern = ExplainableObjectDict()
        for up in self.usage_patterns:
            self.hourly_occurrences_per_usage_pattern[up] = self.compute_hourly_occurrences_for_usage_pattern(up)

    def update_hourly_avg_occurrences_per_usage_pattern(self):
        self.hourly_avg_occurrences_per_usage_pattern = ExplainableObjectDict()
        for up in self.usage_patterns:
            hourly_avg_job_occurrences = compute_nb_avg_hourly_occurrences(
                self.hourly_occurrences_per_usage_pattern[up], self.request_duration)

            self.hourly_avg_occurrences_per_usage_pattern[up] = hourly_avg_job_occurrences.set_label(
                f"Average hourly {self.name} occurrences in {up.name}")

    def compute_hourly_data_exchange_for_usage_pattern(self, usage_pattern, data_exchange_type: str):
        data_exchange_type_no_underscore = data_exchange_type.replace("_", " ")

        hourly_data_exchange = EmptyExplainableObject()
        data_exchange_per_hour = (getattr(self, data_exchange_type) / self.duration_in_full_hours).set_label(
            f"{data_exchange_type_no_underscore} per hour for job {self.name} in {usage_pattern.name}")

        for hour_shift in range(0, self.duration_in_full_hours.magnitude):
            if not isinstance(self.hourly_occurrences_per_usage_pattern[usage_pattern], EmptyExplainableObject):
                hourly_data_exchange += (
                        self.hourly_occurrences_per_usage_pattern[usage_pattern].return_shifted_hourly_quantities(
                            hour_shift) * data_exchange_per_hour)

        return hourly_data_exchange.set_label(
                f"Hourly {data_exchange_type_no_underscore} for {self.name} in {usage_pattern.name}")

    def update_hourly_data_upload_per_usage_pattern(self):
        self.hourly_data_upload_per_usage_pattern = ExplainableObjectDict()
        for up in self.usage_patterns:
            self.hourly_data_upload_per_usage_pattern[up] = self.compute_hourly_data_exchange_for_usage_pattern(
                up, "data_upload")

    def update_hourly_data_download_per_usage_pattern(self):
        self.hourly_data_download_per_usage_pattern = ExplainableObjectDict()
        for up in self.usage_patterns:
            self.hourly_data_download_per_usage_pattern[up] = self.compute_hourly_data_exchange_for_usage_pattern(
                up, "data_download")
            
    def sum_calculated_attribute_across_usage_patterns(
            self, calculated_attribute_name: str, calculated_attribute_label: str):
        hourly_calc_attr_summed_across_ups = EmptyExplainableObject()
        for usage_pattern in self.usage_patterns:
            hourly_calc_attr_summed_across_ups += getattr(self, calculated_attribute_name)[usage_pattern]

        return hourly_calc_attr_summed_across_ups.set_label(
                f"Hourly {self.name} {calculated_attribute_label} across usage patterns")

    def update_hourly_occurrences_across_usage_patterns(self):
        self.hourly_occurrences_across_usage_patterns = self.sum_calculated_attribute_across_usage_patterns(
            "hourly_occurrences_per_usage_pattern", "occurrences")

    def update_hourly_avg_occurrences_across_usage_patterns(self):
        self.hourly_avg_occurrences_across_usage_patterns = self.sum_calculated_attribute_across_usage_patterns(
            "hourly_avg_occurrences_per_usage_pattern", "average occurrences")

    def update_hourly_data_upload_across_usage_patterns(self):
        self.hourly_data_upload_across_usage_patterns = self.sum_calculated_attribute_across_usage_patterns(
            "hourly_data_upload_per_usage_pattern", "data upload")