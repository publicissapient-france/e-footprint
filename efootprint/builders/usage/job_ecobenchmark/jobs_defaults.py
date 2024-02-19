from efootprint.core.usage.job import Job, JobTypes
from efootprint.builders.usage.job_ecobenchmark.ecobenchmark_data_analysis import ECOBENCHMARK_DATA
from typing import List

import pandas as pd

ECOBENCHMARK_DF=pd.read_csv(ECOBENCHMARK_DATA)

def ecobenchmark_job(technology: str, service: str, implementation_details: str ="default"):
    #load_dataframe
    tech_row=ECOBENCHMARK_DF[ECOBENCHMARK_DF['service']==technology & ECOBENCHMARK_DF['use_case']==implementation_details]

    cpu_needed=SourceValue(tech_row['avg_cpu_core_per_request']*u.core/u.uj,ecobenchmark_source)
    ram_needed=
    job_type=JobTypes.UNDETERMINED
    output_args.update(kwargs)
    return Job(name, **output_args)

#v1
#monjob =  ecobenchmark_job("go-pgx",monservice)


#v2
#monjob =  ecobenchmark_job("go-pgx",JobTypes.DATA_WRITE,monservice)
#monjob =  ecobenchmark_job("go-pgx",JobTypes.DATA_READ,monservice)
#monjob =  ecobenchmark_job("go-pgx",JobTypes.NOTIFICATION,monservice)

def get_ecobenchmark_technologies() -> List[str]:
    #load distinct technologies from dataframe
    return []


JOB_DEFAULT_RAM_NEEDED = 1.15 * 10^9
JOB_DEFAULT_CPU_NEEDED = 0.52
JOB_DEFAULT_DURATION= 0.40





def default_data_write(name="Default Data Write", **kwargs):
    output_args = {
        "data_upload": 8000,
        "data_download": 2000,
        "request_duration": JOB_DEFAULT_DURATION,
        "cpu_needed": JOB_DEFAULT_CPU_NEEDED, 
        "ram_needed": JOB_DEFAULT_RAM_NEEDED,
        "job_type": JobTypes.DATA_WRITE
    }

    output_args.update(kwargs)

    return Job(name, **output_args)

def default_data_read(name="Default Data Read", **kwargs):
    output_args = {
        "data_upload": 1000,
        "data_download": 4000,
        "request_duration": JOB_DEFAULT_DURATION,
        "cpu_needed": JOB_DEFAULT_CPU_NEEDED, 
        "ram_needed": JOB_DEFAULT_RAM_NEEDED,
        "job_type": JobTypes.DATA_READ
    }

    output_args.update(kwargs)

    return Job(name, **output_args)

def default_data_list(name="Default Data List", **kwargs):
    output_args = {
        "data_upload": 1000,
        "data_download": 15000,
        "request_duration": JOB_DEFAULT_DURATION,
        "cpu_needed": JOB_DEFAULT_CPU_NEEDED, 
        "ram_needed": JOB_DEFAULT_RAM_NEEDED,
        "job_type": JobTypes.DATA_LIST
    }

    output_args.update(kwargs)

    return Job(name, **output_args)

def default_data_simple_analytic(name="Default Data Simple Analytic", **kwargs):
    output_args = {
        "data_upload": 1000,
        "data_download": 5000,
        "request_duration": JOB_DEFAULT_DURATION,
        "cpu_needed": JOB_DEFAULT_CPU_NEEDED, 
        "ram_needed": JOB_DEFAULT_RAM_NEEDED,
        "job_type": JobTypes.DATA_SIMPLE_ANALYTIC
    }

    output_args.update(kwargs)

    return Job(name, **output_args)