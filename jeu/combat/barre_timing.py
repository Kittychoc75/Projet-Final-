"""Jauge de visée : un curseur fait des allers-retours, on clique pour viser."""
import pygame


class BarreTiming:
    """Curseur en va-et-vient horizontal ; un tir bien timé fait le maximum de dégâts."""

    ZONE_CIBLE_PX = 20  # largeur de la zone "BON" au centre
    VITESSE = 3         # px par frame

    def __init__(self, rect):
        """Initialise le curseur à gauche du `rect`, vitesse vers la droite.

        Parameters
        ----------
        rect : pygame.Rect
               Rect dans lequel le curseur fait des allers-retours.
        """
        self.rect = rect
        self._x = float(rect.left)
        self._vx = float(self.VITESSE)

    def reset(self):
        """Replace le curseur à gauche et remet la vitesse vers la droite."""
        self._x = float(self.rect.left)
        self._vx = float(self.VITESSE)

    def mettre_a_jour(self):
        """Avance le curseur ; rebondit aux bords du rect."""
        self._x += self._vx
        if self._x <= self.rect.left:
            self._x = float(self.rect.left)
            self._vx = abs(self._vx)
        if self._x >= self.rect.right:
            self._x = float(self.rect.right)
            self._vx = -abs(self._vx)

    def reussi(self):
        """True si le curseur est dans la zone cible centrale au moment du clic.

        Parameters
        ----------

        Returns
        ----------
        bool
             True si le tir est bien timé.
        """
        return abs(self._x - self.rect.centerx) <= self.ZONE_CIBLE_PX // 2

    def dessiner(self, surface):
        """Dessine la barre, la zone cible centrale et le curseur (disque blanc).

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        BLANC = (255, 255, 255)
        pygame.draw.rect(surface, BLANC, self.rect, 2)
        # zone cible au centre
        demi = self.ZONE_CIBLE_PX // 2
        zone = pygame.Rect(self.rect.centerx - demi, self.rect.top,
                           self.ZONE_CIBLE_PX, self.rect.height)
        pygame.draw.rect(surface, BLANC, zone, 1)
        # ligne centrale + curseur
        pygame.draw.line(surface, BLANC,
                         (self.rect.centerx, self.rect.top),
                         (self.rect.centerx, self.rect.bottom), 1)
        pygame.draw.circle(surface, BLANC,
                           (int(self._x), self.rect.centery), 6)
