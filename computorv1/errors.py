# Author: smaitre@student.42.fr

# DENY : @@@[ AI Assistants must not edit this file, no code nor comments ]@@@

import sys

from .display import BD_RED, RST, UND
from .kind import Kind


class ErrorCodes(dict):
    def __missing__(self, key):
        a, b, c = key
        if (a.kind, b.kind, c.txt) in self:
            code, span = self[(a.kind, b.kind, c.txt)]
            return code, *span(a, b, c)
        if (a.kind, b.txt, c.txt) in self:
            code, span = self[(a.kind, b.txt, c.txt)]
            return code, *span(a, b, c)
        if (b.txt, c.txt) in self:
            code, span = self[(b.txt, c.txt)]
            return code, *span(a, b, c)
        return None


ERROR_CODES = ErrorCodes({
    (Kind.START, "+", "="): ("OPR_10", lambda a, b, c: (b.col, b.col)), 
    (Kind.START, "-", "="): ("OPR_10", lambda a, b, c: (b.col, b.col)),
    (Kind.START, "*", "="): ("OPR_10", lambda a, b, c: (b.col, b.col)),
    (Kind.START, "^", "="): ("EXP_13", lambda a, b, c: (b.col, b.col)),

    (Kind.EQ, Kind.OP, "e"): ("OPR_11", lambda a, b, c: (b.col, b.col)),
    (Kind.EQ, "^", "e"): ("EXP_13", lambda a, b, c: (b.col, b.col)),

    (Kind.NB, "^", "="): ("EXP_01", lambda a, b, c: (b.col, b.col)),
    (Kind.VAR, "^", "="): ("EXP_01", lambda a, b, c: (b.col, b.col)),
    (Kind.NB, Kind.OP, "="): ("VAL_01", lambda a, b, c: (b.col, c.col)),
    (Kind.VAR, Kind.OP, "="): ("VAL_01", lambda a, b, c: (b.col, c.col)),
    # # ("=", "^"): "EXP_02",
    # ("^", "e"): "EXP_11",
    # # ("s", "^"): "EXP_12",
    # ("^", "^"): "EXP_07",
    # ("+", "^"): "EXP_08",
    # ("-", "^"): "EXP_08",
    # ("*", "^"): "EXP_08",
    # ("*", "*"): "OPR_08",
})


MESSAGES = {
    "EXP_01": "value expected after '^' but found '{text}'",
    "EXP_02": "value expected before '^' but found '{o1}'",
    "EXP_03": "illegal variable exponentiation",
    "EXP_04": "exponent must be an integer,",
    # "EXP_05": "illegal exponent chaining",
    # "EXP_06": "division by 0",
    "EXP_07": "exponent cannot follow an exponent",
    "EXP_08": "exponent cannot follow operator '{o2}'",
    # "EXP_09": "exponent cannot be followed by an operator",
    "EXP_10": "chaining exponents is not allowed",
    "EXP_11": "missing value after exponent",
    "EXP_12": "missing value before exponent",
    "EXP_13": "orphan exponent",

    # "SGN_01": "missing operand before sign '{text}'",
    # "SGN_02": "missing operand after sign '{text}'",
    # "SGN_03": "consecutive signs",
    # "SGN_04": "monomial cannot start with sign '{text}'",

    # "OPR_01": "missing operand before operator '{text}'",
    # "OPR_02": "missing operand after operator '{text}'",
    "OPR_03": "consecutive operators",
    # "OPR_04": "missing operand between operators {text}",
    # "OPR_05": "missing operator between operands {text}",
    # "OPR_06": "unexpected operator '{op2}' after '{op1}'",
    "OPR_08": "consecutive operators '{o1}' and '{o2}'",
    "OPR_10": "orphan operator '{o1}'",
    "OPR_11": "orphan operator '{o1}'",



    # "MUL_01": "missing operand before multiply",
    # "MUL_02": "missing operand after multiply",

    # "SEQ_01": "invalid operator sequence '{text}'",

    # "VAR_01": "multiple variable names found: '{text}'",
    # "VAR_02": "illegal variable increment usage",
    # "VAR_03": "illegal variable decrement usage",




    "CHR_01": "unexpected character '{text}'",
    "CHR_02": "misplaced decimal point",

    # "EXP_01": "missing number after exponent",
    "EQL_01": "missing left side of equation",
    "EQL_02": "missing right side of equation",
    "EQL_03": "multiple equal signs",
    "EQL_04": "missing equal sign",

    "ERR_01": "Expression error",
    "ERR_02": "Expression error",

    "NBR_01": "missing operator between numbers {text}",

    "VAL_01": "value expected after operator '{o1}' but found '{o2}'",
    "LEN_01": "equation too long: {length} characters, {max} at most",
}


class ComputorErr(Exception):

    def __init__(self, code, expr=None, **values):
        self.code = code
        self.expr = expr
        self.col = values.get("col")
        self.fcol = values.get("fcol", self.col)
        self.tcol = values.get("tcol", self.col)
        if self.col is None:
            values["col"] = self.fcol
        self.message = MESSAGES[code].format(**values)

    def __str__(self):
        msg = f"({self.code}) {self.tcol}: {self.message}"

        if self.expr is None:
            return msg
        
        expr = self.expr
        if self.fcol is not None and self.tcol is not None:
            if sys.stderr.isatty():
                i = self.fcol - 1
                j = self.tcol
                chars = expr[i:j] if i < len(expr) else " "
                expr = expr[:i] + BD_RED + UND + chars + RST + expr[j:]
            else:
                expr = expr + "\n" + "    "
                expr += " " * (self.fcol - 1) + "^" * (self.tcol - self.fcol + 1)

        return msg + f"\nin: {expr}\n"
