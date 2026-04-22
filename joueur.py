import pygame
import config

class Perso(pygame.sprite.Sprite):
    def __init__(self, x, y): 
        super().__init__() 
        self.x = x
        self.y = y 
        self.vitesse = config.VITESSE_PERSO

        self.image = pygame.image.load("images/perso_front.png")
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        self.image_down = pygame.image.load("images/perso_front.png") 
        self.image_up = pygame.image.load("images/perso_back.png")
        self.image_left = pygame.image.load("images/perso_left.png")
        self.image_right = pygame.image.load("images/perso_right.png")
        
    def mouvement(self, dt):
        pressed_keys = pygame.key.get_pressed() 

        if pressed_keys[pygame.K_UP]: 
            self.y -= self.vitesse * dt

            # Vérification limite en haut
            if self.y < self.rect.height/2:
                self.y = self.rect.height/2
            self.rect.center = (int(self.x), int(self.y))
            self.image = self.image_up

        if pressed_keys[pygame.K_DOWN]: 
            self.y += self.vitesse * dt 

            # Vérification limite en bas
            if self.y + self.rect.height/2 > config.HAUTEUR: 
                self.y = config.HAUTEUR - self.rect.height/2
            self.rect.center = (int(self.x), int(self.y))
            self.image = self.image_down

        if pressed_keys[pygame.K_LEFT]: 
            self.x -= self.vitesse * dt

            # Vérification limite à gauche
            if self.x < self.rect.width/2:
                self.x = self.rect.width/2
            self.rect.center = (int(self.x), int(self.y))
            self.image = self.image_left

        if pressed_keys[pygame.K_RIGHT]: 
            self.x += self.vitesse * dt 

            # Vérification limite à droite
            if self.x + self.rect.width/2 > config.LARGEUR:
               self.x = config.LARGEUR - self.rect.width/2
            self.rect.center = (int(self.x), int(self.y))
            self.image = self.image_right

    def dessiner(self, surface):
        surface.blit(self.image, self.rect)