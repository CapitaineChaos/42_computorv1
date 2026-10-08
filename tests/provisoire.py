# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Provisoire, le temps d'écrire le parser : lance test_saisie.py seul et n'affiche que les
# écarts, sans en-têtes unittest ni traceback. Pas de préfixe test_, unittest ne le voit pas.

import sys
import unittest
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import tests.test_saisie as saisie  # noqa: E402


class Report(unittest.TestResult):
    def addFailure(self, test, err):
        super().addFailure(test, err)
        count, lines = str(err[1]).split("\n", 1)
        print(f"\n{test._testMethodName[5:]}  {test.shortDescription()}  ({count})")
        print(lines)

    def addError(self, test, err):
        super().addError(test, err)
        print(f"\n{test._testMethodName[5:]}  plantage du test : {err[0].__name__}: {err[1]}")


tests = unittest.defaultTestLoader.loadTestsFromModule(saisie)
result = Report()
tests.run(result)
failed = len(result.failures) + len(result.errors)
print(f"\n{result.testsRun - failed} groupes conformes sur {result.testsRun}")
