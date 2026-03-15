import pygame

class Perso:
    def __init__(self, x, y, vitesse, direction): 
        self.x = x 
        self.y = y 
        self.vitesse = vitesse
        self.direction = direction
        
        self.image_down = pygame.image.load("images/perso_down.png") 
        self.image_up = pygame.image.load("images/perso_up.png")
        self.image_left = pygame.image.load("images/perso_left.png")
        self.image_right = pygame.image.load("images/perso_right.png")
        self.image = pygame.image.load("images/perso_down.png")
    
    def mouvement(self, keys):
        if keys[pygame.K_UP] == True:
            self.y -= self.vitesse
            self.direction = "up"
            self.image = self.image_up
        elif keys[pygame.K_DOWN] == True:
            self.y += self.vitesse
            self.direction = "down"
            self.image = self.image_down
        elif keys[pygame.K_LEFT] == True:
            self.x -= self.vitesse
            self.direction = "left"
            self.image = self.image_left
        elif keys[pygame.K_RIGHT] == True:
            self.x += self.vitesse
            self.direction = "right"
            self.image = self.image_right

    def rafraichir(self, surface, keys):
        self.mouvement(keys)
        surface.blit(self.image, (self.x, self.y))