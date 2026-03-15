from perso import Perso
import pygame 

class Gameplay:
    def __init__(self, screen):
        self.screen = screen
        self.perso = Perso(100, 100, 3, "down")
        
    def update(self):   
        keys = pygame.key.get_pressed()
        self.perso.rafraichir(self.screen, keys)

 
    
   