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
from jeu import Ecran, Gameplay, config, sauvegarde
from jeu.menu import Menu
from jeu.scenario import Scenario

pygame.font.init()
parseur = argparse.ArgumentParser(description="Pixel Fall")
parseur.add_argument(
    "--debug",
    action="store_true",
    help="Affiche les hitboxes, masques de collision, spawn et sortie.",
)
arguments = parseur.parse_args()

surface = pygame.display.set_mode((config.LARGEUR, config.HAUTEUR), pygame.RESIZABLE)
pygame.display.set_caption("Pixel Fall")

gameplay = None
ecran = None
en_cours = True
while en_cours:
    menu = Menu(surface)
    intention = menu.executer()
    surface = pygame.display.get_surface()

    if intention == Menu.QUITTER:
        en_cours = False
        break

    if intention == Menu.REINITIALISER:
        gameplay = None
        ecran = None

    if gameplay is None:
        scenario = Scenario("scenario.yaml")
        gameplay = Gameplay(surface, scenario=scenario, debug=arguments.debug)
        ecran = Ecran(gameplay)
        etat_sauve = sauvegarde.charger()
        if etat_sauve:
            gameplay.restaurer(etat_sauve)

    surface = ecran.appliquer_taille(surface.get_size())

    horloge = pygame.time.Clock()
    en_jeu = True
    while en_jeu:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_jeu = False
                en_cours = False
            elif evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
                en_jeu = False
            elif evenement.type == pygame.VIDEORESIZE:
                surface = ecran.appliquer_taille(evenement.size)
            gameplay.gerer_evenements(evenement)

        dt = horloge.tick(60)
        gameplay.mettre_a_jour(dt)
        pygame.display.update()

    # Le jeu vient de se mettre en pause (ESC) ou de fermer la fenêtre : on sauvegarde.
    if gameplay is not None:
        sauvegarde.sauvegarder(gameplay.etat())

    surface = pygame.display.get_surface()

pygame.quit()
