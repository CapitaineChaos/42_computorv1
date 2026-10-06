class ComputorError(Exception):

    def __init__(self, message, code=None):
        self.message = message
        self.code = code

    def __str__(self):
        return f"{'(' + self.code + ') ' if self.code else ''}{self.message}"
