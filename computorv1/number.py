# doc: https://docs.python.org/3/tutorial/floatingpoint.html#tut-fp-issues
FRACTION_TOLERANCE = 1e-12
MAX_DENOMINATOR = 10000
DIGITS = 15

# Hors de ces bornes, b², 4ac ou -b/2a dépassent la capacité d'un float.
MAX_VALUE = 1e100
MIN_VALUE = 1e-100


# formule: https://docs.python.org/3/library/math.html#math.isclose
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# Deux apports opposés qui s'annulent, aux erreurs d'arrondi près : 0.3 et 0.1 + 0.2.
def cancels(up, down):
    return isclose(up, down)


# code: https://en.wikipedia.org/w/index.php?title=Integer_square_root&oldid=1374012916#Algorithm_using_binary_search
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


# formule: https://en.wikipedia.org/w/index.php?title=Integer_square_root&oldid=1374012916#Introductory_remark
def sqrt(y):
    return isqrt(round(y * 100**DIGITS)) / 10**DIGITS


# code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L357-L412
def limit_denominator(numerator, denominator, max_denominator=1000000):
    if max_denominator < 1:
        raise ValueError("max_denominator should be at least 1")
    if denominator <= max_denominator:
        return numerator, denominator

    p0, q0, p1, q1 = 0, 1, 1, 0
    n, d = numerator, denominator
    while True:
        a = n // d
        q2 = q0 + a * q1
        if q2 > max_denominator:
            break
        p0, q0, p1, q1 = p1, q1, p0 + a * p1, q2
        n, d = d, n - a * d
    k = (max_denominator - q0) // q1

    if 2 * d * (q0 + k * q1) <= denominator:
        return p1, q1
    else:
        return p0 + k * p1, q0 + k * q1


# doc: https://docs.python.org/3/library/stdtypes.html#float.as_integer_ratio
def fraction(x):
    if x != x or x in (float("inf"), float("-inf")):
        return None
    p, q = limit_denominator(*x.as_integer_ratio(), MAX_DENOMINATOR)
    if not isclose(x, p / q, rel_tol=FRACTION_TOLERANCE, abs_tol=FRACTION_TOLERANCE):
        return None
    return p, q


# formule: https://en.wikipedia.org/w/index.php?title=Repeating_decimal&oldid=1375973380#Every_rational_number_is_either_a_terminating_or_repeating_decimal
def terminates(q):
    for prime in (2, 5):
        while q % prime == 0:
            q //= prime
    return q == 1


# doc: https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
def fmt(x):
    if x != 0.0 and abs(x) < 1e-6:
        return "%g" % x
    text = ("%.6f" % x).rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def real(x):
    f = fraction(x)
    if f and not terminates(f[1]):
        return "%d/%d ≈ %s" % (f[0], f[1], fmt(x))
    return fmt(x)
