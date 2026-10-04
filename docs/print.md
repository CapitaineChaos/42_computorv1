# Print

`print(*objects, sep=' ', end='\n', file=None, flush=False)`

- sep : Définit la chaîne de caractères insérée entre chaque valeur affichée. `' '` par défaut
- end : Définit la chaîne de caractères ajoutée à la toute fin de l'affichage. `'\n'` par défaut
- file : Rediriger la sortie vers un objet fichier 
- flush : Force le vidage immédiat du flux de sortie



 
## Mode texte
```python
# Écrire (et écraser) dans un fichier
with open("journal.txt", "w", encoding="utf-8") as f:
    print("Première ligne du journal.", file=f)

# Ajouter du texte à la fin d'un fichier existant
with open("journal.txt", "a", encoding="utf-8") as f:
    print("Nouvelle entrée en fin de fichier.", file=f)
```

## Flux standards du système (sys)
Accès aux flux standards du terminal.
- sys.stdout (Standard Output)
- sys.stderr (Standard Error)
```python
import sys

# Équivaut au print classique
print("Message normal", file=sys.stdout)

# Afficher explicitement une erreur dans le flux d'erreur
print("ERREUR : Le fichier est introuvable !", file=sys.stderr)
```


## Flux en mémoire (io.StringIO)
Simuler un fichier directement dans la RAM. Utile pour capturer le texte généré par un `print()`
On peut le manipuler plus tard comme une var string c'est cool
```python
import io

# Création d'un fichier virtuel en mémoire
flux_memoire = io.StringIO()

# On print à l'intérieur
print("Texte capturé en mémoire", file=flux_memoire)
print("Deuxième ligne", file=flux_memoire)

# Récupération du contenu sous forme de chaîne de caractères
contenu = flux_memoire.getvalue()
print("Résultat récupéré :", contenu) 

flux_memoire.close()
```

## Custom Wrappers
On peut intercepter ce que `print()` envoie si classe possède la méthode write().
```python
class MonJournaliseur:
    def write(self, message):
        if message.strip():
            sys.stdout.write(f"[LOG] {message}\n")
            
    def flush(self):
        # Requis par certaines implémentations de print()
        sys.stdout.flush()

journal = MonJournaliseur()
print("Bonjour le monde !", file=journal)
# Résultat dans la console : [LOG] Bonjour le monde !
```



