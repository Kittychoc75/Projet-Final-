"""Chargement de sprite avec placeholder en cas d'asset manquant.

Permet de coder/tester sans avoir tous les assets — l'erreur se voit visuellement
plutôt que par un crash.
"""
import os

import pygame

from jeu.ui import polices


def charger_avec_fallback(chemin, taille):
    """Charge l'image et la scale à `taille`. Si absente, retourne un carré gris labellisé.

    Parameters
    ----------
    chemin : str
             Chemin du PNG à charger.
    taille : tuple[int, int]
             Dimensions cibles (largeur, hauteur) en pixels.

    Returns
    ----------
    pygame.Surface
           Image scalée ou placeholder gris.
    """
    if os.path.exists(chemin):
        try:
            img = pygame.image.load(chemin)
            img = img.convert_alpha() if img.get_alpha() is not None else img.convert()
            return pygame.transform.smoothscale(img, taille)
        except pygame.error:
            pass
    return _placeholder(taille, os.path.basename(chemin))


def _placeholder(taille, label):
    """Carré gris labellisé avec `label` (nom du fichier manquant) à `taille` donnée.

    Parameters
    ----------
    taille : tuple[int, int]
             Dimensions (largeur, hauteur) en pixels.
    label : str
            Texte à afficher au centre du carré.

    Returns
    ----------
    pygame.Surface
           Surface placeholder.
    """
    surf = pygame.Surface(taille, pygame.SRCALPHA)
    surf.fill((80, 80, 80))
    pygame.draw.rect(surf, (180, 180, 180), surf.get_rect(), 2)
    police = polices.pixelade(max(10, min(taille[1] // 8, 22)))
    rendu = police.render(label or "?", True, (220, 220, 220))
    surf.blit(
        rendu,
        ((taille[0] - rendu.get_width()) // 2,
         (taille[1] - rendu.get_height()) // 2),
    )
    return surf
