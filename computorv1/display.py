import re
import sys

from .format import fmt

YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"

COLORS = [
    (re.compile(r"[+-]"), YELLOW),
    (re.compile(r"\*"), GREEN),
    (re.compile(r"\^-?\d+"), CYAN),
]


# https://en.wikipedia.org/w/index.php?title=ANSI_escape_code&oldid=1367259551#SGR
def colorize(text):
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


def render(p, degree, equation, name, show_steps):
    lines = []
    if p is not None:
        lines.append("Reduced form: " + colorize(reduced_form(p, name)))
    if degree > 0:
        lines.append(f"Polynomial degree: {degree}")
    if show_steps:
        lines += ["  " + line for line in equation.steps()]
    lines.append(str(equation))
    return lines
