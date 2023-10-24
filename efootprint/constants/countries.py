from efootprint.constants.units import u
from efootprint.constants.sources import SourceValue, Source, SourceObject, Sources
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject

import pytz


class Country(ModelingObject):
    def __init__(
            self, name: str, short_name: str, average_carbon_intensity: SourceValue, year: int, timezone: SourceObject):
        super().__init__(name)
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
        self.timezone.set_name(f"{self.name} timezone")

    @property
    def device_populations(self):
        return self.modeling_obj_containers

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self):
        return self.device_populations


def tz(timezone: str):
    return SourceObject(pytz.timezone(timezone), Sources.USER_INPUT)


class Countries:
    # TODO: Add other countries and automate data retrieval
    source = Source("Our world in data", "https://ourworldindata.org/energy#country-profiles")
    FRANCE = Country("France", "FRA", SourceValue(85 * u.g / u.kWh, source), 2022, tz('Europe/Paris'))
    # EUROPE = Country("Europe", "EUR", SourceValue(278 * u.g / u.kWh, source), 2022, None)
    GERMANY = Country("Germany", "DEU", SourceValue(386 * u.g / u.kWh, source), 2022, tz('Europe/Berlin'))
    FINLAND = Country("Finland", "FIN", SourceValue(132 * u.g / u.kWh, source), 2022, tz('Europe/Helsinki'))
    AUSTRIA = Country("Austria", "AUT", SourceValue(158 * u.g / u.kWh, source), 2022, tz('Europe/Vienna'))
    POLAND = Country("Poland", "POL", SourceValue(635 * u.g / u.kWh, source), 2022, tz('Europe/Warsaw'))
    NORWAY = Country("Norway", "NOR", SourceValue(26 * u.g / u.kWh, source), 2021, tz('Europe/Oslo'))
    HUNGARY = Country("Hungary", "HUN", SourceValue(223 * u.g / u.kWh, source), 2022, tz('Europe/Budapest'))
    UNITED_KINGDOM = Country("United Kingdom", "GBR", SourceValue(268 * u.g / u.kWh, source), 2021, tz('Europe/London'))
    BELGIUM = Country("Belgium", "BEL", SourceValue(165 * u.g / u.kWh, source), 2022, tz('Europe/Brussels'))
    ITALY = Country("Italy", "IT", SourceValue(371 * u.g / u.kWh, source), 2022, tz('Europe/Rome'))
    ROMANIA = Country("Romania", "RO", SourceValue(264 * u.g / u.kWh, source), 2022, tz('Europe/Bucharest'))
    MALAYSIA = Country("Malaysia", "MY", SourceValue(549 * u.g / u.kWh, source), 2021, tz('Asia/Kuala_Lumpur'))
    MOROCCO = Country("Morocco", "MA", SourceValue(610 * u.g / u.kWh, source), 2021, tz('Africa/Casablanca'))
    TUNISIA = Country("Tunisia", "TN", SourceValue(468 * u.g / u.kWh, source), 2021, tz('Africa/Tunis'))
    ALGERIA = Country("Algeria", "DZ", SourceValue(488 * u.g / u.kWh, source), 2021, tz('Africa/Algiers'))
    SENEGAL = Country("Senegal", "SN", SourceValue(503 * u.g / u.kWh, source), 2021, tz('Africa/Dakar'))
    # UNITED_STATES = Country("United States", "US", SourceValue(379 * u.g / u.kWh, source), 2021, None)
    # BRAZIL = Country("Brazil", "BR", SourceValue(159 * u.g / u.kWh, source), 2021, None)
