from .format import real, wrap


def steps(kind, roots, values, name):
    if kind == "linear":
        return linear_steps(values, roots, name)
    if kind in ("double", "positive", "negative"):
        return quadratic_steps(kind, values, roots, name)
    return []


def linear_steps(values, roots, name):
    a, b = values["a"], values["b"]
    return [
        f"a = {real(a)}, b = {real(b)}",
        f"{name} = -b / a = {real(-b)} / {wrap(a)} = {real(roots[0])}",
    ]


def quadratic_steps_1(values):
    a, b, c, delta = values["a"], values["b"], values["c"], values["delta"]
    h, k = values["vertex"]
    lines = [
        f"Coeffs:",
        f"     a = {real(a)}",
        f"     b = {real(b)}",
        f"     c = {real(c)}",
        f"delta  = b² - 4ac",
        f"       = {wrap(b)}² - 4 * {wrap(a)} * {wrap(c)}",
        f"       = {real(delta)}",
        f"vertex = (-b / 2a, -delta / 4a)",
        f"       = (-{wrap(b)}/(2*{wrap(a)}), -{wrap(delta)}/(4*{wrap(a)}))",
        f"       = ({real(-b)}/{wrap(2*a)}, {real(-delta)}/{wrap(4*a)})",
        f"       = ({real(h)}, {real(k)})",
        f"       is a {'minimum' if a > 0 else 'maximum'}",
    ]
    return lines

def quadratic_steps_2(kind, delta, roots, name):
    lines = []
    if kind == "double":
        lines = [
            f"{name} = x-coordinate of vertex",
            f"       = {real(roots[0])}",
        ]
    elif kind == "positive":
        for i, sign in enumerate("+-"):
            formula = f"{name}{i + 1} = (-b {sign} √delta) / 2a"
            numbers = f"({real(-b)} {sign} √{real(delta)}) / {wrap(2 * a)}"
            lines = [
                f"{formula} = {numbers} = {real(roots[i])}",
            ]
    else:
        re, im = roots[0]
        lines = [
            f"-b / 2a = {real(-b)} / {wrap(2 * a)} = {real(re)}",
            f"√-delta / 2a = √{real(-delta)} / {wrap(2 * a)} = {real(im)}"
        ]
    return lines
