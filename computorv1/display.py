from .number import fmt, fraction, real

HEADLINES = {
    "all": "Any real number is a solution.",
    "none": "No solution.",
    "linear": "The solution is:",
    "double": "Discriminant is zero, the solution is:",
    "positive": "Discriminant is strictly positive, the two solutions are:",
    "negative": "Discriminant is strictly negative, the two complex solutions are:",
    "high": "The polynomial degree is strictly greater than 2, I can't solve.",
}


def reduced_form(p):
    if not p:
        return "0 * X^0 = 0"
    text = ""
    for degree, c in enumerate(p):
        term = "%s * X^%d" % (fmt(abs(c)), degree)
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


def root(r):
    if not isinstance(r, complex):
        return real(r)
    return "%s %s %s" % (ratio(r.real), "-" if r.imag < 0 else "+", imaginary(abs(r.imag)))


def render(p, solution):
    lines = ["Reduced form: " + reduced_form(p)]
    if solution.kind not in ("all", "none"):
        lines.append("Polynomial degree: %d" % (len(p) - 1))
    lines += ["  " + step for step in solution.steps]
    lines.append(HEADLINES[solution.kind])
    lines += [root(r) for r in solution.roots]
    return lines
