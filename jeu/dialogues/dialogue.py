"""Runtime d'un dialogue : itère sur une liste de messages avec callback de fin optionnel."""


class Dialogue:
    """Dialogue d'un personnage : suite de messages + couleurs spéciales par mot."""

    def __init__(self, personnage, messages, couleurs_speciales=None, on_termine=None):
        """Initialise au premier message. `on_termine` est appelé à la fin du dernier message.

        Parameters
        ----------
        personnage : Personnage
                     PNJ qui parle (sprites carte + dialogue).
        messages : list[str]
                   Suite des messages à afficher.
        couleurs_speciales : dict | None
                             Map mot → couleur RGB pour les mots spéciaux.
        on_termine : callable | None
                     Callback `() -> None` appelé à la fin du dialogue.
        """
        self.personnage = personnage
        self.messages = list(messages)
        self.couleurs_speciales = dict(couleurs_speciales or {})
        self.index = 0
        self.on_termine = on_termine

    def message_courant(self):
        """Texte du message à afficher (toujours valide tant qu'on n'a pas appelé `suivant` après le dernier).

        Parameters
        ----------

        Returns
        ----------
        str
             Message à afficher actuellement.
        """
        return self.messages[self.index]

    def suivant(self):
        """Avance au message suivant. Retourne False si on était sur le dernier.

        Parameters
        ----------

        Returns
        ----------
        bool
             True si on a avancé, False si on était sur le dernier message.
        """
        if self.index + 1 < len(self.messages):
            self.index += 1
            return True
        return False

    def reinitialiser(self):
        """Remet le dialogue au premier message (rejouable)."""
        self.index = 0
