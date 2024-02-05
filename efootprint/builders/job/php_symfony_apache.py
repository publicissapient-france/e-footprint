from efootprint.core.usage.job import Job, JobTypes

#Data Source : https://github.com/Boavizta/ecobenchmark-applicationweb-backend/tree/main/results - data from 2022/06/27 & 28
JOB_DEFAULT_RAM_NEEDED = 6.459156 * 10^8
JOB_DEFAULT_CPU_NEEDED = 1.601595
JOB_DEFAULT_DURATION= 1.096195

TECH_CASE = "Php Symfony Apache"


def php_symfony_apache_data_write(name=TECH_CASE+" Data Write", **kwargs):
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

def php_symfony_apache_data_read(name=TECH_CASE+" Data Read", **kwargs):
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

def php_symfony_apache_data_list(name=TECH_CASE+" Data List", **kwargs):
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

def php_symfony_apache_data_simple_analytic(name=TECH_CASE+" Data Simple Analytic", **kwargs):
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