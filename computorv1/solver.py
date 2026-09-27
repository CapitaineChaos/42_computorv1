from .fraction import sqrt


# Renvoie (cas, solutions, valeurs du calcul) : ("linear", [x], {"a": a, "b": b}).
def solve(p):
    degree = len(p) - 1
    if degree < 0:
        return "all", [], {}
    if degree == 0:
        return "none", [], {}
    if degree == 1:
        return linear(p)
    if degree == 2:
        return quadratic(p)
    return "high", [], {}


# formule: https://en.wikipedia.org/w/index.php?title=Linear_equation&oldid=1359797583#One_variable
def linear(p):
    b, a = p
    return "linear", [-b / a], {"a": a, "b": b}


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_formula&oldid=1376700315
# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_equation&oldid=1368768952#Discriminant
# Δ est exact, le cas se choisit sans tolérance. Seul √Δ peut être irrationnel : il est
# alors un float, et les solutions qui en dépendent aussi. Complexe : (réel, imaginaire).
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


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_formula&oldid=1376700315#Numerical_calculation
# √Δ approché : quand b ≈ ±√Δ, -b ± √Δ efface ses premiers chiffres, et avec eux ceux qui
# sont justes. La solution concernée vient alors de x1 · x2 = c / a, sans soustraction.
# 10⁻²⁰x² + x + 1 = 0 donnait x1 = -49960 au lieu de -1.
def distinct_roots(a, b, c, root):
    if b > 0:
        x2 = (-b - root) / (2 * a)
        return [c / (a * x2), x2]
    x1 = (-b + root) / (2 * a)
    return [x1, c / (a * x1)]


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_function&oldid=1360283093#Vertex
def vertex(a, b, delta):
    return -b / (2 * a), -delta / (4 * a)
