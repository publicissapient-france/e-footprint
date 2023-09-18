from footprint_model.constants.units import u
from footprint_model.constants.sources import SourceValue, Source


class Country:
    def __init__(self, name: str, short_name: str, average_carbon_intensity: SourceValue, year: int, timezone: str):
        self.name = name
        self.short_name = short_name
        # "[time]**2 / [length]**2" corresponds to mass over energy I.U.
        if not average_carbon_intensity.value.check("[time]**2 / [length]**2"):
            raise ValueError(
                "Variable 'average_carbon_intensity' does not have mass over energy "
                "('[time]**2 / [length]**2') dimensionality"
            )
        self.average_carbon_intensity = average_carbon_intensity
        self.average_carbon_intensity.set_name(f"Average carbon intensity of {self.name}")
        self.year = year
        self.timezone = timezone


class Countries:
    # TODO: Add other countries and automate data retrieval
    source = Source("Our world in data", "https://ourworldindata.org/energy#country-profiles")
    FRANCE = Country("France", "FRA", SourceValue(85 * u.g / u.kWh, source), 2022, 'Europe/Paris')
    # EUROPE = Country("Europe", "EUR", SourceValue(278 * u.g / u.kWh, source), 2022, None)
    GERMANY = Country("Germany", "DEU", SourceValue(386 * u.g / u.kWh, source), 2022, 'Europe/Berlin')
    FINLAND = Country("Finland", "FIN", SourceValue(132 * u.g / u.kWh, source), 2022, 'Europe/Helsinki')
    AUSTRIA = Country("Austria", "AUT", SourceValue(158 * u.g / u.kWh, source), 2022, 'Europe/Vienna')
    POLAND = Country("Poland", "POL", SourceValue(635 * u.g / u.kWh, source), 2022, 'Europe/Warsaw')
    NORWAY = Country("Norway", "NOR", SourceValue(26 * u.g / u.kWh, source), 2021, 'Europe/Oslo')
    HUNGARY = Country("Hungary", "HUN", SourceValue(223 * u.g / u.kWh, source), 2022, 'Europe/Budapest')
    UNITED_KINGDOM = Country("United Kingdom", "GBR", SourceValue(268 * u.g / u.kWh, source), 2021, 'Europe/London')
    BELGIUM = Country("Belgium", "BEL", SourceValue(165 * u.g / u.kWh, source), 2022, 'Europe/Brussels')
    ITALY = Country("Italy", "IT", SourceValue(371 * u.g / u.kWh, source), 2022, 'Europe/Rome')
    ROMANIA = Country("Romania", "RO", SourceValue(264 * u.g / u.kWh, source), 2022, 'Europe/Bucharest')
    MALAYSIA = Country("Malaysia", "MY", SourceValue(549 * u.g / u.kWh, source), 2021, 'Asia/Kuala_Lumpur')
    MOROCCO = Country("Morocco", "MA", SourceValue(610 * u.g / u.kWh, source), 2021, 'Africa/Casablanca')
    TUNISIA = Country("Tunisia", "TN", SourceValue(468 * u.g / u.kWh, source), 2021, 'Africa/Tunis')
    ALGERIA = Country("Algeria", "DZ", SourceValue(488 * u.g / u.kWh, source), 2021, 'Africa/Algiers')
    SENEGAL = Country("Senegal", "SN", SourceValue(503 * u.g / u.kWh, source), 2021, 'Africa/Dakar')
    # UNITED_STATES = Country("United States", "US", SourceValue(379 * u.g / u.kWh, source), 2021, None)
    # BRAZIL = Country("Brazil", "BR", SourceValue(159 * u.g / u.kWh, source), 2021, None)
