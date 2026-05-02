import pygame 
import config
from joueur import Perso
from monde import Monde 

class Gameplay(): 
    def __init__(self, screen):
        self.screen = screen
        self.perso = Perso(200.0, 700.0)

        self.monde = Monde()
        
    def update(self, dt):
        self.perso.mouvement(dt) 
        self.monde.suivre_joueur(self.perso.x, self.perso.y) 
        self.monde.dessiner_monde(self.screen) 
        self.perso.dessiner_joueur(self.screen, self.monde.camera_x, self.monde.camera_y)
        
        
  

 
    
   