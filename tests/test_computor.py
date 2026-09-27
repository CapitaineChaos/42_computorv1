import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from os.path import abspath, dirname, join

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.cli import main  # noqa: E402
from computorv1.number import fmt, fraction, sqrt, terminates  # noqa: E402
from computorv1.parser import ComputorError, parse  # noqa: E402
from tests.corpus import CRASHERS, EQUATIONS, REFUSED  # noqa: E402


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
            "-0.475131\n0.905239\n",
        )

    def test_linear(self):
        self.check(
            "5 * X^0 + 4 * X^1 = 4 * X^0",
            "Reduced form: 1 * X^0 + 4 * X^1 = 0\nPolynomial degree: 1\nThe solution is:\n-0.25\n",
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
            "-1/5 + 2i/5\n-1/5 - 2i/5\n",
        )

    def test_fractions(self):
        _, out, _ = run("3 * x = 1")
        self.assertTrue(out.endswith("The solution is:\n1/3 ≈ 0.333333\n"))
        _, out, _ = run("x^2 + x + 1 = 0")
        self.assertTrue(out.endswith("-1/2 + 0.866025i\n-1/2 - 0.866025i\n"))
        _, out, _ = run("x^2 + 1 = 0")
        self.assertTrue(out.endswith("0 + i\n0 - i\n"))

    def test_double(self):
        _, out, _ = run("x^2 - 2 * x + 1 = 0")
        self.assertTrue(out.endswith("Discriminant is zero, the solution is:\n1\n"))


class FreeForm(unittest.TestCase):
    def test_subject_bonus(self):
        self.assertEqual(parse("5 + 4 * X + X^2= X^2"), [5.0, 4.0])

    def test_normalizations(self):
        self.assertEqual(parse("3x = 1"), [-1.0, 3.0])
        self.assertEqual(parse("X^0 * 8 = 2X"), [8.0, -2.0])
        self.assertEqual(parse("x - - 2 = 0"), [2.0, 1.0])
        self.assertEqual(parse("-x^2 = 4"), [-4.0, 0.0, -1.0])
        self.assertEqual(parse("9.3X^10 = 0.5"), [-0.5] + [0.0] * 9 + [9.3])
        self.assertEqual(parse(".5 = 5.X"), [0.5, -5.0])

    def test_products(self):
        self.assertEqual(parse("X * X = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(parse("2 * 3 * X = 1"), [-1.0, 6.0])
        self.assertEqual(parse("X^2 * X^0 * 0.5 = 2"), [-2.0, 0.0, 0.5])
        self.assertEqual(parse("3x^2x = 1"), [-1.0, 0.0, 0.0, 3.0])
        self.assertEqual(parse("XXX = 8"), [-8.0, 0.0, 0.0, 1.0])
        self.assertEqual(parse("X^1X^1 = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(parse("X3 = 6"), [-6.0, 3.0])
        self.assertEqual(parse("X.5 = 1"), [-1.0, 0.5])

    def test_signed_coefficients(self):
        self.assertEqual(parse("-0.5 * X^0 + -3 * X^1 = 0"), [-0.5, -3.0])
        self.assertEqual(parse("X = - -2"), [-2.0, 1.0])

    def test_high_exponents_cancel(self):
        self.assertEqual(parse("x^20 + x = x^20 + 1"), [-1.0, 1.0])
        self.assertEqual(parse("x^999999999 = x^999999999"), [])

    def test_case(self):
        self.assertEqual(parse("x^2 = X"), [0.0, -1.0, 1.0])

    def test_any_single_letter(self):
        self.assertEqual(parse("y^2 = 4"), [-4.0, 0.0, 1.0])
        self.assertEqual(parse("3a + 1 = 0"), [1.0, 3.0])
        self.assertEqual(parse("B^2 = B"), [0.0, -1.0, 1.0])

    def test_numeric_powers(self):
        self.assertEqual(parse("-2^2 + 3x = 0"), [-4.0, 3.0])
        self.assertEqual(parse("-22^2 = 484x"), [-484.0, -484.0])
        self.assertEqual(parse("3.1^2x^2 = 0"), [0.0, 0.0, 3.1**2])
        self.assertEqual(parse("-2^-3 + 3x + 2x = 0"), [-0.125, 5.0])
        for source in ("2^0.5 = x", "0^-1 = 1", "10^400 = x"):
            with self.assertRaises(ComputorError, msg=source):
                parse(source)

    def test_magnitudes_refused(self):
        for source in ("10^400 = x", "99^-159 = x", "51X841 = X*X18*99⁻¹59"):
            with self.assertRaises(ComputorError, msg=source):
                parse(source)

    def test_chained_exponents_refused(self):
        for source in ("x^2^3 = 0", "2^3^2 = x", "9^9^9 = x", "x²^3 = 1"):
            with self.assertRaises(ComputorError, msg=source):
                parse(source)

    def test_unicode_exponents(self):
        self.assertEqual(parse("3x² + 4x + 4 = 8"), [-4.0, 4.0, 3.0])
        self.assertEqual(parse("2y³ = 16"), [-16.0, 0.0, 0.0, 2.0])
        self.assertEqual(parse("X¹⁰ = 1"), [-1.0] + [0.0] * 9 + [1.0])
        self.assertEqual(parse("X⁰ = 1"), [])
        self.assertEqual(parse("x^2 = x²"), [])
        self.assertEqual(parse("x⁻¹ = x⁻¹"), [])
        self.assertEqual(parse("3²x = 9"), [-9.0, 9.0])

    def test_negative_exponent_must_cancel(self):
        self.assertEqual(parse("x^-1 = x^-1"), [])
        self.assertEqual(parse("x^-1 + 1 = x^-1"), [1.0])
        with self.assertRaises(ComputorError):
            parse("1 * X^-1 + 1 * X^0 = 0")

    def test_float_noise_cancels(self):
        self.assertEqual(parse("0.1 * x + 0.2 * x = 0.3 * x"), [])
        self.assertEqual(parse("x^2 + 0.1 * x + 0.2 * x = 0.3 * x"), [0.0, 0.0, 1.0])


class Students42(unittest.TestCase):
    """Équations tirées des dépôts computorv1 d'autres étudiants, voir corpus.py."""

    def test_reduced_forms(self):
        for source, expected in EQUATIONS:
            self.assertEqual(parse(source), expected, source)

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


class Errors(unittest.TestCase):
    def error(self, source):
        with self.assertRaises(ComputorError) as caught:
            parse(source)
        return caught.exception.text, caught.exception.position

    def test_positions(self):
        self.assertEqual(self.error("x % 2 = 0"), (None, 2))
        self.assertEqual(self.error("x + y = 0"), (None, 4))
        self.assertEqual(self.error("x^0.5 = 2"), (None, 1))
        self.assertEqual(self.error("2 3 = X"), (None, 1))
        self.assertEqual(self.error("X^1 0 = 1"), (None, 3))
        self.assertEqual(self.error("5 * X^0"), (None, 7))
        self.assertEqual(self.error("x = 1 = 2"), (None, 6))
        self.assertEqual(self.error("= x"), (None, 0))
        self.assertEqual(self.error("x =   "), (None, 2))
        self.assertEqual(self.error("x^-1 = 0"), (None, None))
        self.assertEqual(self.error("x^1.5 = 0"), (None, 1))
        self.assertEqual(self.error("x + = 0"), ("+", 1))
        self.assertEqual(self.error("3 * * X = 1"), ("+3**X^1", 3))
        self.assertEqual(self.error("3 * = X"), ("+3*", 3))
        self.assertEqual(self.error("+ * X = 1"), ("+*X^1", 1))
        self.assertEqual(self.error("* X = 1"), ("*X^1", 0))
        self.assertEqual(self.error("1 + 2 * x^11 = 0"), (None, None))

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
        status, out, err = run("x % 2 = 0")
        self.assertEqual((status, out), (1, ""))
        self.assertEqual(err, "computor: unexpected character '%'\n    x % 2 = 0\n      ^\n")
        _, _, err = run("1 + 2 * x^11 = 0")
        self.assertEqual(err, "computor: reduced degree 11 greater than 10\n")
        _, _, err = run("x = 1 = 2")
        self.assertEqual(
            err,
            "computor: expected one '=' between two sides\n    x = 1 = 2\n          ^\n",
        )


class Extras(unittest.TestCase):
    def test_steps(self):
        _, out, _ = run("x^2 - x - 6 = 0")
        self.assertIn("  Δ = b² - 4ac = (-1)² - 4 * 1 * (-6) = 25\n", out)
        self.assertIn("  x1 = (-b + √Δ) / 2a = (1 + √25) / 2 = 3\n", out)
        self.assertIn("  vertex = (-b / 2a, c - b² / 4a) = (0.5, -6.25), minimum\n", out)
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
            open(solver, "w").write(
                source.replace("def solve(p):", "def solve(p):\n    raise RuntimeError('boum')", 1)
            )
            result = subprocess.run(
                [join(copy, "computor"), "x = 1"], capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 70)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("internal error: RuntimeError: boum", result.stderr)


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
        self.assertEqual(fmt(sqrt(2)), "1.414214")
        self.assertEqual(sqrt(0.25), 0.5)
        self.assertEqual(sqrt(1e20), 1e10)

    def test_fraction(self):
        self.assertEqual(fraction(-0.2), (-1, 5))
        self.assertEqual(fraction(1 / 3), (1, 3))
        self.assertEqual(fraction(3.0), (3, 1))
        self.assertIsNone(fraction(sqrt(2)))
        self.assertTrue(terminates(40))
        self.assertFalse(terminates(12))

    def test_fmt(self):
        self.assertEqual(fmt(4.0), "4")
        self.assertEqual(fmt(-0.0000001), "-1e-07")
        self.assertEqual(fmt(0.0), "0")
        self.assertEqual(fmt(2 / 3), "0.666667")


if __name__ == "__main__":
    unittest.main()
