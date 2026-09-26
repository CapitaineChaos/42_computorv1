# computorv1

Solves polynomial equations of degree 2 or lower. Python 3.8+, standard library only.

```
$> ./computor "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0
Polynomial degree: 2
Discriminant is strictly positive, the two solutions are:
0.905239
-0.475131
```

Without an equation, equations are read from stdin, one per line.

## Options

| Flag | Effect |
| --- | --- |
| `-e`, `--exact` | exact roots: irreducible fractions and radicals |
| `-s`, `--steps` | intermediate steps |
| `-p N`, `--precision N` | decimals of the approximations, default 6 |

```
$> ./computor -e -s "x^2 - x - 1 = 0"
Reduced form: -1 * X^0 - 1 * X^1 + 1 * X^2 = 0
Polynomial degree: 2
  a = 1, b = -1, c = -1
  delta = b^2 - 4ac = (-1)^2 - 4 * 1 * (-1) = 5
  sqrt(delta) = √5
  X = (-b +/- sqrt(delta)) / 2a = (1 +/- √5) / 2
Discriminant is strictly positive, the two solutions are:
(1 + √5) / 2 ~ 1.618034
(1 - √5) / 2 ~ -0.618034
```

## Bonus

- Free form entry: `5 + 4X + X^2 = X^2`, `(x + 2)(x - 3) = 0`, `2(x + 1)^2 = 8`, `x / 3 = 1`.
- Input errors reported with their position:

```
$> ./computor "x % 2 = 0"
computor: unexpected character '%'
    x % 2 = 0
      ^
```

- Irreducible fractions, in the reduced form and in the roots.
- Exact roots: radicals for an irrational discriminant, `a + bi` for a negative one.
- Intermediate steps.

## Design

Coefficients and roots stay exact from end to end: `Rational` holds a pair of integers,
`Root` holds `a + b*sqrt(r)`. Decimals are produced only at print time, by integer
division and an integer square root — the subject bans math library calls.

Exit status: 0, 1 on an invalid equation, 2 on invalid usage.

The subject's examples print no `Polynomial degree` line for a degree 0 reduced form;
this follows them.

## Layout

```
computor              entry point
computorv1/rational   exact rationals, integer square root
computorv1/parser     tokens, grammar, polynomial arithmetic
computorv1/solver     discriminant, exact roots
computorv1/cli        arguments, output, error reporting
tests/                unittest suite
```

## Make

`venv`, `run EQ="..."`, `test`, `lint`, `format`, `clean`, `fclean`, `re`.
