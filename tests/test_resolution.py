# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Forme réduite, degré, discriminant et solutions, sur des saisies valides. Ce qui est
# accepté ou refusé, et avec quel code, est dans test_saisie.py.

import sys
import unittest
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.fraction import Fraction  # noqa: E402
from computorv1.parser import parse  # noqa: E402
from computorv1.reduce import MAX_REDUCED_DISP, coeffs_to_array  # noqa: E402
from tests.common import run  # noqa: E402
from tests.corpus import CRASHERS, EQUATIONS, IMPLICIT, UNSOLVED  # noqa: E402


# Coefficients exacts convertis en float, pour comparer aux listes du corpus. Densifie
# sans tenir compte de MAX_REDUCED_DISP : ce que le corpus vérifie est la réduction.
def reduced(source):
    coefficients, degree, _ = parse(source)
    return [float(c) for c in coeffs_to_array(coefficients, degree)]


class Subject(unittest.TestCase):
    def check(self, source, expected):
        status, out, err = run(source)
        results = [line for line in out.splitlines(True) if not line.startswith("  ")]
        header = f"computor: equation 1: {source}\n\n"
        self.assertEqual((status, "".join(results), err), (0, header + expected, ""))

    def test_positive(self):
        self.check(
            "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0",
            "Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly positive, the two solutions are:\n"
            "X1 = -0.475131\nX2 = 0.905239\n",
        )

    def test_linear(self):
        self.check(
            "5 * X^0 + 4 * X^1 = 4 * X^0",
            "Reduced form: 1 * X^0 + 4 * X^1 = 0\nPolynomial degree: 1\n"
            "The solution is:\nX = -0.25\n",
        )

    def test_high(self):
        self.check(
            "8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0",
            "Reduced form: 5 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 0\n"
            "Polynomial degree: 3\n"
            "The polynomial degree is strictly greater than 2, I can't solve.\n",
        )

    def test_identity(self):
        self.check(
            "6 * X^0 = 6 * X^0", "Reduced form: 0 * X^0 = 0\nAny real number is a solution.\n"
        )

    def test_impossible(self):
        self.check("10 * X^0 = 15 * X^0", "Reduced form: -5 * X^0 = 0\nNo solution.\n")

    def test_negative(self):
        self.check(
            "1 * X^0 + 2 * X^1 + 5 * X^2 = 0",
            "Reduced form: 1 * X^0 + 2 * X^1 + 5 * X^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly negative, the two complex solutions are:\n"
            "X1 = -1/5 + 2i/5\nX2 = -1/5 - 2i/5\n",
        )

    def test_fractions(self):
        _, out, _ = run("3 * x = 1")
        self.assertTrue(out.endswith("The solution is:\nx = 1/3 ≈ 0.333333\n"))
        _, out, _ = run("x^2 + x + 1 = 0")
        self.assertTrue(out.endswith("x1 = -1/2 + 0.866025i\nx2 = -1/2 - 0.866025i\n"))
        _, out, _ = run("x^2 + 1 = 0")
        self.assertTrue(out.endswith("x1 = 0 + i\nx2 = 0 - i\n"))

    def test_double(self):
        _, out, _ = run("x^2 - 2 * x + 1 = 0")
        self.assertTrue(out.endswith("Discriminant is zero, the solution is:\nx = 1\n"))


class Reduction(unittest.TestCase):
    def test_subject_bonus(self):
        self.assertEqual(reduced("5 + 4 * X + X^2= X^2"), [5.0, 4.0])

    def test_products(self):
        self.assertEqual(reduced("X * X = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(reduced("2 * 3 * X = 1"), [-1.0, 6.0])
        self.assertEqual(reduced("X^2 * X^0 * 0.5 = 2"), [-2.0, 0.0, 0.5])
        self.assertEqual(reduced("X^0 * 8 = 2 * X"), [8.0, -2.0])

    def test_signed_coefficients(self):
        self.assertEqual(reduced("-0.5 * X^0 + 3 * -X^1 = 0"), [-0.5, -3.0])
        self.assertEqual(reduced("3 * -x = 1"), [-1.0, -3.0])
        self.assertEqual(reduced("x - -2 = 0"), [2.0, 1.0])

    # Convention mathématique, pas celle de bc : -2^2 vaut -4, bc donne 4.
    def test_numeric_powers(self):
        self.assertEqual(reduced("-2^2 + 3 * x = 0"), [-4.0, 3.0])
        self.assertEqual(reduced("-22^2 = 484 * x"), [-484.0, -484.0])
        self.assertEqual(reduced("3.1^2 * x^2 = 0"), [0.0, 0.0, 9.61])
        self.assertEqual(reduced("2^-3 = x"), [0.125, -1.0])
        # Plus de seuil sur l'exposant : 1^1001 est instantané, donc il est calculé.
        self.assertEqual(reduced("1^1001 = x"), [1.0, -1.0])

    # L'exposant ne porte que sur ce qui le précède immédiatement : 3x^2x vaut 3 * x^2 * x.
    def test_implicit(self):
        self.assertEqual(reduced("3x = 1"), [-1.0, 3.0])
        self.assertEqual(reduced("X3 = 6"), [-6.0, 3.0])
        self.assertEqual(reduced("X.5 = 1"), [-1.0, 0.5])
        self.assertEqual(reduced("XXX = 8"), [-8.0, 0.0, 0.0, 1.0])
        self.assertEqual(reduced("3x^2x = 1"), [-1.0, 0.0, 0.0, 3.0])
        self.assertEqual(reduced("3.1^2x^2 = 0"), [0.0, 0.0, 9.61])

    def test_high_exponents_cancel(self):
        self.assertEqual(reduced("x^20 + x = x^20 + 1"), [-1.0, 1.0])
        self.assertEqual(reduced("x^999999999 = x^999999999"), [])

    def test_any_single_letter(self):
        self.assertEqual(reduced("y^2 = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(reduced("3 * a + 1 = 0"), [1.0, 3.0])
        self.assertEqual(reduced("B^2 = B"), [0.0, -1.0, 1.0])

    def test_unknown_name(self):
        self.assertEqual(parse("3 * b + 1 = 0")[2], "b")
        self.assertEqual(parse("1 = 2")[2], "X")
        _, out, _ = run("-s", "b^2 - 1 = 0")
        self.assertIn("\nReduced form: -1 * b^0 + 0 * b^1 + 1 * b^2 = 0\n", out)
        self.assertIn("  b1 = (-b + rac(delta)) / 2a", out)
        self.assertIn("  (b is the unknown of the equation, not the coefficient b)\n", out)
        self.assertTrue(out.endswith("b1 = 1\nb2 = -1\n"))
        _, out, _ = run("-s", "3 * y = 1")
        self.assertNotIn("not the coefficient", out)
        _, out, _ = run("2 * B = 1")
        self.assertTrue(out.endswith("B = 0.5\n"))

    def test_exact_arithmetic(self):
        self.assertEqual(reduced("0.1 * x + 0.2 * x = 0.3 * x"), [])
        self.assertEqual(reduced("x^2 + 0.1 * x + 0.2 * x = 0.3 * x"), [0.0, 0.0, 1.0])

    def test_close_values_stay_different(self):
        coefficients, degree, _ = parse("x = 1.0000000001 * x")
        self.assertEqual(coeffs_to_array(coefficients, degree), [0, Fraction(-1, 10**10)])
        _, out, _ = run("x^2 + 2 * x + 0.9999999999 = 0")
        self.assertIn("the two solutions are", out)


class Precision(unittest.TestCase):
    # Refusées à la conversion en float, donc au rendu et non au parsing.
    def test_magnitudes_refused(self):
        tiny = "0." + "0" * 317 + "494315"
        for source in (
            "10^400 = x",
            "51 * X * 841 = X * X * 18 * " + tiny,
            tiny + " * X^2 + X + 1 = 0",
        ):
            status, _, err = run(source)
            self.assertEqual(status, 1, source)
            self.assertEqual(err, "computor: number too large\n", source)
        status, _, err = run("0." + "0" * 400 + "1 * X = 1")
        self.assertEqual((status, err), (1, "computor: number too small\n"))

    # La puissance flottante déborde avant de construire un entier gigantesque.
    def test_power_overflow(self):
        with self.assertRaises(OverflowError):
            parse("2^999999999 = x")
        status, _, err = run("2^999999999 = x")
        self.assertEqual(status, 1)
        self.assertEqual(err, "computor: number too large\n")

    def test_power_underflow(self):
        status, _, err = run("0.5^999999999 = x")
        self.assertEqual((status, err), (1, "computor: number too small\n"))
        self.assertEqual(reduced("1^999999999 = x"), [1.0, -1.0])

    # 1e-317 est représentable, même dénormalisé : plus rien ne justifie de le refuser.
    def test_subnormal_is_solved(self):
        _, out, _ = run("0." + "0" * 317 + "494315 = x")
        self.assertIn("x = 4.94315e-318\n", out)

    def test_exact_delta(self):
        for source in ("x^2 + 0.2 * x + 0.01 = 0", "x^2 + 10.3 * x - 10.1 * x + 0.01 = 0"):
            _, out, _ = run("-s", source)
            self.assertIn("Discriminant is zero", out, source)
            self.assertIn("         = (-0.1, 0)\n         is a minimum\n", out, source)

    def test_exact_roots(self):
        # Avec des floats, √36 et 6 s'annulaient mal : x1 valait 1.4803e-16 au lieu de 0.
        _, out, _ = run("-3 * x^2 = -6 * x")
        self.assertTrue(out.endswith("x1 = 0\nx2 = 2\n"))
        _, out, _ = run("9 * x^2 = 4")
        self.assertTrue(out.endswith("x1 = 2/3 ≈ 0.666667\nx2 = -2/3 ≈ -0.666667\n"))

    def test_irrational_roots_precision(self):
        # -b + √Δ avec b ≈ √Δ : x1 valait -49960 au lieu de -1.
        _, out, _ = run("0." + "0" * 19 + "1 * x^2 + x + 1 = 0")
        self.assertTrue(out.endswith("x1 = -1\nx2 = -100000000000000000000\n"))
        # √Δ à 15 décimales fixes valait 0 : 15 chiffres significatifs maintenant.
        _, out, _ = run("x^2 - 0." + "0" * 39 + "2 = 0")
        self.assertTrue(out.endswith("x1 = 1.41421e-20\nx2 = -1.41421e-20\n"))


class Students42(unittest.TestCase):
    """Équations tirées des dépôts computorv1 d'autres étudiants, voir corpus.py."""

    def test_reduced_forms(self):
        for source, expected in EQUATIONS + IMPLICIT:
            self.assertEqual(reduced(source), expected, source)

    def test_old_crashers(self):
        for source, cause in CRASHERS:
            status, out, err = run(source)
            self.assertIn(status, (0, 1), cause)
            self.assertTrue(out or err, cause)

    def test_unsolved_without_reduced_form(self):
        for source, degree in UNSOLVED:
            status, out, err = run(source)
            self.assertEqual((status, err), (0, ""), source)
            self.assertNotIn("Reduced form", out, source)
            self.assertIn("Polynomial degree: %d\n" % degree, out, source)
            self.assertIn("strictly greater than 2", out, source)

    # Le degré 3 garde sa forme réduite, le degré 4 ne l'a plus.
    def test_reduced_form_stops_after_max(self):
        self.assertEqual(MAX_REDUCED_DISP, 3)
        _, out, _ = run("x^3 = 0")
        self.assertIn("Reduced form: 0 * x^0 + 0 * x^1 + 0 * x^2 + 1 * x^3 = 0\n", out)
        _, out, _ = run("x^4 = 0")
        self.assertNotIn("Reduced form", out)
        self.assertIn("Polynomial degree: 4\n", out)


if __name__ == "__main__":
    unittest.main()
