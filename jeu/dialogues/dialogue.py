class Dialogue:
    """Dialogue d'un personnage : suite de messages + couleurs spéciales par mot."""

    def __init__(self, personnage, messages, couleurs_speciales=None, on_termine=None):
        self.personnage = personnage
        self.messages = list(messages)
        self.couleurs_speciales = dict(couleurs_speciales or {})
        self.index = 0
        self.on_termine = on_termine

    def message_courant(self):
        return self.messages[self.index]

    def suivant(self):
        """Avance au message suivant. Retourne False si on était sur le dernier."""
        if self.index + 1 < len(self.messages):
            self.index += 1
            return True
        return False

    def reinitialiser(self):
        self.index = 0
