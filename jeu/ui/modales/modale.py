# jeu/ui/modales/modale.py
"""Classe de base des modales UI : icône optionnelle + panneau scalable + contenu surchargeable."""
import pygame

class Modale:
    """Modale générique : icône (clic = toggle) + panneau de fond + contenu propre aux sous-classes."""

    def __init__(self, panneau, icone=None, centree=False):
        """Stocke `icone` (None = ouverture programmatique) et `panneau` (objet redimensionnable).

        Parameters
        ----------
        panneau : object
                  Objet avec `redimensionner(echelle)` et `dessiner(surface)`.
        icone : ElementUI | None
                Icône cliquable qui toggle la modale (None = piloté ailleurs).
        centree : bool
                  True pour centrer le panneau au dessin.
        """
        self.icone = icone        # ElementUI | None — None = ouverture programmatique
        self.panneau = panneau    # objet avec redimensionner(echelle) et dessiner(surface)
        if hasattr(panneau, "centree"):
            panneau.centree = centree
        self.ouvert = False

    @property
    def bloque_jeu(self):
        """True si la modale ouverte doit empêcher le perso de bouger. Surcharger au besoin.

        Parameters
        ----------

        Returns
        ----------
        bool
             True si la modale bloque le jeu.
        """
        return False

    def gerer_evenement(self, evenement):
        """Toggle `ouvert` quand l'icône est cliquée (no-op si pas d'icône).

        Parameters
        ----------
        evenement : pygame.event.Event
                    Événement pygame courant.
        """
        if self.icone is None:
            return
        if (evenement.type == pygame.MOUSEBUTTONUP
                and evenement.button == 1
                and self.icone.contient(evenement.pos)):
            self.ouvert = not self.ouvert

    def mettre_a_jour(self, dt):
        """No-op par défaut ; surcharger pour le contenu animé.

        Parameters
        ----------
        dt : int
             Durée écoulée depuis la dernière frame en millisecondes.
        """
        # À surcharger dans les sous-classes qui ont du contenu animé.
        pass

    def redimensionner(self, echelle):
        """Propage le resize à l'icône, au panneau et au contenu.

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer.
        """
        if self.icone is not None:
            self.icone.redimensionner(echelle)
        self.panneau.redimensionner(echelle)
        self.redimensionner_contenu(echelle)

    def redimensionner_contenu(self, echelle):
        """No-op par défaut ; surcharger pour redimensionner jauges/labels/etc.

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer.
        """
        # À surcharger dans les sous-classes pour propager le resize
        # au contenu propre à chaque modale (jauges, labels, …).
        pass

    def dessiner_contenu(self, surface):
        """No-op par défaut ; surcharger pour dessiner jauges/labels/etc.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        # À surcharger dans les sous-classes pour afficher
        # le contenu propre à chaque modale (jauges, labels, …).
        pass

    def dessiner(self, surface):
        """Dessine l'icône, puis le panneau et le contenu si la modale est ouverte.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        if self.icone is not None:
            self.icone.dessiner(surface)
        if self.ouvert:
            self.panneau.dessiner(surface)
            self.dessiner_contenu(surface)
