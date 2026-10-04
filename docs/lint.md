# Lint

[Ruff linting](https://blog.stephane-robert.info/docs/developper/programmation/python/ruff/)


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

### Lire un code de règle

- La lettre désigne l'outil d'origine
- Le premier chiffre désigne une catégorie
- Les numéros suivants désignent la règle dans cette catégorie


### `E` et `W` : pycodestyle

Mêmes catégories pour les deux :
- `E` : erreur
- `W` : avertissement


| Préfixe | Catégorie         | Exemple                                |
|---------|-------------------|----------------------------------------|
| `E1`    | indentation       | `E101` tabulations et espaces mélangés |
| `E2`    | espaces           | preview                                |
| `E3`    | lignes vides      | preview                                |
| `E4`    | imports           | `E401` `import os, sys`                |
| `E5`    | longueur de ligne | `E501` ligne de plus de 100 caractères |
| `E7`    | instructions      | `E722` `except:` nu                    |
| `E9`    | exécution         | `E902` fichier illisible               |
| `W1`    | indentation       | `W191` indentation par tabulation      |
| `W2`    | espaces           | `W291` espaces en fin de ligne         |
| `W5`    | longueur de ligne | `W505` docstring trop longue           |
| `W6`    | obsolescence      | `W605` `"\d"` au lieu de `r"\d"`       |

### `F` : Pyflakes

| Préfixe | Catégorie                  | Exemple                          |
|---------|----------------------------|----------------------------------|
| `F4`    | imports                    | `F401` import non utilisé        |
| `F5`    | chaînes `%` et `.format()` | `F507` `"%s %s" % (a,)`          |
| `F6`    | comparaisons, dicts        | `F632` `x is "a"`                |
| `F7`    | instruction mal placée     | `F701` `break` hors d'une boucle |
| `F8`    | noms                       | `F821` nom indéfini              |
| `F9`    | raise                      | `F901` `raise NotImplemented`    |

### `I` : isort, ordre des imports

| Code   | Vérification                         |
|--------|--------------------------------------|
| `I001` | imports non triés ou mal groupés     |
| `I002` | import obligatoire absent (inactive) |



### `B` : flake8-bugbear, bugs probables

| Code   | Exemple                | Problème                           |
|--------|------------------------|------------------------------------|
| `B006` | `def f(x=[])`          | liste partagée par tous les appels |
| `B007` | `for i in x:` sans `i` | variable de boucle inutile         |
| `B904` | `raise` sans `from`    | masque l'exception d'origine       |
| `B905` | `zip()` sans `strict=` | tronque la liste la plus longue    |

### Règles par défaut et règles preview

- Sans `select` : `E4`, `E7`, `E9` et `F`
- Preview : `E2`, `E3`, `E1` sauf `E101`, inactives sauf `preview = true`
