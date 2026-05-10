"""Barre horizontale type jauge de vie/XP : valeur clampée, libellé optionnel, scalable."""
import pygame
from pygame.math import Vector2

from jeu.ui import polices


class Jauge:
    """Barre `valeur / valeur_max` avec fond, remplissage coloré, bordure et libellé."""


    COULEUR_FOND = (182, 181, 249)
    COULEUR_BORDURE = (133, 132, 180)
    COULEUR_TEXTE = (255, 255, 255)
    TAILLE_POLICE = 20
    PADDING = 5

    def __init__(self, valeur, valeur_min, valeur_max, position, largeur, hauteur, couleur, texte=""):
        """Initialise la jauge ; `texte` apparaît au format `texte: valeur/valeur_max`.

        Parameters
        ----------
        valeur : int
                 Valeur courante affichée par la jauge.
        valeur_min : int
                     Valeur minimale (gauche de la jauge).
        valeur_max : int
                     Valeur maximale (droite de la jauge).
        position : tuple[int, int]
                   Position (x, y) en coords logiques.
        largeur : int
                  Largeur logique de la jauge en pixels.
        hauteur : int
                  Hauteur logique de la jauge en pixels.
        couleur : tuple[int, int, int]
                  Couleur RGB de la portion remplie.
        texte : str
                Libellé affiché à gauche (vide = pas de libellé).
        """
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
        """Borne `valeur` dans [valeur_min, valeur_max].

        Parameters
        ----------
        valeur : int
                 Valeur à borner.

        Returns
        ----------
        int
             Valeur bornée entre valeur_min et valeur_max.
        """
        return max(self.valeur_min, min(self.valeur_max, valeur))

    def mettre_a_jour(self, nouvelle_valeur):
        """Met à jour la valeur affichée et re-rend le texte du libellé.

        Parameters
        ----------
        nouvelle_valeur : int
                          Nouvelle valeur courante.
        """
        self.valeur = self._clamper(nouvelle_valeur)
        self._rendre_texte()

    def calculer_pourcentage(self):
        """Retourne la part remplie de la jauge ∈ [0, 1].

        Parameters
        ----------

        Returns
        ----------
        float
             Pourcentage de remplissage entre 0.0 et 1.0.
        """
        return (self.valeur - self.valeur_min) / (self.valeur_max - self.valeur_min)

    def _rendre_texte(self):
        """Pré-rend la surface texte ; None si pas de libellé."""
        if not self.texte:
            self._texte_surface = None
            return
        self._texte_surface = self._police.render(
            f"{self.texte}: {self.valeur}/{self.valeur_max}",
            True,
            self.COULEUR_TEXTE,
        )

    def redimensionner(self, echelle):
        """Recalcule position, taille et police selon `echelle`.

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer.
        """
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
        """Dessine fond, remplissage, bordure et libellé.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        pygame.draw.rect(surface, self.COULEUR_FOND, (self._x, self._y, self._largeur, self._hauteur))
        largeur_remplie = int(self._largeur * self.calculer_pourcentage())
        pygame.draw.rect(surface, self.couleur, (self._x, self._y, largeur_remplie, self._hauteur))
        pygame.draw.rect(surface, self.COULEUR_BORDURE, (self._x, self._y, self._largeur, self._hauteur), 2)
        if self._texte_surface is not None:
            surface.blit(self._texte_surface, (self._x + self._padding_x, self._y + self._padding_y))
