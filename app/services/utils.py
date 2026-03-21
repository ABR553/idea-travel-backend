from decimal import Decimal
from typing import Protocol


class HasLocale(Protocol):
    locale: str


def resolve_translation[T: HasLocale](
    translations: list[T], locale: str
) -> T | None:
    for t in translations:
        if t.locale == locale:
            return t
    for t in translations:
        if t.locale == "es":
            return t
    return None


def to_float(value: Decimal | float) -> float:
    return float(value) if isinstance(value, Decimal) else value
