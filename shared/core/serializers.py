"""Lightweight serializer helpers for non-DRF consumers."""

from dataclasses import dataclass
from typing import Iterable, List

from .models import Number


@dataclass(slots=True)
class NumberDTO:
    area_code: str
    phone_number: str
    cost: int

    @property
    def full_number(self) -> str:
        return f"{self.area_code}{self.phone_number}"

    @classmethod
    def from_model(cls, instance: Number) -> "NumberDTO":
        return cls(area_code=instance.area_code, phone_number=instance.phone_number, cost=instance.cost)


def serialize_numbers(queryset: Iterable[Number]) -> List[dict]:
    return [
        {
            "area_code": obj.area_code,
            "phone_number": obj.phone_number,
            "full_number": obj.full_number,
            "cost": obj.cost,
        }
        for obj in queryset
    ]


__all__ = ["NumberDTO", "serialize_numbers"]
