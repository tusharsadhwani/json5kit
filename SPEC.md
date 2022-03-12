# json5-rt CST spec

> Currently a work in progress

- comments:

  ```python
  JSON5Comment(
    source: str,
  )
  ```

  example:

  `// abc def`: `JSON5Comment(source=" abc def")`

- strings and numbers:

  JSON5 has various ways to represent strings and numbers, so to preserve the
  original formatting of them, their literal source is stored alongside the
  actual value.

  ```python
  JSON5Number(
    source: str,
    value: float,
  )
  ```

  ```python
  JSON5String(
    source: str,
    value: str,
  )
  ```

  examples:

  - "hello": `JSON5String(source='"hello"', value="hello")`

  - ```python
    'ab\
    cd'
    ```

    -> `JSON5String(source="'ab\\\ncd'", value="abcd", quotes="'")`

  - `.42`: `JSON5Number(source=".42", value=0.42)`

- values:

  Stores all JSON types, and their leading and trailing whitespace. Also stores
  the comment that occurs just after this value.

  ```python
  JSON5Value(
    value: Union[None, bool, JSON5String, JSON5Number, JSON5Array, JSON5Object],
    whitespace_before: str = '',
    whitespace_after: str = '',
    trailing_comma: bool = True,
    whitespace_after_trailing_comma: str = '',
  )
  ```

- arrays:

  ```python
  JSON5Array(
    items: list[JSON5ArrayMember],
  )
  ```

  ```python
  JSON5ArrayMember(
    value: JSON5Value,
    trailing_comment: Optional[JSON5Comment] = None,
    whitespace_before_comment: Optional[str] = None,
    trailing_whitespace: str = '',
  )
  ```

  examples:

  - `[ null,10.,"foo",[42 ], false]`:

    ```python
    JSON5Array(
      items=[
        JSON5ArrayMember(JSON5Value(None, whitespace_before=" ")),
        JSON5ArrayMember(JSON5Value(JSON5Number(source="10.", value=10.0))),
        JSON5ArrayMember(JSON5Value(JSON5String(source='"foo"', value="foo"))),
        JSON5ArrayMember(JSON5Value(
          JSON5Array(items=JSON5Number(source="42", value=42.0)),
          whitespace_after=" ",
        )),
        JSON5ArrayMember(JSON5Value(False, whitespace_before=" ")),
      ],
    )
    ```

  - ```javascript
    [
      null,  // comment
      12.3,
    ]`
    ```

    ->

    ```python
    JSON5Array(
      items=[
        JSON5ArrayMember(
          JSON5Value(
            value=None,
            whitespace_before="\n  ",
          ),
          trailing_comma=True,
          whitespace_after_trailing_comma="  ",
          trailing_comment=JSON5Comment("// comment"),
        ),
        JSON5ArrayMember(
          JSON5Value(JSON5Number(source="10.", value=10.0)),
          trailing_comma=True,
          whitespace_after_trailing_comma="\n",
        ),
      ],
    )
    ```

- keys:

  Both extend the `JSON5Key` base class.

  ```python
  JSON5IdentifierKey(
    value: str,
    trailing_comment: Optional[JSON5Comment] = None,
  )
  ```

  ```python
  JSON5StringKey(
    value: JSON5String,
    trailing_comment: Optional[JSON5Comment] = None,
  )
  ```

  examples:

  - `myKey`: `JSON5IdentifierKey(value='myKey')`
  - `$_anotherKey123`: `JSON5IdentifierKey(value='$_anotherKey123')`
  - `"key1"`: `JSON5StringKey(value=JSON5String(source='"key1"', value="key1")`

- objects:

  ```python
  JSON5Object(
    items: list[JSON5ObjectMember],
  )
  ```

  ```python
  JSON5ObjectMember(
    key: JSON5Key,
    value: JSON5Value,
    whitespace_before_key: str,
    whitespace_before_colon: str,
    trailing_comment: Optional[JSON5Comment] = None,
    whitespace_before_comment: Optional[str] = None,
  )
  ```

  examples:

  - ```python
    {
      abc: "some \
    text",
      "another key" : 100  // Comment
    }
    ```

    Outputs:

    ```python
    JSON5Object(
      items=[
        JSON5ObjectMember(
          key=JSON5IdentifierKey("abc"),
          value=JSON5Value(
            value=JSON5String(
              source='"some \\\ntext"',
              value="some text",
            ),
            leading_whitespace=" ",
          ),
          trailing_comma=True,
          whitespace_before_key="\n  ",
        ),
        JSON5ObjectMember(
          key=JSON5StringKey(
            JSON5String(
              source='"another string"',
              value="another string",
            ),
          ),
          value=JSON5Value(
            value=JSON5Number(source="42", value=42.0),
            trailing_whitespace=
          )
          trailing_comment=JSON5Comment("// Comment")
          whitespace_after_colon=" ",
          whitespace_before_comment="  ",
        )
      ]
    )
    ```

- Notes:

  - Parsing a usual json5 source currently would return a `JSON5Value` which
    wraps a `JSON5Object`. Maybe I should subclass `JSON5Value` to `JSON5Module`
    just to have a top level object storing leading and trailing whitespace.
    Also, leading comments in file.

  - Leading comments also need to be handled in arrays/objects:

    ```javascript
    [
      // leading comment
      "abc", // trailing comment
      "def", // trailing comment
    ];
    ```

  - TODO: whitespace after a trailing comment on last item, but before `]` / `}`
