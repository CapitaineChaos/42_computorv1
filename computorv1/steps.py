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


def quadratic_steps(kind, values, roots, name):
    a, b, c, delta = values["a"], values["b"], values["c"], values["delta"]
    h, k = values["vertex"]
    lines = [
        f"a = {real(a)}, b = {real(b)}, c = {real(c)}",
        f"Δ = b² - 4ac = {wrap(b)}² - 4 * {wrap(a)} * {wrap(c)} = {real(delta)}",
        f"vertex = (-b / 2a, -Δ / 4a) = ({real(h)}, {real(k)}), {'minimum' if a > 0 else 'maximum'}",
    ]
    if kind == "double":
        lines.append(f"{name} = -b / 2a = {real(-b)} / {wrap(2 * a)} = {real(roots[0])}")
    elif kind == "positive":
        for i, sign in enumerate("+-"):
            formula = f"{name}{i + 1} = (-b {sign} √Δ) / 2a"
            numbers = f"({real(-b)} {sign} √{real(delta)}) / {wrap(2 * a)}"
            lines.append(f"{formula} = {numbers} = {real(roots[i])}")
    else:
        re, im = roots[0]
        lines.append(f"-b / 2a = {real(-b)} / {wrap(2 * a)} = {real(re)}")
        lines.append(f"√-Δ / 2a = √{real(-delta)} / {wrap(2 * a)} = {real(im)}")
    return lines
