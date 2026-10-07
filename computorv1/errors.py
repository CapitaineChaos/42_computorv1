MESSAGES = {
    "LXR_01": "unexpected character '{text}' at column {col}",
    "NBR_01": "missing operator between numbers at column {col}",
    "EXP_01": "missing operand after exponent at column {col}",
    "SGN_01": "consecutive signs at column {col}",
    "EQL_01": "multiple equal signs at column {col}",
    "EQL_02": "missing left side of equation at column {col}",
    "EQL_03": "missing right side of equation at column {col}",
    "EQL_04": "missing equal sign",
    "MUL_01": "missing operand after multiply at column {col}, ",

    "EQ01": "missing left side of equation",
    "EQ02": "missing equal sign at column {col}",
    "EQ03": "unexpected '{text}' at column {col}",
    "EQ04": "missing right side of equation",
    "ST01": "consecutive signs at column {col}",
    "TE01": "ambigous usage of operator at column {col}, '{text}'",
    "TE02": "missing operator between numbers at column {col}",
    "FA01": "factor expected at column {col}",
    "FA02": "unexpected '{text}' at column {col}",
    "FA03": "unknown already defined, illegal name '{text}'",
    "EX01": "exponent error: missing number at column {col}",
    "EX02": "exponent must not have a sign at column {col}",
    "EX03": "exponent must be an integer at column {col}",
    "EX04": "chained exponent is ambiguous at column {col}",
    "EX05": "missing base for exponent at column {col}",
    "EX06": "exponent cannot be applied to operator at column {col}",
}


class ComputorError(Exception):

    def __init__(self, code, **values):
        self.code = code
        self.message = MESSAGES[code].format(**values)

    def __str__(self):
        return f"({self.code}) {self.message}"
