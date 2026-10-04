# Package

Créer un package Python personnalisé pour organiser les modules

[Doc Python](https://docs.python.org/3/tutorial/modules.html#packages)

- module  : un fichier `.py`
- package : un dossier de modules avec un fichier `__init__.py` à la racine

## `__init__.py` : façade

Sans façade, il faudrait connaître le module exact :
Un peu comme en Java

```python
from computorv1.parser import parse
from computorv1.solver import solve
from computorv1.errors import ComputorError
```

L'API du package est exposée dans `__init__.py` :

```python
from .errors import ComputorError
from .parser import parse
from .solver import solve
```
