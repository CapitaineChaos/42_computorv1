# Lint

Ruff is configured in `pyproject.toml`: `line-length = 100` (flake8 allows 79 by
default, ruff 88) and `select = ["E", "F", "W", "I", "B"]`, the rules checked.

### Reading a rule code

A code is a letter, the tool that first defined the rule, then a number. The first digit
is a category, the others number the rule inside it: `E501` is pycodestyle (`E`), line
length (`5`), rule `01`. `select` enables every code starting with what it lists: `"E"`
enables all `E` rules, `"E4"` only `E401`, `E402`...

To read the full description of a rule: `/dev/shm/computorv1/.venv/bin/ruff rule E501`.

### `E` and `W`: pycodestyle, PEP 8 style

`E` is an error, `W` a warning. Same categories for both.

| Prefix | Category    | Rules active here                                                   |
|--------|-------------|---------------------------------------------------------------------|
| `E1`   | indentation | `E101` tabs and spaces mixed                                        |
| `E2`   | whitespace  | none, see [preview](#default-and-preview-rules)                     |
| `E3`   | blank lines | none, see [preview](#default-and-preview-rules)                     |
| `E4`   | imports     | `E401` `import os, sys`, `E402` import below other code             |
| `E5`   | line length | `E501` line over 100 characters                                     |
| `E7`   | statements  | `E701` `if x: y` on one line, `E702` `a; b`, `E703` final `;`,      |
|        |             | `E711` `== None`, `E712` `== True`, `E713` `not x in y`,            |
|        |             | `E714` `not x is y`, `E721` `type(x) == int`, `E722` bare `except:`,|
|        |             | `E731` `f = lambda: ...`, `E741`-`E743` names `l`, `O`, `I`         |
| `E9`   | runtime     | `E902` file cannot be read                                          |
| `W1`   | indentation | `W191` tab used to indent                                           |
| `W2`   | whitespace  | `W291` spaces at end of line, `W293` spaces on a blank line,        |
|        |             | `W292` no newline at end of file                                    |
| `W5`   | line length | `W505` docstring line too long, inactive: needs `max-doc-length`    |
| `W6`   | deprecation | `W605` invalid escape such as `"\d"`, write `r"\d"`                 |

### `F`: Pyflakes, code that is wrong whatever its style

| Prefix | Category                      | Examples                                        |
|--------|-------------------------------|-------------------------------------------------|
| `F4`   | imports                       | `F401` unused import, `F403` `from x import *`  |
| `F5`   | `%` and `.format()` strings   | `F507` `"%s %s" % (a,)`: wrong argument count   |
| `F6`   | comparisons, dicts            | `F601` key twice in a dict, `F632` `x is "a"`   |
| `F7`   | statement in the wrong place  | `F701` `break` outside a loop, `F706` `return`  |
|        |                               | outside a function                              |
| `F8`   | names                         | `F821` undefined name, `F841` unused variable,  |
|        |                               | `F811` redefined before use                     |
| `F9`   | raise                         | `F901` `raise NotImplemented` instead of        |
|        |                               | `NotImplementedError`                           |

### `I`: isort, import order

`I001`: imports not sorted, or not grouped as standard library, third party, then local.
`I002` (inactive, needs `required-imports`): an import every file must have.

### `B`: flake8-bugbear, likely bugs

Here the digits do not group by category. `B0xx` are the plugin's original rules, `B9xx`
the ones it calls opinionated. Examples: `B006` `def f(x=[])`, the list is shared by
every call; `B007` loop variable never used; `B904` `raise` inside `except` without
`from`, which hides the original exception; `B905` `zip()` without `strict=`, which
silently drops the end of the longer list.

### Default and preview rules

Without `select`, ruff checks only `E4`, `E7`, `E9` and `F`: the rules that do not
overlap with its formatter. Line length, blank lines and whitespace are left to
`ruff format` (`make format`), which rewrites them as black would.

In ruff, `E2`, `E3` and all of `E1` except `E101` are
"preview" rules: still under test, off unless `preview = true` is added under
`[tool.ruff.lint]`. So `make lint` does not report a missing space around `=`;
`make format` fixes it instead.
