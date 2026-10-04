from math import isinf

from .fraction import Fraction

MAX_DENOMINATOR = 10000


def fmt(x):
    f = float(x)
    if isinf(f):
        raise OverflowError
    if f != 0.0 and abs(f) < 1e-6:
        return f"{f:g}"
    text = ("%.6f" % f).rstrip("0").rstrip(".")
    return "0" if text == "-0" else text



def fraction(x):
    if not isinstance(x, Fraction) or x.denominator > MAX_DENOMINATOR:
        return None
    return x.numerator, x.denominator


# https://en.wikipedia.org/w/index.php?title=Repeating_decimal&oldid=1375973380#Every_rational_number_is_either_a_terminating_or_repeating_decimal
def terminates(q):
    for prime in (2, 5):
        while q % prime == 0:
            q //= prime
    return q == 1


def real(x):
    f = fraction(x)
    if f and not terminates(f[1]):
        return f"{f[0]}/{f[1]} ≈ {fmt(x)}"
    return fmt(x)


# Nombre négatif entre parenthèses, dans une formule : 4 * (-9.3) * 4.
def wrap(x):
    return f"({real(x)})" if x < 0 else real(x)


def ratio(x):
    f = fraction(x)
    if not f:
        return fmt(x)
    return str(f[0]) if f[1] == 1 else f"{f[0]}/{f[1]}"


def imaginary(y):
    f = fraction(y)
    if not f:
        return fmt(y) + "i"
    p, q = f
    return ("" if p == 1 else str(p)) + "i" + ("" if q == 1 else f"/{q}")


# Solution complexe : couple (partie réelle, partie imaginaire).
def root(r):
    if not isinstance(r, tuple):
        return real(r)
    re, im = r
    return f"{ratio(re)} {'-' if im < 0 else '+'} {imaginary(abs(im))}"
