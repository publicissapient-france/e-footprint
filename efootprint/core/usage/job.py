from efootprint.constants.units import u
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.service import Service
from efootprint.constants.sources import SourceValue

from typing import List, Set, Type, Optional

class JobTypes:
    AUTH = "auth"
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_LIST = "data_list"
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
    def __init__(self, 
                 name: str, 
                 service: Service, 
                 data_upload: SourceValue, 
                 data_download: SourceValue,
                 request_duration: SourceValue,
                 cpu_needed: SourceValue, 
                 ram_needed: SourceValue, 
                 job_type: JobTypes = JobTypes.UNDEFINED,
                 description: str = ""):
        super().__init__(name)
        self.description = description
        self.service = service
        if not data_upload.value.check("[]/[user_journey]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[]/[user_journey]' dimensionality")
        if not data_download.value.check("[]/[user_journey]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[]/[user_journey]' dimensionality")
        self.data_upload = data_upload
        self.data_upload.set_name(f"Data upload of request {self.name}")
        self.data_download = data_download
        self.data_download.set_name(f"Data download of request {self.name}")

        if not request_duration.value.check("[time]"):
            raise ValueError("Variable 'request_duration' does not have the appropriate '[time]' dimensionality")
        self.request_duration = request_duration
        self.request_duration.set_name(f"Request duration to {self.service.name} in {self.name}")

        # check ram_needed value format
        if not ram_needed.value.check("[] / [user_journey]"):
            raise ValueError(
                "Variable 'ram_needed' does not have the appropriate '[] / [user_journey]' dimensionality")
        self.ram_needed = ram_needed
        self.ram_needed.set_name(f"RAM needed on server {self.service.server.name} to process {self.name}")

        # check cpu_need value format
        if not cpu_needed.value.check("[cpu] / [user_journey]"):
            raise ValueError(
                "Variable 'cpu_needed' does not have the appropriate '[cpu] / [user_journey]' dimensionality")
        self.cpu_needed = cpu_needed
        self.cpu_needed.set_name(f"CPU needed on server {self.service.server.name} to process {self.name}")

