# Les signaux

## rAPPEL

|Signal	|N°|	Origine typique	|Action par défaut|
|-|-|-|-|
|SIGHUP |	1 |	terminal fermé|	terminer|
|SIGINT |	2 |	Ctrl+C|	terminer|
|SIGQUIT |	3 |	Ctrl+\ |	core dump|
|SIGKILL |	9 |	kill -9|	terminer (non interceptable)|
|SIGSEGV |	11 |	accès mémoire invalide|	core dump|
|SIGPIPE |	13 |	écriture dans un pipe sans lecteur|	terminer|
|SIGTERM |	15 |	kill|	terminer|
|SIGCHLD |	17 |	un fils s’est terminé|	ignorer|
|SIGTSTP |	20 |	Ctrl+Z|	suspendre|

## Intercepter les signaux

Installation du gestionnaire de signaux par le module signal évidemment.

```python
import signal, sys

def on_term(signum, frame):
    print("arrêt propre", file=sys.stderr)
    sys.exit(0)

signal.signal(signal.SIGTERM, on_term)
```


## Le cas du clavier

SIGINT lève KeyboardInterrupt qui hérite de BaseException.
C'est pour pas qu'un `except Exception:` l'intercepte bêtement...

```python
except KeyboardInterrupt:
    print(file=sys.stderr)
    return 130
```


## Le cas du pipe

Quand on fait ça par exemple : 

```bash
python3 -c "for i in range(10**6): print(i)" | head -1
```

On obtient une jolie erreur (on ignore le Traceback) :
En fait deux erreurs
```txt
BrokenPipeError: [Errno 32] Broken pipe
Exception ignored while flushing sys.stdout:
BrokenPipeError: [Errno 32] Broken pipe
```


Parce que en C on a pas ce problème, par défaut ça meurt en silence (sauf quand c'est vraiment très grave).
Pour régler ça en python on fait ça :

```python
except BrokenPipeError:
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    return 1
```
Quand on redirige dans `/dev/null` il n'y a plus d'échec de vidage du tampon dans un pipe mort, donc la 2èeme erreur ne se déclenche plus.

