import pygame
import sys
import subprocess
import os
import shutil

pygame.init()

#Configuration de la fenêtre de jeu
largeur, hauteur = 1000, 570
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Pixel Fall")

#Couleurs
BLANC = (255, 255, 255)  
NOIR = (0, 0, 0) 
GRIS = (200, 200, 200)  


def dessiner_bouton(bouton):
    pygame.draw.rect(ecran, GRIS, bouton["rectangle"])
    pygame.draw.rect(ecran, NOIR, bouton["rectangle"], 2)
    texte_surf = police.render(bouton["texte"], True, NOIR)
    rect_texte = texte_surf.get_rect(center=bouton["rectangle"].center)
    ecran.blit(texte_surf, rect_texte)

def bouton_clique(bouton, pos):
    return bouton["rectangle"].collidepoint(pos)


arriere_plan = pygame.image.load("images/fond_menu.JPG")  
arriere_plan = pygame.transform.scale(arriere_plan, (largeur, hauteur))  

#Les polices pour écrire du texte
police = pygame.font.Font("PIXELADE.TTF", 26)
police_bouton = pygame.font.Font("PIXELADE.TTF", 28)  

# Nos quatre boutons
boutons = [
    {"texte": "Jouer", "rectangle": pygame.Rect(75, 339, 180, 38)},
    {"texte": "Reset", "rectangle": pygame.Rect(75, 414, 180, 38)},
    {"texte": "Sauvegardes", "rectangle": pygame.Rect(774, 339, 180, 38)},
    {"texte": "Paramètres", "rectangle": pygame.Rect(774, 414, 180, 38)}
]

def dessiner_boutons():
    for bouton in boutons:
        dessiner_bouton(bouton)

# La boucle principale du jeu 
en_cours = True
while en_cours:
    #On regarde les événements
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False  
        elif evenement.type == pygame.MOUSEBUTTONDOWN:
            #L'utilisateur clique et on vérifie quel bouton
            position_souris = pygame.mouse.get_pos()
            for bouton in boutons:
                if bouton_clique(bouton, position_souris):  # Si c'est un bouton
                    if bouton["texte"] == "Jouer":
                        #Lance le jeu
                        subprocess.Popen([sys.executable, 'main.py'])
                        en_cours = False
                    elif bouton["texte"] == "Paramètres":
                        pass 
                        en_cours = False
                    elif bouton["texte"] == "Sauvegardes":
                        dossier_sauvegarde = "sauvegardes"
                        if not os.path.exists(dossier_sauvegarde):
                            os.makedirs(dossier_sauvegarde)
                        if sys.platform == 'win32':
                            os.startfile(dossier_sauvegarde)
                        elif sys.platform == 'darwin':
                            subprocess.run(['open', dossier_sauvegarde])
                        else:
                            pass

                    elif bouton["texte"] == "Reset":
                        dossier_sauvegarde = "sauvegardes"
                        if os.path.exists(dossier_sauvegarde):
                            shutil.rmtree(dossier_sauvegarde)
                        subprocess.Popen([sys.executable, 'main.py'])
                        en_cours = False

    ecran.blit(arriere_plan, (0, 0))
    dessiner_boutons()
    pygame.display.flip() 

#Fermer Pygame
pygame.quit()
sys.exit() 
