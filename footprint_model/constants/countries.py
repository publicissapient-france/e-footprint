from footprint_model.constants.units import u
from footprint_model.constants.sources import SourceValue, Source


class Country:
    def __init__(self, name: str, short_name: str, average_carbon_intensity: SourceValue, year: int):
        self.name = name
        self.short_name = short_name
        self.average_carbon_intensity = average_carbon_intensity
        self.average_carbon_intensity.set_name(f"average carbon intensity of {self.name}")
        self.year = year

    def __post_init__(self):
        # "[time]**2 / [length]**2" corresponds to mass over energy I.U.
        if not self.average_carbon_intensity.check("[time]**2 / [length]**2"):
            raise ValueError(
                "Variable 'average_carbon_intensity' does not have mass over energy "
                "('[time]**2 / [length]**2') dimensionality"
            )


class Countries:
    # TODO: Add other countries and automate data retrieval
    source = Source("Our world in data", "https://ourworldindata.org/energy#country-profiles")
    FRANCE = Country("France", "FRA", SourceValue(85 * u.g / u.kWh, source), 2022)
    EUROPE = Country("Europe", "EUR", SourceValue(278 * u.g / u.kWh, source), 2022)
    GERMANY = Country("Germany", "DEU", SourceValue(386 * u.g / u.kWh, source), 2022)
    FINLAND = Country("Finland", "FIN", SourceValue(132 * u.g / u.kWh, source), 2022)
    AUSTRIA = Country("Austria", "AUT", SourceValue(158 * u.g / u.kWh, source), 2022)
    POLAND = Country("Poland", "POL", SourceValue(635 * u.g / u.kWh, source), 2022)
    NORWAY = Country("Norway", "NOR", SourceValue(26 * u.g / u.kWh, source), 2021)
    HUNGARY = Country("Hungary", "HUN", SourceValue(223 * u.g / u.kWh, source), 2022)
    UNITED_KINGDOM = Country("United Kingdom", "GBR", SourceValue(268 * u.g / u.kWh, source), 2021)
    BELGIUM = Country("Belgium", "BEL", SourceValue(165 * u.g / u.kWh, source), 2022)
    ITALY = Country("Italy", "IT", SourceValue(371 * u.g / u.kWh, source), 2022)
    ROMANIA = Country("Romania", "RO", SourceValue(264 * u.g / u.kWh, source), 2022)
    MALAYSIA = Country("Malaysia", "MY", SourceValue(549 * u.g / u.kWh, source), 2021)
    MOROCCO = Country("Morocco", "MA", SourceValue(610 * u.g / u.kWh, source), 2021)
    TUNISIA = Country("Tunisia", "TN", SourceValue(468 * u.g / u.kWh, source), 2021)
    ALGERIA = Country("Algeria", "DZ", SourceValue(488 * u.g / u.kWh, source), 2021)
    SENEGAL = Country("Senegal", "SN", SourceValue(503 * u.g / u.kWh, source), 2021)
    UNITED_STATES = Country("United States", "US", SourceValue(379 * u.g / u.kWh, source), 2021)
    BRAZIL = Country("Brazil", "BR", SourceValue(159 * u.g / u.kWh, source), 2021)
