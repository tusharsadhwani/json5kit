"""json5-rt - A roundtrip parser for JSON5."""
from __future__ import annotations

import string
from typing import Literal, Sequence, cast

from json5_rt.nodes import (
    Json5Array,
    Json5ArrayMember,
    Json5Boolean,
    Json5Data,
    Json5Null,
    Json5Number,
    Json5String,
    Json5Value,
)


class Json5ParseError(Exception):
    """Raised when the JSON5 string has bad syntax."""

    def __init__(self, message: str, index: int) -> None:
        super().__init__(message)
        self.index = index


class Json5Parser:
    """Parser that converts a JSON5 string into a CST."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.current = 0

    @property
    def scanned(self) -> int:
        """Returns True if the source has been fully scanned."""
        return self.current >= len(self.source)

    def advance(self) -> None:
        """Advance the current pointer."""
        if self.scanned:
            return

        self.current += 1

    def previous(self) -> str:
        """Returns the previously read character."""
        return self.source[self.current - 1]

    def peek(self) -> str:
        """Returns the current character, without actually consuming it."""
        if self.scanned:
            return ""

        return self.source[self.current]

    def peek_next(self) -> str:
        """Returns the character one ahead of the current character."""
        if self.current + 1 >= len(self.source):
            return ""

        return self.source[self.current + 1]

    def read_char(self) -> str:
        """
        Reads one character from the source.
        If the source has been exhausted, returns an empty string.
        """
        char = self.peek()
        self.advance()

        return char

    def match_next(self, chars: Sequence[str]) -> bool:
        """
        Returns True and reads one character from source, but only if it
        matches any of the given characters. Returns False otherwise.
        """
        if self.scanned:
            return False

        if self.source[self.current] in chars:
            self.advance()
            return True

        return False

    def consume(self, char: str) -> None:
        """
        Consumes the expected character type from source. If the character
        doesn't match current, raises a parse error.
        """
        if self.scanned:
            raise Json5ParseError(
                f"Expected to find '{char}', found EOF",
                index=self.current,
            )

        current_char = self.read_char()
        if current_char != char:
            raise Json5ParseError(
                f"Expected to find '{char}', found '{current_char}'",
                index=self.current,
            )

    def parse(self) -> Json5Value:
        """Scans the source to produce a JSON5 CST."""
        value = self.parse_value()

        # Ensure no more data exists
        if not self.scanned:
            token = self.read_char()
            raise Json5ParseError(f"Unexpected {token}", self.current)

        return value

    def parse_value(self) -> Json5Value:
        """Parse a JSON5 value with whitespace information."""
        start_index = self.current

        # Step 1: Read left whitespace
        while not self.scanned and self.peek() in string.whitespace:
            self.advance()

        whitespace_left = self.current

        # Step 2: Parse the actual data
        json_data = self.parse_data()

        # Step 3: Read right whitespace
        whitespace_right = self.current
        while not self.scanned and self.peek() in string.whitespace:
            self.advance()

        # Step 4: Make the value
        whitespace_before = self.source[start_index:whitespace_left]
        whitespace_after = self.source[whitespace_right : self.current]
        value = Json5Value(json_data, whitespace_before, whitespace_after)

        return value

    def parse_data(self) -> Json5Data:
        if self.scanned:
            raise Json5ParseError(
                "Expected to find JSON5 data, found EOF",
                index=self.current,
            )

        if self.source[self.current : self.current + 4] == "null":
            self.current += 4
            return Json5Null()

        if self.source[self.current : self.current + 4] == "true":
            self.current += 4
            return Json5Boolean(True)

        if self.source[self.current : self.current + 5] == "false":
            self.current += 5
            return Json5Boolean(False)

        if self.match_next(('"', "'")):
            # TODO: can remove once mypy has better type narrowing
            # ref: https://github.com/python/mypy/issues/12535
            quote_char = cast(Literal['"', "'"], self.previous())
            return self.parse_string(quote_char)

        # TODO: leading decimal?
        if self.peek() in string.digits:
            return self.parse_number()

        if self.match_next("["):
            return self.parse_array()

        raise NotImplementedError(self.source[self.current])

    def parse_comment(self) -> None:
        """Reads and discards a comment. A comment goes on till a newline."""
        while not self.scanned and self.peek() != "\n":
            self.advance()

    # def parse_identifier(self) -> Json5Key:
    #     """Scans keywords and variable names."""
    #     # TODO: not full ECMA syntax
    #     while not self.scanned and (self.peek().isalnum() or self.peek() == "_"):
    #         self.advance()

    def parse_string(self, quote_char: Literal["'", '"']) -> Json5String:
        # TODO: this is probably not all escapes
        start_index = self.current
        unescaped_chars = []
        while not self.scanned and self.peek() != quote_char:
            char = self.read_char()

            if char != "\\":
                unescaped_chars.append(char)
                continue

            # Escaping the next character
            next_char = self.peek()
            if next_char == "":
                raise Json5ParseError("Unterminated string", index=start_index)

            if next_char == "\n":
                pass  # trailing backslash means ignore the newline
            elif next_char == "\\":
                unescaped_chars.append("\\")
            elif next_char == "n":
                unescaped_chars.append("\n")
            elif next_char == "t":
                unescaped_chars.append("\t")
            elif next_char == "'":
                unescaped_chars.append("'")
            elif next_char == '"':
                unescaped_chars.append('"')
            else:
                escape = char + next_char
                raise Json5ParseError(
                    f"Unknown escape sequence: '{escape}'",
                    index=self.current,
                )

            self.advance()

        # Ensure end quote
        self.consume(quote_char)

        value = "".join(unescaped_chars)
        content = quote_char + self.source[start_index : self.current]
        return Json5String(content, value, quote_char)

    def parse_number(self) -> Json5Number:
        # TODO: exponent syntax support
        start_index = self.current

        while self.peek().isdigit():
            self.advance()

        # decimal support
        if self.peek() == ".":
            if self.peek_next().isdigit():
                self.advance()
                while self.peek().isdigit():
                    self.advance()

        content = self.source[start_index : self.current]
        return Json5Number(content, value=float(content))

    def parse_array(self) -> Json5Array:
        items: list[Json5ArrayMember] = []
        while not self.scanned and not self.match_next("]"):
            value = self.parse_value()

            # Trailing comma not necessary for last element
            if self.peek() == "]":
                comma = False
                break

            self.consume(",")
            comma = True

            items.append(Json5ArrayMember(value, comma))

        trailing_whitespace_start = self.current
        while not self.scanned and self.peek() in string.whitespace:
            self.advance()

        trailing_whitespace = self.source[trailing_whitespace_start : self.current]
        return Json5Array(items, trailing_whitespace)


def parse(source: str) -> Json5Value:
    return Json5Parser(source).parse()
