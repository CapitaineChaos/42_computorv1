# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Ce que le programme répond à une saisie valide. Ce qui est accepté ou refusé, et avec quel
# code, est dans test_saisie.py.
#
# Solution, Steps, Precision : du polynôme réduit à la réponse, sans passer par le parser
# (build_eq). Sortie comparée en entier.
# Reduction : de la saisie à la forme réduite, par le programme entier.

import sys
import unittest
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.builder import build_eq  # noqa: E402
from computorv1.fraction import from_decimal  # noqa: E402
from tests.common import run  # noqa: E402


# Polynôme réduit donné par {degré: coefficient en texte décimal}.
def answer(coefficients, name="x", steps=False):
    coeffs = {degree: from_decimal(c) for degree, c in coefficients.items()}
    degree = max((d for d, c in coeffs.items() if c != 0), default=-1)
    return "\n".join(build_eq(coeffs, degree, name).lines(steps)) + "\n"


class Solution(unittest.TestCase):
    def test_linear(self):
        self.assertEqual(
            answer({0: "-4", 1: "2"}),
            "Reduced form: -4 * x^0 + 2 * x^1 = 0\nPolynomial degree: 1\nThe solution is:\nx = 2\n",
        )

    def test_linear_decimal(self):
        self.assertTrue(answer({0: "1", 1: "4"}).endswith("\nx = -0.25\n"))

    # Développement décimal infini : fraction exacte, puis valeur approchée.
    def test_linear_repeating(self):
        self.assertTrue(answer({0: "-1", 1: "3"}).endswith("\nx = 1/3 ≈ 0.333333\n"))

    def test_two_roots(self):
        self.assertEqual(
            answer({0: "-6", 1: "-1", 2: "1"}),
            "Reduced form: -6 * x^0 - 1 * x^1 + 1 * x^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly positive, the two solutions are:\n"
            "x1 = 3\n"
            "x2 = -2\n",
        )

    def test_two_roots_subject(self):
        self.assertEqual(
            answer({0: "4", 1: "4", 2: "-9.3"}, name="X"),
            "Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly positive, the two solutions are:\n"
            "X1 = -0.475131\n"
            "X2 = 0.905239\n",
        )

    def test_two_roots_repeating(self):
        self.assertTrue(
            answer({0: "-4", 2: "9"}).endswith("\nx1 = 2/3 ≈ 0.666667\nx2 = -2/3 ≈ -0.666667\n")
        )

    def test_double_root(self):
        self.assertEqual(
            answer({0: "1", 1: "-2", 2: "1"}),
            "Reduced form: 1 * x^0 - 2 * x^1 + 1 * x^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is zero, the solution is:\n"
            "x = 1\n",
        )

    def test_complex_roots(self):
        self.assertEqual(
            answer({0: "1", 1: "2", 2: "5"}),
            "Reduced form: 1 * x^0 + 2 * x^1 + 5 * x^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly negative, the two complex solutions are:\n"
            "x1 = -1/5 + 2i/5\n"
            "x2 = -1/5 - 2i/5\n",
        )

    def test_complex_pure_imaginary(self):
        self.assertTrue(answer({0: "1", 2: "1"}).endswith("\nx1 = 0 + i\nx2 = 0 - i\n"))

    def test_complex_irrational(self):
        self.assertTrue(
            answer({0: "1", 1: "1", 2: "1"}).endswith(
                "\nx1 = -1/2 + 0.866025i\nx2 = -1/2 - 0.866025i\n"
            )
        )

    def test_all_reals(self):
        self.assertEqual(answer({}), "Reduced form: 0 * x^0 = 0\nAny real number is a solution.\n")

    def test_no_solution(self):
        self.assertEqual(answer({0: "-5"}), "Reduced form: -5 * x^0 = 0\nNo solution.\n")

    def test_degree_three(self):
        self.assertEqual(
            answer({3: "1"}),
            "Reduced form: 0 * x^0 + 0 * x^1 + 0 * x^2 + 1 * x^3 = 0\n"
            "Polynomial degree: 3\n"
            "The polynomial degree is strictly greater than 2, I can't solve.\n",
        )

    # Au-delà du degré 3, plus de forme réduite.
    def test_degree_four(self):
        self.assertEqual(
            answer({4: "1"}),
            "Polynomial degree: 4\n"
            "The polynomial degree is strictly greater than 2, I can't solve.\n",
        )

    # Aucun tableau de 10^12 coefficients construit.
    def test_huge_degree(self):
        self.assertTrue(answer({10**12: "1"}).startswith("Polynomial degree: 1000000000000\n"))

    def test_unknown_name(self):
        self.assertEqual(
            answer({0: "-1", 1: "2"}, name="B"),
            "Reduced form: -1 * B^0 + 2 * B^1 = 0\n"
            "Polynomial degree: 1\n"
            "The solution is:\n"
            "B = 0.5\n",
        )


class Steps(unittest.TestCase):
    def test_two_roots(self):
        self.assertEqual(
            answer({0: "-6", 1: "-1", 2: "1"}, steps=True),
            "Reduced form: -6 * x^0 - 1 * x^1 + 1 * x^2 = 0\n"
            "Polynomial degree: 2\n"
            "  Coeffs:\n"
            "       a = 1\n"
            "       b = -1\n"
            "       c = -6\n"
            "  delta  = b^2 - 4ac\n"
            "         = (-1)^2 - 4 * 1 * (-6)\n"
            "         = 25\n"
            "  vertex = (-b / 2a, -delta / 4a)\n"
            "         = (-(-1)/(2*1), -25/(4*1))\n"
            "         = (1/2, -25/4)\n"
            "         = (0.5, -6.25)\n"
            "         is a minimum\n"
            "  x1 = (-b + rac(delta)) / 2a = (1 + rac(25)) / 2 = 3\n"
            "  x2 = (-b - rac(delta)) / 2a = (1 - rac(25)) / 2 = -2\n"
            "Discriminant is strictly positive, the two solutions are:\n"
            "x1 = 3\n"
            "x2 = -2\n",
        )

    def test_linear(self):
        self.assertIn(
            "  a = 2, b = -4\n  x = -b / a = 4 / 2 = 2\n", answer({0: "-4", 1: "2"}, steps=True)
        )

    def test_double_root(self):
        self.assertIn(
            "  x = x-coordinate of vertex\n    = 1\n",
            answer({0: "1", 1: "-2", 2: "1"}, steps=True),
        )

    def test_complex_roots(self):
        self.assertIn(
            "  -b / 2a = -2 / 10 = -0.2\n  -rac(delta) / 2a = rac(16) / 10 = 0.4\n",
            answer({0: "1", 1: "2", 2: "5"}, steps=True),
        )

    def test_vertex_maximum(self):
        self.assertIn(
            "         = (0, 1)\n         is a maximum\n",
            answer({0: "1", 2: "-1"}, steps=True),
        )

    # Une inconnue nommée a, b ou c se confond avec les coefficients des étapes.
    def test_coefficient_name(self):
        note = "  (b is the unknown of the equation, not the coefficient b)\n"
        self.assertIn(note, answer({0: "-1", 2: "1"}, name="b", steps=True))
        self.assertNotIn("not the coefficient", answer({0: "-1", 2: "1"}, name="y", steps=True))

    def test_hidden_by_default(self):
        self.assertNotIn("delta", answer({0: "-6", 1: "-1", 2: "1"}))


class Precision(unittest.TestCase):
    # -b + √Δ avec b ≈ √Δ : en flottants, x1 valait -49960 au lieu de -1.
    def test_cancellation(self):
        tiny = "0." + "0" * 19 + "1"
        self.assertTrue(
            answer({0: "1", 1: "1", 2: tiny}).endswith("\nx1 = -1\nx2 = -100000000000000000000\n")
        )

    # √Δ arrondi à un nombre fixe de décimales valait 0.
    def test_tiny_delta(self):
        tiny = "-0." + "0" * 39 + "2"
        self.assertTrue(
            answer({0: tiny, 2: "1"}).endswith("\nx1 = 1.41421e-20\nx2 = -1.41421e-20\n")
        )

    # En flottants, √36 - 6 donnait 1.4803e-16 au lieu de 0.
    def test_exact_zero_root(self):
        self.assertTrue(answer({1: "6", 2: "-3"}).endswith("\nx1 = 0\nx2 = 2\n"))

    def test_exact_zero_delta(self):
        self.assertTrue(answer({0: "0.01", 1: "0.2", 2: "1"}).endswith("\nx = -0.1\n"))

    def test_close_values_stay_different(self):
        self.assertIn("two solutions", answer({0: "0.9999999999", 1: "2", 2: "1"}))

    def test_subnormal(self):
        tiny = "0." + "0" * 317 + "494315"
        self.assertTrue(answer({0: tiny, 1: "-1"}).endswith("\nx = 4.94315e-318\n"))

    # Remonte jusqu'à cli.answer, qui affiche « number too large ».
    def test_too_large(self):
        with self.assertRaises(OverflowError):
            answer({0: "1" + "0" * 400, 1: "1"})


def reduced(source):
    _, out, _ = run(source)
    lines = [line for line in out.splitlines() if line.startswith("Reduced form: ")]
    return lines[0].removeprefix("Reduced form: ") if lines else None


class Reduction(unittest.TestCase):
    def test_subject(self):
        self.assertEqual(
            reduced("5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"),
            "4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0",
        )

    def test_free_form(self):
        self.assertEqual(reduced("5 + 4 * X + X^2= X^2"), "5 * X^0 + 4 * X^1 = 0")
        self.assertEqual(reduced("x^2 = 4"), "-4 * x^0 + 0 * x^1 + 1 * x^2 = 0")

    def test_like_terms(self):
        self.assertEqual(reduced("2 * x + 3 * x = 5"), "-5 * x^0 + 5 * x^1 = 0")

    def test_right_side_moved(self):
        self.assertEqual(reduced("4 = x"), "4 * x^0 - 1 * x^1 = 0")

    def test_everything_cancels(self):
        self.assertEqual(reduced("x = x"), "0 * x^0 = 0")

    def test_no_unknown(self):
        self.assertEqual(reduced("1 = 2"), "-1 * X^0 = 0")

    def test_degree_drops(self):
        self.assertEqual(reduced("x^2 - x^2 + x = 0"), "0 * x^0 + 1 * x^1 = 0")
        self.assertEqual(reduced("x^20 + x = x^20 + 1"), "-1 * x^0 + 1 * x^1 = 0")

    def test_products(self):
        self.assertEqual(reduced("X * X = 4"), "-4 * X^0 + 0 * X^1 + 1 * X^2 = 0")
        self.assertEqual(reduced("2 * 3 * X = 1"), "-1 * X^0 + 6 * X^1 = 0")
        self.assertEqual(reduced("X^2 * X^0 * 0.5 = 2"), "-2 * X^0 + 0 * X^1 + 0.5 * X^2 = 0")

    def test_signs(self):
        self.assertEqual(reduced("3 * -x = 1"), "-1 * x^0 - 3 * x^1 = 0")
        self.assertEqual(reduced("x - -2 = 0"), "2 * x^0 + 1 * x^1 = 0")
        self.assertEqual(reduced("+x = 1"), "-1 * x^0 + 1 * x^1 = 0")

    # Convention mathématique, pas celle de bc : -2^2 vaut -4.
    def test_power_before_sign(self):
        self.assertEqual(reduced("-x^2 = 1"), "-1 * x^0 + 0 * x^1 - 1 * x^2 = 0")
        self.assertEqual(reduced("-2^2 + 3 * x = 0"), "-4 * x^0 + 3 * x^1 = 0")

    def test_numeric_power(self):
        self.assertEqual(reduced("3 * 2^2 * x = 1"), "-1 * x^0 + 12 * x^1 = 0")

    # L'exposant ne porte que sur ce qui le précède : 3x^2x vaut 3 * x^2 * x.
    def test_implicit(self):
        self.assertEqual(reduced("3x = 1"), "-1 * x^0 + 3 * x^1 = 0")
        self.assertEqual(reduced("xx = 4"), "-4 * x^0 + 0 * x^1 + 1 * x^2 = 0")
        self.assertEqual(reduced("3x^2x = 1"), "-1 * x^0 + 0 * x^1 + 0 * x^2 + 3 * x^3 = 0")

    def test_exact_decimals(self):
        self.assertEqual(reduced("0.1 * x + 0.2 * x = 0.3 * x"), "0 * x^0 = 0")
        self.assertEqual(reduced("x = 1.0000000001 * x"), "0 * x^0 - 1e-10 * x^1 = 0")

    def test_unknown_name(self):
        self.assertEqual(reduced("y^2 = 4"), "-4 * y^0 + 0 * y^1 + 1 * y^2 = 0")
        self.assertEqual(reduced("B^2 = B"), "0 * B^0 - 1 * B^1 + 1 * B^2 = 0")

    def test_huge_degree(self):
        status, out, err = run("x^999999999999 = 1")
        self.assertEqual((status, err), (0, ""))
        self.assertIn("Polynomial degree: 999999999999\n", out)

    # Ni plantage ni calcul interminable.
    def test_too_large(self):
        for source in ("10^400 = x", "2^999999999 = x"):
            status, _, err = run(source)
            self.assertEqual((status, err), (1, "computor: number too large\n"), source)


if __name__ == "__main__":
    unittest.main()
