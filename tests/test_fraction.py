# Author : CLAUDE OPUS 5.5

# Arithmétique exacte et mise en forme des nombres, sans passer par une équation.

import sys
import unittest
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.format import fmt, fraction, terminates  # noqa: E402
from computorv1.fraction import Fraction, from_decimal, gcd, sqrt  # noqa: E402


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
