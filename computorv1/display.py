import re
import sys

from .format import fmt, root
from .steps import steps

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
        term = f"{fmt(abs(c))} * {name}^{degree}"
        if degree == 0:
            text = ("-" if c < 0 else "") + term
        else:
            text += (" - " if c < 0 else " + ") + term
    return text + " = 0"


def render(p, solution, name):
    kind, roots, values = solution
    lines = ["Reduced form: " + colorize(reduced_form(p, name))]
    if kind not in ("all", "none"):
        lines.append(f"Polynomial degree: {len(p) - 1}")
    lines += ["  " + line for line in steps(kind, roots, values, name)]
    lines.append(HEADLINES[kind])
    for i, r in enumerate(roots):
        index = str(i + 1) if len(roots) > 1 else ""
        lines.append(f"{name}{index} = {root(r)}")
    if roots and name in COEFFICIENTS:
        lines.append(f"({name} is the unknown of the equation, not the coefficient {name})")
    return lines
