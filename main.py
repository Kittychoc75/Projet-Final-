import pygame
import config
from gameplay import Gameplay

screen = pygame.display.set_mode((config.LARGEUR, config.HAUTEUR))
screen.fill((255, 255, 255))
pygame.display.set_caption("Pixel Fall")
gameplay = Gameplay(screen) 

jeu_actif = True
while jeu_actif:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jeu_actif = False
    
    gameplay.update()
    pygame.display.update()

pygame.quit()