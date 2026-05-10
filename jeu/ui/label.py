"""Libellé encadré : texte court entouré d'un rectangle vide (titres de panneaux)."""
import pygame
from pygame.math import Vector2

from jeu.ui import polices


class Label:
    """Encart de texte (titre) entouré d'une bordure simple."""

    COULEUR = (133, 132, 180)
    PADDING = 10
    TAILLE_POLICE = 35

    def __init__(self, position, texte=""):
        """Crée un libellé à `position` (coords logiques) affichant `texte`.

        Parameters
        ----------
        position : tuple[int, int]
                   Position (x, y) en coords logiques.
        texte : str
                Texte du libellé (vide = invisible).
        """
        self.position = Vector2(position)
        self.texte = texte
        self.redimensionner(Vector2(1, 1))

    def redimensionner(self, echelle):
        """Recalcule la surface texte et les paddings selon `echelle`.

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer.
        """
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
        """Dessine la bordure puis le texte centré dedans (no-op si pas de texte).

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        if self._texte_surface is None:
            return
        largeur = self._texte_surface.get_width() + self._padding_x * 2
        hauteur = self._texte_surface.get_height() + self._padding_y * 2
        pygame.draw.rect(surface, self.COULEUR, (self._x, self._y, largeur, hauteur), 2)
        surface.blit(self._texte_surface, (self._x + self._padding_x, self._y + self._padding_y))
