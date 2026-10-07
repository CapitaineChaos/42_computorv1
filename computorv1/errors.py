MESSAGES = {
    "LXR_01": "unexpected character '{text}' at column {col}",

    "NBR_01": "missing operator between numbers at column {col}",

    "EXP_01": "missing operand after exponent at column {col}",
    "EXP_02": "missing operand before exponent at column {col}",

    "SGN_01": "consecutive signs at column {col}",
    "SGN_02": "missing operand before sign at column {col}",
    "SGN_03": "missing operand after sign at column {col}",

    "EQL_01": "multiple equal signs at column {col}",
    "EQL_02": "missing left side of equation at column {col}",
    "EQL_03": "missing right side of equation at column {col}",
    "EQL_04": "missing equal sign",

    "MUL_01": "missing operand after multiply at column {col}",
    "MUL_02": "missing operand before multiply at column {col}",

    "VAR_01": "multiple variables found: '{text}' at column {col}",

}


class ComputorError(Exception):

    def __init__(self, code, **values):
        self.code = code
        self.message = MESSAGES[code].format(**values)

    def __str__(self):
        return f"({self.code}) {self.message}"
