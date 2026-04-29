from depart import Depart 
import config 

class Monde: 
    def __init__(self): 
        self.niveau = Depart()
        self.camera_x = 0
        self.camera_y = 0

    def suivre_joueur(self, x, y):
        self.camera_x = x - config.LARGEUR / 2
        self.camera_y = y - config.HAUTEUR / 2
        
        if self.camera_x < 0:
            self.camera_x = 0

        if self.camera_y < 0:
            self.camera_y = 0

        if self.camera_x > self.niveau.largeur - config.LARGEUR:
            self.camera_x = self.niveau.largeur - config.LARGEUR

        if self.camera_y > self.niveau.hauteur - config.HAUTEUR:
            self.camera_y = self.niveau.hauteur - config.HAUTEUR

    def dessiner_monde(self, screen): 
        screen.blit(self.niveau.image, (-self.camera_x, -self.camera_y)) 