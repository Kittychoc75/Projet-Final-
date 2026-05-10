"""Entités runtime utilisées pendant un combat : ennemi, cœur du joueur, projectiles."""
import math
import random

import pygame


class EnnemiCombat:
    """Sprite + PV de l'ennemi pendant le combat. Animation 2 frames."""

    def __init__(self, nom, sprites, pv, periode_anim, centre):
        """Initialise PV et alterne entre `sprites` toutes les `periode_anim` frames.

        Parameters
        ----------
        nom : str
              Nom du monstre (pour la barre PV).
        sprites : list[pygame.Surface]
                  Au moins une surface ; deux pour animer.
        pv : int
             Points de vie initiaux et max.
        periode_anim : int
                       Frames entre deux changements d'image.
        centre : tuple[int, int]
                 Position (cx, cy) en pixels où ancrer le sprite.
        """
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
        """Avance l'animation (alternance 2 frames) et synchronise le rect."""
        if len(self.sprites) > 1:
            self._tick += 1
            if self._tick % self.periode == 0:
                self._frame = 1 - self._frame
        self.rect = self.sprites[self._frame].get_rect(center=self.centre)

    def dessiner(self, surface):
        """Blitte la frame courante.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        surface.blit(self.sprites[self._frame], self.rect)


class Coeur:
    """Petit sprite mobile dans l'arène pendant la phase défense."""

    VITESSE = 4
    INVINCIBILITE = 22  # frames d'invincibilité après une touche

    def __init__(self, image, zone):
        """Place le cœur au centre de `zone` (le rect ne sortira jamais de cette zone).

        Parameters
        ----------
        image : pygame.Surface
                Sprite du cœur.
        zone : pygame.Rect
               Rect dans lequel le cœur peut se déplacer.
        """
        self.image = image
        self.zone = zone
        self.rect = image.get_rect(center=zone.center)
        self.invincible = 0

    def reset(self):
        """Recentre le cœur et annule l'invincibilité."""
        self.rect.center = self.zone.center
        self.invincible = 0

    def mettre_a_jour(self):
        """Décrémente le compteur d'invincibilité."""
        if self.invincible > 0:
            self.invincible -= 1

    def bouger(self, touches):
        """Déplace le cœur selon les touches fléchées, clampé à la zone.

        Parameters
        ----------
        touches : pygame.key.ScancodeWrapper
                  État courant des touches (issu de pygame.key.get_pressed()).
        """
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
        """Active l'invincibilité après une touche."""
        self.invincible = self.INVINCIBILITE

    def dessiner(self, surface):
        """Blitte le sprite (clignote pendant l'invincibilité).

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        # clignote pendant l'invincibilité
        if self.invincible == 0 or (self.invincible // 4) % 2 == 0:
            surface.blit(self.image, self.rect)


class Projectile:
    """Petit cercle qui se déplace en ligne droite."""

    def __init__(self, x, y, vx, vy, rayon, couleur):
        """Initialise position, vitesse, taille et couleur ; `vivant=True`.

        Parameters
        ----------
        x : float
            Position X initiale en pixels.
        y : float
            Position Y initiale en pixels.
        vx : float
             Vitesse horizontale en pixels par frame.
        vy : float
             Vitesse verticale en pixels par frame.
        rayon : int
                Rayon du disque en pixels.
        couleur : tuple[int, int, int]
                  Couleur RGB du projectile.
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.rayon = int(rayon)
        self.couleur = couleur
        self.vivant = True

    def rect(self):
        """Bounding-box carrée centrée sur le projectile.

        Parameters
        ----------

        Returns
        ----------
        pygame.Rect
               Carré 2*rayon centré sur (x, y).
        """
        return pygame.Rect(int(self.x - self.rayon), int(self.y - self.rayon),
                           self.rayon * 2, self.rayon * 2)

    def mettre_a_jour_sortie(self, zone_sortie):
        """Pour les projectiles ennemis : meurt s'il sort de la zone.

        Parameters
        ----------
        zone_sortie : pygame.Rect
                      Rect au-delà duquel le projectile est désactivé.
        """
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
        """Dessine le projectile comme un disque plein.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        pygame.draw.circle(surface, self.couleur,
                           (int(self.x), int(self.y)), self.rayon)


def vitesse_vers(x0, y0, x1, y1, vitesse):
    """Vecteur normalisé (vx, vy) à `vitesse` dirigé de (x0,y0) vers (x1,y1).

    Parameters
    ----------
    x0 : float
         Position X de départ.
    y0 : float
         Position Y de départ.
    x1 : float
         Position X de la cible.
    y1 : float
         Position Y de la cible.
    vitesse : float
              Norme du vecteur retourné.

    Returns
    ----------
    tuple[float, float]
           Vecteur (vx, vy) de norme `vitesse` (ou (0, 0) si départ = cible).
    """
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0.0, 0.0
    return (dx / dist) * vitesse, (dy / dist) * vitesse


def point_bord(rect):
    """Retourne un point aléatoire sur l'un des 4 côtés du rect.

    Parameters
    ----------
    rect : pygame.Rect
           Rect dont on tire un point sur le contour.

    Returns
    ----------
    tuple[int, int]
           Coordonnées (x, y) du point.
    """
    cote = random.choice(("g", "d", "h", "b"))
    if cote == "g":
        return rect.left, random.randint(rect.top, rect.bottom)
    if cote == "d":
        return rect.right, random.randint(rect.top, rect.bottom)
    if cote == "h":
        return random.randint(rect.left, rect.right), rect.top
    return random.randint(rect.left, rect.right), rect.bottom
