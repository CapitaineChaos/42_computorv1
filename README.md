# computorv1

Solves polynomial equations of degree 2 or lower. Python 3.10+, standard library only.

```
$> ./computor "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0
Polynomial degree: 2
  a = -9.3, b = 4, c = 4
  Δ = b² - 4ac = 4² - 4 * (-9.3) * 4 = 164.8
  vertex = (-b / 2a, -Δ / 4a) = (20/93 ≈ 0.215054, 412/93 ≈ 4.430108), maximum
  x1 = (-b + √Δ) / 2a = (-4 + √164.8) / (-18.6) = -0.475131
  x2 = (-b - √Δ) / 2a = (-4 - √164.8) / (-18.6) = 0.905239
Discriminant is strictly positive, the two solutions are:
X1 = -0.475131
X2 = 0.905239
```

## Usage

```
./computor "3x = 1"        one equation
./computor < file          one equation per line, blank lines skipped
./computor                 same, typed on the terminal, Ctrl-D to end
```

On stdin, answers are separated by a blank line, an invalid line does not stop the
following ones, and the exit status is 1 if any line was invalid. Bytes that are not
UTF-8 become `�` instead of crashing the read.

## Output

- `Reduced form`: every term moved to the left side, one term per degree from `X^0` up.
- `Polynomial degree`: highest degree left after reduction. Degrees 3 to 10 are printed
  with "I can't solve"; above 10 the equation is refused.
- Indented lines: the calculation, formula first, then the same formula with the numbers.
  - `Δ` is the discriminant `b² - 4ac`: positive gives two real solutions, zero one,
    negative two complex ones.
  - `vertex` is the top or bottom point of the curve `y = aX² + bX + c`, at
    `X = -b / 2a`, `y = -Δ / 4a`: `minimum` when `a > 0` (curve opens upwards),
    `maximum` when `a < 0`.
- Numbers are printed with at most 6 decimals, trailing zeros removed (`0.5`, not
  `0.500000`). Below `0.000001` they switch to scientific notation (`1e-07`) instead of
  printing `0`.
- A result whose decimals never end is also given as a fraction: `1/3 ≈ 0.333333`. See
  [Fractions](#fractions).

On a terminal, the reduced form is coloured: signs yellow, `*` green, exponents cyan. The
colours are ANSI escape codes, invisible characters such as `\033[33m` (switch to yellow)
and `\033[0m` (back to normal) that a terminal interprets. In a file or a pipe they would
show up as garbage, so they are only written when stdout is a terminal (`isatty()`).

## Input

Beyond the subject's `a * X^n` form:

| Accepted                  | Example                  | Read as                        |
|---------------------------|--------------------------|--------------------------------|
| any single letter         | `3y + 1 = 0`, `B^2 = B`  | the unknown, named as typed    |
| `*` left out              | `3x = 1`, `x3 = 1`       | `3 * x^1`                      |
| exponent left out         | `x = 1`                  | `x^1`                          |
| unicode exponents         | `3x² = 1`, `X¹⁰ = 1`     | `3 * x^2`, `X^10`              |
| several X in one term     | `X * X = 4`, `X^2 * X`   | exponents add: `X^2`, `X^3`    |
| powers of numbers         | `2^3 * X = 1`            | `8 * X^1`                      |
| sign before a power       | `-2^2 + 3x = 0`          | `-(2^2)`, so `-4`              |
| several signs             | `--x = 1`, `-1 * -X = 0` | `+x^1`, `+X^1`                 |
| missing digit around `.`  | `.5 = X`, `5. = X`       | `0.5`, `5`                     |
| terms in any order        | `X^2 + 1 = X^2 + X`      | reduced to `1 - X = 0`         |

The first letter found is the unknown, exactly as typed, and the whole output uses it: reduced
form, calculation lines and solutions. `b² = 4` gives `1 * b^2`, then `b1 = 2` and `b2 = -2`.
Any other letter, even the same one in another case, is refused. Without any letter, `X`.
If the unknown is `a`, `b` or `c`, like a coefficient in the calculation lines, a last line
says so: `(b is the unknown of the equation, not the coefficient b)`.

| Refused            | Message                                  | Why                                        |
|--------------------|------------------------------------------|--------------------------------------------|
| `x + y`, `x = X`   | second unknown                           | one unknown only, case included            |
| `2(x + 1) = 0`     | parentheses are not supported            | would need expanding the product           |
| `2^3^2 = x`        | chained exponent is ambiguous            | see below                                  |
| `X^1.5 = 1`        | exponent must be an integer              | the subject has integer exponents only     |
| `x^-1 = 1`         | negative exponent after reduction        | not a polynomial                           |
| `x^11 = 1`         | reduced degree greater than 10           | `MAX_DEGREE` in `parser.py`                |
| `2 3 = x`          | missing operator between numbers         | removing spaces would read `23`            |
| `10^101 * X = 1`   | number too large                         | see below                                  |
| `x = 1 = 2`, `= 1` | expected one '=' between two sides       |                                            |

- **Chained exponents**: `2^3^2` is `2^(3^2) = 512` in mathematics and Python, but
  `(2^3)^2 = 64` in Excel and MATLAB, which read left to right. Without parentheses the
  reader cannot say which one is meant, so it is refused.
- **Negative exponents** are read, and refused only if a negative degree is left after
  reduction: `x^-1 + x = x^-1` is `x = 0`.
- **Magnitude**: a number above `1e100` or, except zero, below `1e-100` is refused
  (`MAX_VALUE`, `MIN_VALUE` in `number.py`). A float stops at about `1.8e308`: beyond
  those bounds, `b²`, `4ac` or `-b / 2a` would become infinite or `0`.

Errors show where the problem is, with `^` under the character:

```
$> ./computor "x % 2 = 0"
computor: unexpected character '%'
    x % 2 = 0
      ^
```

## How the parser works

1. **Check** (`split_sides`, `check_characters`): exactly one `=` with something on each
   side, then the refused cases above, on the raw text so the `^` points at what was typed.
2. **Normalize** (`normalize`): each side goes through the regex substitutions of
   `parser.NORMALIZATIONS`, in order, each one commented with an example. They end with
   one signed term per word and `*` between factors: `3x² - x` becomes `+3*X^2 -X^1`.
3. **Read** (`read_terms`, `multiply_factors`): each term is split on `*`, each factor is
   a number or `X`, each with an optional exponent. Numbers multiply, exponents of X add.
4. **Reduce** (`add_terms`, `reduce`): terms of the same degree are summed, those of the
   right side subtracted.

## Rounding errors

Floats are not exact: `0.1 + 0.2 - 0.3` gives `5.5e-17`, and `0.2 * 0.2 - 4 * 0.01`
gives `6.9e-18`, both instead of `0`. Left alone, `0.1x + 0.2x = 0.3x` would keep a tiny
`X^1` term, and `x² + 0.2x + 0.01 = 0` would get two solutions instead of one.

So every number that can be `0` is compared with its **margin**: the largest rounding
error it can contain. Below its margin, it is set to exactly `0`.

**Epsilon.** `sys.float_info.epsilon`, `2.2e-16`, is the gap between `1.0` and the next
float. One rounding changes a number by at most `epsilon / 2` of its size. The margins
count one `epsilon` per rounding, twice the worst case.

**Coefficients** (`multiply_factors`, `add_terms` in `parser.py`). A term's roundings are
counted while it is read: 2 per number (reading it, multiplying it in), plus `n + 1`
for a power `^n`, which multiplies the error of the number by `n`. The margin of a
degree then adds up, for each term, `roundings × epsilon × |term|`, plus the rounding of
each addition. For `0.1x + 0.2x = 0.3x` the margin is `4.9e-16`, above `5.5e-17`: the
coefficient is `0`.

**Discriminant** (`delta_margin` in `solver.py`). `a`, `b` and `c` arrive with their
margins `ma`, `mb`, `mc`. The worst error they pass on to `b²` is `(|b| + mb)² - b²`, to
`ac` it is `(|a| + ma)(|c| + mc) - |ac|`. The margin of `Δ` is that inherited error plus
the roundings of `b * b`, `4 * a * c` and the subtraction. If `|Δ|` is below it, `Δ` is
`0`: the solution is double, and the `Δ` and `vertex` lines print `0`.

A fixed tolerance would not work. The previous one, `1e-9` (Python's default for
`math.isclose`), made `1` and `1.0000000001` equal: `x = 1.0000000001x` answered "Any
real number is a solution" instead of `x = 0`, and `x² + 2x + 0.9999999999 = 0` gave one
solution instead of two. With margins, a difference is ignored only if rounding alone
can explain it.

## Fractions

`fraction(x)` in `number.py`:

1. `x.as_integer_ratio()` gives the exact fraction stored in the float, with a power of 2
   as denominator: `1/3` is stored as `6004799503160661/18014398509481984`.
2. `limit_denominator` finds the closest fraction whose denominator is at most `10000`
   (`MAX_DENOMINATOR`): `1/3`. It is copied from CPython's `fractions.Fraction`, which
   uses continued fractions.
3. The fraction is kept only if it equals `x` within `1e-12`, so an irrational such as
   `√2` is never shown as a fraction.

The fraction is printed only if its decimals never end, that is when the denominator has
a prime factor other than 2 and 5: `1/3 ≈ 0.333333`, but `1/4` is printed `0.25`.

Square roots are computed without `math.sqrt`: `isqrt` finds the integer square root by
binary search, and `sqrt(y) = isqrt(y × 10³⁰) / 10¹⁵` keeps 15 decimals.

## Exit status

| Code | When                                                                            |
|------|---------------------------------------------------------------------------------|
| 0    | answered, including "No solution." and degrees 3 to 10                          |
| 1    | invalid equation                                                                |
| 70   | bug in computor                                                                 |
| 120  | output closed before the end, e.g. `\| head -1`                                 |
| 130  | Ctrl-C                                                                          |

- **70** is `EX_SOFTWARE`, "internal software error", in `sysexits.h`. The `computor` entry
  point catches any exception and prints one line instead of a traceback. The rest of the
  code catches only the exceptions it expects, so a test calling a function directly
  still gets the real traceback of a bug.
- **120** is the status Python itself exits with when it cannot flush stdout at the end.
  On `BrokenPipeError` (the reader of the pipe is gone), computor points stdout to
  `/dev/null` so that final flush does not fail a second time with an error message.
- **130** is 128 + 2, 2 being the number of `SIGINT`, the signal Ctrl-C sends. A shell
  reports 128 + n for a program killed by signal n; computor catches Ctrl-C and returns
  the same status.

## Sources

A comment above a function gives its source:

- `# code: URL`: the function copies that code.
  `isqrt` (Wikipedia, binary search), `limit_denominator` (CPython `fractions.py`),
  `colorize` (Wikipedia, ANSI escape codes).
- `# formule: URL`: the function applies that formula.
  `isclose` (Python `math.isclose`, used for [fractions](#fractions)), `sqrt`, `terminates` (decimals end iff the
  denominator has only 2 and 5 as prime factors), `multiply_factors` and `read_number`
  (`xᵃ · xᵇ = xᵃ⁺ᵇ`), `linear`, `quadratic`, `vertex`.
- `# doc: URL`: the function relies on the Python behaviour documented there.
  `fraction` (`float.as_integer_ratio`), `fmt` (`%` formatting), `split_sides`,
  `check_characters`, `normalize` (`re` module), `read_terms` (`str.split`), `read_stdin`
  (`sys.stdin`), `close_quietly` (SIGPIPE), the `computor` entry point (`Exception`,
  `sysexits`).

Wikipedia links carry `oldid=`, a fixed revision of the page, so the cited text does not
change. A function without such a comment was written for this project.

## Layout

```
computor                 entry point, turns a crash into exit status 70
computorv1/cli.py        argument or stdin, exit status
computorv1/parser.py     check, normalize, read, reduce
computorv1/solver.py     degree 0, 1 or 2: solutions and calculation lines
computorv1/display.py    output text and colours
computorv1/number.py     square root, fractions, number formatting
tests/test_computor.py   unittest suite
tests/corpus.py          inputs taken from 456 GitHub repositories of 42 students
```

`corpus.py` holds three lists:

- `EQUATIONS` (453): equations from those repositories' READMEs and test scripts, with
  their reduced form. Each expected form was checked by evaluating the original equation
  with Python's `eval()` at several values of X and comparing with the polynomial.
- `REFUSED` (84): inputs that must be refused, with the start of the expected message.
- `CRASHERS` (8): inputs that once crashed computor or made it answer wrong, each with
  the cause. Some were found by fuzzing (feeding the program large numbers of random or
  mutated inputs until one breaks it), the others by trying edge cases. They are kept so
  the same bug cannot come back unnoticed.

## Make

| Target              | Does                                                    |
|---------------------|---------------------------------------------------------|
| `make run`          | reads equations from stdin                              |
| `make run "3x = 1"` | solves that equation, quotes required                   |
| `make test`         | runs the unittest suite                                 |
| `make lint`         | checks the code with ruff, see [Lint](#lint)            |
| `make format`       | applies ruff's automatic fixes, then reformats the code |
| `make clean`        | removes `__pycache__` from the copy                     |
| `make fclean`       | removes `/dev/shm/computorv1`                           |
| `make re`           | `fclean`, then copies the code and reinstalls ruff      |

`make run` and `make test` first copy the code to `/dev/shm/computorv1`, a directory kept
in RAM, and run it from there. Ruff is installed in a virtualenv there too, on the first
`make lint` or `make format`, and runs with `--no-cache`. So nothing but the code is ever
written into the repository: no `__pycache__`, no virtualenv, no `.ruff_cache`.

## Lint

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
