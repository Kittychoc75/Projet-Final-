# jeu/ui/element.py
import pygame
from pygame.math import Vector2

class ElementUI:
    def __init__(self, chemin_image, position=(0, 0), centree=False):
        self.originale = pygame.image.load(chemin_image)
        self.position = Vector2(position)
        self.centree = centree
        self.image = self.originale
        self.rect = self.image.get_rect(topleft=(int(position[0]), int(position[1])))

    def redimensionner(self, echelle):
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
        return self.rect.collidepoint(point)

    def dessiner(self, surface):
        if self.centree:
            self.rect.center = surface.get_rect().center
        surface.blit(self.image, self.rect.topleft)