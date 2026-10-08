import logging
from typing import Any, NamedTuple

from .errors import ComputorErr
from .fraction import Fraction, from_decimal
from .lexer import tokenize, Token
from .reduce import reduce

MAX_LEN = 200


def parse(source):
    logging.basicConfig(level=logging.DEBUG, format="\033[36mPARSER:\033[0m \033[35m%(message)s\033[0m")
    if len(source) > MAX_LEN:
        raise ComputorErr("LEN_01", length=len(source), max=MAX_LEN)
    parser = Parser(source)
    # left, right = parser.eq_sides()
    parser.parse()
    print("-------------------------------------------------")
    # coefficients, degree = reduce(left, right)
    # return coefficients, degree, parser.name


class Monomial(NamedTuple):
    terms: list[Any]
    degree: int
    coeff: int

# À 42 on aime le parsing alors on parse à fond....
class Parser:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.var = None
        self.monomials : list[Monomial] = []
        self.current_monomial : Monomial | None = None
        self.hist = ""
        self.histn = ""
        self.histo = []

    @property
    def name(self):
        return self.var or "X"

    def to_monomial(self, token):
        if not self.current_monomial:
            self.current_monomial = Monomial([], 0, 1)
        self.current_monomial.terms.append(token)

    def store_monomial(self):
        if self.current_monomial:
            self.monomials.append(self.current_monomial)
            self.current_monomial = None

    def new_monomial(self, sign):
        self.store_monomial()
        self.current_monomial = Monomial([], 0, sign)

    def history(self, token):
        self.hist += token.code
        if token.kind != "SKIP":
            self.histn += token.code
        if token.kind == "OP":
            self.histo.append(token)
        logging.debug(f"history: {self.hist}")

    def parse(self):
        ptk = None
        equal = False
        s = self.source
        space = False
        last_exp = None
        for tk in tokenize(self.source):
            # logging.debug(f"token: {token}")

            self.history(tk)

            # if tk.txt == "^":
            #     last_exp = tk

            if self.histn.endswith(("^v", "^-v")):
                raise ComputorErr("EXP_03", s, col=tk.col)

            if self.hist.endswith("v++"):
                raise ComputorErr("VAR_02", s, col=tk.col - 2)

            if self.hist.endswith("++v"):
                raise ComputorErr("VAR_02", s, col=tk.col)
            
            if self.hist.endswith("v--"):
                raise ComputorErr("VAR_03", s, col=tk.col - 2)

            if self.hist.endswith("--v"):
                raise ComputorErr("VAR_03", s, col=tk.col)

            if self.histn.endswith(("^n", "^-n")) and "." in tk.txt:
                raise ComputorErr("EXP_04", s, col=tk.col + tk.txt.index("."))

            if self.histn.endswith(("s*", "=*", "^*")):
                raise ComputorErr("OPR_01", s, text=tk.txt, col=tk.col)

            if self.histn.endswith(("+*", "-*", "**",)):
                raise ComputorErr("MUL_01", s, col=tk.col)

            if self.histn.endswith(("^=", "^e")):
                raise ComputorErr("EXP_01", s, col=ptk.col)

            if self.histn.endswith(("^-n^", "^n^")):
                raise ComputorErr("EXP_05", s, col=tk.col)
            
            if not ptk:
                ptk = tk
                continue

            if tk.kind == "VAR":
                if self.var is None:
                    self.var = tk.txt
                elif self.var != tk.txt:
                    raise ComputorErr("VAR_01", s, text=tk.txt, col=tk.col)
                
            if tk.kind == "SKIP":
                space = True
                continue

            if tk.kind == "MISMATCH":
                raise ComputorErr("CHR_01", s, text=tk.txt, col=tk.col)

            if tk.kind == "EQ":
                if equal:
                    raise ComputorErr("EQL_03", s, col=tk.col)
                if ptk.kind == "START":
                    raise ComputorErr("EQL_01", s, col=tk.col)
                equal = True

            # if tk.code in "*^+":
            #     if ptk.code in "*^":
            #         t = f"'{ptk.txt}' and '{tk.txt}'"
            #         raise ComputorErr("OPR_04", s, text=t, col=ptk.col)

            if tk.kind == "NB":
                if ptk.kind == "NB":
                    t = f"'{ptk.txt}' and '{tk.txt}'"
                    raise ComputorErr("OPR_05", s, text=t, col=ptk.col + 1)
                
            if tk.kind == "END":
                if ptk.kind == "EQ":
                    raise ComputorErr("EQL_02", s, col=ptk.col)
                if tk.kind == "EQ" and ptk.kind == "OP":
                    raise ComputorErr("OPR_02", s, text=ptk.txt, col=ptk.col)

            if tk.code == "^":
                if ptk.kind not in ("NB", "VAR"):
                    raise ComputorErr("EXP_02", s, col=tk.col)

            if ptk.kind == "^":
                if tk.kind not in ("NB", "VAR"):
                    raise ComputorErr("EXP_01", s, col=tk.col)

            # if ptk.kind == "OP":
            #     if tk.kind in ("EQ", "END"):
            #         raise ComputorErr("OPR_02", s, text=ptk.txt, col=ptk.col)

            # Un monôme est forcément délimité par 
            # START
            # END
            # EQ
            # + 
            # - (si prev != * ni ^)
            if tk.code in "s=e+" or (tk.code == "-" and ptk.code not in "*^"):
                # if tk.code == "+" and ptk.code in "s=":
                #     raise ComputorErr("SGN_04", s, text=tk.txt, col=tk.col)
                if tk.code == "END":
                    self.store_monomial()
                    continue
                sign = -1 if equal else 1
                sign = sign * (-1 if tk.code == "-" else 1)
                self.new_monomial(sign)
            else:
                self.to_monomial(tk)

            ptk = tk
            space = False

        if not equal:
            raise ComputorErr("EQL_04", s)
        
        for m in self.monomials:
            logging.debug(f"monomial: {m}")

   