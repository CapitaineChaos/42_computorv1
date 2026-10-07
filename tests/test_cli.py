# Author : CLAUDE OPUS 5.5

# Programme vu de l'extérieur : arguments, stdin, codes de sortie, messages, couleurs.

import io
import os
import pty
import shutil
import subprocess
import sys
import tempfile
import unittest
from os.path import abspath, dirname, join

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from computorv1.cli import main  # noqa: E402
from tests.common import run  # noqa: E402

ROOT = dirname(dirname(abspath(__file__)))


class Errors(unittest.TestCase):
    def test_no_equation(self):
        sys.stdin, stdin = io.TextIOWrapper(io.BytesIO(b"\n  \n")), sys.stdin
        try:
            status, out, err = run()
        finally:
            sys.stdin = stdin
        self.assertEqual((status, out, err), (1, "", "computor: no equation\n"))

    def test_empty_argument(self):
        status, out, err = run("")
        self.assertEqual((status, out), (1, "computor: equation 1: \n\n"))
        self.assertEqual(err, "computor: (EQL_04) missing equal sign\n")

    # Un refus sort en 1, avec l'en-tête seul sur stdout et le message sur stderr.
    def test_report(self):
        status, out, err = run("x % 2 = 0")
        self.assertEqual((status, out), (1, "computor: equation 1: x % 2 = 0\n\n"))
        self.assertEqual(err, "computor: (LXR_01) unexpected character '%' at column 3\n")
        _, _, err = run("x = 1 = 2")
        self.assertEqual(err, "computor: (EQL_01) multiple equal signs at column 7\n")


class Extras(unittest.TestCase):
    def test_steps(self):
        _, out, _ = run("-s", "x^2 - x - 6 = 0")
        self.assertIn("  delta  = b^2 - 4ac\n         = (-1)^2 - 4 * 1 * (-6)\n", out)
        self.assertIn("         = 25\n", out)
        self.assertIn("  x1 = (-b + rac(delta)) / 2a = (1 + rac(25)) / 2 = 3\n", out)
        self.assertIn("         = (0.5, -6.25)\n         is a minimum\n", out)
        _, out, _ = run("-s", "-x^2 + 1 = 0")
        self.assertIn("         = (0, 1)\n         is a maximum\n", out)
        _, out, _ = run("x^2 - x - 6 = 0")
        self.assertNotIn("delta", out)

    def test_stdin(self):
        sys.stdin, stdin = io.TextIOWrapper(io.BytesIO(b"x = 1\n\n2 * x = 1\n")), sys.stdin
        try:
            _, out, _ = run()
        finally:
            sys.stdin = stdin
        self.assertEqual(out.count("The solution is:"), 2)


class EntryPoint(unittest.TestCase):
    def test_internal_error_is_caught(self):
        with tempfile.TemporaryDirectory() as copy:
            shutil.copy(join(ROOT, "computor"), copy)
            shutil.copytree(join(ROOT, "computorv1"), join(copy, "computorv1"))
            solver = join(copy, "computorv1", "builder.py")
            source = open(solver).read()
            header = "def build_eq(coeffs, degree, name):"
            open(solver, "w").write(
                source.replace(header, header + "\n    raise RuntimeError('boum')", 1)
            )
            result = subprocess.run(
                [join(copy, "computor"), "x = 1"], capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 70)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("internal error: RuntimeError: boum", result.stderr)


class Colors(unittest.TestCase):
    def test_no_colors_when_piped(self):
        _, out, _ = run("5 * X^0 + 4 * X^1 = 0")
        self.assertNotIn("\033", out)

    def test_colors_on_a_terminal(self):
        script = (
            "import sys; sys.path.insert(0, %r); "
            "from computorv1.display import colorize; print(colorize('4 * X^0 - 1 * X^1'))"
        )
        primary, secondary = pty.openpty()
        result = subprocess.run(
            [sys.executable, "-c", script % ROOT],
            stdout=secondary,
            stderr=subprocess.PIPE,
            text=True,
        )
        os.close(secondary)
        printed = os.read(primary, 4096).decode()
        os.close(primary)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("\033[32m*\033[0m", printed)
        self.assertIn("\033[36m^0\033[0m", printed)
        self.assertIn("\033[33m-\033[0m", printed)


class Streams(unittest.TestCase):
    # Vrai pipe fermé en lecture : main redirige stdout vers /dev/null avec dup2,
    # ce qui exige un descripteur réel.
    def test_broken_pipe(self):
        read, write = os.pipe()
        os.close(read)
        out, stdout = open(write, "w"), sys.stdout
        try:
            sys.stdout = out
            self.assertEqual(main(["x = 1"]), 1)
        finally:
            sys.stdout = stdout
            out.close()

    def test_stdin_bad_bytes(self):
        stdin = sys.stdin
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(b"\xff = x\nx = 1\n"))
            status, out, err = run()
        finally:
            sys.stdin = stdin
        self.assertEqual(status, 1)
        self.assertIn("The solution is:", out)

    def test_argv_bad_bytes(self):
        status, _, err = run("x\udcff = 0")
        self.assertEqual(
            (status, err), (1, "computor: (LXR_01) unexpected character '�' at column 2\n")
        )


if __name__ == "__main__":
    unittest.main()
