# Author : CLAUDE OPUS 5.5

import io
import os
import pty
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from os.path import abspath, dirname, join

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.cli import main  # noqa: E402
from computorv1.errors import ComputorError  # noqa: E402
from computorv1.format import fmt, fraction, terminates  # noqa: E402
from computorv1.fraction import Fraction, from_decimal, gcd, sqrt  # noqa: E402
from computorv1.parser import parse  # noqa: E402
from computorv1.reduce import MAX_REDUCED_DISP, dense  # noqa: E402
from tests.corpus import CRASHERS, EQUATIONS, REFUSED, UNSOLVED  # noqa: E402


# Coefficients exacts convertis en float, pour comparer aux listes du corpus. Densifie
# sans tenir compte de MAX_REDUCED_DISP : ce que le corpus vérifie est la réduction.
def reduced(source):
    coefficients, degree, _ = parse(source)
    return [float(c) for c in dense(coefficients, degree)]


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = main(list(argv))
    return status, out.getvalue(), err.getvalue()


class Subject(unittest.TestCase):
    def check(self, source, expected):
        status, out, err = run(source)
        results = [line for line in out.splitlines(True) if not line.startswith("  ")]
        self.assertEqual((status, "".join(results), err), (0, expected, ""))

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


class FreeForm(unittest.TestCase):
    def test_subject_bonus(self):
        self.assertEqual(reduced("5 + 4 * X + X^2= X^2"), [5.0, 4.0])

    def test_normalizations(self):
        self.assertEqual(reduced("3x = 1"), [-1.0, 3.0])
        self.assertEqual(reduced("X^0 * 8 = 2X"), [8.0, -2.0])
        self.assertEqual(reduced("x - - 2 = 0"), [2.0, 1.0])
        self.assertEqual(reduced("-x^2 = 4"), [-4.0, 0.0, -1.0])
        self.assertEqual(reduced("9.3X^10 = 0.5"), [-0.5] + [0.0] * 9 + [9.3])
        self.assertEqual(reduced(".5 = 5.X"), [0.5, -5.0])

    def test_products(self):
        self.assertEqual(reduced("X * X = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(reduced("2 * 3 * X = 1"), [-1.0, 6.0])
        self.assertEqual(reduced("X^2 * X^0 * 0.5 = 2"), [-2.0, 0.0, 0.5])
        self.assertEqual(reduced("3x^2x = 1"), [-1.0, 0.0, 0.0, 3.0])
        self.assertEqual(reduced("XXX = 8"), [-8.0, 0.0, 0.0, 1.0])
        self.assertEqual(reduced("X^1X^1 = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(reduced("X3 = 6"), [-6.0, 3.0])
        self.assertEqual(reduced("X.5 = 1"), [-1.0, 0.5])

    def test_signed_coefficients(self):
        self.assertEqual(reduced("-0.5 * X^0 + -3 * X^1 = 0"), [-0.5, -3.0])
        self.assertEqual(reduced("X = - -2"), [-2.0, 1.0])

    def test_high_exponents_cancel(self):
        self.assertEqual(reduced("x^20 + x = x^20 + 1"), [-1.0, 1.0])
        self.assertEqual(reduced("x^999999999 = x^999999999"), [])

    def test_case(self):
        with self.assertRaises(ComputorError):
            parse("x^2 = X")

    def test_any_single_letter(self):
        self.assertEqual(reduced("y^2 = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(reduced("3a + 1 = 0"), [1.0, 3.0])
        self.assertEqual(reduced("B^2 = B"), [0.0, -1.0, 1.0])

    def test_unknown_name(self):
        self.assertEqual(parse("3b + 1 = 0")[2], "b")
        self.assertEqual(parse("1 = 2")[2], "X")
        _, out, _ = run("b^2 - 1 = 0")
        self.assertTrue(out.startswith("Reduced form: -1 * b^0 + 0 * b^1 + 1 * b^2 = 0\n"))
        self.assertIn("  b1 = (-b + √Δ) / 2a", out)
        note = "(b is the unknown of the equation, not the coefficient b)\n"
        self.assertTrue(out.endswith("b1 = 1\nb2 = -1\n" + note))
        _, out, _ = run("3y = 1")
        self.assertNotIn("not the coefficient", out)
        _, out, _ = run("2B = 1")
        self.assertTrue(out.endswith("B = 0.5\n"))

    def test_numeric_powers(self):
        self.assertEqual(reduced("-2^2 + 3x = 0"), [-4.0, 3.0])
        self.assertEqual(reduced("-22^2 = 484x"), [-484.0, -484.0])
        self.assertEqual(reduced("3.1^2x^2 = 0"), [0.0, 0.0, 9.61])
        self.assertEqual(reduced("-2^-3 + 3x + 2x = 0"), [-0.125, 5.0])
        with self.assertRaises(ComputorError):
            parse("2^0.5 = x")
        with self.assertRaises(ZeroDivisionError):
            parse("0^-1 = 1")
        # Plus de seuil sur l'exposant : 1^1001 est instantané, donc il est calculé.
        self.assertEqual(reduced("1^1001 = x"), [1.0, -1.0])

    # Refusées à la conversion en float, donc au rendu et non au parsing.
    def test_magnitudes_refused(self):
        for source in ("10^400 = x", "51X841 = X*X18*99⁻¹59", "99^-159 * X^2 + X + 1 = 0"):
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
        status, _, err = run("2^-999999999 = x")
        self.assertEqual((status, err), (1, "computor: number too small\n"))
        self.assertEqual(reduced("1^999999999 = x"), [1.0, -1.0])

    # 1e-317 est représentable, même dénormalisé : plus rien ne justifie de le refuser.
    def test_subnormal_is_solved(self):
        _, out, _ = run("99^-159 = x")
        self.assertIn("x = 4.94315e-318\n", out)

    def test_chained_exponents_refused(self):
        for source in ("x^2^3 = 0", "2^3^2 = x", "9^9^9 = x", "x²^3 = 1"):
            with self.assertRaises(ComputorError, msg=source):
                parse(source)

    def test_unicode_exponents(self):
        self.assertEqual(reduced("3x² + 4x + 4 = 8"), [-4.0, 4.0, 3.0])
        self.assertEqual(reduced("2y³ = 16"), [-16.0, 0.0, 0.0, 2.0])
        self.assertEqual(reduced("X¹⁰ = 1"), [-1.0] + [0.0] * 9 + [1.0])
        self.assertEqual(reduced("X⁰ = 1"), [])
        self.assertEqual(reduced("x^2 = x²"), [])
        self.assertEqual(reduced("x⁻¹ = x⁻¹"), [])
        self.assertEqual(reduced("x⁺² = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(reduced("3²x = 9"), [-9.0, 9.0])

    def test_negative_exponent_must_cancel(self):
        self.assertEqual(reduced("x^-1 = x^-1"), [])
        self.assertEqual(reduced("x^-1 + 1 = x^-1"), [1.0])
        with self.assertRaises(ComputorError):
            parse("1 * X^-1 + 1 * X^0 = 0")

    def test_exact_arithmetic(self):
        self.assertEqual(reduced("0.1 * x + 0.2 * x = 0.3 * x"), [])
        self.assertEqual(reduced("x^2 + 0.1 * x + 0.2 * x = 0.3 * x"), [0.0, 0.0, 1.0])

    def test_close_values_stay_different(self):
        coefficients, degree, _ = parse("x = 1.0000000001 * x")
        self.assertEqual(dense(coefficients, degree), [0, Fraction(-1, 10**10)])
        _, out, _ = run("x^2 + 2x + 0.9999999999 = 0")
        self.assertIn("the two solutions are", out)

    def test_exact_delta(self):
        for source in ("x^2 + 0.2x + 0.01 = 0", "x^2 + 10.3x - 10.1x + 0.01 = 0"):
            _, out, _ = run(source)
            self.assertIn("Discriminant is zero", out, source)
            self.assertIn(" = 0\n  vertex = (-b / 2a, -Δ / 4a) = (-0.1, 0), minimum\n", out)

    def test_exact_roots(self):
        # Avec des floats, √36 et 6 s'annulaient mal : x1 valait 1.4803e-16 au lieu de 0.
        _, out, _ = run("-3x^2 = -6x")
        self.assertTrue(out.endswith("x1 = 0\nx2 = 2\n"))
        _, out, _ = run("9x^2 = 4")
        self.assertTrue(out.endswith("x1 = 2/3 ≈ 0.666667\nx2 = -2/3 ≈ -0.666667\n"))

    def test_irrational_roots_precision(self):
        # -b + √Δ avec b ≈ √Δ : x1 valait -49960 au lieu de -1.
        _, out, _ = run("10^-20 x^2 + x + 1 = 0")
        self.assertTrue(out.endswith("x1 = -1\nx2 = -100000000000000000000\n"))
        # √Δ à 15 décimales fixes valait 0 : 15 chiffres significatifs maintenant.
        _, out, _ = run("x^2 - 2*10^-40 = 0")
        self.assertTrue(out.endswith("x1 = 1.41421e-20\nx2 = -1.41421e-20\n"))


class Students42(unittest.TestCase):
    """Équations tirées des dépôts computorv1 d'autres étudiants, voir corpus.py."""

    def test_reduced_forms(self):
        for source, expected in EQUATIONS:
            self.assertEqual(reduced(source), expected, source)

    def test_old_crashers(self):
        for source, cause in CRASHERS:
            status, out, err = run(source)
            self.assertIn(status, (0, 1), cause)
            self.assertTrue(out or err, cause)

    def test_refused_without_crash(self):
        for source, message in REFUSED:
            status, out, err = run(source)
            self.assertEqual((status, out), (1, ""), source)
            self.assertTrue(err.startswith("computor: " + message), (source, err))

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


class Errors(unittest.TestCase):
    # Un refus doit lever ComputorError, pas une autre exception : un TypeError ici sort
    # en « internal error » et 70 au lieu du message.
    def test_refused_by_the_parser(self):
        sources = (
            "x % 2 = 0",
            "x + y = 0",
            "x^0.5 = 2",
            "2 3 = X",
            "X^1 0 = 1",
            "5 * X^0",
            "x = 1 = 2",
            "= x",
            "x =   ",
            "x^-1 = 0",
            "x^1.5 = 0",
            "x + = 0",
            "3 * * X = 1",
            "3 * = X",
            "+ * X = 1",
            "* X = 1",
        )
        for source in sources:
            with self.assertRaises(ComputorError, msg=source):
                parse(source)

    def test_no_equation(self):
        sys.stdin, stdin = io.StringIO("\n  \n"), sys.stdin
        try:
            status, out, err = run()
        finally:
            sys.stdin = stdin
        self.assertEqual((status, out, err), (1, "", "computor: no equation\n"))

    def test_empty_argument(self):
        status, out, err = run("")
        self.assertEqual((status, out), (1, ""))
        self.assertIn("expected one '='", err)

    def test_report(self):
        status, _, err = run("x % 2 = 0")
        self.assertEqual(status, 1)
        self.assertEqual(err, "computor: unexpected character '%'\n")
        _, _, err = run("x = 1 = 2")
        self.assertEqual(err, "computor: expected one '=' between two sides\n")


class Extras(unittest.TestCase):
    def test_steps(self):
        _, out, _ = run("x^2 - x - 6 = 0")
        self.assertIn("  Δ = b² - 4ac = (-1)² - 4 * 1 * (-6) = 25\n", out)
        self.assertIn("  x1 = (-b + √Δ) / 2a = (1 + √25) / 2 = 3\n", out)
        self.assertIn("  vertex = (-b / 2a, -Δ / 4a) = (0.5, -6.25), minimum\n", out)
        _, out, _ = run("-x^2 + 1 = 0")
        self.assertIn("(0, 1), maximum\n", out)

    def test_stdin(self):
        sys.stdin, stdin = io.StringIO("x = 1\n\n2 * x = 1\n"), sys.stdin
        try:
            _, out, _ = run()
        finally:
            sys.stdin = stdin
        self.assertEqual(out.count("The solution is:"), 2)


class EntryPoint(unittest.TestCase):
    def test_internal_error_is_caught(self):
        root = dirname(dirname(abspath(__file__)))
        with tempfile.TemporaryDirectory() as copy:
            shutil.copy(join(root, "computor"), copy)
            shutil.copytree(join(root, "computorv1"), join(copy, "computorv1"))
            solver = join(copy, "computorv1", "solver.py")
            source = open(solver).read()
            header = "def solve(p, degree):"
            open(solver, "w").write(
                source.replace(header, header + "\n    raise RuntimeError('boum')", 1)
            )
            result = subprocess.run(
                [join(copy, "computor"), "x = 1"], capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 70)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("internal error: RuntimeError: boum", result.stderr)


class Colors(unittest.TestCase):
    def test_no_colors_when_piped(self):
        _, out, _ = run("5 * X^0 + 4 * X^1 = 0")
        self.assertNotIn("\033", out)

    def test_colors_on_a_terminal(self):
        script = (
            "import sys; sys.path.insert(0, %r); "
            "from computorv1.display import colorize; print(colorize('4 * X^0 - 1 * X^1'))"
        )
        root = dirname(dirname(abspath(__file__)))
        primary, secondary = pty.openpty()
        result = subprocess.run(
            [sys.executable, "-c", script % root],
            stdout=secondary,
            stderr=subprocess.PIPE,
            text=True,
        )
        os.close(secondary)
        printed = os.read(primary, 4096).decode()
        os.close(primary)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("\033[32m*\033[0m", printed)
        self.assertIn("\033[36m^0\033[0m", printed)
        self.assertIn("\033[33m-\033[0m", printed)


class Streams(unittest.TestCase):
    def test_broken_pipe(self):
        class Closed(io.StringIO):
            def write(self, text):
                raise BrokenPipeError(32, "Broken pipe")

        out, stdout = Closed(), sys.stdout
        try:
            sys.stdout = out
            self.assertEqual(main(["x = 1"]), 120)
        finally:
            sys.stdout = stdout

    def test_stdin_bad_bytes(self):
        stdin = sys.stdin
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"\xff = x\nx = 1\n"))
            status, out, err = run()
        finally:
            sys.stdin = stdin
        self.assertEqual(status, 1)
        self.assertIn("The solution is:", out)


class Number(unittest.TestCase):
    def test_sqrt(self):
        self.assertEqual(fmt(sqrt(Fraction(2))), "1.414214")
        self.assertEqual(sqrt(Fraction(1, 4)), Fraction(1, 2))
        self.assertEqual(sqrt(Fraction(10**20)), Fraction(10**10))
        self.assertIsInstance(sqrt(Fraction(9, 2)), float)

    def test_fraction(self):
        self.assertEqual(fraction(from_decimal("0.2") * -1), (-1, 5))
        self.assertEqual(fraction(Fraction(1, 3)), (1, 3))
        self.assertIsNone(fraction(Fraction(1, 10001)))
        self.assertIsNone(fraction(sqrt(Fraction(2))))
        self.assertTrue(terminates(40))
        self.assertFalse(terminates(12))

    def test_exact(self):
        self.assertEqual(from_decimal("0.1") + from_decimal("0.2"), from_decimal("0.3"))
        self.assertEqual(from_decimal("9.3"), Fraction(93, 10))
        self.assertEqual(from_decimal("12"), Fraction(12))
        self.assertEqual(Fraction(1, 3) * 3, 1)
        self.assertEqual(Fraction(2) ** -3, Fraction(1, 8))
        self.assertEqual(Fraction(6, -4), Fraction(-3, 2))
        self.assertEqual(1 - Fraction(1, 3), Fraction(2, 3))
        self.assertTrue(Fraction(-1, 3) < 0 < Fraction(1, 10**100))
        self.assertIsInstance(Fraction(1, 2) + 0.5, float)

    def test_gcd(self):
        self.assertEqual(gcd(1071, 462), 21)
        self.assertEqual(gcd(6, -4), 2)
        self.assertEqual(gcd(0, 5), 5)

    def test_fmt(self):
        self.assertEqual(fmt(4.0), "4")
        self.assertEqual(fmt(-0.0000001), "-1e-07")
        self.assertEqual(fmt(0.0), "0")
        self.assertEqual(fmt(2 / 3), "0.666667")


if __name__ == "__main__":
    unittest.main()
