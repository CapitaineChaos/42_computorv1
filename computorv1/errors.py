# Saisie refusée : le message, et si possible la position du caractère fautif dans text,
# le texte tapé par défaut, pour que cli.py affiche un ^ dessous.
class ComputorError(Exception):
    def __init__(self, message, position=None, text=None):
        super().__init__(message)
        self.position = position
        self.text = text
