from jeu.monde.niveaux.depart import Depart
from jeu.monde.niveaux.foret import Foret
from jeu.monde.niveaux.ruines import Ruines
from jeu.monde.niveaux.temple import Temple
from jeu.monde.niveaux.village import Village

__all__ = ["Depart", "Foret", "Ruines", "Temple", "Village"]

# Lookup par nom (utilisé par scenario.yaml).
PAR_NOM = {cls.NOM: cls for cls in (Depart, Foret, Village, Ruines, Temple)}
