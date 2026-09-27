from .format import real, wrap

# Lignes de calcul : chaque formule, puis la même avec les nombres. Les formules et leurs
# sources sont dans solver.py.


def steps(kind, roots, values, name):
    if kind == "linear":
        return linear_steps(values, roots, name)
    if kind in ("double", "positive", "negative"):
        return quadratic_steps(kind, values, roots, name)
    return []


def linear_steps(values, roots, name):
    a, b = values["a"], values["b"]
    return [
        "a = %s, b = %s" % (real(a), real(b)),
        "%s = -b / a = %s / %s = %s" % (name, real(-b), wrap(a), real(roots[0])),
    ]


def quadratic_steps(kind, values, roots, name):
    a, b, c, delta = values["a"], values["b"], values["c"], values["delta"]
    h, k = values["vertex"]
    lines = [
        "a = %s, b = %s, c = %s" % (real(a), real(b), real(c)),
        "Δ = b² - 4ac = %s² - 4 * %s * %s = %s" % (wrap(b), wrap(a), wrap(c), real(delta)),
        "vertex = (-b / 2a, -Δ / 4a) = (%s, %s), %s"
        % (real(h), real(k), "minimum" if a > 0 else "maximum"),
    ]
    if kind == "double":
        lines.append("%s = -b / 2a = %s / %s = %s" % (name, real(-b), wrap(2 * a), real(roots[0])))
    elif kind == "positive":
        for i, sign in enumerate("+-"):
            formula = "%s%d = (-b %s √Δ) / 2a" % (name, i + 1, sign)
            numbers = "(%s %s √%s) / %s" % (real(-b), sign, real(delta), wrap(2 * a))
            lines.append("%s = %s = %s" % (formula, numbers, real(roots[i])))
    else:
        re, im = roots[0]
        lines.append("-b / 2a = %s / %s = %s" % (real(-b), wrap(2 * a), real(re)))
        lines.append("√-Δ / 2a = √%s / %s = %s" % (real(-delta), wrap(2 * a), real(im)))
    return lines
