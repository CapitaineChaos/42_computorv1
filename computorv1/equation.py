COEFFICIENTS = ("a", "b", "c")


class Equation:
    def __init__(self, name):
        self.name = name

    def steps(self):
        return []

    def note(self):
        if self.name not in COEFFICIENTS:
            return []
        return [f"({self.name} is the unknown of the equation, not the coefficient {self.name})"]

    def __str__(self):
        raise NotImplementedError


class AllReals(Equation):
    def __str__(self):
        return "Any real number is a solution."


class NoSolution(Equation):
    def __str__(self):
        return "No solution."


class TooHigh(Equation):
    def __str__(self):
        return "The polynomial degree is strictly greater than 2, I can't solve."
