import logging
import os
from datetime import datetime

from efootprint.constants.files import create_folder, EFOOTPRINT_ROOT_PATH

logger = logging.getLogger('footprint-model')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def write_logs_to_file(input_logger=logger, input_formatter=formatter, log_level=logging.INFO):
    log_path = create_folder(os.path.join(EFOOTPRINT_ROOT_PATH, "logs"))
    today_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_path, today_str + ".log")
    fh = logging.FileHandler(log_file)
    fh.setFormatter(input_formatter)
    fh.setLevel(log_level)
    input_logger.addHandler(fh)


if os.environ.get("WRITE_EFOOTPRINT_LOGS", None) is not None:
    write_logs_to_file(log_level=logging.DEBUG)
