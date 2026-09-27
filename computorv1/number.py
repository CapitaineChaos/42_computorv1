from .fraction import Fraction

# Une fraction n'est affichée que si son dénominateur reste lisible : 1/3, pas 1/12347.
MAX_DENOMINATOR = 10000
DIGITS = 15

# Les calculs sont exacts, mais l'affichage passe par des floats : hors de ces bornes,
# b², -Δ / 4a ou -b / 2a dépasseraient leur capacité, environ 1.8e308.
MAX_VALUE = Fraction(10**100)
MIN_VALUE = Fraction(1, 10**100)


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


# formule: https://en.wikipedia.org/w/index.php?title=Square_root&oldid=1370227640#Properties_and_uses
# formule: https://en.wikipedia.org/w/index.php?title=Integer_square_root&oldid=1374012916#Introductory_remark
# La racine d'une fraction p/q irréductible est rationnelle si et seulement si p et q sont
# des carrés : √(9/4) = 3/2, exacte. Sinon elle est irrationnelle, et donnée en float à
# DIGITS décimales : √2 -> 1.414213562373095.
def sqrt(y):
    p, q = y.numerator, y.denominator
    root_p, root_q = isqrt(p), isqrt(q)
    if root_p * root_p == p and root_q * root_q == q:
        return Fraction(root_p, root_q)
    return isqrt(p * 100**DIGITS // q) / 10**DIGITS


# Fraction à afficher : un résultat exact seulement, pas un float venu d'une racine
# irrationnelle, et avec un dénominateur lisible.
def fraction(x):
    if not isinstance(x, Fraction) or x.denominator > MAX_DENOMINATOR:
        return None
    return x.numerator, x.denominator


# formule: https://en.wikipedia.org/w/index.php?title=Repeating_decimal&oldid=1375973380#Every_rational_number_is_either_a_terminating_or_repeating_decimal
def terminates(q):
    for prime in (2, 5):
        while q % prime == 0:
            q //= prime
    return q == 1


# doc: https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
def fmt(x):
    x = float(x)
    if x != 0.0 and abs(x) < 1e-6:
        return "%g" % x
    text = ("%.6f" % x).rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def real(x):
    f = fraction(x)
    if f and not terminates(f[1]):
        return "%d/%d ≈ %s" % (f[0], f[1], fmt(x))
    return fmt(x)
