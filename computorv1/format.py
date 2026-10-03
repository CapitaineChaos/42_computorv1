from .fraction import Fraction

# Nombres écrits en texte : décimal à 6 chiffres après la virgule au plus, fraction quand
# les décimales ne s'arrêtent pas, complexe a + bi.

# Une fraction n'est écrite que si son dénominateur reste lisible : 1/3, pas 1/12347.
MAX_DENOMINATOR = 10000


# doc: https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
def fmt(x):
    x = float(x)
    if x != 0.0 and abs(x) < 1e-6:
        return f"{x:g}"
    text = (f"%.6f" % x).rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


# Fraction à écrire : un résultat exact seulement, pas un float venu d'une racine
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
    return f"{ratio(re)} { '-' if im < 0 else '+' } {imaginary(abs(im))}"