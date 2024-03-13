from efootprint.constants.units import u
from efootprint.constants.sources import Source,Sources
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject

import pytz
from typing import List


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
        self.average_carbon_intensity = average_carbon_intensity.set_label(f"Average carbon intensity of {self.name}")
        self.year = year
        self.timezone = timezone.set_label(f"{self.name} timezone")

    @property
    def device_populations(self):
        return self.modeling_obj_containers

    @property
    def systems(self) -> List:
        return list(set(sum([device_pop.systems for device_pop in self.device_populations], start=[])))

    @property
    def modeling_objects_whose_attributes_depend_directly_on_me(self):
        return self.device_populations


def tz(timezone: str):
    return SourceObject(pytz.timezone(timezone), Sources.USER_DATA)


def country_generator(country_name, country_short_name, country_avg_carbon_int, year, timezone):
    def return_country():
        return Country(country_name, country_short_name, country_avg_carbon_int, year, timezone)

    return return_country


class Countries:
    # TODO: Add other countries and automate data retrieval
    source = Source("Our world in data", "https://ourworldindata.org/energy#country-profiles")
    FRANCE = country_generator("France", "FRA", SourceValue(85 * u.g / u.kWh, source), 2022, tz('Europe/Paris'))
    # EUROPE = country_generator("Europe", "EUR", SourceValue(278 * u.g / u.kWh, source), 2022, None)
    GERMANY = country_generator("Germany", "DEU", SourceValue(386 * u.g / u.kWh, source), 2022, tz('Europe/Berlin'))
    FINLAND = country_generator("Finland", "FIN", SourceValue(132 * u.g / u.kWh, source), 2022, tz('Europe/Helsinki'))
    AUSTRIA = country_generator("Austria", "AUT", SourceValue(158 * u.g / u.kWh, source), 2022, tz('Europe/Vienna'))
    POLAND = country_generator("Poland", "POL", SourceValue(635 * u.g / u.kWh, source), 2022, tz('Europe/Warsaw'))
    NORWAY = country_generator("Norway", "NOR", SourceValue(26 * u.g / u.kWh, source), 2021, tz('Europe/Oslo'))
    HUNGARY = country_generator("Hungary", "HUN", SourceValue(223 * u.g / u.kWh, source), 2022, tz('Europe/Budapest'))
    UNITED_KINGDOM = country_generator("United Kingdom", "GBR", SourceValue(268 * u.g / u.kWh, source), 2021, tz('Europe/London'))
    BELGIUM = country_generator("Belgium", "BEL", SourceValue(165 * u.g / u.kWh, source), 2022, tz('Europe/Brussels'))
    ITALY = country_generator("Italy", "IT", SourceValue(371 * u.g / u.kWh, source), 2022, tz('Europe/Rome'))
    ROMANIA = country_generator("Romania", "RO", SourceValue(264 * u.g / u.kWh, source), 2022, tz('Europe/Bucharest'))
    MALAYSIA = country_generator("Malaysia", "MY", SourceValue(549 * u.g / u.kWh, source), 2021, tz('Asia/Kuala_Lumpur'))
    MOROCCO = country_generator("Morocco", "MA", SourceValue(610 * u.g / u.kWh, source), 2021, tz('Africa/Casablanca'))
    TUNISIA = country_generator("Tunisia", "TN", SourceValue(468 * u.g / u.kWh, source), 2021, tz('Africa/Tunis'))
    ALGERIA = country_generator("Algeria", "DZ", SourceValue(488 * u.g / u.kWh, source), 2021, tz('Africa/Algiers'))
    SENEGAL = country_generator("Senegal", "SN", SourceValue(503 * u.g / u.kWh, source), 2021, tz('Africa/Dakar'))
    # UNITED_STATES = country_generator("United States", "US", SourceValue(379 * u.g / u.kWh, source), 2021, None)
    # BRAZIL = country_generator("Brazil", "BR", SourceValue(159 * u.g / u.kWh, source), 2021, None)
