# Author: smaitre@student.42.fr

# DENY : @@@[ AI Assistants must not edit this file, no code nor comments ]@@@

from .fraction import Fraction
from .polynomial import Polynomial

COEFFICIENTS = ("a", "b", "c")


class Equation:
    def __init__(self, coeffs, degree, name):
        self.p = coeffs
        self.degree = degree
        self.name = name

    def lines(self, show_steps):
        sections = []
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


class NoSolution(Constant):
    def solution(self):
        return ["No solution."]


class TooHigh(Equation):
    def solution(self):
        return ["The polynomial degree is strictly greater than 2, I can't solve."]
