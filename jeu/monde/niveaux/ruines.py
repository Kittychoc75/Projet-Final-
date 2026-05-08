from jeu.monde.niveau import Niveau

class Ruines(Niveau):
    def __init__(self):
        super().__init__(
            chemin_image="images/ruines.png",
            chemin_mur="images/ruines_mur.png",
            chemin_meta="images/ruines_meta.png",
        )
        