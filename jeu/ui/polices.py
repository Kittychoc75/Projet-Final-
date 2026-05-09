"""Chargement centralisé des polices du jeu (chemin absolu).

Toutes les classes UI passent par ici pour rendre du texte, ce qui garantit
une typographie cohérente et un chemin indépendant du dossier d'exécution.
"""
from pathlib import Path

import pygame

_CHEMIN_PIXELADE = Path(__file__).resolve().parent.parent.parent / "fonts" / "PIXELADE.TTF"


def pixelade(taille):
    """Retourne la police PIXELADE chargée à la taille demandée (en pixels)."""
    return pygame.font.Font(str(_CHEMIN_PIXELADE), max(1, int(taille)))
