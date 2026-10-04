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
  [Exact arithmetic](#exact-arithmetic).

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

Powers of numbers use `math.pow`, so their range and precision are those of Python
floats. An overflow raises `OverflowError`; a nonzero base whose power becomes zero
raises `ValueError`. The CLI reports these errors. There is no timer or exponent cap.
The floating-point result is stored as a fraction for subsequent calculations; this
does not recover precision lost during the power calculation.

| Refused            | Message                                  | Why                                        |
|--------------------|------------------------------------------|--------------------------------------------|
| `x + y`, `x = X`   | second unknown                           | one unknown only, case included            |
| `2(x + 1) = 0`     | parentheses are not supported            | would need expanding the product           |
| `2^3^2 = x`        | chained exponent is ambiguous            | see below                                  |
| `X^1.5 = 1`        | exponent must be an integer              | the subject has integer exponents only     |
| `x^-1 = 1`         | negative exponent after reduction        | not a polynomial                           |
| `x^11 = 1`         | reduced degree greater than 10           | `MAX_DEGREE` in `reduce.py`                |
| `2 3 = x`          | missing operator between numbers         | removing spaces would read `23`            |
| `2^999999999 = x`  | number too large                         | floating-point power overflows             |
| `2^-999999999 = x` | number too small                         | nonzero power rounds to zero               |
| `x = 1 = 2`, `= 1` | expected one '=' between two sides       |                                            |
