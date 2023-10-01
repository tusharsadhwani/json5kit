from __future__ import annotations
from textwrap import dedent

import pytest

import json5kit


@pytest.mark.parametrize(
    ("source",),
    (
        ('"abc"',),
        ("'abc123'",),
        ('"abc" ',),
        (" 'abc'  ",),
        (" 42  ",),
        ("+32",),
        ("-32",),
        ("234.9  ",),
        ("[1, 2, 'abc',]",),
        ("\n[true,]\t\n",),
        (
            """
            [
                8.50,
                null,    // why is this here?
                1.34,
            ]
            """,
        ),
        (
            """
               // comment
               // comment
            [  // comment
               // comment
               "a"  // comment
                    // comment
                ,   // comment
                // comment
            ] // comment
              // comment
            """,
        ),
        ('{  "a" : 1, "b":  true }  ',),
        (
            """
            {  "a" : 
                        1,
                    "b":  [  // comment
                    // comment
               123  // comment
                    // comment
                ,   // comment
                456  ,
                // comment
            ] // comment
            }
            """,
        ),
    ),
)
def test_json5_roundtrip(source: str) -> None:
    """Tests if a JSON5 snippet can be parsed and roundtripped."""
    assert json5kit.parse(source).to_source() == source


def test_json5_visitor_transformer() -> None:
    source = dedent(
        """
        {
          "items": [1, 2, 4],  // change this to 3
        }
        """
    )
    json = '{"items":[1,2,4]}'
    expected_source = dedent(
        """
        {
          "items": [1, 2, 3],  // change this to 3
        }
        """
    )
    expected_json = '{"items":[1,2,3]}'
    tree = json5kit.parse(source)

    class CollectNumbers(json5kit.Json5Visitor):
        def __init__(self) -> None:
            self.numbers: list[float] = []

        def visit_Number(self, node: json5kit.Json5Number) -> None:
            self.numbers.append(node.value)

    visitor = CollectNumbers()
    visitor.visit(tree)
    assert visitor.numbers == [1, 2, 4]
    # Ensure original tree isn't changed
    assert tree.to_source() == source
    assert tree.to_json() == json

    class ReplaceFourWithThree(json5kit.Json5Transformer):
        def visit_Number(self, node: json5kit.Json5Number) -> json5kit.Json5Number:
            if node.value == 4:
                return node.replace(value=3)

            return node

    modified_tree = ReplaceFourWithThree().visit(tree)

    assert modified_tree.to_source() == expected_source
    assert modified_tree.to_json() == expected_json
    # The original tree changes as well.
    assert tree.to_source() == expected_source
    assert tree.to_json() == expected_json


@pytest.mark.parametrize(
    ("source", "json"),
    (
        (
            """
            {
                foo: "bar", // test
                barBaz_buzz1: // another comment
                    [
                        "stuff",
                        'other stuff',
                    ],
                'more keys': null, // heh
            }
            """,
            '{"foo":"bar","barBaz_buzz1":["stuff","other stuff"],"more keys":null}',
        ),
    ),
)
def test_json5_to_json(source: str, json: str) -> None:
    """Tests to ensure JSON5 features are parsed and converted to JSON properly."""
    assert json5kit.parse(source).to_source() == source
    assert json5kit.parse(source).to_json() == json
