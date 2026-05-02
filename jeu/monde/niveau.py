import pygame
from pygame.math import Vector2

from jeu.monde.couleurs_meta import COULEUR_SORTIE, COULEUR_SPAWN


class Niveau:
    """Niveau de jeu : décor + masque de collisions + masque méta.

    Les sous-classes fournissent les chemins de fichiers via `super().__init__()`.
    """

    TAILLE_MIN_SORTIE = 20  # une sortie de 1 px est gonflée à 20×20 pour être déclenchable

    def __init__(self, chemin_image, chemin_mur, chemin_meta):
        self.image = pygame.image.load(chemin_image).convert_alpha()
        self.masque_image = pygame.image.load(chemin_mur).convert_alpha()
        meta = pygame.image.load(chemin_meta).convert_alpha()
        self._verifier_dimensions(meta)
        self.masque = pygame.mask.from_surface(self.masque_image)
        self.spawn = self._chercher_point(meta, COULEUR_SPAWN)
        self.sortie = self._chercher_zone(meta, COULEUR_SORTIE, self.TAILLE_MIN_SORTIE)
        if self.spawn is None:
            raise ValueError(
                f"Aucun pixel vert (spawn) dans {chemin_meta}. "
                "Peindre un pixel #00FF00 dans le calque méta."
            )

    def _verifier_dimensions(self, meta):
        if self.masque_image.get_size() != self.image.get_size():
            raise ValueError(
                f"Dimensions masque mur {self.masque_image.get_size()} "
                f"!= image {self.image.get_size()}"
            )
        if meta.get_size() != self.image.get_size():
            raise ValueError(
                f"Dimensions masque meta {meta.get_size()} "
                f"!= image {self.image.get_size()}"
            )

    @staticmethod
    def _chercher_point(meta, couleur):
        """Centre du blob de cette couleur. Utile pour un point unique (spawn)."""
        rect = Niveau._bounding_rect(meta, couleur)
        return Vector2(rect.center) if rect else None

    @staticmethod
    def _chercher_zone(meta, couleur, taille_min=1):
        """Bounding rect du blob, gonflé à `taille_min` minimum. Utile pour zone de trigger."""
        rect = Niveau._bounding_rect(meta, couleur)
        if rect is None:
            return None
        if rect.width < taille_min or rect.height < taille_min:
            rect.inflate_ip(
                max(0, taille_min - rect.width),
                max(0, taille_min - rect.height),
            )
        return rect

    @staticmethod
    def _bounding_rect(meta, couleur):
        masque = pygame.mask.from_threshold(
            meta, (*couleur, 255), threshold=(5, 5, 5, 0)
        )
        rects = masque.get_bounding_rects()
        return rects[0] if rects else None

    @property
    def largeur(self):
        return self.image.get_width()

    @property
    def hauteur(self):
        return self.image.get_height()
