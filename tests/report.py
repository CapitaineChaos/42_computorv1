# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Lance test_saisie.py seul, sans en-têtes unittest ni traceback. Pas de préfixe test_,
# unittest ne le voit pas.
#   common                codes, écarts de tous les groupes
#   common numéros        codes, toutes les saisies de ces groupes, conformes ou non
#   common ok [numéros]   codes, groupes entièrement conformes
#   display [numéros]     message de chaque refus tel que le programme l'affiche, sans
#                         variantes d'espacement ni saisies trop longues, pour vérifier
#                         les colonnes à l'œil
# Numéro : N pour un sujet entier, N.M pour un seul de ses groupes.
#
# Code attendu exigé tel quel : les attentes de test_saisie.py suivent la numérotation de
# tables `messages` des classes d'erreur (errors.py). Un code attendu absent de ces tables est
# marqué « à créer ». REJECTED : refus sous un code de ces tables hors UNK_ et ERR_ ; une
# ébauche « [ @@@ … ] » est un écart.

import io
import re
import sys
import unittest
from contextlib import redirect_stdout
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import tests.test_saisie as saisie  # noqa: E402
from computorv1.display import BD_RED, CYAN, GREEN, RST  # noqa: E402
from computorv1.errors import ComputorException  # noqa: E402
from computorv1.parser import MAX_LEN, parse  # noqa: E402

MODES = ("common", "display")
if sys.argv[1:2] not in ([mode] for mode in MODES):
    sys.exit(f"report: mode {' ou '.join(MODES)} attendu")
DISPLAY = sys.argv[1] == "display"


# Codes de toutes les classes d'erreur : chacune porte sa table dans `messages`.
def all_messages(cls=ComputorException):
    codes = dict(getattr(cls, "messages", {}))
    for sub in cls.__subclasses__():
        codes |= all_messages(sub)
    return codes


MESSAGES = all_messages()

# KO : accepté au lieu de refusé ou l'inverse, plantage, ébauche. WRONG : refusé comme
# attendu, mais sous un autre code ; compte comme écart.
if sys.stdout.isatty():
    KO, OK, WRONG = f"{BD_RED}KO{RST}", f"{GREEN}OK{RST}", f"{CYAN}OK{RST}"
else:
    KO, OK, WRONG = "KO ", "OK ", "OK~"

SHOW_OK = not DISPLAY and "ok" in sys.argv[2:]
WANTED = [arg for arg in sys.argv[2:] if arg != "ok"]
DETAIL = bool(WANTED) and not SHOW_OK


def real(code):
    shaped = re.fullmatch(r"[A-Z]{3}_\d\d", code) is not None
    return shaped and code in MESSAGES and code[:3] not in ("UNK", "ERR")


def conforms(got, expected):
    if expected == saisie.REJECTED:
        return got is not None and real(got)
    return got == expected


def name(test):
    return f"{NUMBER[test.id()]}  {type(test).__name__}.{test._testMethodName[5:]}"


def head(test):
    return f"{name(test)}  {test.shortDescription()}"


# Remplace Input.check. Une variante d'espacement n'est listée que si son verdict diffère de
# l'original ; les saisies conformes ne sont listées qu'en détail.
def check(self, cases):
    seen, lines, bad, wrong = set(), [], 0, 0
    for source, expected in cases:
        if source in saisie.PENDING:
            PENDING_SEEN[source] = NUMBER[self.id()]
        original = saisie.verdict(source)
        for form in [source, *saisie.respaced(source)]:
            if form in seen:
                continue
            seen.add(form)
            got = original if form == source else saisie.verdict(form)
            if form != source and got == original:
                continue
            good = conforms(got, expected)
            refused = expected is not None and got is not None and real(got)
            bad += not good
            wrong += not good and refused
            if good and not DETAIL:
                continue
            mark = OK if good else WRONG if refused else KO
            missing = expected not in (None, saisie.REJECTED, *MESSAGES)
            pending = saisie.PENDING.get(form)
            lines.append(
                f"  {mark}  {saisie.shown(form):44}"
                f" obtenu {got or 'accepté':20} attendu {expected or 'accepté'}"
                + ("  (à créer)" if missing else "")
                + (f"  (à trancher : {pending})" if pending else "")
            )
    if DETAIL or (bad and not SHOW_OK):
        codes = f" dont {wrong} de code" if wrong else ""
        print(f"\n{head(self)}  ({bad} écarts{codes} sur {len(seen)})")
        print("\n".join(lines))
    if bad:
        self.fail()


# Colonne que l'en-tête « (code) colonne: message » affiche, entre parenthèses, puis code et
# colonnes du refus (« col 3 », ou « col 3-5 » sur plusieurs caractères), puis lignes du
# message sous l'en-tête ; None si la saisie est acceptée. Un caractère non imprimable
# devient '·' : un seul caractère, les colonnes restent.
def rendering(source):
    try:
        with redirect_stdout(io.StringIO()):
            parse(source)
    except ComputorException as error:
        if error.expr is not None:
            error.expr = "".join(c if c.isprintable() else "·" for c in error.expr)
        header, *block = str(error).rstrip("\n").split("\n")
        shown = re.match(r"\(\w+\) ([^:]*):", header)
        label = f"{'(' + (shown.group(1) if shown else '?') + ')':>4} {error.code}"
        if error.fcol is not None:
            same = error.tcol in (None, error.fcol)
            label += f" col {error.fcol}" + ("" if same else f"-{error.tcol}")
        return label, block
    except Exception as error:
        return saisie.crash(error), []
    return None


# Remplace Input.check en mode display : saisies d'origine seules, refus seuls. Au-delà de
# MAX_LEN, refus en bloc (CPT_02) : aucune colonne à vérifier.
def show(self, cases):
    lines = []
    for source, _ in cases:
        if len(source) > MAX_LEN:
            continue
        shown = rendering(source)
        if shown is None:
            continue
        label, block = shown
        width = max(len(label), len("(99) OPR_01 col 199-200"))
        if not block:
            lines.append(f"  {label:{width}}  (sans saisie) {saisie.shown(source)}")
            continue
        lines.append(f"  {label:{width}}  {block[0]}")
        lines += [f"  {'':{width}}  {line}" for line in block[1:]]
    if lines:
        print(f"\n{head(self)}")
        print("\n".join(lines))


saisie.Input.check = show if DISPLAY else check

# Saisies de saisie.PENDING rencontrées : saisie → numéro de groupe.
PENDING_SEEN = {}


class Report(unittest.TestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        if SHOW_OK:
            print(head(test))

    def addError(self, test, err):
        super().addError(test, err)
        if SHOW_OK:
            return
        print(f"\n{name(test)}  plantage du test : {err[0].__name__}: {err[1]}")


# Sujets et groupes dans l'ordre de test_saisie.py. Un groupe ajouté décale les numéros
# suivants de son sujet.
TOPICS = [
    cls
    for cls in vars(saisie).values()
    if isinstance(cls, type) and issubclass(cls, saisie.Input) and cls is not saisie.Input
]
groups, NUMBER = [], {}
for i, topic in enumerate(TOPICS, 1):
    methods = [method for method in vars(topic) if method.startswith("test_")]
    for j, method in enumerate(methods, 1):
        test = topic(method)
        groups.append(test)
        NUMBER[test.id()] = f"{i}.{j}"

numbers = set(NUMBER.values()) | {str(i) for i in range(1, len(TOPICS) + 1)}
unknown = [arg for arg in WANTED if arg not in numbers]
if unknown:
    topics = ", ".join(f"{i} {topic.__name__}" for i, topic in enumerate(TOPICS, 1))
    sys.exit(f"report: {' '.join(unknown)} inconnu ; sujets {topics}")
if WANTED:
    groups = [
        test
        for test in groups
        if NUMBER[test.id()] in WANTED or NUMBER[test.id()].split(".")[0] in WANTED
    ]

result = Report()
unittest.TestSuite(groups).run(result)
if DISPLAY:
    sys.exit()
failed = len(result.failures) + len(result.errors)
print(f"\n{result.testsRun - failed} groupes conformes sur {result.testsRun}")
if PENDING_SEEN:
    print("\nÀ trancher :")
    questions = {}
    for source, number in PENDING_SEEN.items():
        questions.setdefault(saisie.PENDING[source], []).append((number, source))
    for question, cases in questions.items():
        numbers = " ".join(sorted({number for number, _ in cases}))
        examples = ", ".join(saisie.shown(source) for _, source in cases[:3])
        print(f"  {question}\n    {len(cases)} saisies, groupes {numbers} : {examples}")
