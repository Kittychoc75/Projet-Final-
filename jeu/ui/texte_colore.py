"""Rendu de texte avec coloration par mot et word-wrap.

Sépare le calcul du layout (positions des tokens) du rendu (qui peut être
animé via `chars_visibles` pour un effet machine à écrire).
"""
import re

import pygame

COULEUR_CODE = (180, 80, 255)
_TOKEN_PATTERN = re.compile(r"\([01\s]+\)|\S+")


def _couleur(token, dict_couleurs, defaut, couleur_code):
    if token.startswith("("):
        return couleur_code
    return dict_couleurs.get(token, defaut)


def calculer_layout(texte, police, largeur_max, dict_couleurs, couleur_defaut, espacement_ligne=4, couleur_code=COULEUR_CODE):
    """Pré-calcule positions et surfaces rendues de chaque token (avec word-wrap).

    Retourne (layout, hauteur_ligne) où layout est une liste de dicts :
    {token, surface, x, y, chars_avant}
    """
    tokens = _TOKEN_PATTERN.findall(texte)
    espace_w = police.size(" ")[0]
    hauteur_ligne = police.get_height() + espacement_ligne
    layout = []
    x = 0
    y = 0
    chars_so_far = 0
    for i, token in enumerate(tokens):
        token_w = police.size(token)[0]
        if i > 0:
            if x + espace_w + token_w > largeur_max:
                # passage à la ligne ; le caractère espace devient un saut
                x = 0
                y += hauteur_ligne
                chars_so_far += 1
            else:
                x += espace_w
                chars_so_far += 1
        couleur = _couleur(token, dict_couleurs, couleur_defaut, couleur_code)
        surface = police.render(token, True, couleur)
        layout.append({
            "token": token,
            "surface": surface,
            "couleur": couleur,
            "x": x,
            "y": y,
            "chars_avant": chars_so_far,
        })
        x += token_w
        chars_so_far += len(token)
    return layout, hauteur_ligne


def dessiner_layout(surface, layout, police, rect, chars_visibles, hauteur_ligne):
    """Dessine le layout pré-calculé, jusqu'à `chars_visibles` caractères du texte original."""
    for entree in layout:
        if entree["y"] + hauteur_ligne > rect.height:
            break
        chars_avant = entree["chars_avant"]
        if chars_avant >= chars_visibles:
            break
        chars_dispo = chars_visibles - chars_avant
        token = entree["token"]
        if chars_dispo >= len(token):
            # Token entier visible : on blit la surface pré-rendue (cache).
            surface.blit(entree["surface"], (rect.left + entree["x"], rect.top + entree["y"]))
        else:
            # Token coupé : on rend la portion visible (rare, juste la frame courante).
            partiel = token[:chars_dispo]
            rendu = police.render(partiel, True, entree["couleur"])
            surface.blit(rendu, (rect.left + entree["x"], rect.top + entree["y"]))
            break
