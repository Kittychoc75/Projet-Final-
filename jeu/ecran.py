import pygame

class Ecran:
    """Gère la fenêtre pygame: création, redimensionnement au ratio du monde."""

    def __init__(self, gameplay):
        self.gameplay = gameplay

    def appliquer_taille(self, taille):
        taille_corrigee = self.gameplay.monde.taille_corrigee(taille)
        surface = pygame.display.set_mode(taille_corrigee, pygame.RESIZABLE)
        self.gameplay.redimensionner(surface)
        return surface
