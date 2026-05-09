"""Bandeau de texte transitoire affiché en haut de l'écran (indices, alertes)."""
import pygame
from pygame.math import Vector2

from jeu.ui import polices


class IndiceFlottant:
    DUREE = 2500.0       # ms total
    FADE_OUT = 500.0     # ms du fondu de fin
    TAILLE_POLICE = 22
    COULEUR = (255, 255, 255)
    COULEUR_FOND = (0, 0, 0, 180)
    PADDING = 14
    MARGE_TOP = 30
    RAYON = 8

    def __init__(self):
        self.message = None
        self._restant = 0.0
        self._echelle = Vector2(1, 1)
        self._surface = None

    def afficher(self, message):
        if not message:
            return
        self.message = message
        self._restant = self.DUREE
        self._construire_surface()

    def redimensionner(self, echelle):
        self._echelle = Vector2(echelle)
        if self.message:
            self._construire_surface()

    def mettre_a_jour(self, dt):
        if self._restant <= 0:
            return
        self._restant -= dt
        if self._restant <= 0:
            self.message = None
            self._surface = None

    def dessiner(self, surface):
        if self._surface is None:
            return
        rect = self._surface.get_rect()
        rect.midtop = (
            surface.get_width() // 2,
            int(self.MARGE_TOP * self._echelle.y),
        )
        alpha = 255
        if self._restant < self.FADE_OUT:
            alpha = max(0, int(self._restant / self.FADE_OUT * 255))
        self._surface.set_alpha(alpha)
        surface.blit(self._surface, rect.topleft)

    def _construire_surface(self):
        taille = max(1, int(self.TAILLE_POLICE * self._echelle.y))
        police = polices.pixelade(taille)
        rendu = police.render(self.message, True, self.COULEUR)
        padding = max(1, int(self.PADDING * self._echelle.y))
        w = rendu.get_width() + padding * 2
        h = rendu.get_height() + padding * 2
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bg, self.COULEUR_FOND, bg.get_rect(), border_radius=self.RAYON)
        bg.blit(rendu, (padding, padding))
        self._surface = bg
