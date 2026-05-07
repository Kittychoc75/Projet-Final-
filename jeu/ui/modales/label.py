import pygame 

class Label:
    def __init__(self, position, texte=""):  
        self.texte = texte
        self.position = position

        self.police = pygame.font.SysFont("8-bit Operator", 40)
        self.padding = 10
    
    def dessiner(self, surface):
        if self.texte:
            texte_surface = self.police.render(f"{self.texte}", True, (133, 132, 180))
            pygame.draw.rect(surface, (133, 132, 180), (*self.position, texte_surface.get_width() + self.padding * 2, texte_surface.get_height() + self.padding * 2), 2) 
            surface.blit(texte_surface, (self.position[0] + self.padding, self.position[1] + self.padding)) 