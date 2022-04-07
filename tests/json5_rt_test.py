from __future__ import annotations

import pytest

import json5_rt


@pytest.mark.parametrize(
    ("source",),
    (
        ('"abc"',),
        ("'abc123'",),
        ('"abc" ',),
        (" 'abc'  ",),
        (" 42  ",),
        ("234.9  ",),
    ),
)
def test_json5_roundtrip(source: str) -> None:
    """Tests if a JSON5 snippet can be parsed and roundtripped."""
    assert json5_rt.parse(source).to_json5() == source
