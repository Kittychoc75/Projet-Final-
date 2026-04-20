import pygame
import config

class Perso(pygame.sprite.Sprite):
    def __init__(self, x, y): 
        super().__init__() 
        self.x = x 
        self.y = y 
        self.vitesse = config.VITESSE_PERSO
        #self.direction = direction
        self.image = pygame.image.load("images/perso_down.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

        self.image_down = pygame.image.load("images/perso_down.png") 
        self.image_up = pygame.image.load("images/perso_up.png")
        self.image_left = pygame.image.load("images/perso_left.png")
        self.image_right = pygame.image.load("images/perso_right.png")
        
    def mouvement(self):
        pressed_keys = pygame.key.get_pressed() 
        if pressed_keys[pygame.K_UP]: 
            if self.rect.top > 0:
                self.rect.move_ip(0, -self.vitesse) 
            #self.direction = "up" 
            self.image = self.image_up
        elif pressed_keys[pygame.K_DOWN]: 
            if self.rect.bottom < config.HAUTEUR:
                self.rect.move_ip(0, self.vitesse) 
            #self.direction = "down" 
            self.image = self.image_down
        elif pressed_keys[pygame.K_LEFT]: 
            if self.rect.left > 0:
                self.rect.move_ip(-self.vitesse, 0) 
            #self.direction = "left" 
            self.image = self.image_left
        elif pressed_keys[pygame.K_RIGHT]: 
            if self.rect.right < config.LARGEUR:
                self.rect.move_ip(self.vitesse, 0) 
            #self.direction = "right" 
            self.image = self.image_right
       

    def dessiner(self, surface):
        self.mouvement()
        surface.blit(self.image, self.rect)