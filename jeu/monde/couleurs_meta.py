"""Couleurs des marqueurs dans les masques meta des niveaux.

Chaque marqueur est UN pixel (ou un petit blob) peint dans `<niveau>_meta.png`.
Pour ajouter un nouveau type de marqueur, ajouter une couleur ici puis la lire
dans `Niveau`.
"""

COULEUR_SPAWN = (0, 255, 0)      # vert  — apparition du perso
COULEUR_SORTIE = (255, 0, 0)     # rouge — sortie vers niveau suivant
