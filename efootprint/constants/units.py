from efootprint.constants.files import CUSTOM_UNITS_PATH

from pint import UnitRegistry

u = UnitRegistry()
u.load_definitions(CUSTOM_UNITS_PATH)
u.default_locale = 'en_EN'
