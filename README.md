# json5kit

A Roundtrip parser and CST for JSON, JSONC and JSON5.

> Currently a work in progress

Currently supports parsing all of JSON syntax, and converting it back to source.
Also supports single line `// comments`.

## Installation

```bash
pip install json5kit
```

## Usage

> This is not the intended way to use the library. The correct way to modify a
> tree would be to use visitors, which will be added soon.

```python
>>> source = """
... {
...   "items": [1, 2, 4],  // change this to 3
... }
... """
>>> import json5kit
>>> tree = json5kit.parse(source)
>>> print(tree.to_source())

{
  "items": [1, 2, 4],  // change this to 3
}

>>> tree.value.data[0][1].members[2] = json5kit.Json5Number('3', 3, [])
>>> print(tree.to_source())

{
  "items": [1, 2, 3],  // change this to 3
}
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
