import re

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


# p vaut None au-delà de reduce.MAX_REDUCED_DISP : la section disparaît.
def reduced_form(p, name):
    if p is None:
        return []
    return ["Reduced form: " + colorize(terms(p, name))]


def terms(p, name):
    if not p:
        return f"0 * {name}^0 = 0"
    text = ""
    for degree, c in enumerate(p):
        term = f"{fmt(abs(c))} * {name}^{degree}"
        if degree == 0:
            text = ("-" if c < 0 else "") + term
        else:
            text += (" - " if c < 0 else " + ") + term
    return text + " = 0"
