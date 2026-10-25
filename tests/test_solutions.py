# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Valeurs des solutions, par le programme entier. Forme de la sortie : test_resolution.py.
#
# Attendus tirés des coefficients par formule fermée, jamais relevés sur la sortie. x1 et x2
# comparés sans ordre. Tolérance de l'affichage : 6 décimales, 6 chiffres significatifs sous
# 1e-6 ; zéro exigé exact. Une fraction affichée devant « ≈ » est lue exacte.

import re
import subprocess
import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from itertools import combinations, product
from os.path import abspath, dirname, join

ROOT = dirname(dirname(abspath(__file__)))
sys.path.insert(0, ROOT)

from tests.common import run  # noqa: E402

COMPUTOR = join(ROOT, "computor")
TIMEOUT = 5

# unittest masque la pile des modules qui définissent __unittest.
__unittest = True

# Issues sans valeur, reconnues à leur libellé.
ALL, NONE, HIGH = "real number", "no solution", "can't solve"

SOLUTION = re.compile(r"[xX][12]? = (.+)")
COMPLEX = re.compile(r"(\S+) ([+-]) (\S+)")


def number(text):
    p, _, q = text.partition("/")
    return int(p) / int(q) if q else float(p)


# 2i/5, i/2, -i, 0.866025i
def imaginary(text):
    negative = text.startswith("-")
    digits = text.lstrip("+-").replace("i", "")
    if not digits or digits.startswith("/"):
        digits = "1" + digits
    return -number(digits) if negative else number(digits)


def value(text):
    text = text.partition(" ≈ ")[0]
    pair = COMPLEX.fullmatch(text)
    if pair:
        real, sign, im = pair.groups()
        return complex(number(real), imaginary(sign + im))
    if "i" in text:
        return complex(0, imaginary(text))
    return complex(number(text))


def close(got, want):
    if want == 0:
        return got == 0
    if abs(want) < 1e-6:
        return abs(got - want) <= 1e-5 * abs(want)
    return abs(got - want) <= 1e-6 * max(1, abs(want))


def same(got, want):
    return close(got.real, want.real) and close(got.imag, want.imag)


def matches(got, wanted):
    left = list(got)
    for want in wanted:
        hit = next((g for g in left if same(g, want)), None)
        if hit is None:
            return False
        left.remove(hit)
    return not left


def conjugates(real, im):
    return complex(real, im), complex(real, -im)


# Nom du test → (cas conformes, cas), affiché en fin de module : unittest ne compte que les
# méthodes, pas leurs subTest.
SUMMARY = {}


def tearDownModule():
    width = max(len(name) for name in SUMMARY)
    passed_all, total_all = 0, 0
    print(file=sys.stderr)
    for name, (passed, total) in SUMMARY.items():
        print(f"  {name:{width}}  {passed:>3}/{total}", file=sys.stderr)
        passed_all += passed
        total_all += total
    print(f"  {'total':{width}}  {passed_all:>3}/{total_all}", file=sys.stderr)


class Case(unittest.TestCase):
    def check(self, cases):
        passed = 0
        for source, expected in cases:
            with self.subTest(source):
                self.verify(source, expected)
                passed += 1
        SUMMARY[f"{type(self).__name__}.{self._testMethodName}"] = (passed, len(cases))

    def verify(self, source, expected):
        status, out, err = run(source)
        self.assertEqual((status, err), (0, ""), out)
        lines = map(SOLUTION.fullmatch, out.splitlines())
        got = [value(line[1]) for line in lines if line]
        if isinstance(expected, str):
            self.assertIn(expected, out.lower(), out)
            self.assertEqual(got, [], out)
            return
        wanted = [complex(want) for want in expected]
        self.assertTrue(matches(got, wanted), f"attendu {expected}\n{out}")


class Linear(Case):
    def test_values(self):
        self.check([
            ("2 * x + 4 = 0", (-2,)),
            ("3 * x = 1", (1 / 3,)),
            ("4 = x", (4,)),
            ("-x = 7", (-7,)),
            ("7 * x = 0", (0,)),
            ("0.5 * x - 0.25 = 0", (0.5,)),
            ("5 * X^0 + 4 * X^1 = 4 * X^0", (-0.25,)),
        ])

    # Le terme de plus haut degré s'annule.
    def test_degree_drops(self):
        self.check([
            ("5 + 4 * X + X^2 = X^2", (-1.25,)),
            ("x^2 + x = x^2 + 1", (1,)),
            ("x^3 - x^3 + 2 * x = 3", (1.5,)),
        ])


class TwoRoots(Case):
    def test_rational(self):
        self.check([
            ("x^2 - 5 * x + 6 = 0", (2, 3)),
            ("x^2 = 4", (2, -2)),
            ("2 * x^2 + 3 * x - 2 = 0", (0.5, -2)),
            ("-x^2 + 2 * x + 3 = 0", (3, -1)),
            ("x * x - 2 * x = 3", (3, -1)),
            ("3 * x^2 = 6 * x", (0, 2)),
            ("0.1 * x^2 - 0.3 * x + 0.2 = 0", (1, 2)),
            ("x^2 - 1000000 = 0", (1000, -1000)),
        ])

    def test_irrational(self):
        self.check([
            ("x^2 - 2 = 0", (2**0.5, -(2**0.5))),
            ("3 * x^2 - 2 = 0", ((2 / 3) ** 0.5, -((2 / 3) ** 0.5))),
            ("x^2 + x - 1 = 0", ((-1 + 5**0.5) / 2, (-1 - 5**0.5) / 2)),
            (
                "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0",
                ((4 + 164.8**0.5) / 18.6, (4 - 164.8**0.5) / 18.6),
            ),
        ])


class DoubleRoot(Case):
    def test_values(self):
        self.check([
            ("x^2 - 2 * x + 1 = 0", (1,)),
            ("4 * x^2 + 4 * x + 1 = 0", (-0.5,)),
            ("-x^2 + 6 * x = 9", (3,)),
            ("x^2 = 0", (0,)),
            ("0.01 + 0.2 * x + x^2 = 0", (-0.1,)),
        ])


class Complex(Case):
    def test_values(self):
        self.check([
            ("x^2 + 1 = 0", conjugates(0, 1)),
            ("4 * x^2 + 9 = 0", conjugates(0, 1.5)),
            ("x^2 + 2 * x + 5 = 0", conjugates(-1, 2)),
            ("5 * x^2 + 2 * x + 1 = 0", conjugates(-0.2, 0.4)),
            ("x^2 + x + 1 = 0", conjugates(-0.5, 3**0.5 / 2)),
            ("-2 * x^2 + x - 1 = 0", conjugates(0.25, 7**0.5 / 4)),
        ])


class NoValue(Case):
    def test_all_reals(self):
        self.check([
            ("x = x", ALL),
            ("42 * X^0 = 42 * X^0", ALL),
            ("x^2 + x = x^2 + x", ALL),
        ])

    def test_no_solution(self):
        self.check([
            ("1 = 2", NONE),
            ("4 * X^0 = 8", NONE),
            ("x^2 + 1 = x^2", NONE),
        ])

    def test_degree_too_high(self):
        self.check([
            ("x^3 = 1", HIGH),
            ("8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0", HIGH),
        ])


class Writing(Case):
    def test_products(self):
        self.check([
            ("3x^2 = 12", (2, -2)),
            ("xx = 4", (2, -2)),
            ("x * x * 2 = 8", (2, -2)),
            ("x^1 * x = 9", (3, -3)),
            ("x^2 * x^0 = 4", (2, -2)),
            ("2 * 3 * x = 12", (2,)),
            ("3 * 2^2 * x = 24", (2,)),
            ("x * 0.5 = 0.25", (0.5,)),
        ])

    def test_signs(self):
        self.check([
            ("-2^2 + x = 0", (4,)),
            ("-x^2 = -9", (3, -3)),
            ("x * -x = -4", (2, -2)),
            ("3 * -x = 6", (-2,)),
            ("x - -2 = 0", (-2,)),
            ("+x = 1", (1,)),
            ("--x = 5", (5,)),
            ("x = ---1", (-1,)),
        ])

    def test_constants(self):
        self.check([
            ("2^3 = x", (8,)),
            ("x^0 = x", (1,)),
        ])

    # Termes répartis des deux côtés, semblables à regrouper.
    def test_both_sides(self):
        self.check([
            ("0 = x^2 - 4", (2, -2)),
            ("6 + x^2 = 5 * x", (2, 3)),
            ("x^2 = x", (0, 1)),
            ("2 * x^2 - x = x^2 + 2", (2, -1)),
            ("x^2 - 3 * x = x - 4", (2,)),
            ("x^2 + x^2 = 8", (2, -2)),
            ("1.5 * x + 0.5 * x = 4", (2,)),
            ("4 * x^2 - 4 * x^2 + x^2 = 1", (1, -1)),
            ("5 * x^2 = 5 * x^2 + x", (0,)),
        ])


# Développement décimal infini : affichage « p/q ≈ … », ou décimal seul au-delà d'un
# dénominateur de 10000.
class Fractions(Case):
    def test_values(self):
        self.check([
            ("7 * x = 22", (22 / 7,)),
            ("21 * x^2 - x - 2 = 0", (1 / 3, -2 / 7)),
            ("9 * x^2 = 4", (2 / 3, -2 / 3)),
            ("3 * x^2 + x = 0", (0, -1 / 3)),
            ("9 * x^2 - 6 * x + 1 = 0", (1 / 3,)),
            ("9 * x^2 + 6 * x + 5 = 0", conjugates(-1 / 3, 2 / 3)),
            ("3 * x^2 + 2 * x + 1 = 0", conjugates(-1 / 3, 2**0.5 / 3)),
        ])

    def test_large_denominator(self):
        self.check([
            ("10007 * x = 1", (1 / 10007,)),
            ("10007 * x^2 = 1", (10007**-0.5, -(10007**-0.5))),
        ])


class Precision(Case):
    def test_values(self):
        tiny = "0." + "0" * 39 + "2"
        self.check([
            # -b + √Δ avec √Δ ≈ b : annulation en flottants, dans les deux sens de b.
            ("0.00000000000000000001 * x^2 + x + 1 = 0", (-1, -1e20)),
            ("0.00000000000000000001 * x^2 - x + 1 = 0", (1, 1e20)),
            ("x^2 - 100000000 * x + 1 = 0", (1e8, 1e-8)),
            ("x^2 + 100000000 * x + 1 = 0", (-1e8, -1e-8)),
            (f"x^2 = {tiny}", (2**0.5 * 1e-20, -(2**0.5) * 1e-20)),
            ("x^2 + 2 * x + 0.9999999999 = 0", (-1 + 1e-5, -1 - 1e-5)),
            ("x = 0.000000000000000000000000000001", (1e-30,)),
        ])

    def test_extremes(self):
        self.check([
            ("1000000000000000 * x^2 - 1 = 0", (1e15**-0.5, -(1e15**-0.5))),
            ("x^2 = 1000000000000000", (1e15**0.5, -(1e15**0.5))),
            ("x = 123456789012345678901234567890", (1.2345678901234568e29,)),
            # Δ = -4e-16 : partie imaginaire 1e-8.
            ("x^2 + 2 * x + 1.0000000000000001 = 0", conjugates(-1, 1e-8)),
        ])


# Sous-processus avec délai : un calcul interminable échoue au lieu de bloquer la suite.
# Attendu : (code de sortie, libellé).
class Limits(Case):
    def verify(self, source, expected):
        status, label = expected
        result = None
        try:
            result = subprocess.run(
                [sys.executable, COMPUTOR, source],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            pass
        if result is None:
            self.fail(f"pas de réponse en {TIMEOUT} s")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, status, output)
        self.assertIn(label, output.lower(), output)

    def test_values(self):
        self.check([
            ("x^999999999999 = 1", (0, HIGH)),
            ("10^400 = x", (1, "number too large")),
            ("2^999999999 = x", (1, "number too large")),
        ])


# Décimaux finis : leurs produits restent finis, l'équation s'écrit sans arrondi.
LEADING = [Fraction(a) for a in ("1", "-1", "2", "-0.5", "4")]
ROOTS = [Fraction(r) for r in ("-3", "-1.5", "0", "0.25", "1", "2", "10")]
REAL_PARTS = [Fraction(p) for p in ("-2", "0", "0.5", "3")]
IMAGINARY_PARTS = [Fraction(q) for q in ("0.5", "1", "4")]
FRACTIONS = [Fraction(r) for r in ("1/3", "-2/7", "5/6", "-1/9", "4/11", "7/3")]
GRID_A = [Fraction(a) for a in ("-2", "-1", "0.5", "1", "3")]
GRID_BC = [Fraction(v) for v in ("-4", "-1", "0", "2", "5")]

UNKNOWN = {2: " * x^2", 1: " * x", 0: ""}


def decimal(fraction):
    exact = Decimal(fraction.numerator) / Decimal(fraction.denominator)
    return format(exact, "f")


# {degré: coefficient} → « 2 * x^2 - 0.5 * x + 3 = 0 », termes nuls omis.
def equation(coeffs):
    text = ""
    for degree in (2, 1, 0):
        coeff = coeffs.get(degree, 0)
        if coeff == 0:
            continue
        term = decimal(abs(coeff)) + UNKNOWN[degree]
        if text == "":
            text = "-" + term if coeff < 0 else term
        elif coeff < 0:
            text += " - " + term
        else:
            text += " + " + term
    return (text or "0") + " = 0"


# a(x - r1)(x - r2)
def from_roots(a, r1, r2):
    return equation({2: a, 1: -a * (r1 + r2), 0: a * r1 * r2})


# a(q1·x - p1)(q2·x - p2), racines p1/q1 et p2/q2 : coefficients entiers.
def from_fractions(a, r1, r2):
    p1, q1 = r1.numerator, r1.denominator
    p2, q2 = r2.numerator, r2.denominator
    return equation({2: a * q1 * q2, 1: -a * (q1 * p2 + q2 * p1), 0: a * p1 * p2})


# a(x² - 2px + p² + q²), racines p ± qi
def from_conjugates(a, p, q):
    return equation({2: a, 1: -2 * a * p, 0: a * (p * p + q * q)})


def by_formula(a, b, c):
    delta = b * b - 4 * a * c
    if delta == 0:
        return (float(-b / (2 * a)),)
    if delta > 0:
        root = float(delta) ** 0.5
        return ((float(-b) + root) / float(2 * a), (float(-b) - root) / float(2 * a))
    root = float(-delta) ** 0.5
    return conjugates(float(-b / (2 * a)), root / float(2 * a))


class Generated(Case):
    def test_linear(self):
        cases = []
        for a, r in product(LEADING, ROOTS):
            cases.append((equation({1: a, 0: -a * r}), (float(r),)))
        self.check(cases)

    def test_two_roots(self):
        cases = []
        for a, (r1, r2) in product(LEADING, combinations(ROOTS, 2)):
            cases.append((from_roots(a, r1, r2), (float(r1), float(r2))))
        self.check(cases)

    def test_double_root(self):
        cases = []
        for a, r in product(LEADING, ROOTS):
            cases.append((from_roots(a, r, r), (float(r),)))
        self.check(cases)

    def test_fractions(self):
        cases = []
        for a, (r1, r2) in product(LEADING, combinations(FRACTIONS, 2)):
            cases.append((from_fractions(a, r1, r2), (float(r1), float(r2))))
        for a, r in product(LEADING, FRACTIONS):
            cases.append((from_fractions(a, r, r), (float(r),)))
        self.check(cases)

    def test_complex(self):
        cases = []
        for a, p, q in product(LEADING, REAL_PARTS, IMAGINARY_PARTS):
            cases.append((from_conjugates(a, p, q), conjugates(float(p), float(q))))
        self.check(cases)

    def test_formula(self):
        cases = []
        for a, b, c in product(GRID_A, GRID_BC, GRID_BC):
            cases.append((equation({2: a, 1: b, 0: c}), by_formula(a, b, c)))
        self.check(cases)


if __name__ == "__main__":
    unittest.main()
