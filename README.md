# computorv1

Solves polynomial equations of degree 2 or lower. Python 3.10+, standard library only.

```
$> ./computor "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0
Polynomial degree: 2
  a = -9.3, b = 4, c = 4
  Δ = b² - 4ac = 4² - 4 * (-9.3) * 4 = 164.8
  vertex = (-b / 2a, c - b² / 4a) = (20/93 ≈ 0.215054, 412/93 ≈ 4.430108), maximum
  x1 = (-b + √Δ) / 2a = (-4 + √164.8) / (-18.6) = -0.475131
  x2 = (-b - √Δ) / 2a = (-4 - √164.8) / (-18.6) = 0.905239
Discriminant is strictly positive, the two solutions are:
-0.475131
0.905239
```

Without an equation, equations are read from stdin, one per line.

On a terminal the reduced form is coloured: signs yellow, `*` green, exponents cyan. Piped
or redirected output carries no escape codes.

## Bonus

Free form entry: `5 + 4 * X + X^2 = X^2`, `3x = 1`, `.5 = X`, `X * X = 4`, `-1 * -X = 0`,
`3y² + 4y + 4 = 8`, `X¹⁰ = 1`, `-2^2 + 3x = 0`, exponents in any order or repeated. Any
single letter is the unknown, a second one is an error.

Each side is rewritten by successive `re.sub` (`parser.NORMALIZATIONS`) until terms are
separated by spaces and factors by `*`; terms are then split on spaces, factors on `*`, and
each factor must be a number or X, followed by exponents: numbers multiply, exponents of
X add. A chain such as `2^3^2` is refused: it is 512 in mathematics, 64 in Excel and
MATLAB, and there are no parentheses here to tell them apart. A negative exponent is read,
then refused only if it survives the reduction, which `x^-1 = x^-1` does not. The reduced
degree is capped at 10.

Input errors, reported with their position:

```
$> ./computor "x % 2 = 0"
computor: unexpected character '%'
    x % 2 = 0
      ^
```

Irreducible fractions when the decimal writing does not terminate:

```
$> ./computor "5 * X^0 = 4 * X^0 + 7 * X^1"
...
1/7 ≈ 0.142857
```

Intermediate steps and vertex of the parabola, always shown:

```
$> ./computor "5 * X^0 + 13 * X^1 + 3 * X^2 = 1 * X^0 + 1 * X^1"
Reduced form: 4 * X^0 + 12 * X^1 + 3 * X^2 = 0
Polynomial degree: 2
  a = 3, b = 12, c = 4
  Δ = b² - 4ac = 12² - 4 * 3 * 4 = 96
  vertex = (-b / 2a, -Δ / 4a) = (-2, -8), minimum
  x1 = (-b + √Δ) / 2a = (-12 + √96) / 6 = -0.367007
  x2 = (-b - √Δ) / 2a = (-12 - √96) / 6 = -3.632993
Discriminant is strictly positive, the two solutions are:
-0.367007
-3.632993
```

## Sources

Each sourced function is preceded by its URL, Wikipedia links pinned to a revision:

- `# code:` the function reproduces that code: `limit_denominator` (CPython `fractions.py`),
  `isqrt` (Wikipedia, binary search).
- `# formule:` the function transcribes that formula: `isclose`, `multiply_factors`,
  `read_number`, `sqrt`, `terminates`, `linear`, `quadratic`, `vertex`.
- `# doc:` the function relies on that documented behaviour: `check_unknown`, `normalize`,
  `split_sides`, `read_terms`, `fraction`, `fmt`.

Functions without a URL are glue written here.

## Layout

```
computor                 entry point
computorv1/number.py     integer square root, limit_denominator, formatting
computorv1/parser.py     checks, normalization, terms and factors, reduction
computorv1/solver.py     degree 0 to 2, discriminant, vertex, steps
computorv1/display.py    output text
computorv1/cli.py        arguments, stdin, exit status
tests/                   unittest suite, corpus.py holds 536 real inputs
```

Exit status: 0, 1 on an invalid equation, 70 on an internal error, 120 on a closed pipe,
130 on Ctrl-C. The entry point turns any unexpected exception into a one-line message; the
code itself never catches broadly, so tests and fuzzing still see real failures.

## Make

`run EQ="..."`, `test`, `lint`, `format`, `clean`, `fclean`, `re`.
