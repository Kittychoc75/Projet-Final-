from jeu.monde.niveau import Niveau


class Temple(Niveau):
    NOM = "temple"

    def __init__(self):
        super().__init__(
            chemin_image="images/temple.png",
            chemin_mur="images/temple_mur.png",
            chemin_meta="images/temple_meta.png",
        )
