# Author: smaitre@student.42.fr

# DENY : @@@[ AI Assistants must not edit this file, no code nor comments ]@@@

import sys

from .display import BD_RED, RST, UND
from .kind import Kind


class ErrorCodes(dict):
    def __missing__(self, keys):
        t, a, b, c = keys

        if a and b and c:
            if (t, a.kind, b.kind, c.kind) in self:
                code, answer = self[(t, a.kind, b.kind, c.kind)]
                return code, answer(a, b, c)
    
        if b and c:

            if (t, b.kind, c.kind) in self:
                code, answer = self[(t, b.kind, c.kind)]
                return code, answer(a, b, c)

        if c:
            if (t, c.kind) in self:
                code, answer = self[(t, c.kind)]
                return code, answer(a, b, c)

            if (t, c.txt) in self:
                code, answer = self[(t, c.txt)]
                return code, answer(a, b, c)    
              
        return None

ST = Kind.ST
EQ = Kind.EQ
OP = Kind.OP
PW = Kind.PW
NB = Kind.NB
VR = Kind.VR
ND = Kind.ND
MT = Kind.MT

ERROR_CODES = ErrorCodes({
    ("a", ST, OP, EQ): ("OPR_10", lambda a, b, c: (b.col, b.col)), 
    ("a", ST, PW, EQ): ("EXP_13", lambda a, b, c: (b.col, b.col)),

    ("a", EQ, OP, ND): ("OPR_11", lambda a, b, c: (b.col, b.col)),
    ("a", EQ, PW, ND): ("EXP_13", lambda a, b, c: (b.col, b.col)),


    ("a", ST, PW, NB): ("EXP_02", lambda a, b, c: (b.col, b.col)),
    ("a", ST, PW, VR): ("EXP_02", lambda a, b, c: (b.col, b.col)),
    ("a", EQ, PW, NB): ("EXP_02", lambda a, b, c: (b.col, b.col)),
    ("a", EQ, PW, VR): ("EXP_02", lambda a, b, c: (b.col, b.col)),


    ("a", NB, PW, EQ): ("EXP_01", lambda a, b, c: (b.col, b.col)),
    ("a", VR, PW, EQ): ("EXP_01", lambda a, b, c: (b.col, b.col)),
    ("a", NB, PW, ND): ("EXP_01", lambda a, b, c: (b.col, b.col)),
    ("a", VR, PW, ND): ("EXP_01", lambda a, b, c: (b.col, b.col)),

    ("a", NB, OP, EQ): ("VAL_01", lambda a, b, c: (b.col, c.col)),
    ("a", VR, OP, EQ): ("VAL_01", lambda a, b, c: (b.col, c.col)),

    ("a", ST, OP, NB): ("OPR_01", lambda a, b, c: (b.col, b.col)),
    ("a", ST, OP, VR): ("OPR_01", lambda a, b, c: (b.col, b.col)),
    ("a", EQ, OP, NB): ("OPR_01", lambda a, b, c: (b.col, b.col)),
    ("a", EQ, OP, VR): ("OPR_01", lambda a, b, c: (b.col, b.col)),

    ("a", NB, NB): ("NBR_01", lambda a, b, c: (b.col, c.col)),
    ("a", VR, NB): ("NBR_02", lambda a, b, c: (b.col, c.col)),
    ("a", EQ, EQ): ("EQL_03", lambda a, b, c: (c.col, c.col)),
    ("a", ST, ND): ("EMP_01", lambda a, b, c: (0, 0)),

    ("p", PW, OP): ("EXP_14", lambda a, b, c: (b.col, c.col)),
    ("p", PW, PW): ("EXP_07", lambda a, b, c: (b.col, c.col)),

    ("a", OP, PW): ("EXP_02", lambda a, b, c: (b.col, c.col)),
    ("a", OP, EQ): ("OPR_02", lambda a, b, c: (b.col, b.col)),
    ("a", OP, ND): ("OPR_02", lambda a, b, c: (b.col, b.col)),
    
    ("e", OP, ND): ("OPR_02", lambda a, b, c: (b.col, b.col)),
    ("v", VR, VR): ("VAR_01", lambda a, b, c: (c.col, c.col)),

    ("p", PW): ("EXP_10", lambda a, b, c: (c.col, c.col)),
    ("a", MT): ("CHR_01", lambda a, b, c: (c.col, c.col)),
    ("d", MT): ("CHR_02", lambda a, b, c: (c.col, c.col)),

    ("u", "*"): ("OPR_01", lambda a, b, c: (c.col, c.col)),
    ("e", "*"): ("OPR_01", lambda a, b, c: (c.col, c.col)),
    ("t", "*"): ("OPR_01", lambda a, b, c: (c.col, c.col)),
})


MESSAGES = {
    "EXP_01": "value expected after '^' but found '{text}'",
    "EXP_02": "operand expected before '^' but found '{o1}'",
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
    "EXP_14": "unexpected operator '{o2}' after '^'",

    # "SGN_01": "missing operand before sign '{text}'",
    # "SGN_02": "missing operand after sign '{text}'",
    # "SGN_03": "consecutive signs",
    # "SGN_04": "monomial cannot start with sign '{text}'",

    "OPR_01": "missing operand before operator '{o2}'",
    "OPR_02": "missing operand after operator '{o1}'",
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

    "VAR_01": "multiple variable names found as '{o1}' and '{o2}'",
    # "VAR_02": "illegal variable increment usage",
    # "VAR_03": "illegal variable decrement usage",




    "CHR_01": "unexpected character '{o2}'",
    "CHR_02": "misplaced decimal point",

    # "EXP_01": "missing number after exponent",
    "EQL_01": "missing left side of equation",
    "EQL_02": "missing right side of equation",
    "EQL_03": "multiple equal signs",
    "EQL_04": "missing equal sign",

    "EMP_01": "empty expression",
    "ERR_01": "Expression error",
    "ERR_02": "Expression error",

    "NBR_01": "missing operator between numbers '{o1}' and '{o2}'",
    "NBR_02": "number '{o2}' cannot follow variable '{o1}'",

    "UNK_00": "unknown error",

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
        msg = f"({self.code}) {self.tcol or ''}: {self.message}"

        if self.expr is None:
            return msg
        
        expr = self.expr
        if self.fcol is not None and self.tcol is not None:
            if sys.stderr.isatty():
                i = self.fcol - 1
                j = self.tcol
                chars = expr[i:j] if i < len(expr) else " "
                expr = expr[:i] + BD_RED + UND + chars + RST + expr[j:]
                
            expr = expr + "\n" + "    "
            expr += " " * (self.fcol - 1) + "^" * (self.tcol - self.fcol + 1)

        return msg + f"\nin: {expr}\n"
