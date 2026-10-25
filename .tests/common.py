# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

import io
import logging
from contextlib import redirect_stderr, redirect_stdout

from computorv1.cli import main

# Les traces DEBUG du parser noient la sortie des tests.
logging.disable(logging.CRITICAL)


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = main(list(argv))
    return status, out.getvalue(), err.getvalue()
