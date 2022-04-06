from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class Json5Data:
    source: str


@dataclass
class Json5Value:
    data: Json5Data
    whitespace_before: str
    whitespace_after: str

    def to_json5(self) -> str:
        return self.whitespace_before + self.data.source + self.whitespace_after


@dataclass
class Json5String(Json5Data):
    value: str
    quotes: Literal['"', "'"]


@dataclass
class Json5Number(Json5Data):
    value: float
