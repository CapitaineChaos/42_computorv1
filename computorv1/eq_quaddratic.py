from .eq import Equation
from .format import real, root, wrap
from .fraction import sqrt


class Quadratic(Equation):
    def __init__(self, coeffs, degree, name, delta):
        super().__init__(coeffs, degree, name)
        self.c, self.b, self.a = self.p
        self.delta = delta
        self.h = -self.b / (2 * self.a)
        self.k = -delta / (4 * self.a)

    def steps(self):
        a, b, c, delta = self.a, self.b, self.c, self.delta
        h, k = self.h, self.k
        return self.note() + [
            "Coeffs:",
            f"     a = {real(a)}",
            f"     b = {real(b)}",
            f"     c = {real(c)}",
            "delta  = b^2 - 4ac",
            f"       = {wrap(b)}^2 - 4 * {wrap(a)} * {wrap(c)}",
            f"       = {real(delta)}",
            "vertex = (-b / 2a, -delta / 4a)",
            f"       = (-{wrap(b)}/(2*{wrap(a)}), -{wrap(delta)}/(4*{wrap(a)}))",
            f"       = ({real(-b)}/{wrap(2*a)}, {real(-delta)}/{wrap(4*a)})",
            f"       = ({real(h)}, {real(k)})",
            f"       is a {'minimum' if a > 0 else 'maximum'}",
        ] + self.root_steps()

    def root_steps(self):
        raise NotImplementedError


class DoubleRoot(Quadratic):
    def root_steps(self):
        return [
            f"{self.name} = x-coordinate of vertex",
            f"{' ' * len(self.name)} = {real(self.h)}",
        ]

    def solution(self):
        return ["Discriminant is zero, the solution is:", f"{self.name} = {real(self.h)}"]


class TwoRoots(Quadratic):
    def __init__(self, coeffs, degree, name, delta):
        super().__init__(coeffs, degree, name, delta)
        self.x1, self.x2 = distinct_roots(self.a, self.b, self.c, sqrt(delta))

    def root_steps(self):
        a, b, delta, name = self.a, self.b, self.delta, self.name
        return [
            f"{name}1 = (-b + rac(delta)) / 2a"
            f" = ({real(-b)} + rac({real(delta)})) / {wrap(2 * a)} = {real(self.x1)}",
            f"{name}2 = (-b - rac(delta)) / 2a"
            f" = ({real(-b)} - rac({real(delta)})) / {wrap(2 * a)} = {real(self.x2)}",
        ]

    def solution(self):
        return [
            "Discriminant is strictly positive, the two solutions are:",
            f"{self.name}1 = {real(self.x1)}",
            f"{self.name}2 = {real(self.x2)}",
        ]


class ComplexRoots(Quadratic):
    def __init__(self, coeffs, degree, name, delta):
        super().__init__(coeffs, degree, name, delta)
        self.im = sqrt(-delta) / (2 * self.a)

    def root_steps(self):
        a, b, delta = self.a, self.b, self.delta
        return [
            f"-b / 2a = {real(-b)} / {wrap(2 * a)} = {real(self.h)}",
            f"-rac(delta) / 2a = rac({real(-delta)}) / {wrap(2 * a)} = {real(self.im)}",
        ]

    def solution(self):
        return [
            "Discriminant is strictly negative, the two complex solutions are:",
            f"{self.name}1 = {root((self.h, self.im))}",
            f"{self.name}2 = {root((self.h, -self.im))}",
        ]


def distinct_roots(a, b, c, root):
    if b > 0:
        x2 = (-b - root) / (2 * a)
        return [c / (a * x2), x2]
    x1 = (-b + root) / (2 * a)
    return [x1, c / (a * x1)]
