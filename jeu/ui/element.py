# jeu/ui/element.py
"""Élément graphique simple : image positionnée (top-left ou centrée) et redimensionnable."""
import pygame
from pygame.math import Vector2

class ElementUI:
    """Image PNG positionnable, scalable, avec test de collision sur clic."""

    def __init__(self, chemin_image, position=(0, 0), centree=False):
        """Charge `chemin_image` et la positionne en (position) ou centrée sur la surface.

        Parameters
        ----------
        chemin_image : str
                       Chemin du PNG à charger.
        position : tuple[int, int]
                   Position (x, y) en coords logiques.
        centree : bool
                  True pour recentrer l'image dans la surface au dessin.
        """
        self.originale = pygame.image.load(chemin_image)
        self.position = Vector2(position)
        self.centree = centree
        self.image = self.originale
        self.rect = self.image.get_rect(topleft=(int(position[0]), int(position[1])))

    def redimensionner(self, echelle):
        """Met à l'échelle l'image et recalcule la position selon `echelle`.

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer.
        """
        l = max(1, int(self.originale.get_width()  * echelle.x))
        h = max(1, int(self.originale.get_height() * echelle.y))
        self.image = pygame.transform.scale(self.originale, (l, h))
        if self.centree:
            self.rect = self.image.get_rect()              # centre fixé au dessin
        else:
            self.rect = self.image.get_rect(
                topleft=(int(self.position.x * echelle.x),
                         int(self.position.y * echelle.y))
            )

    def contient(self, point):
        """True si `point` (x, y) est dans le rect de l'élément.

        Parameters
        ----------
        point : tuple[int, int]
                Coordonnées (x, y) à tester.

        Returns
        ----------
        bool
             True si le point est dans le rect.
        """
        return self.rect.collidepoint(point)

    def dessiner(self, surface):
        """Blitte l'image (recentre la frame courante si `centree`).

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        if self.centree:
            self.rect.center = surface.get_rect().center
        surface.blit(self.image, self.rect.topleft)