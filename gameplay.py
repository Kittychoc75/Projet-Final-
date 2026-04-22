import pygame 
import config
from joueur import Perso

class Gameplay(): 
    def __init__(self, screen):
        self.screen = screen
        self.perso = Perso(160.0, 300.0)
        
    def update(self, dt):
        self.screen.fill((255, 255, 255))
        self.perso.mouvement(dt) 
        self.perso.dessiner(self.screen)
        
  

 
    
   