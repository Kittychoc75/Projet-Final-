from jeu.monde.niveau import Niveau


class Depart(Niveau):
    """Niveau de départ : tutoriel/intro, premier décor visible au lancement."""

    NOM = "depart"

    def __init__(self):
        """Charge les assets `debut.png`, `debut_mur.png`, `debut_meta.png`."""
        super().__init__(
            chemin_image="images/debut.png",
            chemin_mur="images/debut_mur.png",
            chemin_meta="images/debut_meta.png",
        )
