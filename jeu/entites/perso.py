import pygame
from pygame.math import Vector2
from jeu import config

class _Sprites:
    """Encapsule les 4 sprites directionnels et leurs versions redimensionnées."""

    _FICHIERS = {
        'down': "images/perso_front.png",
        'up': "images/perso_back.png",
        'left': "images/perso_left.png",
        'right': "images/perso_right.png",
    }

    def __init__(self):
        self.originaux = {d: pygame.image.load(f) for d, f in self._FICHIERS.items()}
        self.redimensionnes = dict(self.originaux)

    def redimensionner(self, echelle):
        self.redimensionnes = {
            d: pygame.transform.scale(
                img,
                (max(1, int(img.get_width() * echelle.x)),
                 max(1, int(img.get_height() * echelle.y))),
            )
            for d, img in self.originaux.items()
        }

    def taille_originale(self, direction):
        return Vector2(self.originaux[direction].get_size())


class Perso(pygame.sprite.Sprite):
    HITBOX_LARGEUR = 30
    HITBOX_HAUTEUR = 20

    def __init__(self, x, y):
        super().__init__()
        # Position en coordonnées du monde original (jamais re-dimensionnée au redimensionnement).
        self.position = Vector2(x, y)
        self.direction = 'down'
        self.sprites = _Sprites()
        self.echelle = Vector2(1.0, 1.0)
        self.image = self.sprites.redimensionnes[self.direction]
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

    @property
    def hitbox(self):
        """Rect aux pieds du perso, en coordonnées du monde original."""
        sprite_h = self.sprites.taille_originale(self.direction).y
        return pygame.Rect(
            int(self.position.x - self.HITBOX_LARGEUR / 2),
            int(self.position.y + sprite_h / 2 - self.HITBOX_HAUTEUR),
            self.HITBOX_LARGEUR,
            self.HITBOX_HAUTEUR,
        )

    def redimensionner(self, echelle):
        self.echelle = Vector2(echelle)
        self.sprites.redimensionner(self.echelle)
        self.image = self.sprites.redimensionnes[self.direction]
        self.rect = self.image.get_rect()

    def _appliquer_limites(self, taille_monde):
        demi = self.sprites.taille_originale(self.direction) / 2
        self.position.x = max(demi.x, min(self.position.x, taille_monde.x - demi.x))
        self.position.y = max(demi.y, min(self.position.y, taille_monde.y - demi.y))

    def mouvement(self, dt, monde):
        touches = pygame.key.get_pressed()
        deplacement = config.VITESSE_PERSO * dt

        dx = 0
        dy = 0
        if touches[pygame.K_LEFT]:
            dx -= deplacement
            self.direction = 'left'
        if touches[pygame.K_RIGHT]:
            dx += deplacement
            self.direction = 'right'
        if touches[pygame.K_UP]:
            dy -= deplacement
            self.direction = 'up'
        if touches[pygame.K_DOWN]:
            dy += deplacement
            self.direction = 'down'

        # Collision séparée par axe → permet de glisser le long d'un mur
        if dx:
            self.position.x += dx
            if monde.collision(self.hitbox):
                self.position.x -= dx
        if dy:
            self.position.y += dy
            if monde.collision(self.hitbox):
                self.position.y -= dy

        self._appliquer_limites(monde.taille_originale)
        self.image = self.sprites.redimensionnes[self.direction]
        self.rect = self.image.get_rect(
            center=(int(self.position.x * self.echelle.x),
                    int(self.position.y * self.echelle.y))
        )

    def dessiner(self, surface):
        surface.blit(self.image, self.rect.topleft)
