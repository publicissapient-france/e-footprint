from efootprint.constants.units import u
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.service import Service
from efootprint.constants.sources import SourceValue

from typing import List, Set, Type, Optional

class JobTypes:
    DATABASE_READ = "database_read"
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

