"""Entités runtime utilisées pendant un combat : ennemi, cœur du joueur, projectiles."""
import math
import random

import pygame


class EnnemiCombat:
    """Sprite + PV de l'ennemi pendant le combat. Animation 2 frames."""

    def __init__(self, nom, sprites, pv, periode_anim, centre):
        self.nom = nom
        self.sprites = sprites           # liste d'au moins 1 surface
        self.pv_max = pv
        self.pv = pv
        self.periode = max(1, periode_anim)
        self.centre = centre
        self._tick = 0
        self._frame = 0
        self.rect = sprites[0].get_rect(center=centre)

    def mettre_a_jour(self):
        if len(self.sprites) > 1:
            self._tick += 1
            if self._tick % self.periode == 0:
                self._frame = 1 - self._frame
        self.rect = self.sprites[self._frame].get_rect(center=self.centre)

    def dessiner(self, surface):
        surface.blit(self.sprites[self._frame], self.rect)


class Coeur:
    """Petit sprite mobile dans l'arène pendant la phase défense."""

    VITESSE = 4
    INVINCIBILITE = 22  # frames d'invincibilité après une touche

    def __init__(self, image, zone):
        self.image = image
        self.zone = zone
        self.rect = image.get_rect(center=zone.center)
        self.invincible = 0

    def reset(self):
        self.rect.center = self.zone.center
        self.invincible = 0

    def mettre_a_jour(self):
        if self.invincible > 0:
            self.invincible -= 1

    def bouger(self, touches):
        dx = dy = 0
        if touches[pygame.K_LEFT]:
            dx = -self.VITESSE
        if touches[pygame.K_RIGHT]:
            dx = self.VITESSE
        if touches[pygame.K_UP]:
            dy = -self.VITESSE
        if touches[pygame.K_DOWN]:
            dy = self.VITESSE
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(self.zone)

    def encaisser(self):
        self.invincible = self.INVINCIBILITE

    def dessiner(self, surface):
        # clignote pendant l'invincibilité
        if self.invincible == 0 or (self.invincible // 4) % 2 == 0:
            surface.blit(self.image, self.rect)


class Projectile:
    """Petit cercle qui se déplace en ligne droite."""

    def __init__(self, x, y, vx, vy, rayon, couleur):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.rayon = int(rayon)
        self.couleur = couleur
        self.vivant = True

    def rect(self):
        return pygame.Rect(int(self.x - self.rayon), int(self.y - self.rayon),
                           self.rayon * 2, self.rayon * 2)

    def mettre_a_jour_sortie(self, zone_sortie):
        """Pour les projectiles ennemis : meurt s'il sort de la zone."""
        self.x += self.vx
        self.y += self.vy
        if not zone_sortie.collidepoint(int(self.x), int(self.y)):
            self.vivant = False

    def mettre_a_jour_haut(self):
        """Pour le tir du joueur : meurt en haut de l'écran."""
        self.x += self.vx
        self.y += self.vy
        if self.y < -80:
            self.vivant = False

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.couleur,
                           (int(self.x), int(self.y)), self.rayon)


def vitesse_vers(x0, y0, x1, y1, vitesse):
    """Vecteur normalisé (vx, vy) à `vitesse` dirigé de (x0,y0) vers (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0.0, 0.0
    return (dx / dist) * vitesse, (dy / dist) * vitesse


def point_bord(rect):
    """Retourne un point aléatoire sur l'un des 4 côtés du rect."""
    cote = random.choice(("g", "d", "h", "b"))
    if cote == "g":
        return rect.left, random.randint(rect.top, rect.bottom)
    if cote == "d":
        return rect.right, random.randint(rect.top, rect.bottom)
    if cote == "h":
        return random.randint(rect.left, rect.right), rect.top
    return random.randint(rect.left, rect.right), rect.bottom
