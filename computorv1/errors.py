import sys

from .display import BD_RED, RST, UND

MESSAGES = {
    "CHR_01": "unexpected character '{text}' at column {col}",

    "EXP_01": "missing operand after exponent at column {col}",
    "EXP_02": "missing operand before exponent at column {col}",
    "EXP_03": "illegal variable exponentiation at column {col}",
    "EXP_04": "exponent must be an integer, at column {col}",
    "EXP_05": "illegal exponent chaining at column {col}",
    "EXP_06": "division by 0 at column {col}",

    "SGN_01": "missing operand before sign '{text}' at column {col}",
    "SGN_02": "missing operand after sign '{text}' at column {col}",
    "SGN_03": "consecutive signs at column {col}",
    "SGN_04": "monomial cannot start with sign '{text}' at column {col}",

    "OPR_01": "missing operand before operator '{text}' at column {col}",
    "OPR_02": "missing operand after operator '{text}' at column {col}",
    "OPR_03": "consecutive operators at column {col}",
    "OPR_04": "missing operand between operators {text} at column {col}",
    "OPR_05": "missing operator between operands {text} at column {col}",
    "OPR_06": "unexpected operator '{op2}' after '{op1}' at column {col}",

    "EQL_01": "missing left side of equation at column {col}",
    "EQL_02": "missing right side of equation at column {col}",
    "EQL_03": "multiple equal signs at column {col}",
    "EQL_04": "missing equal sign",

    "MUL_01": "missing operand before multiply at column {col}",
    "MUL_02": "missing operand after multiply at column {col}",

    "VAR_01": "multiple variable names found: '{text}' at column {col}",
    "VAR_02": "illegal variable increment usage at column {col}",
    "VAR_03": "illegal variable decrement usage at column {col}",

    "LEN_01": "equation too long: {length} characters, {max} at most",
}


class ComputorErr(Exception):

    def __init__(self, code, expr=None, **values):
        self.code = code
        self.expr = expr
        self.col = values.get("col")
        self.message = MESSAGES[code].format(**values)

    def __str__(self):
        msg = f"({self.code}) {self.message}"
        if self.expr is None:
            return msg
        expr = self.expr
        if self.col is not None and sys.stderr.isatty():
            i = self.col - 1
            char = expr[i] if i < len(expr) else " "
            expr = expr[:i] + BD_RED + UND + char + RST + expr[i + 1:]
        return msg + f"\nin: {expr}"
