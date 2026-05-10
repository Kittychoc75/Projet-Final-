from jeu.monde.niveau import Niveau


class Ruines(Niveau):
    """Niveau ruines : décor abandonné, étape avancée de la chaîne de niveaux."""

    NOM = "ruines"

    def __init__(self):
        """Charge les assets `ruines.png`, `ruines_mur.png`, `ruines_meta.png`."""
        super().__init__(
            chemin_image="images/ruines.png",
            chemin_mur="images/ruines_mur.png",
            chemin_meta="images/ruines_meta.png",
        )
