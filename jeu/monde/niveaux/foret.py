from jeu.monde.niveau import Niveau

class Foret(Niveau):
    def __init__(self):
        super().__init__(
            chemin_image="images/foret.png",
            chemin_mur="images/foret_mur.png",
            chemin_meta="images/foret_meta.png",
        )
