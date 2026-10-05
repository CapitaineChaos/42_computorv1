from .display import reduced_form
from .reduce import MAX_REDUCED_DISP
from .fraction import Fraction

COEFFICIENTS = ("a", "b", "c")


class Equation:
    def __init__(self, coeffs, degree, name):
        if degree > MAX_REDUCED_DISP:
            self.p = None
        else:
            self.p = [coeffs.get(d, Fraction(0)) for d in range(degree + 1)]

        self.degree = degree
        self.name = name

    def lines(self, show_steps):
        pass
        sections = [reduced_form(self.p, self.name), self.degree_line()]
        if show_steps:
            sections.append(["  " + line for line in self.steps()])
        sections.append(self.solution())
        return [line for section in sections for line in section]

    def degree_line(self):
        return [f"Polynomial degree: {self.degree}"]

    def steps(self):
        return []

    def note(self):
        if self.name not in COEFFICIENTS:
            return []
        return [f"({self.name} is the unknown of the equation, not the coefficient {self.name})"]

    def solution(self):
        raise NotImplementedError



class Constant(Equation):
    # Override
    def degree_line(self):
        return []


class AllReals(Constant):
    def solution(self):
        return ["Any real number is a solution."]


class NoSolution(Constant):
    def solution(self):
        return ["No solution."]


class TooHigh(Equation):
    def solution(self):
        return ["The polynomial degree is strictly greater than 2, I can't solve."]
