import re
import sys

from .number import fmt, fraction, real

YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"

# Ce qui est coloré dans la forme réduite : signes, multiplications, exposants.
COLORS = [
    (re.compile(r"[+-]"), YELLOW),
    (re.compile(r"\*"), GREEN),
    (re.compile(r"\^-?\d+"), CYAN),
]

HEADLINES = {
    "all": "Any real number is a solution.",
    "none": "No solution.",
    "linear": "The solution is:",
    "double": "Discriminant is zero, the solution is:",
    "positive": "Discriminant is strictly positive, the two solutions are:",
    "negative": "Discriminant is strictly negative, the two complex solutions are:",
    "high": "The polynomial degree is strictly greater than 2, I can't solve.",
}

# Noms des coefficients dans les lignes de calcul, que l'inconnue peut porter aussi.
COEFFICIENTS = ("a", "b", "c")


# code: https://en.wikipedia.org/w/index.php?title=ANSI_escape_code&oldid=1367259551#SGR
# doc: https://docs.python.org/3/library/io.html#io.IOBase.isatty
def colorize(text):
    if not sys.stdout.isatty():
        return text
    for pattern, color in COLORS:
        text = pattern.sub(color + r"\g<0>" + RESET, text)
    return text


def reduced_form(p, name):
    if not p:
        return "0 * %s^0 = 0" % name
    text = ""
    for degree, c in enumerate(p):
        term = "%s * %s^%d" % (fmt(abs(c)), name, degree)
        if degree == 0:
            text = ("-" if c < 0 else "") + term
        else:
            text += (" - " if c < 0 else " + ") + term
    return text + " = 0"


def ratio(x):
    f = fraction(x)
    if not f:
        return fmt(x)
    return str(f[0]) if f[1] == 1 else "%d/%d" % f


def imaginary(y):
    f = fraction(y)
    if not f:
        return fmt(y) + "i"
    p, q = f
    return ("" if p == 1 else str(p)) + "i" + ("" if q == 1 else "/%d" % q)


# Solution complexe : couple (partie réelle, partie imaginaire).
def root(r):
    if not isinstance(r, tuple):
        return real(r)
    re, im = r
    return "%s %s %s" % (ratio(re), "-" if im < 0 else "+", imaginary(abs(im)))


def render(p, solution, name):
    lines = ["Reduced form: " + colorize(reduced_form(p, name))]
    if solution.kind not in ("all", "none"):
        lines.append("Polynomial degree: %d" % (len(p) - 1))
    lines += ["  " + step for step in solution.steps]
    lines.append(HEADLINES[solution.kind])
    for i, r in enumerate(solution.roots):
        index = str(i + 1) if len(solution.roots) > 1 else ""
        lines.append("%s%s = %s" % (name, index, root(r)))
    if solution.roots and name in COEFFICIENTS:
        lines.append("(%s is the unknown of the equation, not the coefficient %s)" % (name, name))
    return lines
