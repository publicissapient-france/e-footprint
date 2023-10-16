import os

PROJECT_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
FOOTPRINT_MODEL_PATH = os.path.join(PROJECT_ROOT_PATH, "footprint_model")
CUSTOM_UNITS_PATH = os.path.join(FOOTPRINT_MODEL_PATH, "constants", "custom_units.txt")
PDF_EXPORTS = os.path.join(PROJECT_ROOT_PATH, "use_cases", "pdf_exports")