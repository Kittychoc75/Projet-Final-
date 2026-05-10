from jeu.monde.niveau import Niveau


class Foret(Niveau):
    """Niveau forêt : décor extérieur intermédiaire de la chaîne de niveaux."""

    NOM = "foret"

    def __init__(self):
        """Charge les assets `foret.png`, `foret_mur.png`, `foret_meta.png`."""
        super().__init__(
            chemin_image="images/foret.png",
            chemin_mur="images/foret_mur.png",
            chemin_meta="images/foret_meta.png",
        )
