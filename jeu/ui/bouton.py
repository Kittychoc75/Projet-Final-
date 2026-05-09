import pygame
from pygame.math import Vector2

from jeu.ui import polices


class Bouton:
    COULEUR_FOND = (200, 200, 200)
    COULEUR_BORDURE = (0, 0, 0)
    COULEUR_TEXTE = (0, 0, 0)
    TAILLE_POLICE = 28

    def __init__(self, position, largeur, hauteur, texte):
        self.position = Vector2(position)
        self.largeur = largeur
        self.hauteur = hauteur
        self.texte = texte
        self.redimensionner(Vector2(1, 1))

    def redimensionner(self, echelle):
        self.echelle = Vector2(echelle)
        x = int(self.position.x * self.echelle.x)
        y = int(self.position.y * self.echelle.y)
        l = max(1, int(self.largeur * self.echelle.x))
        h = max(1, int(self.hauteur * self.echelle.y))
        self._rect = pygame.Rect(x, y, l, h)
        taille_police = max(1, int(self.TAILLE_POLICE * self.echelle.y))
        police = polices.pixelade(taille_police)
        self._texte_surface = police.render(self.texte, True, self.COULEUR_TEXTE)
        self._texte_rect = self._texte_surface.get_rect(center=self._rect.center)

    def contient(self, point):
        return self._rect.collidepoint(point)

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.COULEUR_FOND, self._rect)
        pygame.draw.rect(surface, self.COULEUR_BORDURE, self._rect, 2)
        surface.blit(self._texte_surface, self._texte_rect)
