from __future__ import annotations

from typing import Protocol


class Json5Node(Protocol):
    """Sets the expectation from a JSON5 node: be able to convert back to source."""

    trailing_trivia_nodes: list[Json5Trivia]

    def to_json5(self) -> str:
        ...

    def to_json(self) -> str:
        ...


class Json5Primitive:
    """Base class for primitive JSON types such as booleans, null, integers etc."""

    def __init__(
        self,
        source: str,
        value: object,
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        self.source = source
        self.value = value
        self.trailing_trivia_nodes = trailing_trivia_nodes

    def to_json5(self) -> str:
        return self.source + "".join(
            trivia.source for trivia in self.trailing_trivia_nodes
        )

    def to_json(self) -> str:
        return self.source


class Json5Null(Json5Primitive):
    def __init__(self, trailing_trivia_nodes: list[Json5Trivia]) -> None:
        super().__init__(
            source="null",
            value=None,
            trailing_trivia_nodes=trailing_trivia_nodes,
        )


class Json5Boolean(Json5Primitive):
    def __init__(
        self,
        source: str,
        value: bool,
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        super().__init__(source, value, trailing_trivia_nodes)


class Json5Number(Json5Primitive):
    def __init__(
        self,
        source: str,
        value: float,
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        super().__init__(source, value, trailing_trivia_nodes)


class Json5String(Json5Primitive):
    def __init__(
        self,
        source: str,
        value: str,
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        super().__init__(source, value, trailing_trivia_nodes)


class Json5Container:
    """
    Base class for "container nodes", i.e. nodes that contain other nodes.

    This distinction is required because container nodes can have leading trivia
    nodes, while primitive nodes like ints and booleans cannot.

    Examples of container nodes include files, arrays and objects.
    """

    def __init__(
        self,
        leading_trivia_nodes: list[Json5Trivia],
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        self.leading_trivia_nodes = leading_trivia_nodes
        self.trailing_trivia_nodes = trailing_trivia_nodes

    def to_json5(self) -> str:
        """Converts the node back to its original source."""
        raise NotImplementedError

    def to_json(self) -> str:
        raise NotImplementedError


class Json5File(Json5Container):
    def __init__(
        self,
        value: Json5Node,
        leading_trivia_nodes: list[Json5Trivia],
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        super().__init__(leading_trivia_nodes, trailing_trivia_nodes)
        self.value = value

    def to_json5(self) -> str:
        """Converts the node back to its original source."""
        return (
            "".join(trivia.source for trivia in self.leading_trivia_nodes)
            + self.value.to_json5()
            + "".join(trivia.source for trivia in self.trailing_trivia_nodes)
        )

    def to_json(self) -> str:
        """Converts the node to JSON, without whitespace."""
        return self.value.to_json()


class Json5Array(Json5Container):
    def __init__(
        self,
        members: list[Json5Node],
        leading_trivia_nodes: list[Json5Trivia],
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        super().__init__(leading_trivia_nodes, trailing_trivia_nodes)
        self.members = members

    def to_json5(self) -> str:
        """Converts the node back to its original source."""
        return (
            "["
            + "".join(trivia.source for trivia in self.leading_trivia_nodes)
            + "".join(member.to_json5() for member in self.members)
            + "]"
            + "".join(trivia.source for trivia in self.trailing_trivia_nodes)
        )

    def to_json(self) -> str:
        """Converts the node to JSON, without whitespace."""
        return "[" + ",".join(member.to_json() for member in self.members) + "]"


class Json5Object(Json5Container):
    def __init__(
        self,
        data: dict[Json5Primitive, Json5Primitive],
        leading_trivia_nodes: list[Json5Trivia],
        trailing_trivia_nodes: list[Json5Trivia],
    ) -> None:
        super().__init__(leading_trivia_nodes, trailing_trivia_nodes)
        self.data = data

    def to_json5(self) -> str:
        """Converts the node back to its original source."""
        return (
            "{"
            + "".join(trivia.source for trivia in self.leading_trivia_nodes)
            + "".join(
                f"{key.to_json5()}:{value.to_json5()}"
                for key, value in self.data.items()
            )
            + "".join(trivia.source for trivia in self.trailing_trivia_nodes)
            + "}"
        )

    def to_json(self) -> str:
        """Converts the node to JSON, without whitespace."""
        return (
            "{"
            + ",".join(
                f"{key.to_json()}:{value.to_json()}" for key, value in self.data.items()
            )
            + "}"
        )


class Json5Trivia:
    """Base class for "trivial" information like whitespace, newlines and comments."""

    def __init__(self, source: str) -> None:
        self.source = source


class Json5Comment(Json5Trivia):
    """JSON5 single line comments, eg. `// foo`."""


class Json5Whitespace(Json5Trivia):
    """Any run of continuous whitespace characters in a JSON5 file."""


class Json5Newline(Json5Trivia):
    """Newline character in a JSON5 file."""

    def __init__(self) -> None:
        super().__init__(source="\n")


class Json5Comma(Json5Trivia):
    """Comma character in a JSON5 file"""

    def __init__(self) -> None:
        super().__init__(source=",")