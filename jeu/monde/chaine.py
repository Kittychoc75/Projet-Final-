"""Chaîne ordonnée des niveaux du jeu.

Quand le perso entre dans la zone `sortie` du niveau courant, le jeu passe au
suivant dans cette liste. Si le dernier niveau est atteint, le jeu reste dessus.

Contrainte: tous les niveaux de la chaîne doivent avoir les mêmes dimensions
(image + masques). Sinon le ratio change et le perso est rescalé entre niveaux.
"""

from jeu.monde.niveaux import Depart, Foret

CHAINE = [
    Depart,
    Foret,
]
