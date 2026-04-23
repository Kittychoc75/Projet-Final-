import pygame  # Pour faire fonctionner le jeu
import sys  # Pour quitter proprement
import subprocess  # Pour lancer des trucs du système
import os  # Pour gérer les dossiers et fichiers


# On lance Pygame
pygame.init()

# Configuration de la fenêtre de jeu
largeur, hauteur = 1000, 570  # Les dimensions de notre écran
ecran = pygame.display.set_mode((largeur, hauteur))  # Créer la fenêtre
pygame.display.set_caption("Pixel Falls")  # Titre de la fenêtre

# Les couleurs qu'on va utiliser (format RGB)
BLANC = (255, 255, 255)  # Blanc
NOIR = (0, 0, 0)  # Noir
GRIS = (200, 200, 200)  # Gris pour les boutons

# On charge l'image de fond
arriere_plan = pygame.image.load("fond_menu.JPG")  
arriere_plan = pygame.transform.scale(arriere_plan, (largeur, hauteur))  

# Les polices pour écrire du texte
police = pygame.font.Font(None, 36)  # Grande police pour les boutons
petite_police = pygame.font.Font(None, 24)  # Petite police pour le bas de l'écran

# Nos quatre boutons (position et texte)
boutons = [
    {"texte": "Jouer", "rectangle": pygame.Rect(75, 339, 180, 38)},  # Gauche haut
    {"texte": "Reset", "rectangle": pygame.Rect(75, 414, 180, 38)},  # Gauche bas
    {"texte": "Sauvegardes", "rectangle": pygame.Rect(774, 339, 180, 38)},  # Droite haut
    {"texte": "Paramètres", "rectangle": pygame.Rect(774, 414, 180, 38)}  # Droite bas
]

# Fonction pour dessiner les boutons
def dessiner_boutons():
    for bouton in boutons:
        # Traçer le bouton en gris
        pygame.draw.rect(ecran, GRIS, bouton["rectangle"])
        # Ajouter une bordure noire
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
