from .eq import Equation
from .format import real, wrap


class Linear(Equation):
    def __init__(self, p, degree, name):
        super().__init__(p, degree, name)
        self.b, self.a = self.p
        self.x = -self.b / self.a

    def steps(self):
        a, b, name = self.a, self.b, self.name
        return self.note() + [
            f"a = {real(a)}, b = {real(b)}",
            f"{name} = -b / a = {real(-b)} / {wrap(a)} = {real(self.x)}",
        ]

    def solution(self):
        return ["The solution is:", f"{self.name} = {real(self.x)}"]
