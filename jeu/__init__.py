"""Package racine du jeu : ré-exporte les classes principales pour `from jeu import …`."""
from jeu.ecran import Ecran
from jeu.gameplay import Gameplay

__all__ = ["Ecran", "Gameplay"]
