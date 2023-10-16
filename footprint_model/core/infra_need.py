from footprint_model.constants.explainable_quantities import ExplainableQuantity

from typing import List
from dataclasses import dataclass


@dataclass
class InfraNeed:
    ram: List[ExplainableQuantity]
    storage: ExplainableQuantity
    cpu: List[ExplainableQuantity]

    def __post_init__(self):
        # Todo: Simplify unit checking by creating a custom dataclass
        for ram_value in self.ram:
            if not ram_value.value.check("[data]"):
                raise ValueError("Variable 'ram' does not have octet dimensionality")
        if not self.storage.value.check("[data] / [time]"):
            raise ValueError("Variable 'storage' does not have octet over time dimensionality")
        for cpu_value in self.cpu:
            if not cpu_value.value.check("[cpu]"):
                raise ValueError("Variable 'cpu' does not have core dimensionality")

    def __add__(self, other):
        if not isinstance(other, InfraNeed):
            raise ValueError(f"Can only add InfraNeed objects with other InfraNeed objects, not with {type(other)}")
        else:
            return InfraNeed(
                ram=[self_ram + ram_other for self_ram, ram_other in zip(self.ram, other.ram)],
                storage=self.storage + other.storage,
                cpu=[self_cpu + cpu_other for self_cpu, cpu_other in zip(self.cpu, other.cpu)])

