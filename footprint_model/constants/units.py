from footprint_model.constants.files import PROJECT_ROOT_PATH

import os
from pint import UnitRegistry

u = UnitRegistry()
u.load_definitions(os.path.join(PROJECT_ROOT_PATH, "custom_units.txt"))
