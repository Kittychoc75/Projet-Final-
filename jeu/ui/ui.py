# jeu/ui/ui.py
from jeu.ui.modales.inventaire import Inventaire

class UI:
    def __init__(self):
        self.modales = [
            Inventaire(),
            # Pause(), Carte(), Dialogue(), … s'ajoutent ici
        ]

    def redimensionner(self, echelle):
        for m in self.modales:
            m.redimensionner(echelle)

    def gerer_clic(self, evenement):
        for m in self.modales:
            m.gerer_clic(evenement)

    def dessiner(self, surface):
        for m in self.modales:
            m.dessiner(surface)