# jeu/ui/modales/modale.py
import pygame

class Modale:
    def __init__(self, panneau, icone=None, centree=False):
        self.icone = icone        # ElementUI | None — None = ouverture programmatique
        self.panneau = panneau    # objet avec redimensionner(echelle) et dessiner(surface)
        if hasattr(panneau, "centree"):
            panneau.centree = centree
        self.ouvert = False

    @property
    def bloque_jeu(self):
        """True si la modale ouverte doit empêcher le perso de bouger. Surcharger au besoin."""
        return False

    def gerer_evenement(self, evenement):
        if self.icone is None:
            return
        if (evenement.type == pygame.MOUSEBUTTONUP
                and evenement.button == 1
                and self.icone.contient(evenement.pos)):
            self.ouvert = not self.ouvert

    def mettre_a_jour(self, dt):
        # À surcharger dans les sous-classes qui ont du contenu animé.
        pass

    def redimensionner(self, echelle):
        if self.icone is not None:
            self.icone.redimensionner(echelle)
        self.panneau.redimensionner(echelle)
        self.redimensionner_contenu(echelle)

    def redimensionner_contenu(self, echelle):
        # À surcharger dans les sous-classes pour propager le resize
        # au contenu propre à chaque modale (jauges, labels, …).
        pass

    def dessiner_contenu(self, surface):
        # À surcharger dans les sous-classes pour afficher
        # le contenu propre à chaque modale (jauges, labels, …).
        pass

    def dessiner(self, surface):
        if self.icone is not None:
            self.icone.dessiner(surface)
        if self.ouvert:
            self.panneau.dessiner(surface)
            self.dessiner_contenu(surface)
