import os

import pandas as pd
import requests

from efootprint.abstract_modeling_classes.source_objects import SourceValue, Sources
from efootprint.constants.units import u
from efootprint.logger import logger

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ECOBENCHMARK_RESULTS_LINK = "https://raw.githubusercontent.com/Boavizta/ecobenchmark-applicationweb-backend/628f86a7e5816a49670b0837fa7507cf2e620531/results/results/20220628-193500.csv"


def download_file_from_url(url, file_path, overwrite=False):
    if not overwrite and os.path.exists(file_path):
        logger.info(f"File {file_path.replace(ROOT_PATH, '')} already exists, we do not overwrite it")
        return
    logger.info(f"Download file at url {url} to {file_path.replace(ROOT_PATH, '')}")
    r = requests.get(url, stream=True)
    with open(file_path, "wb") as f:
        for chunk in r.iter_content(10 ** 5):
            f.write(chunk)


ecobenchmark_raw_file = os.path.join(ROOT_PATH, "ecobenchmark_results__raw.csv")
download_file_from_url(ECOBENCHMARK_RESULTS_LINK, ecobenchmark_raw_file)
df = pd.read_csv(ecobenchmark_raw_file)

nb_of_application_server_cpu_cores_hypothesis = 24 #TODO: to update with OVH server specs
nb_of_database_server_cpu_cores_hypothesis = 8 #TODO: to update with OVH server specs

df["avg_ram_in_MB"] = (df["application_ram_avg"] + df["database_ram_avg"]) / 1e6 #Unit MB (not MiB)
df["avg_cpu_cores"] = (df["application_cpu_avg"] * nb_of_database_server_cpu_cores_hypothesis
                       + df["database_cpu_avg"] * nb_of_database_server_cpu_cores_hypothesis)

ecobenchmark_duration_in_s = 10 * 60  # TODO: To check with Jérémie Drouet
average_request_duration_in_s_hypothesis = 1  # TODO: Get a better number from next eco-benchmark analysis


def default_request_duration():
    return SourceValue(average_request_duration_in_s_hypothesis * u.s, Sources.HYPOTHESIS)


df["nb_requests_in_parallel"] = df["http_reqs"] * average_request_duration_in_s_hypothesis / ecobenchmark_duration_in_s

output_df = df[
    ["service", "use_case", "iterations", "http_reqs", "nb_requests_in_parallel", "avg_ram_in_MB", "avg_cpu_cores"]
].groupby(["service", "use_case"], as_index=False).mean()

output_df["avg_ram_per_request_in_MB"] = output_df["avg_ram_in_MB"] / output_df["nb_requests_in_parallel"]
output_df["avg_cpu_core_per_request"] = output_df["avg_cpu_cores"] / output_df["nb_requests_in_parallel"]

ECOBENCHMARK_DATA = os.path.join(ROOT_PATH, "ecobenchmark_data_for_job_defaults.csv")
output_df.to_csv(ECOBENCHMARK_DATA, index=False)

