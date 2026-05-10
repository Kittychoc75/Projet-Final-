"""Monde : niveau courant + image scalée à la fenêtre + tests de collision."""
import pygame
from pygame.math import Vector2


class Monde:
    """Encapsule le niveau courant et la version mise à l'échelle de son image."""

    def __init__(self, surface, niveau_initial):
        """Instancie `niveau_initial()` et scale son image à la taille de `surface`.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage de référence pour la taille de départ.
        niveau_initial : type[Niveau]
                         Classe du niveau à instancier au démarrage.
        """
        self.niveau = niveau_initial()
        self.image = self.niveau.image
        self.redimensionner(surface.get_size())

    @property
    def taille_originale(self):
        """Taille (largeur, hauteur) du niveau en pixels source.

        Parameters
        ----------

        Returns
        ----------
        pygame.math.Vector2
               (largeur, hauteur) du niveau en pixels source.
        """
        return Vector2(self.niveau.largeur, self.niveau.hauteur)

    @property
    def taille_fenetre(self):
        """Taille courante de l'image affichée (post-scale).

        Parameters
        ----------

        Returns
        ----------
        pygame.math.Vector2
               (largeur, hauteur) de l'image affichée.
        """
        return Vector2(self.image.get_size())

    @property
    def echelle(self):
        """Vecteur (sx, sy) = taille_fenetre / taille_originale.

        Parameters
        ----------

        Returns
        ----------
        pygame.math.Vector2
               Facteur d'échelle entre coords originales et fenêtre.
        """
        return Vector2(
            self.taille_fenetre.x / self.taille_originale.x,
            self.taille_fenetre.y / self.taille_originale.y,
        )

    def redimensionner(self, taille):
        """Re-scale l'image du niveau à `taille` (sans toucher le masque source).

        Parameters
        ----------
        taille : tuple[int, int]
                 Nouvelle taille (largeur, hauteur) en pixels.
        """
        self.image = pygame.transform.scale(self.niveau.image, taille)

    def taille_corrigee(self, taille):
        """Ajuste `taille` pour respecter le ratio du monde (pas de déformation).

        Parameters
        ----------
        taille : tuple[int, int]
                 Taille demandée (largeur, hauteur) en pixels.

        Returns
        ----------
        tuple[int, int]
               Taille corrigée pour préserver le ratio.
        """
        nouvelle_l, nouvelle_h = max(1, taille[0]), max(1, taille[1])
        ratio = self.taille_originale.x / self.taille_originale.y
        if nouvelle_l / nouvelle_h > ratio:
            nouvelle_l = int(nouvelle_h * ratio)
        else:
            nouvelle_h = int(nouvelle_l / ratio)
        return (max(1, nouvelle_l), max(1, nouvelle_h))

    def collision(self, hitbox):
        """True si la hitbox (Rect en coords monde original) chevauche un mur.

        Parameters
        ----------
        hitbox : pygame.Rect
                 Hitbox en coordonnées monde original à tester.

        Returns
        ----------
        bool
             True si la hitbox chevauche un pixel du masque mur.
        """
        rect_mask = pygame.mask.Mask((hitbox.width, hitbox.height), fill=True)
        return self.niveau.masque.overlap(rect_mask, hitbox.topleft) is not None

    def changer_niveau(self, classe_niveau):
        """Charge un nouveau niveau et conserve la taille de fenêtre courante.

        Parameters
        ----------
        classe_niveau : type[Niveau]
                        Classe du niveau à instancier.
        """
        taille_actuelle = (int(self.taille_fenetre.x), int(self.taille_fenetre.y))
        self.niveau = classe_niveau()
        self.image = self.niveau.image
        self.redimensionner(taille_actuelle)

    def dessiner(self, surface, scenario):
        """Blitte la map en (0,0) puis dessine les sprites carte (PNJ, objets de quête).

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        scenario : Scenario
                   Scénario courant (fournit personnages/objets à dessiner).
        """
        surface.blit(self.image, (0, 0))
        self.niveau.dessiner_sprites_carte(surface, self.echelle, scenario)
