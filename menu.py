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

# Classe pour les boutons
class Button:
    def __init__(self, text, rect):
        self.text = text
        self.rect = rect

    def draw(self, screen, font):
        # Dessiner le bouton
        pygame.draw.rect(screen, GRIS, self.rect)
        pygame.draw.rect(screen, NOIR, self.rect, 2)
        # Écrire le texte
        text_surf = font.render(self.text, True, NOIR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# On charge l'image de fond
arriere_plan = pygame.image.load("fond_menu.JPG")  
arriere_plan = pygame.transform.scale(arriere_plan, (largeur, hauteur))  

# Les polices pour écrire du texte
police = pygame.font.Font(None, 36)  
petite_police = pygame.font.Font(None, 24)  

# Nos quatre boutons
boutons = [
    Button("Jouer", pygame.Rect(75, 339, 180, 38)),
    Button("Reset", pygame.Rect(75, 414, 180, 38)),
    Button("Sauvegardes", pygame.Rect(774, 339, 180, 38)),
    Button("Paramètres", pygame.Rect(774, 414, 180, 38))
]

# Fonction pour dessiner les boutons
def dessiner_boutons():
    for bouton in boutons:
        bouton.draw(ecran, police)

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
                if bouton.is_clicked(position_souris):  # Si c'est un bouton
                    if bouton.text == "Jouer":
                        # Continuer le jeu
                        pass
                    elif bouton.text == "Paramètres":
                        # Ouvrir les paramètres
                        subprocess.run([sys.executable, 'parametres.py'])
                    elif bouton.text == "Sauvegardes":
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

                    elif bouton.text == "Reset":
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
