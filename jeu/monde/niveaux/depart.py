from jeu.monde.niveau import Niveau

class Depart(Niveau):
    def __init__(self):
        super().__init__(
            chemin_image="images/debut.png",
            chemin_mur="images/debut_mur.png",
            chemin_meta="images/debut_meta.png",
        )
