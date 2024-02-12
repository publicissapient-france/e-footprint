from efootprint.core.usage.job import Job, JobTypes

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