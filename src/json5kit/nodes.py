from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol


class Json5Data(Protocol):
    @property
    def source(self) -> str:
        ...


@dataclass
class Json5Comment:
    comment: str
    whitespace_before_comment: str

    @property
    def value(self) -> str:
        return self.whitespace_before_comment + self.comment


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
    whitespace_after_comma: str
    trailing_comments: list[Json5Comment] = field(default_factory=list)

    @property
    def source(self) -> str:
        value = self.value.to_json5()
        if self.comma:
            value += ","

        return (
            value
            + self.whitespace_after_comma
            + "".join("//" + comment.value for comment in self.trailing_comments)
        )


@dataclass
class Json5Array:
    items: list[Json5ArrayMember]
    trailing_whitespace: str = ""
    trailing_comments: list[str] = field(default_factory=list)

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
    trailing_comments: list[Json5Comment] = field(default_factory=list)

    def to_json5(self) -> str:
        return (
            self.whitespace_before
            + self.data.source
            + self.whitespace_after
            + "".join(self.trailing_comments)
        )


# NOTE: so I think associating comments with Json5Value is a fine decision.
# Most of the comments can end up being associated with a value. The few exceptions
# being ones at the beginning of an array/objecy, and comments after the colon in an
# object. But those can be added to Json5Array and Json5Object, it's alright.
#
# Also note that no special distinction is needed for a comment on the same line as a
# Json5value compared to one that's on the next line, as that's done via the
# whitespace_after field having a newline or not having a newline in it.
#
# There's still a lot of places where comments can go, for eg:
#
#    // comment
#    // comment
# [  // comment
#    // comment
#    "a"  // comment
#         // comment
#     ,   // comment
#     // comment
# ] // comment
#   // comment
#
# So it needs more proper speccing.
