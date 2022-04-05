from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class Json5Value:
    source: str


@dataclass
class Json5Object:
    value: Json5Value
    whitespace_before: str
    whitespace_after: str

    def to_json5(self) -> str:
        return self.whitespace_before + self.value.source + self.whitespace_after


@dataclass
class Json5String(Json5Value):
    value: str
    quotes: Literal['"', "'"]


@dataclass
class Json5Number(Json5Value):
    value: float
