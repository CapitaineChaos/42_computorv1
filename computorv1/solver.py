from .display import real
from .fraction import sqrt


# Renvoie un tuple (cas, solutions, lignes de calcul) : ("linear", [x], steps).
def solve(p, name):
    degree = len(p) - 1
    if degree < 0:
        return "all", [], []
    if degree == 0:
        return "none", [], []
    if degree == 1:
        return linear(p, name)
    if degree == 2:
        return quadratic(p, name)
    return "high", [], []


# formule: https://en.wikipedia.org/w/index.php?title=Linear_equation&oldid=1359797583#One_variable
def linear(p, name):
    b, a = p
    x = -b / a
    steps = [
        "a = %s, b = %s" % (real(a), real(b)),
        "%s = -b / a = %s / %s = %s" % (name, real(-b), wrap(a), real(x)),
    ]
    return "linear", [x], steps


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_formula&oldid=1376700315
# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_equation&oldid=1368768952#Discriminant
# Δ est exact, le cas se choisit sans tolérance. Seul √Δ peut être irrationnel : il est
# alors un float, et les solutions qui en dépendent aussi.
def quadratic(p, name):
    c, b, a = p
    delta = b * b - 4 * a * c
    steps = [
        "a = %s, b = %s, c = %s" % (real(a), real(b), real(c)),
        "Δ = b² - 4ac = %s² - 4 * %s * %s = %s" % (wrap(b), wrap(a), wrap(c), real(delta)),
        vertex(b, a, delta),
    ]
    if delta == 0:
        x = -b / (2 * a)
        steps.append("%s = -b / 2a = %s / %s = %s" % (name, real(-b), wrap(2 * a), real(x)))
        return "double", [x], steps
    if delta > 0:
        x1, x2 = distinct_roots(a, b, c, sqrt(delta))
        steps.append(
            "%s1 = (-b + √Δ) / 2a = (%s + √%s) / %s = %s"
            % (name, real(-b), real(delta), wrap(2 * a), real(x1))
        )
        steps.append(
            "%s2 = (-b - √Δ) / 2a = (%s - √%s) / %s = %s"
            % (name, real(-b), real(delta), wrap(2 * a), real(x2))
        )
        return "positive", [x1, x2], steps
    re = -b / (2 * a)
    im = sqrt(-delta) / (2 * a)
    steps.append("-b / 2a = %s / %s = %s" % (real(-b), wrap(2 * a), real(re)))
    steps.append("√-Δ / 2a = √%s / %s = %s" % (real(-delta), wrap(2 * a), real(im)))
    return "negative", [(re, im), (re, -im)], steps


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_formula&oldid=1376700315#Numerical_calculation
# √Δ approché : quand b ≈ ±√Δ, -b ± √Δ efface ses premiers chiffres, et avec eux ceux qui
# sont justes. La solution concernée vient alors de x1 · x2 = c / a, sans soustraction.
# 10⁻²⁰x² + x + 1 = 0 donnait x1 = -49960 au lieu de -1.
def distinct_roots(a, b, c, root):
    if b > 0:
        x2 = (-b - root) / (2 * a)
        return c / (a * x2), x2
    x1 = (-b + root) / (2 * a)
    return x1, c / (a * x1)


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_function&oldid=1360283093#Vertex
def vertex(b, a, delta):
    h = -b / (2 * a)
    k = -delta / (4 * a)
    extremum = "minimum" if a > 0 else "maximum"
    return "vertex = (-b / 2a, -Δ / 4a) = (%s, %s), %s" % (real(h), real(k), extremum)


def wrap(x):
    return "(%s)" % real(x) if x < 0 else real(x)
