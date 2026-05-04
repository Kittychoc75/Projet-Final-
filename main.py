"""
Nom du projet : Pixel Fall
Auteur : Sibylle Ménard - Eva Wang-Cheng - Inès Choron
Date début : 13/12/2025
Date de fin : 11/05/2026
Description : Inspiré du jeu Undertale, Pixel Fall est un jeu de plateforme 2D 
              où le joueur, aspiré par son ordinateur, doit explorer un monde, 
              vaincre ou épargner des ennemis et compléter des quêtes 
              afin d'en sortir.
Entrée : Le joueur utilise les touches fléchées pour se déplacer
Sortie : Le joueur doit compléter des quêtes pour progresser 
"""

import argparse
import pygame
from jeu import Ecran, Gameplay

parseur = argparse.ArgumentParser(description="Pixel Fall")
parseur.add_argument(
    "--debug",
    action="store_true",
    help="Affiche les hitboxes, masques de collision, spawn et sortie.",
)
arguments = parseur.parse_args()

surface = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
pygame.display.set_caption("Pixel Fall")

gameplay = Gameplay(surface, debug=arguments.debug)
ecran = Ecran(gameplay)
surface = ecran.appliquer_taille(surface.get_size())

horloge = pygame.time.Clock()
jeu_actif = True

while jeu_actif:
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            jeu_actif = False
        elif evenement.type == pygame.VIDEORESIZE:
            surface = ecran.appliquer_taille(evenement.size)
        gameplay.gerer_evenements(evenement)

    dt = horloge.tick(60)
    gameplay.mettre_a_jour(dt)
    pygame.display.update()

pygame.quit()
