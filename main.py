import pygame
from gameplay import Gameplay 

pygame.init() 

LARGEUR = 800
HAUTEUR = 600

screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
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