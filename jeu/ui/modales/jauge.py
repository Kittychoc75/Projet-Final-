import pygame 

class Jauge:
    def __init__(self, valeur, min, max, position, largeur, hauteur, couleur, texte=""):  
        self.valeur = valeur
        self.min = min
        self.max = max
        self.position = position
        self.largeur = largeur
        self.hauteur = hauteur
        self.couleur = couleur

        self.police = pygame.font.SysFont("8-bit Operator", 20)  # Police pour afficher le texte de la jauge
        self.texte = texte

    def mettre_a_jour(self, nouvelle_valeur):
        self.valeur = max(self.min, min(self.max, nouvelle_valeur))
    
    def calculer_pourcentage(self, valeur):
        # Calcul le pourcentage de la jauge : 0 = barre vide; 1 = barre pleine 
        return (valeur - self.min) / (self.max - self.min)

    def dessiner(self, surface):
        # Fond de la jauge 
        pygame.draw.rect(surface, (182, 181, 249), (*self.position, self.largeur, self.hauteur))
        largeur_remplie = self.largeur * self.calculer_pourcentage(self.valeur)
        pygame.draw.rect(surface, self.couleur, (*self.position, largeur_remplie, self.hauteur))
        # Bordure de la jauge
        pygame.draw.rect(surface, (133, 132, 180), (*self.position, self.largeur, self.hauteur), 2) 
        if self.texte:
            texte_surface = self.police.render(f"{self.texte}: {self.valeur}/{self.max}", True, (255, 255, 255))
            surface.blit(texte_surface, (self.position[0] + 5, self.position[1] + 5))