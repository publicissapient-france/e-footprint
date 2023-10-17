from footprint_model.constants.units import u

from dataclasses import dataclass
from pint import Quantity


@dataclass
class Country:
    name: str
    short_name: str
    average_carbon_intensity: Quantity  # g C02 eq /kWh

    def __post_init__(self):
        # "[time]**2 / [length]**2" corresponds to mass over energy I.U.
        if not self.average_carbon_intensity.check("[time]**2 / [length]**2"):
            raise ValueError(
                "Variable 'average_carbon_intensity' does not have mass over energy "
                "('[time]**2 / [length]**2') dimensionality"
            )


class Countries:
    FRANCE = Country("France", "FR", 100 * u.g / u.kWh)
    EUROPE = Country("Europe", "EU", 250 * u.g / u.kWh)
