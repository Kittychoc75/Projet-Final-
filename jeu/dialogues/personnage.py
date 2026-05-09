import pygame
from pygame.math import Vector2


class Personnage:
    """Personnage non-joueur : sprite carte + sprites dialogue (bouche fermée/ouverte)."""

    def __init__(self, nom, couleur_nom, sprite_carte, sprite_dialogue_1, sprite_dialogue_2, facteur_taille_carte=1.0, toujours_visible=False):
        self.nom = nom
        self.couleur_nom = couleur_nom
        self.toujours_visible = toujours_visible
        origine = pygame.image.load(sprite_carte).convert_alpha()
        if facteur_taille_carte != 1.0:
            w = max(1, int(origine.get_width() * facteur_taille_carte))
            h = max(1, int(origine.get_height() * facteur_taille_carte))
            origine = pygame.transform.scale(origine, (w, h))
        self._sprite_carte_origine = origine
        self.sprite_dialogue_1 = pygame.image.load(sprite_dialogue_1).convert_alpha()
        self.sprite_dialogue_2 = pygame.image.load(sprite_dialogue_2).convert_alpha()
        self._sprite_carte_echelle = None
        self._sprite_carte = self._sprite_carte_origine

    def redimensionner_carte(self, echelle):
        echelle = Vector2(echelle)
        if echelle == self._sprite_carte_echelle:
            return
        self._sprite_carte_echelle = echelle
        l = max(1, int(self._sprite_carte_origine.get_width() * echelle.x))
        h = max(1, int(self._sprite_carte_origine.get_height() * echelle.y))
        self._sprite_carte = pygame.transform.scale(self._sprite_carte_origine, (l, h))

    def dessiner_sur_carte(self, surface, position_monde, echelle):
        self.redimensionner_carte(echelle)
        rect = self._sprite_carte.get_rect()
        rect.midbottom = (
            int(position_monde.x * echelle.x),
            int(position_monde.y * echelle.y),
        )
        surface.blit(self._sprite_carte, rect.topleft)

    def sprite_dialogue(self, bouche_ouverte):
        return self.sprite_dialogue_2 if bouche_ouverte else self.sprite_dialogue_1
