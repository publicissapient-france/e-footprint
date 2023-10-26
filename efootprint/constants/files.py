import os


def create_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


PROJECT_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
FOOTPRINT_MODEL_PATH = os.path.join(PROJECT_ROOT_PATH, "efootprint")
CUSTOM_UNITS_PATH = os.path.join(FOOTPRINT_MODEL_PATH, "constants", "custom_units.txt")
PDF_EXPORTS = os.path.join(PROJECT_ROOT_PATH, "use_cases", "pdf_exports")
DATA_PATH = create_folder(os.path.join(PROJECT_ROOT_PATH, "data"))
README_IMAGES_PATH = create_folder(os.path.join(PROJECT_ROOT_PATH, "images"))
