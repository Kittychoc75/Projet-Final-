"""Objet ramassable : sprite affiché sur la carte + dans l'inventaire."""
import pygame
from pygame.math import Vector2


class Objet:
    def __init__(self, id, nom, sprite, facteur_taille_carte=1.0, cache_sur_carte=False):
        self.id = id
        self.nom = nom
        self.cache_sur_carte = cache_sur_carte
        origine = pygame.image.load(sprite).convert_alpha()
        if facteur_taille_carte != 1.0:
            w = max(1, int(origine.get_width() * facteur_taille_carte))
            h = max(1, int(origine.get_height() * facteur_taille_carte))
            origine = pygame.transform.scale(origine, (w, h))
        self._sprite_origine = origine
        self._sprite_carte = origine
        self._echelle_cache = None

    @property
    def sprite_origine(self):
        """Sprite à taille native (post `facteur_taille_carte`). Utilisé par l'inventaire."""
        return self._sprite_origine

    def redimensionner_carte(self, echelle):
        echelle = Vector2(echelle)
        if echelle == self._echelle_cache:
            return
        self._echelle_cache = echelle
        l = max(1, int(self._sprite_origine.get_width() * echelle.x))
        h = max(1, int(self._sprite_origine.get_height() * echelle.y))
        self._sprite_carte = pygame.transform.scale(self._sprite_origine, (l, h))

    def dessiner_sur_carte(self, surface, position_monde, echelle):
        self.redimensionner_carte(echelle)
        rect = self._sprite_carte.get_rect()
        rect.midbottom = (
            int(position_monde.x * echelle.x),
            int(position_monde.y * echelle.y),
        )
        surface.blit(self._sprite_carte, rect.topleft)
