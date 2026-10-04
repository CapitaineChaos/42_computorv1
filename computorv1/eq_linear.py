from .equation import Equation
from .format import real, wrap


class Linear(Equation):
    def __init__(self, p, name):
        super().__init__(name)
        self.b, self.a = p
        self.x = -self.b / self.a

    def steps(self):
        a, b, name = self.a, self.b, self.name
        return self.note() + [
            f"a = {real(a)}, b = {real(b)}",
            f"{name} = -b / a = {real(-b)} / {wrap(a)} = {real(self.x)}",
        ]

    def __str__(self):
        return f"The solution is:\n{self.name} = {real(self.x)}"
