import pint
from pint import UnitRegistry

from efootprint.constants.files import CUSTOM_UNITS_PATH

u = UnitRegistry()
u.load_definitions(CUSTOM_UNITS_PATH)
u.default_locale = 'en_EN'
pint.set_application_registry(u)

from pint_pandas import PintType


u = PintType.ureg
