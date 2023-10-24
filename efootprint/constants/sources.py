from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.constants.units import u
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity

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
    STATE_OF_MOBILE_2022 = Source("DATA.AI - STATE OF MOBILE", "https://www.data.ai/en/GB/state-of-mobile-2022")


SOURCE_VALUE_DEFAULT_NAME = "unnamed source"


class SourceObject(ExplainableObject):
    def __init__(self, value: object, source: Source = Sources.HYPOTHESIS, name: str = SOURCE_VALUE_DEFAULT_NAME):
        super().__init__(value, label=name)
        self.source = source

    def set_name(self, new_name: str):
        if self.left_child or self.right_child:
            raise ValueError("Source values shouldn’t have any child.")
        elif self.label == SOURCE_VALUE_DEFAULT_NAME:
            if self.source != Sources.USER_INPUT:
                self.label = f"{new_name} from {self.source.name}"
            else:
                self.label = f"{new_name}"
        else:
            raise ValueError(f"Trying to set the new label {new_name} would overwrite {self.label}")


class SourceValue(SourceObject, ExplainableQuantity):
    def __init__(self, value: Quantity, source: Source = Sources.HYPOTHESIS, name: str = SOURCE_VALUE_DEFAULT_NAME):
        super().__init__(value, source, name)


if __name__ == "__main__":
    test_source = SourceValue(
        value=78 * u.kg,
        source=Sources.ADEME_STUDY,
    )
    print(test_source)
