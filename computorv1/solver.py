from .fraction import sqrt


def solve(p, degree):
    if degree < 0:
        return "all", [], {}
    if degree == 0:
        return "none", [], {}
    if degree == 1:
        return linear(p)
    if degree == 2:
        return quadratic(p)
    return "high", [], {}


def linear(p):
    b, a = p
    return "linear", [-b / a], {"a": a, "b": b}


def quadratic(p):
    c, b, a = p
    delta = b * b - 4 * a * c
    values = {"a": a, "b": b, "c": c, "delta": delta, "vertex": vertex(a, b, delta)}
    if delta == 0:
        return "double", [-b / (2 * a)], values
    if delta > 0:
        return "positive", distinct_roots(a, b, c, sqrt(delta)), values
    re = -b / (2 * a)
    im = sqrt(-delta) / (2 * a)
    return "negative", [(re, im), (re, -im)], values


def distinct_roots(a, b, c, root):
    if b > 0:
        x2 = (-b - root) / (2 * a)
        return [c / (a * x2), x2]
    x1 = (-b + root) / (2 * a)
    return [x1, c / (a * x1)]


def vertex(a, b, delta):
    return -b / (2 * a), -delta / (4 * a)
