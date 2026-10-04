# Lint

[Ruff linting](https://docs.astral.sh/ruff/linter/)
Bcp d'exemples dans la doc en ligne


Règles ruff organisées par famille :

| Préfixe |	Origine	| Vérification |
|-|-|-|
| E |	pycodestyle |	Erreurs de style (espaces, indentation) |
| W |	pycodestyle |	Avertissements de style |
| F |	Pyflakes |	Erreurs logiques (variables non utilisées, imports manquants) |
| I |	isort |	Organisation des imports |
| B |	flake8-bugbear |	Bugs potentiels et mauvaises pratiques |
| UP |	pyupgrade |	Syntaxe obsolète à moderniser |
| SIM |	flake8-simplify |	Code qui peut être simplifié |
| D |	pydocstyle |	Docstrings manquantes ou mal formatées |
| N |	pep8-naming |	Conventions de nommage |
| S |	flake8-bandit |	Problèmes de sécurité |

## Config

```toml
[tool.ruff.lint]
select = ["E1", "E2", "F", "W", "I", "B"]
ignore = ["F401"]
```

ou 
```toml
[tool.ruff.lint]
preview = true
select = [
    "correctness",
    "suspicious",
    "complexity",
    "performance",
    "style",
]
```

## Règles par défaut et en préversion

Sans `select`, ruff vérifie uniquement les règles `E4`, `E7`, `E9` et `F` :

Dans ruff, `E2`, `E3` et toutes les règles `E1` sauf `E101` sont des règles en **préversion** : toujours en test, désactivées sauf si `preview = true` est ajouté sous `[tool.ruff.lint]`.
