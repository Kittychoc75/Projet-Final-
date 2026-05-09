import pygame
from pygame.math import Vector2

from jeu.ui import polices


class Label:
    COULEUR = (133, 132, 180)
    PADDING = 10
    TAILLE_POLICE = 35

    def __init__(self, position, texte=""):
        self.position = Vector2(position)
        self.texte = texte
        self.redimensionner(Vector2(1, 1))

    def redimensionner(self, echelle):
        self.echelle = Vector2(echelle)
        if self.texte:
            taille_police = max(1, int(self.TAILLE_POLICE * self.echelle.y))
            police = polices.pixelade(taille_police)
            self._texte_surface = police.render(self.texte, True, self.COULEUR)
        else:
            self._texte_surface = None
        self._x = int(self.position.x * self.echelle.x)
        self._y = int(self.position.y * self.echelle.y)
        self._padding_x = int(self.PADDING * self.echelle.x)
        self._padding_y = int(self.PADDING * self.echelle.y)

    def dessiner(self, surface):
        if self._texte_surface is None:
            return
        largeur = self._texte_surface.get_width() + self._padding_x * 2
        hauteur = self._texte_surface.get_height() + self._padding_y * 2
        pygame.draw.rect(surface, self.COULEUR, (self._x, self._y, largeur, hauteur), 2)
        surface.blit(self._texte_surface, (self._x + self._padding_x, self._y + self._padding_y))
