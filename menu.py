import pygame  
import sys 
import subprocess  
import os  


pygame.init()

# Configuration de la fenêtre de jeu
largeur, hauteur = 1000, 570  
ecran = pygame.display.set_mode((largeur, hauteur))  
pygame.display.set_caption("Pixel Falls") 

# Les couleurs qu'on va utiliser (format RGB)
BLANC = (255, 255, 255)  
NOIR = (0, 0, 0) 
GRIS = (200, 200, 200)  

# On charge l'image de fond
arriere_plan = pygame.image.load("fond_menu.JPG")  
arriere_plan = pygame.transform.scale(arriere_plan, (largeur, hauteur))  

# Les polices pour écrire du texte
police = pygame.font.Font(None, 36)  
petite_police = pygame.font.Font(None, 24)  

# Nos quatre boutons (position et texte)
boutons = [
    {"texte": "Jouer", "rectangle": pygame.Rect(75, 339, 180, 38)},  
    {"texte": "Reset", "rectangle": pygame.Rect(75, 414, 180, 38)},  
    {"texte": "Sauvegardes", "rectangle": pygame.Rect(774, 339, 180, 38)},  
    {"texte": "Paramètres", "rectangle": pygame.Rect(774, 414, 180, 38)}  
]

# Fonction pour dessiner les boutons
def dessiner_boutons():
    for bouton in boutons:
        pygame.draw.rect(ecran, GRIS, bouton["rectangle"])
        pygame.draw.rect(ecran, NOIR, bouton["rectangle"], 2)
        # Écrire le texte du bouton
        surface_texte = police.render(bouton["texte"], True, NOIR)
        rect_texte = surface_texte.get_rect(center=bouton["rectangle"].center)
        ecran.blit(surface_texte, rect_texte)

# La boucle principale du jeu 
en_cours = True
while en_cours:
    #On regarde les événements
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False  # L'utilisateur a fermé la fenêtre donc le jeu s'arrete
        elif evenement.type == pygame.MOUSEBUTTONDOWN:
            # L'utilisateur clique et on vérifie quel bouton
            position_souris = pygame.mouse.get_pos()
            for bouton in boutons:
                if bouton["rectangle"].collidepoint(position_souris):  # Si c'est un bouton
                    if bouton["texte"] == "Jouer":
                        # Continuer le jeu
                        pass
                    elif bouton["texte"] == "Paramètres":
                        # Ouvrir les paramètres
                        pass
                    elif bouton["texte"] == "Sauvegardes":
                        # Ouvrir le dossier des sauvegardes
                        dossier_sauvegarde = "sauvegardes"
                        if not os.path.exists(dossier_sauvegarde): # Si le dossier n'existe pas, on le crée
                            os.makedirs(dossier_sauvegarde)
                        if sys.platform == 'win32': # Pour Windows
                            os.startfile(dossier_sauvegarde)
                        elif sys.platform == 'darwin': # Pour macOS
                            subprocess.run(['open', dossier_sauvegarde])
                        else:
                            pass  # Pour autres plateformes, rien faire

                    elif bouton["texte"] == "Reset":
                        # Réinitialiser le jeu
                        pass

    # Afficher l'arrière-plan
    ecran.blit(arriere_plan, (0, 0))
    # Dessiner les boutons
    dessiner_boutons()
    pygame.display.flip() # Mettre à jour l'affichage

# Fermer Pygame
pygame.quit()
sys.exit() 
