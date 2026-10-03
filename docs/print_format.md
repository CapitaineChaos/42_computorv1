# f-strings

Méthode moderne. les autres sont deprecated ou déconseillées.

### Cas classique

```python
nom = "Alice"
age = 25

print(f"Bonjour {nom}, vous avez {age} ans.")
# Résultat : Bonjour Alice, vous avez 25 ans.
```


### Arrondi (Float)

```python
pi = 3.14159265
print(f"Pi arrondi : {pi:.2f}")  # .2f = 2 chiffres après la virgule
# Résultat : Pi arrondi : 3.14
```


### Séparateurs

```python
population = 68000000
print(f"Population : {population:_}")  # Utilise _ ou , comme séparateur
# Résultat : Population : 68_000_000
```


### Pourcentage

```python
score = 0.856
print(f"Taux de réussite : {score:.1%}")
# Résultat : Taux de réussite : 85.6%
```

---

# Alignements et remplissages
- `<` : Aligne le texte à gauche (comportement par défaut pour le texte).
- `>` : Aligne le texte à droite (comportement par défaut pour les nombres).
- `^` : Centre le texte.


### Simple texte

```python
prenom = "Léa"

print(f"|{prenom:<10}|")  # À gauche sur 10 caractères
# Résultat : |Léa       |

print(f"|{prenom:>10}|")  # À droite sur 10 caractères
# Résultat : |       Léa|

print(f"|{prenom:^10}|")  # Centré sur 10 caractères
# Résultat : |   Léa    |
```


### Simple texte + char de remplissage

```python
titre = "Chapitre 1"
page = 42

# Remplissage avec des points (.) pour un sommaire
print(f"{titre:.<25}{page:.>5}")
# Résultat : Chapitre 1...................42

# Remplissage avec des tirets (-) pour un titre centré
print(f"{' FIN ':-^30}")
# Résultat : ------------ FIN -------------
```


### Remplissage de nombres avec des 0

```python
identifiant = 7
print(f"ID: {identifiant:05d}")  # Le 'd' indique un entier (decimal)
# Résultat : ID: 00007

heure = 9
minute = 5
print(f"{heure:02d}:{minute:02d}")
# Résultat : 09:05
```


### Le signe + ou - avec l'alignement (=)

L'alignement = est spécifique aux nombres. Il permet de forcer le signe (+ ou -) à se positionner tout à gauche, et le nombre tout à droite, en remplissant l'espace vide entre les deux.
```python
gain = 150
perte = -80

print(f"Gain  : {gain:=+10}")   # Force le signe '+' ou '-'
print(f"Perte : {perte:=10}")    # Conserve le signe '-' par défaut
# Résultat :
# Gain  : +      150
# Perte : -       80
```

### Tableau dynamique
```python
produits = [("Café", 1.50), ("Croissant au beurre", 2.20), ("Jus d'orange", 3.80)]

print(f"{'PRODUIT':<25} | {'PRIX':^8}")
print("-" * 36)

for nom, prix in produits:
    # Le nom est aligné à gauche sur 25 caractères (rempli d'espaces)
    # Le prix est aligné à droite sur 5 caractères avec 2 décimales
    print(f"{nom:<25} | {prix:>5.2f} €")
```

Résultat
```
PRODUIT                   |   PRIX  
------------------------------------
Café                      |  1.50 €
Croissant au beurre       |  2.20 €
Jus d'orange              |  3.80 €
```