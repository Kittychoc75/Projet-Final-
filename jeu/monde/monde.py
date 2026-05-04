import pygame
from pygame.math import Vector2

from jeu.monde.chaine import CHAINE


class Monde:
    def __init__(self, surface):
        self.niveau = CHAINE[0]()
        self.image = self.niveau.image
        self.redimensionner(surface.get_size())

    @property
    def taille_originale(self):
        return Vector2(self.niveau.largeur, self.niveau.hauteur)

    @property
    def taille_fenetre(self):
        return Vector2(self.image.get_size())

    @property
    def echelle(self):
        return Vector2(
            self.taille_fenetre.x / self.taille_originale.x,
            self.taille_fenetre.y / self.taille_originale.y,
        )

    def redimensionner(self, taille):
        self.image = pygame.transform.scale(self.niveau.image, taille)

    def taille_corrigee(self, taille):
        """Ajuste `taille` pour respecter le ratio du monde (pas de déformation)."""
        nouvelle_l, nouvelle_h = max(1, taille[0]), max(1, taille[1])
        ratio = self.taille_originale.x / self.taille_originale.y
        if nouvelle_l / nouvelle_h > ratio:
            nouvelle_l = int(nouvelle_h * ratio)
        else:
            nouvelle_h = int(nouvelle_l / ratio)
        return (max(1, nouvelle_l), max(1, nouvelle_h))

    def collision(self, hitbox):
        """True si la hitbox (Rect en coords monde original) chevauche un mur."""
        rect_mask = pygame.mask.Mask((hitbox.width, hitbox.height), fill=True)
        return self.niveau.masque.overlap(rect_mask, hitbox.topleft) is not None

    def changer_niveau(self, classe_niveau):
        """Charge un nouveau niveau et conserve la taille de fenêtre courante."""
        taille_actuelle = (int(self.taille_fenetre.x), int(self.taille_fenetre.y))
        self.niveau = classe_niveau()
        self.image = self.niveau.image
        self.redimensionner(taille_actuelle)

    def dessiner(self, surface):
        surface.blit(self.image, (0, 0))
