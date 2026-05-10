from jeu.monde.niveau import Niveau


class Village(Niveau):
    """Niveau village : décor habité, plusieurs PNJ à dialoguer."""

    NOM = "village"

    def __init__(self):
        """Charge les assets `village.png`, `village_mur.png`, `village_meta.png`."""
        super().__init__(
            chemin_image="images/village.png",
            chemin_mur="images/village_mur.png",
            chemin_meta="images/village_meta.png",
        )
