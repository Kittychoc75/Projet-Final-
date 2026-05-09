# jeu/ui/ui.py
from jeu.ui.indice import IndiceFlottant
from jeu.ui.modales.dialogue import ModaleDialogue
from jeu.ui.modales.inventaire import Inventaire


class UI:
    def __init__(self):
        self.inventaire = Inventaire()
        self.dialogue = ModaleDialogue()
        self.indice = IndiceFlottant()
        self.modales = [self.inventaire, self.dialogue]

    def declencher_dialogue(self, dialogue):
        self.dialogue.declencher(dialogue)

    def afficher_indice(self, message):
        self.indice.afficher(message)

    def bloque_jeu(self):
        return any(m.bloque_jeu for m in self.modales)

    def redimensionner(self, echelle):
        for m in self.modales:
            m.redimensionner(echelle)
        self.indice.redimensionner(echelle)

    def gerer_evenement(self, evenement):
        for m in self.modales:
            m.gerer_evenement(evenement)

    def mettre_a_jour(self, dt):
        for m in self.modales:
            m.mettre_a_jour(dt)
        self.indice.mettre_a_jour(dt)

    def dessiner(self, surface):
        for m in self.modales:
            m.dessiner(surface)
        self.indice.dessiner(surface)
