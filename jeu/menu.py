"""Écran d'accueil. Tourne dans le même process que le gameplay (pas de subprocess)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pygame
from pygame.math import Vector2

from jeu import config
from jeu.ui.bouton import Bouton

_RACINE = Path(__file__).resolve().parent.parent
_CHEMIN_FOND = _RACINE / "images" / "fond_menu.png"
_DOSSIER_SAUVEGARDES = _RACINE / "sauvegardes"


class Menu:
    """Écran d'accueil. Boucle bloquante via `executer()` qui retourne une intention."""

    JOUER = "jouer"
    REINITIALISER = "reinitialiser"
    QUITTER = "quitter"

    def __init__(self, surface):
        """Charge le fond et construit les 4 boutons (Jouer, Reset, Sauvegardes, Paramètres).

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage déjà créée par pygame.
        """
        self.surface = surface
        self._fond_origine = pygame.image.load(str(_CHEMIN_FOND))
        self.boutons = {
            "Jouer":       Bouton((72, 380),  173, 43, "Jouer"),
            "Reset":       Bouton((72, 465),  173, 43, "Reset"),
            "Sauvegardes": Bouton((743, 380), 173, 43, "Sauvegardes"),
            "Paramètres":  Bouton((743, 465), 173, 43, "Paramètres"),
        }
        self.intention = None
        self._appliquer(surface.get_size())

    def _appliquer(self, taille):
        """Met à l'échelle le fond et les boutons selon `taille` (largeur, hauteur).

        Parameters
        ----------
        taille : tuple[int, int]
                 Dimensions (largeur, hauteur) de la fenêtre courante.
        """
        echelle = Vector2(taille[0] / config.LARGEUR,
                          taille[1] / config.HAUTEUR)
        self._fond = pygame.transform.scale(self._fond_origine, taille)
        for bouton in self.boutons.values():
            bouton.redimensionner(echelle)

    def redimensionner(self, taille):
        """Redimensionne la fenêtre puis re-applique le layout.

        Parameters
        ----------
        taille : tuple[int, int]
                 Nouvelle taille (largeur, hauteur) en pixels.
        """
        self.surface = pygame.display.set_mode(taille, pygame.RESIZABLE)
        self._appliquer(taille)

    def gerer_evenement(self, evenement):
        """Route les événements pygame vers la sortie / le resize / les boutons.

        Parameters
        ----------
        evenement : pygame.event.Event
                    Événement pygame courant.
        """
        if evenement.type == pygame.QUIT:
            self.intention = self.QUITTER
        elif evenement.type == pygame.VIDEORESIZE:
            self.redimensionner(evenement.size)
        elif evenement.type == pygame.MOUSEBUTTONUP and evenement.button == 1:
            for nom, bouton in self.boutons.items():
                if bouton.contient(evenement.pos):
                    self._action(nom)
                    return

    def _action(self, nom):
        """Exécute l'action associée au bouton `nom` (Jouer/Reset/Sauvegardes/Paramètres).

        Parameters
        ----------
        nom : str
              Libellé du bouton cliqué.
        """
        if nom == "Jouer":
            self.intention = self.JOUER
        elif nom == "Reset":
            if _DOSSIER_SAUVEGARDES.exists():
                shutil.rmtree(_DOSSIER_SAUVEGARDES)
            self.intention = self.REINITIALISER
        elif nom == "Sauvegardes":
            _DOSSIER_SAUVEGARDES.mkdir(exist_ok=True)
            self._ouvrir_dossier(_DOSSIER_SAUVEGARDES)
        elif nom == "Paramètres":
            pass  # à implémenter

    @staticmethod
    def _ouvrir_dossier(chemin):
        """Ouvre `chemin` dans l'explorateur de fichiers natif (Windows/macOS/Linux).

        Parameters
        ----------
        chemin : pathlib.Path
                 Dossier à ouvrir.
        """
        if sys.platform == "win32":
            os.startfile(str(chemin))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(chemin)])
        else:
            subprocess.run(["xdg-open", str(chemin)])

    def dessiner(self):
        """Dessine le fond et tous les boutons sur la surface courante."""
        self.surface.blit(self._fond, (0, 0))
        for bouton in self.boutons.values():
            bouton.dessiner(self.surface)

    def executer(self):
        """Boucle bloquante : tourne à 60 fps jusqu'à ce qu'une intention soit choisie, puis la retourne.

        Parameters
        ----------

        Returns
        ----------
        str
             Intention choisie : JOUER, REINITIALISER ou QUITTER.
        """
        horloge = pygame.time.Clock()
        while self.intention is None:
            for evenement in pygame.event.get():
                self.gerer_evenement(evenement)
            self.dessiner()
            pygame.display.flip()
            horloge.tick(60)
        return self.intention
