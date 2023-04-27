from footprint_model.constants.units import u

from dataclasses import dataclass
from typing import Optional
from pint import Quantity


@dataclass
class Source:
    name: str
    link: Optional[str]


class Sources:
    USER_INPUT = Source("User input", None)
    ADEME_STUDY = Source(
        name="Étude ADEME",
        link="https://docs.google.com/spreadsheets/d/1s-B4WLXAxSE8ddoY9929SX2tPdCZ4OEl/edit#gid=155161832",
    )
    BASE_ADEME_V19 = Source("Base ADEME_V19", "https://data.ademe.fr/datasets/base-carbone(r)")
    REN_SHIFT = Source(
        "REN Shift",
        "https://docs.google.com/spreadsheets/d/1PcVRvt58N3sJM3NBI1WXwyHScy4kUT3Q/edit#gid=986618177",
    )
    ONE_BYTE_MODEL_SHIFT_2018 = Source(
        "One byte model shift 2018",
        "https://docs.google.com/spreadsheets/d/1s-B4WLXAxSE8ddoY9929SX2tPdCZ4OEl/edit#gid=155161832",
    )
    TRAFICOM_STUDY = Source(
        "Traficom study", "https://www.traficom.fi/en/news/first-study-energy-consumption-communications-networks"
    )
    HYPOTHESIS = Source("hypothesis", None)
    ECHOS_DU_NET = Source(
        "echosdunet",
        "https://www.echosdunet.net/dossiers/facture-denergie-peut-on-reduire-consommation-electrique-sa-box-internet",
    )
    STORAGE_EMBODIED_CARBON_STUDY = Source(
        "Dirty secret of SSDs: embodied carbon", "https://arxiv.org/pdf/2207.10793.pdf")
    ARCEP_2022_MOBILE_NETWORK_STUDY = Source(
        "ARCEP - Les SERVICES de communications électroniques en France – 3eme TRIMESTRE 2022",
        "https://www.arcep.fr/fileadmin/reprise/observatoire/3-2022/obs-marches-T3-2022_janv2023.pdf")
    STATE_OF_MOBILE_2022 = Source("DATA.AI - STATE OF MOBILE", "https://www.data.ai/en/go/state-of-mobile-2022")


@dataclass
class SourceValue:
    value: Quantity
    source: Source

    def __post_init__(self):
        if not isinstance(self.value, Quantity):
            raise ValueError(
                "Variable 'value' does not correspond to the appropriate 'Quantity' type, "
                "it is indeed mandatory to define a unit"
            )

    @staticmethod
    def _type_conversion_for_operation(operation_value):
        if isinstance(operation_value, SourceValue):
            return operation_value.value
        else:
            return operation_value

    def __add__(self, other):
        return self.value + self._type_conversion_for_operation(other)

    def __truediv__(self, other):
        return self.value / self._type_conversion_for_operation(other)

    def __mul__(self, other):
        return self.value * self._type_conversion_for_operation(other)

    def __rmul__(self, other):
        return self.value * self._type_conversion_for_operation(other)


if __name__ == "__main__":
    test_source = SourceValue(
        value=78 * u.kg,
        source=Sources.ADEME_STUDY,
    )
    print(test_source)
