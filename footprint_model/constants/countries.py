from footprint_model.constants.units import u

from dataclasses import dataclass
from pint import Quantity


@dataclass
class Country:
    name: str
    short_name: str
    average_carbon_intensity: Quantity  # g C02 eq /kWh
    year: int

    def __post_init__(self):
        # "[time]**2 / [length]**2" corresponds to mass over energy I.U.
        if not self.average_carbon_intensity.check("[time]**2 / [length]**2"):
            raise ValueError(
                "Variable 'average_carbon_intensity' does not have mass over energy "
                "('[time]**2 / [length]**2') dimensionality"
            )


class Countries:
    # TODO: Add other countries and automate data retrieval
    # source https://ourworldindata.org/energy#country-profiles
    FRANCE = Country("France", "FRA", 85 * u.g / u.kWh, 2022)
    EUROPE = Country("Europe", "EUR", 278 * u.g / u.kWh, 2022)
    GERMANY = Country("Germany", "DEU", 386 * u.g / u.kWh, 2022)
    FINLAND = Country("Finland", "FIN", 132 * u.g / u.kWh, 2022)
    AUSTRIA = Country("Austria", "AUT", 158 * u.g / u.kWh, 2022)
    POLAND = Country("Poland", "POL", 635 * u.g / u.kWh, 2022)
    NORWAY = Country("Norway", "NOR", 26 * u.g / u.kWh, 2021)
    HUNGARY = Country("Hungary", "HUN", 223 * u.g / u.kWh, 2022)
    UNITED_KINGDOM = Country("United Kingdom", "GBR", 268 * u.g / u.kWh, 2021)
    BELGIUM = Country("Belgium", "BEL", 165 * u.g / u.kWh, 2022)
    ITALY = Country("Italy", "IT", 371 * u.g / u.kWh, 2022)
    ROMANIA = Country("Romania", "RO", 264 * u.g / u.kWh, 2022)
    MALAYSIA = Country("Malaysia", "MY", 549 * u.g / u.kWh, 2021)
    MOROCCO = Country("Morocco", "MA", 610 * u.g / u.kWh, 2021)
    TUNISIA = Country("Tunisia", "TN", 468 * u.g / u.kWh, 2021)
    ALGERIA = Country("Algeria", "DZ", 488 * u.g / u.kWh, 2021)
    SENEGAL = Country("Senegal", "SN", 503 * u.g / u.kWh, 2021)
    UNITED_STATES = Country("United States", "US", 379 * u.g / u.kWh, 2021)
    BRAZIL = Country("Brazil", "BR", 159 * u.g / u.kWh, 2021)
