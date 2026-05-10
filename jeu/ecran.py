"""Encapsule la fenêtre pygame : applique la taille demandée en respectant le ratio du monde."""
import pygame

class Ecran:
    """Gère la fenêtre pygame: création, redimensionnement au ratio du monde."""

    def __init__(self, gameplay):
        """Garde une référence vers le gameplay pour propager les changements de taille.

        Parameters
        ----------
        gameplay : Gameplay
                   Instance dont le monde sert de référence pour le ratio.
        """
        self.gameplay = gameplay

    def appliquer_taille(self, taille):
        """Applique `taille` (corrigée au ratio du monde) à la fenêtre et propage au gameplay.

        Parameters
        ----------
        taille : tuple[int, int]
                 Largeur et hauteur souhaitées en pixels.

        Returns
        ----------
        pygame.Surface
               Nouvelle surface d'affichage à la taille corrigée.
        """
        taille_corrigee = self.gameplay.monde.taille_corrigee(taille)
        surface = pygame.display.set_mode(taille_corrigee, pygame.RESIZABLE)
        self.gameplay.redimensionner(surface)
        return surface
