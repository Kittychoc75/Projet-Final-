import pygame 
from pygame.math import Vector2

class UI: 
    def __init__(self):
        #self.surface = surface
        self.icon = pygame.image.load("images/icon.png") 
        self.rect_icon = self.icon.get_rect()
        self.rect_icon.topleft = (15, 15) 
        self.ouvert = False 

        self.inventaire = pygame.image.load("images/inventaire.png")
        self.position_inventaire = (350, 130)
        self.rect_inventaire = self.inventaire.get_rect()
        
        #self.croix = pygame.image.load("images/croix.png")
        #self.rect_croix = self.croix.get_rect()
        #self.rect_croix.topleft = (self.position_inventaire[0] + 10, self.position_inventaire[1] + 10)

    def gerer_clic(self, evenement): 
        if evenement.type == pygame.MOUSEBUTTONUP: 
            if evenement.button == 1:  # 1 seul clic gauche
                    if self.rect_icon.collidepoint(evenement.pos):
                        self.ouvert = not self.ouvert
    
    def dessiner(self, surface): 
        surface.blit(self.icon, self.rect_icon) 
        self.rect_inventaire.topleft = self.position_inventaire
        if self.ouvert: 
            # Dessiner l'inventaire
            surface.blit(self.inventaire, self.rect_inventaire)
            #surface.blit(self.croix, self.rect_croix)
    

            