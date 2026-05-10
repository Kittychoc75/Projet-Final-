from jeu.monde.niveau import Niveau


class Temple(Niveau):
    """Niveau temple : dernier décor de la chaîne, fin du parcours."""

    NOM = "temple"

    def __init__(self):
        """Charge les assets `temple.png`, `temple_mur.png`, `temple_meta.png`."""
        super().__init__(
            chemin_image="images/temple.png",
            chemin_mur="images/temple_mur.png",
            chemin_meta="images/temple_meta.png",
        )
