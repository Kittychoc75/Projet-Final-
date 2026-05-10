"""Couleurs des marqueurs dans les masques meta des niveaux.

Chaque marqueur est UN pixel (ou un petit blob) peint dans `<niveau>_meta.png`.
Pour ajouter un nouveau type de marqueur, ajouter une couleur ici puis la lire
dans `Niveau`.
"""

COULEUR_SPAWN = (0, 255, 0)      # vert  — apparition du perso
COULEUR_SORTIE = (255, 0, 0)     # rouge — sortie vers niveau suivant
COULEUR_MONSTRE = (0, 0, 255)     # bleu  — position d'un monstre
COULEUR_QUETE = (255, 0, 255)     # violet — position d'une quête
COULEUR_DIALOGUE = (0, 255, 255)    # cyan   — position d'un dialogue
COULEUR_PASSAGE = (255, 255, 0)     # jaune  — position d'un combat entre niveaux
