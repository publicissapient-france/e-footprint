import os


def create_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


EFOOTPRINT_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CUSTOM_UNITS_PATH = os.path.join(EFOOTPRINT_ROOT_PATH, "constants", "custom_units.txt")
