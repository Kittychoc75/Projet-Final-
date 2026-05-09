import pygame
from pygame.math import Vector2

from jeu.monde.couleurs_meta import (
    COULEUR_DIALOGUE,
    COULEUR_MONSTRE,
    COULEUR_PASSAGE,
    COULEUR_QUETE,
    COULEUR_SORTIE,
    COULEUR_SPAWN,
)


# Mapping nom → RGB pour référencer les couleurs depuis scenario.yaml.
COULEURS_PAR_NOM = {
    "vert": COULEUR_SPAWN,
    "rouge": COULEUR_SORTIE,
    "bleu": COULEUR_MONSTRE,
    "magenta": COULEUR_QUETE,
    "cyan": COULEUR_DIALOGUE,
    "jaune": COULEUR_PASSAGE,
}

# Couleurs balayées au scan d'un meta pour exposer `zones_par_couleur`.
# Spawn et sortie restent traités à part (point unique / unique zone).
_COULEURS_TRIGGERS = ["cyan", "magenta", "jaune", "bleu"]


class Niveau:
    """Niveau de jeu : décor + masque de collisions + masque méta.

    Les sous-classes fournissent les chemins de fichiers via `super().__init__()`,
    ainsi qu'un `NOM` (string) qui sert d'identifiant côté scénario.
    """

    NOM = ""  # à surcharger par les sous-classes
    TAILLE_MIN_SORTIE = 20
    TAILLE_MIN_TRIGGER = 20

    def __init__(self, chemin_image, chemin_mur, chemin_meta):
        self.image = pygame.image.load(chemin_image).convert_alpha()
        self.masque_image = pygame.image.load(chemin_mur).convert_alpha()
        meta = pygame.image.load(chemin_meta).convert_alpha()
        self._verifier_dimensions(meta)
        self.masque = pygame.mask.from_surface(self.masque_image)
        self.spawn = self._chercher_point(meta, COULEUR_SPAWN)
        self.sortie = self._chercher_zone(meta, COULEUR_SORTIE, self.TAILLE_MIN_SORTIE)
        # Pour chaque couleur "trigger", la liste des blobs trouvés dans le meta.
        # Convention : un blob par couleur par niveau (cf. design scénario).
        self.zones_par_couleur = {
            nom: self._chercher_zones(meta, COULEURS_PAR_NOM[nom], self.TAILLE_MIN_TRIGGER)
            for nom in _COULEURS_TRIGGERS
        }
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
        rect = Niveau._bounding_rect(meta, couleur)
        return Vector2(rect.center) if rect else None

    @staticmethod
    def _chercher_zone(meta, couleur, taille_min=1):
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

    @staticmethod
    def _chercher_zones(meta, couleur, taille_min=1):
        masque = pygame.mask.from_threshold(
            meta, (*couleur, 255), threshold=(5, 5, 5, 0)
        )
        rects = masque.get_bounding_rects()
        for rect in rects:
            if rect.width < taille_min or rect.height < taille_min:
                rect.inflate_ip(
                    max(0, taille_min - rect.width),
                    max(0, taille_min - rect.height),
                )
        return list(rects)

    def dessiner_sprites_carte(self, surface, echelle, scenario):
        """Dessine les PNJ visibles selon le scenario, sur leur zone meta."""
        for couleur_nom, zones in self.zones_par_couleur.items():
            if not zones:
                continue
            personnage = scenario.personnage_present(self.NOM, couleur_nom)
            if personnage is None:
                continue
            zone = zones[0]
            position = Vector2(zone.centerx, zone.bottom)
            personnage.dessiner_sur_carte(surface, position, echelle)

    @property
    def largeur(self):
        return self.image.get_width()

    @property
    def hauteur(self):
        return self.image.get_height()
