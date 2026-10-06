import math

DIGITS = 15


def gcd(a, b):
    while b != 0:
        t = b
        b = a % b
        a = t
    return abs(a)


def from_decimal(text: str) -> "Fraction":
    ipart, _, frac = text.partition(".")
    return Fraction(int(ipart + frac), 10 ** len(frac))


def to_fraction(x: float) -> "Fraction":
    if isinstance(x, Fraction):
        return x
    return Fraction(x)


# Nombre rationnel exact a/b, a et b entiers.
class Fraction:
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ZeroDivisionError("division by zero")
        g = gcd(numerator, denominator)
        if denominator < 0:
            g = -g
        self.numerator = numerator // g
        self.denominator = denominator // g

    def __repr__(self) -> str:
        return f"Fraction({self.numerator}, {self.denominator})"

    def __add__(a, b):
        if isinstance(b, float):
            return float(a) + b
        b = to_fraction(b)
        return Fraction(
            a.numerator * b.denominator + b.numerator * a.denominator,
            a.denominator * b.denominator,
        )

    __radd__ = __add__

    def __sub__(a, b):
        if isinstance(b, float):
            return float(a) - b
        b = to_fraction(b)
        return Fraction(
            a.numerator * b.denominator - b.numerator * a.denominator,
            a.denominator * b.denominator,
        )

    # x - Fraction(y, z) => a = Fraction(y, z) et b = x.
    def __rsub__(a, b):
        return -a + b

    def __mul__(a, b):
        if isinstance(b, float):
            return float(a) * b
        b = to_fraction(b)
        return Fraction(a.numerator * b.numerator, a.denominator * b.denominator)

    __rmul__ = __mul__

    def __truediv__(a, b):
        if isinstance(b, float):
            return float(a) / b
        b = to_fraction(b)
        return Fraction(a.numerator * b.denominator, a.denominator * b.numerator)

    def __rtruediv__(a, b):
        if isinstance(b, float):
            return b / float(a)
        return to_fraction(b) / a

    # math.pow ne sert qu'à lever OverflowError avant de calculer un entier géant ;
    # le résultat est exact : 3.1^2 = 961/100 et non 9.610000000000001.
    def __pow__(a, n):
        base = 1 / a if n < 0 else a
        value = math.pow(base, abs(n))
        if value == 0.0 and base != 0:
            raise ValueError("number too small")
        return Fraction(base.numerator ** abs(n), base.denominator ** abs(n))

    def __neg__(a):
        return Fraction(-a.numerator, a.denominator)

    def __abs__(a):
        return -a if a < 0 else a

    def __eq__(a, b):
        b = to_fraction(b)
        return a.numerator == b.numerator and a.denominator == b.denominator

    # Dénominateurs positifs : a/b < c/d si et seulement si ad < bc.
    def __lt__(a, b):
        b = to_fraction(b)
        return a.numerator * b.denominator < b.numerator * a.denominator

    def __gt__(a, b):
        return to_fraction(b) < a

    def __float__(self):
        value = int(self.numerator) / int(self.denominator)
        if value == 0.0 and self.numerator != 0:
            raise ValueError("number too small")
        return value


def isqrt(y):
    L = 0
    R = y + 1

    while L != R - 1:
        M = (L + R) // 2
        if M * M <= y:
            L = M
        else:
            R = M

    return L


def sqrt(y):
    n = y.numerator * y.denominator
    root = isqrt(n)
    if root * root == n:
        return Fraction(root, y.denominator)
    return isqrt(n * 100**DIGITS) / (y.denominator * 10**DIGITS)
