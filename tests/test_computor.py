import io
import subprocess
import sys
import unittest
from os.path import abspath, dirname, join

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.cli import main  # noqa: E402
from computorv1.parser import ComputorError, parse, sub  # noqa: E402
from computorv1.rational import Rational, isqrt, square_free  # noqa: E402
from computorv1.solver import solve  # noqa: E402

BINARY = join(dirname(dirname(abspath(__file__))), "computor")


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    status = main(list(argv), out, err)
    return status, out.getvalue(), err.getvalue()


def reduce_(source):
    left, right, variable = parse(source)
    return sub(left, right), variable


def roots(source):
    poly, variable = reduce_(source)
    return [(root.exact(), root.decimal(6)) for root in solve(poly, variable).roots]


class Arithmetic(unittest.TestCase):
    def test_rational_is_irreducible(self):
        self.assertEqual(Rational(4, 8), Rational(1, 2))
        self.assertEqual(Rational(1, -2), Rational(-1, 2))
        self.assertEqual(Rational.parse("9.3"), Rational(93, 10))
        with self.assertRaises(ZeroDivisionError):
            Rational(1, 0)

    def test_operators(self):
        half = Rational(1, 2)
        self.assertEqual(half + Rational(1, 3), Rational(5, 6))
        self.assertEqual(half - Rational(1, 3), Rational(1, 6))
        self.assertEqual(4 * half, Rational(2))
        self.assertEqual(half / Rational(1, 4), Rational(2))
        self.assertEqual(-half, Rational(-1, 2))

    def test_decimal_rounding(self):
        self.assertEqual(Rational(2, 3).decimal(6), "0.666667")
        self.assertEqual(Rational(-1, 4).decimal(6), "-0.25")
        self.assertEqual(Rational(3).decimal(6), "3")
        self.assertEqual(Rational(1, 3).text(6), "1/3")
        self.assertEqual(Rational(1, 4).text(6), "0.25")

    def test_square_root(self):
        self.assertEqual(Rational(2).sqrt(6).decimal(6), "1.414214")
        self.assertEqual(isqrt(10**20), 10**10)
        self.assertEqual(square_free(4120), (2, 1030))


class Parsing(unittest.TestCase):
    def test_free_form(self):
        self.assertEqual(reduce_("5 + 4 * X + X^2= X^2")[0], reduce_("5 + 4X = 0")[0])
        self.assertEqual(reduce_("(x + 2)(x - 3) = 0")[0], reduce_("x^2 - x - 6 = 0")[0])
        self.assertEqual(reduce_("2(x + 1) = 0")[0], reduce_("2x + 2 = 0")[0])
        self.assertEqual(reduce_("(x + 1)^2 = 0")[0], reduce_("x^2 + 2x + 1 = 0")[0])
        self.assertEqual(reduce_("--x = 1")[0], reduce_("x - 1 = 0")[0])

    def test_coefficients_stay_exact(self):
        poly, _ = reduce_("x / 3 = 0")
        self.assertEqual(poly[1], Rational(1, 3))

    def test_variable_name(self):
        self.assertEqual(reduce_("y + 1 = 0")[1], "Y")
        self.assertEqual(reduce_("42 = 42")[1], "X")

    def test_rejected_inputs(self):
        for source in (
            "x + = 1",
            "x = ",
            "(x + 1 = 0",
            "x + 1",
            "5 = 5 = 5",
            "x^2^3 = 0",
            "x^-1 = 0",
            "1 / x = 0",
            "x + y = 0",
            "x^2.5 = 0",
            "x / 0 = 1",
            "x % 2 = 0",
            "foo = 1",
            "x^2000 = 0",
            "",
        ):
            with self.assertRaises(ComputorError, msg=source):
                parse(source)

    def test_error_points_at_the_fault(self):
        with self.assertRaises(ComputorError) as caught:
            parse("x % 2 = 0")
        self.assertEqual(caught.exception.position, 2)


class Solving(unittest.TestCase):
    def test_subject_order_and_values(self):
        self.assertEqual(
            [decimal for _, decimal in roots("5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0")],
            ["0.905239", "-0.475131"],
        )

    def test_exact_roots(self):
        self.assertEqual([exact for exact, _ in roots("x^2 - 2 = 0")], ["√2", "-√2"])
        self.assertEqual(
            [exact for exact, _ in roots("x^2 - x - 1 = 0")], ["(1 + √5) / 2", "(1 - √5) / 2"]
        )
        self.assertEqual([exact for exact, _ in roots("3x^2 - 7x + 2 = 0")], ["2", "1/3"])

    def test_complex_roots(self):
        self.assertEqual(
            [exact for exact, _ in roots("1 + 2x + 5x^2 = 0")], ["-1/5 + 2i/5", "-1/5 - 2i/5"]
        )
        self.assertEqual([exact for exact, _ in roots("x^2 + 1 = 0")], ["i", "-i"])

    def test_double_root(self):
        self.assertEqual(roots("x^2 + 6x + 9 = 0"), [("-3", "-3")])

    def test_degenerate_cases(self):
        self.assertEqual(solve(*reduce_("6 = 6")).kind, "identity")
        self.assertEqual(solve(*reduce_("10 = 15")).kind, "impossible")
        self.assertEqual(solve(*reduce_("x^3 = 1")).degree, 3)


class CommandLine(unittest.TestCase):
    def check(self, equation, expected):
        status, out, err = run(equation)
        self.assertEqual(status, 0, err)
        self.assertEqual(out, expected)

    def test_subject_examples(self):
        self.check(
            "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0",
            "Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly positive, the two solutions are:\n"
            "0.905239\n-0.475131\n",
        )
        self.check(
            "5 * X^0 + 4 * X^1 = 4 * X^0",
            "Reduced form: 1 * X^0 + 4 * X^1 = 0\nPolynomial degree: 1\nThe solution is:\n-0.25\n",
        )
        self.check(
            "8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0",
            "Reduced form: 5 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 0\n"
            "Polynomial degree: 3\n"
            "The polynomial degree is strictly greater than 2, I can't solve.\n",
        )
        self.check(
            "6 * X^0 = 6 * X^0", "Reduced form: 0 * X^0 = 0\nAny real number is a solution.\n"
        )
        self.check("10 * X^0 = 15 * X^0", "Reduced form: -5 * X^0 = 0\nNo solution.\n")
        self.check(
            "1 * X^0 + 2 * X^1 + 5 * X^2 = 0",
            "Reduced form: 1 * X^0 + 2 * X^1 + 5 * X^2 = 0\n"
            "Polynomial degree: 2\n"
            "Discriminant is strictly negative, the two complex solutions are:\n"
            "-1/5 + 2i/5\n-1/5 - 2i/5\n",
        )

    def test_options(self):
        _, out, _ = run("-e", "x^2 - 2 = 0")
        self.assertIn("√2 ~ 1.414214", out)
        _, out, _ = run("-e", "2x + 1 = 0")
        self.assertTrue(out.endswith("-0.5\n"))
        _, out, _ = run("-s", "x^2 - 2 = 0")
        self.assertIn("delta = b^2 - 4ac", out)
        _, out, _ = run("-p", "2", "x^2 - 2 = 0")
        self.assertIn("1.41\n", out)
        _, out, _ = run("--help")
        self.assertIn("usage: computor", out)

    def test_equation_may_start_with_a_minus(self):
        status, out, _ = run("-x^2 = -4")
        self.assertEqual(status, 0)
        self.assertIn("Polynomial degree: 2", out)

    def test_equation_split_over_arguments(self):
        _, out, _ = run("5", "+", "4", "*", "X", "=", "0")
        self.assertIn("Reduced form: 5 * X^0 + 4 * X^1 = 0", out)

    def test_error_report(self):
        status, out, err = run("x % 2 = 0")
        self.assertEqual((status, out), (1, ""))
        self.assertEqual(err, "computor: unexpected character '%'\n    x % 2 = 0\n      ^\n")

    def test_bad_usage(self):
        status, _, err = run("-p", "nope", "x = 0")
        self.assertEqual(status, 2)
        self.assertIn("precision must be an integer", err)

    def test_stdin(self):
        result = subprocess.run(
            [sys.executable, BINARY],
            input="x + 1 = 0\n\nx^2 = 4\n",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Reduced form:"), 2)


if __name__ == "__main__":
    unittest.main()
