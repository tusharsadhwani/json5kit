from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


class Json5Data(Protocol):
    @property
    def source(self) -> str:
        ...


@dataclass
class Json5Null:
    source = "null"


@dataclass
class Json5Boolean:
    value: bool

    @property
    def source(self) -> str:
        return "true" if self.value else "false"


@dataclass
class Json5String:
    source: str
    value: str
    quotes: Literal['"', "'"]


@dataclass
class Json5Number:
    source: str
    value: float


@dataclass
class Json5ArrayMember:
    value: Json5Value
    comma: bool
    # trailing_comment: Json5Comment | None = None
    # whitespace_before_comment: str | None = None

    @property
    def source(self) -> str:
        value = self.value.to_json5()
        if self.comma:
            value += ","

        return value


@dataclass
class Json5Array:
    items: list[Json5ArrayMember]
    trailing_whitespace: str = ""

    @property
    def source(self) -> str:
        return (
            "["
            + "".join(item.source for item in self.items)
            + "]"
            + self.trailing_whitespace
        )


@dataclass
class Json5Value:
    data: Json5Data
    whitespace_before: str
    whitespace_after: str

    def to_json5(self) -> str:
        return self.whitespace_before + self.data.source + self.whitespace_after
