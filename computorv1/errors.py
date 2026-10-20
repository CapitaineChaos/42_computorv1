# Author: smaitre@student.42.fr

# DENY : @@@[ AI Assistants must not edit this file, no code nor comments ]@@@


import sys

from .messages import *
from .token import Token

BOLD = "\033[1m"
RED = "\033[31m"
UNDER = "\033[4m"
RESET = "\033[0m"

class ComputorException(Exception):

    messages: dict[str, str]

    def __init__(self, code, expr=None, *args, **values):

        self.code = code
        self.expr = expr

        st = args[0:1] if args else []
        nd = args[1:2] if args else []

        st = st[0] if st else None
        nd = nd[0] if nd else None

        self.fcol = st.col if isinstance(st, Token) else None
        self.dcol = nd.col if isinstance(nd, Token) else self.fcol
        self.tcol = self.dcol + len(str(nd if nd is not None else st)) - 1 if self.dcol else None

        self.message = self.messages[code].format(*args, **values)


    def __str__(self):
        msg = f"({self.code}) {self.dcol or ''}: {self.message}"

        if self.expr is None:
            return msg
        
        expr = self.expr
        if self.fcol is not None and self.tcol is not None:
            if sys.stderr.isatty():
                i = self.fcol - 1
                j = self.tcol
                chars = expr[i:j] if i < len(expr) else " "
                expr = expr[:i] + BOLD + RED + UNDER + chars + RESET + expr[j:]
                
            expr = expr + "\n" + "    "
            expr += " " * (self.fcol - 1) + "^" * (self.tcol - self.fcol + 1)

        return msg + f"\nin: {expr}\n"


class InputError(ComputorException):
    messages = INP_MESSAGES
    def __init__(self, code, expr=None, *args):
        super().__init__("INP_" + code, expr, *args)

class EqualError(ComputorException):
    messages = EQL_MESSAGES
    def __init__(self, code, expr=None, *args):
        super().__init__("EQL_" + code, expr, *args)

class PowerError(ComputorException):
    messages = POW_MESSAGES
    def __init__(self, code, expr=None, *args):
        super().__init__("POW_" + code, expr, *args)

class OperError(ComputorException):
    messages = OPR_MESSAGES
    def __init__(self, code, expr=None, *args):
        super().__init__("OPR_" + code, expr, *args)

class CptorError(ComputorException):
    messages = CPT_MESSAGES
    def __init__(self, code, expr=None, *args, **values):
        super().__init__("CPT_" + code, expr, *args, **values)
