"""Moteur runtime du scénario : charge le YAML, gère l'état (flags), répond aux requêtes."""
from jeu.dialogues.dialogue import Dialogue
from jeu.dialogues.personnage import Personnage
from jeu.scenario.chargeur import charger


class Scenario:
    def __init__(self, chemin_yaml):
        donnees = charger(chemin_yaml)
        self.niveau_initial = donnees.niveau_initial
        self.chaine = list(donnees.chaine)
        self.flags = set(donnees.flags_initiaux)
        # Personnages : runtime objects (sprites chargés une fois)
        self.personnages = {
            pid: Personnage(
                nom=p.nom,
                couleur_nom=p.couleur_nom,
                sprite_carte=p.sprite_carte,
                sprite_dialogue_1=p.sprite_dialogue_1,
                sprite_dialogue_2=p.sprite_dialogue_2,
                facteur_taille_carte=p.facteur_taille_carte,
            )
            for pid, p in donnees.personnages.items()
        }
        self._dialogues = donnees.dialogues
        self._transitions = {t.niveau: t for t in donnees.transitions}

    # --- Niveau / chaîne ---

    def niveau_suivant(self, nom):
        if nom not in self.chaine:
            return None
        i = self.chaine.index(nom)
        return self.chaine[i + 1] if i + 1 < len(self.chaine) else None

    def niveau_precedent(self, nom):
        if nom not in self.chaine:
            return None
        i = self.chaine.index(nom)
        return self.chaine[i - 1] if i > 0 else None

    # --- Dialogues ---

    def dialogue_a_declencher(self, nom_niveau, couleur):
        """Retourne le runtime Dialogue à jouer à (niveau, couleur), ou None."""
        for d in self._dialogues:
            if d.niveau == nom_niveau and d.couleur == couleur and self._conditions_ok(d):
                return self._materialiser(d)
        return None

    def personnage_present(self, nom_niveau, couleur):
        """Retourne le Personnage à dessiner sur la carte à (niveau, couleur), ou None.

        Visible tant qu'un dialogue triggerable existe.
        """
        for d in self._dialogues:
            if d.niveau == nom_niveau and d.couleur == couleur and self._conditions_ok(d):
                return self.personnages[d.personnage]
        return None

    def _materialiser(self, data):
        return Dialogue(
            personnage=self.personnages[data.personnage],
            messages=data.messages,
            couleurs_speciales=data.couleurs_speciales,
            on_termine=lambda: self._poser_flags(data.pose_flags),
        )

    def _poser_flags(self, flags):
        for f in flags:
            self.flags.add(f)

    # --- Transitions ---

    def transition_autorisee(self, nom_niveau):
        """Retourne (autorise: bool, indice_echec: str | None)."""
        t = self._transitions.get(nom_niveau)
        if t is None:
            return True, None
        if self._conditions_ok(t):
            return True, None
        return False, t.indice_echec

    # --- Conditions ---

    def _conditions_ok(self, item):
        if any(f in self.flags for f in item.interdit):
            return False
        if not all(f in self.flags for f in item.requiert):
            return False
        return True
