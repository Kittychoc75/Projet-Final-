import pygame 

class Depart: 
    def __init__(self): 
        self.image = pygame.image.load("images/debut.png")
        self.hauteur = self.image.get_height()
        self.largeur = self.image.get_width()

