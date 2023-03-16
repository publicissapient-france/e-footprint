from footprint_model.constants.units import u

from dataclasses import dataclass
from typing import Optional
from pint import Quantity


@dataclass
class Source:
    name: str
    link: Optional[str]


class Sources:
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


if __name__ == "__main__":
    test_source = SourceValue(
        value=78 * u.kg,
        source=Sources.ADEME_STUDY,
    )
    print(test_source)
