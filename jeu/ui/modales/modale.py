# jeu/ui/modales/modale.py
import pygame


class Modale:
    def __init__(self, icone, panneau, centree=False):
        self.icone = icone        # ElementUI
        self.panneau = panneau    # ElementUI
        self.panneau.centree = centree
        self.ouvert = False

    def gerer_clic(self, evenement):
        if (evenement.type == pygame.MOUSEBUTTONUP
                and evenement.button == 1
                and self.icone.contient(evenement.pos)):
            self.ouvert = not self.ouvert

    def redimensionner(self, echelle):
        self.icone.redimensionner(echelle)
        self.panneau.redimensionner(echelle)

    def dessiner(self, surface):
        self.icone.dessiner(surface)
        if self.ouvert:
            self.panneau.dessiner(surface)