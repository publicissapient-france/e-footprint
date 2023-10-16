from footprint_model.core.storage import Storage
from footprint_model.core.server import Server
from footprint_model.constants.sources import SourceValue, Sources
from footprint_model.constants.units import u
from pint import Quantity


class Service:
    def __init__(self, name: str, server: Server, storage: Storage, base_ram_consumption: Quantity,
                 base_cpu_consumption: Quantity = 1 * u.core):
        self.name = name
        self.server = server
        self.storage = storage
        if not base_ram_consumption.check("[data]"):
            raise ValueError("variable 'base_ram_consumption' does not have octet dimensionality")
        if not base_cpu_consumption.check("[cpu]"):
            raise ValueError("variable 'base_cpu_consumption' does not have core dimensionality")
        self.base_ram_consumption = SourceValue(
            base_ram_consumption, Sources.USER_INPUT, f"Base RAM consumption of {self.name}")
        self.base_cpu_consumption = SourceValue(
            base_cpu_consumption, Sources.USER_INPUT, f"Base CPU consumption of {self.name}")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Service):
            return self.name == other.name
        return False


class Request:
    def __init__(self, name: str, service: Service, data_upload: Quantity, data_download: Quantity,
                 duration: Quantity = 1 * u.s, cpu_needed: Quantity = 1 * u.core,
                 server_ram_per_data_transfered : SourceValue = SourceValue(
                     5 * u.dimensionless, Sources.HYPOTHESIS,
                     "Ratio of server RAM needed per quantity of data transferred for one user journey")):
        self.name = name
        self.service = service
        self.duration = SourceValue(duration, Sources.USER_INPUT, f"Duration of request {self.name}")
        if not data_upload.check("[data]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[data]' dimensionality")
        if not data_download.check("[data]"):
            raise ValueError("Variable 'data_upload' does not have the appropriate '[data]' dimensionality")
        self.data_upload = SourceValue(
            data_upload / u.user_journey, Sources.USER_INPUT, f"Data upload of request {self.name}")
        self.data_download = SourceValue(
            data_download / u.user_journey, Sources.USER_INPUT, f"Data download of request {self.name}")
        if not server_ram_per_data_transfered.value.check("[]"):
            raise ValueError(
                "Variable 'server_ram_per_data_transfered' does not have the appropriate '[]' dimensionality")
        self.server_ram_per_data_transfered = server_ram_per_data_transfered

        self.cpu_needed = SourceValue(cpu_needed / u.user_journey, Sources.USER_INPUT,
                                      f"CPU needed on server {self.service.server.name} to process request {self.name}")

    @property
    def ram_needed(self):
        return (self.server_ram_per_data_transfered * self.data_download).define_as_intermediate_calculation(
            f"RAM needed on server {self.service.server.name} to process request {self.name}")
