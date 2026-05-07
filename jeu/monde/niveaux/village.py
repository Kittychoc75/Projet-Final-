from jeu.monde.niveau import Niveau

class Village(Niveau):
    def __init__(self):
        super().__init__(
            chemin_image="images/village.png",
            chemin_mur="images/village_mur.png",
            chemin_meta="images/village_meta.png",
        )