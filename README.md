# json5kit

A Roundtrip parser and CST for JSON, JSONC and JSON5.

[JSON5](https://json5.org) is a superset of JSON, that allows trailing commas,
comments, unquoted and single-quoted object keys, and a lot more.

Currently supports parsing most JSON5 syntax, and converting it back to source.
Also supports single line `// comments`.

## Installation

```bash
pip install json5kit
```

## Usage

```python
>>> source = """
... {
...   items: [1, 2, 4],  // change this to 3
... }
... """
>>> import json5kit
>>> tree = json5kit.parse(source)
>>> print(tree.to_source())

{
  items: [1, 2, 4],  // change this to 3
}

>>> print(tree.to_json())
{"items":[1,2,4]}

>>> # Let's replace the `4` with `3` now:
>>> class ReplaceFourWithThree(json5kit.Json5Transformer):
...     def visit_Number(self, node):
...         if node.value == 4:
...             return node.replace(value=3)
...         return node
...
>>> ReplaceFourWithThree().visit(tree)
>>> print(tree.to_source())

{
  items: [1, 2, 3],  // change this to 3
}
>>> print(tree.to_json())
{"items":[1,2,3]}
```

## Development / Testing

- Clone the project:

  ```bash
  git clone https://github.com/tusharsadhwani/json5kit
  cd json5kit
  ```

- Setup a virtual environment:

  ```bash
  virtualenv venv
  . venv/bin/activate
  ```

- Do an editable install of the project, that way you don't have to keep
  reinstalling:

  ```bash
  pip install -r requirements-dev.txt
  ```

- Run tests:

  ```bash
  pytest
  ```

- Run type checking:

  ```bash
  mypy .
  ```
