import pygame 
import config
from joueur import Perso


class Gameplay:
    def __init__(self, screen):
        self.screen = screen
        self.perso = Perso(100, 100)
        
    def update(self):
        self.screen.fill((255, 255, 255))
        self.perso.dessiner(self.screen)
        
  

 
    
   