import pygame
from pygame.math import Vector2

from jeu.ui import polices


class Jauge:
    COULEUR_FOND = (182, 181, 249)
    COULEUR_BORDURE = (133, 132, 180)
    COULEUR_TEXTE = (255, 255, 255)
    TAILLE_POLICE = 20
    PADDING = 5

    def __init__(self, valeur, valeur_min, valeur_max, position, largeur, hauteur, couleur, texte=""):
        self.valeur_min = valeur_min
        self.valeur_max = valeur_max
        self.position = Vector2(position)
        self.largeur = largeur
        self.hauteur = hauteur
        self.couleur = couleur
        self.texte = texte
        self.valeur = self._clamper(valeur)
        self.redimensionner(Vector2(1, 1))

    def _clamper(self, valeur):
        return max(self.valeur_min, min(self.valeur_max, valeur))

    def mettre_a_jour(self, nouvelle_valeur):
        self.valeur = self._clamper(nouvelle_valeur)
        self._rendre_texte()

    def calculer_pourcentage(self):
        return (self.valeur - self.valeur_min) / (self.valeur_max - self.valeur_min)

    def _rendre_texte(self):
        if not self.texte:
            self._texte_surface = None
            return
        self._texte_surface = self._police.render(
            f"{self.texte}: {self.valeur}/{self.valeur_max}",
            True,
            self.COULEUR_TEXTE,
        )

    def redimensionner(self, echelle):
        self.echelle = Vector2(echelle)
        taille_police = max(1, int(self.TAILLE_POLICE * self.echelle.y))
        self._police = polices.pixelade(taille_police)
        self._x = int(self.position.x * self.echelle.x)
        self._y = int(self.position.y * self.echelle.y)
        self._largeur = max(1, int(self.largeur * self.echelle.x))
        self._hauteur = max(1, int(self.hauteur * self.echelle.y))
        self._padding_x = int(self.PADDING * self.echelle.x)
        self._padding_y = int(self.PADDING * self.echelle.y)
        self._rendre_texte()

    def dessiner(self, surface):
        pygame.draw.rect(surface, self.COULEUR_FOND, (self._x, self._y, self._largeur, self._hauteur))
        largeur_remplie = int(self._largeur * self.calculer_pourcentage())
        pygame.draw.rect(surface, self.couleur, (self._x, self._y, largeur_remplie, self._hauteur))
        pygame.draw.rect(surface, self.COULEUR_BORDURE, (self._x, self._y, self._largeur, self._hauteur), 2)
        if self._texte_surface is not None:
            surface.blit(self._texte_surface, (self._x + self._padding_x, self._y + self._padding_y))
