# jeu/ui/modales/modale.py
import pygame
from jeu.ui.modales.jauge import Jauge
from jeu.ui.modales.label import Label
from jeu.ui.element import ElementUI

class Modale:
    def __init__(self, icone, panneau, centree=False):
        self.icone = icone        # ElementUI
        self.panneau = panneau    # ElementUI
        self.vie = Jauge(100, 0, 100, (700, 250), 200, 30, (94, 199, 118), "VIE")  
        self.xp = Jauge(0, 0, 100, (700, 300), 200, 30, (255, 230, 123), "XP")    
        self.sante = Jauge(0, -100, 100, (700, 350), 200, 30, (245, 121, 158), "SANTÉ")   
        self.texte_informations = Label((680, 160), "INFORMATIONS")
        self.texte_inventaire = Label((377, 160), "INVENTAIRE")
        self.panneau.centree = centree
        self.ouvert = False

    def gerer_clic(self, evenement):
        if (evenement.type == pygame.MOUSEBUTTONUP
                and evenement.button == 1
                and self.icone.contient(evenement.pos)):
            self.ouvert = not self.ouvert

    def redimensionner(self, echelle):
        self.icone.redimensionner(echelle)
        self.panneau.redimensionner(echelle)

    def dessiner(self, surface):
        self.icone.dessiner(surface)
        if self.ouvert:
            self.panneau.dessiner(surface)
            self.vie.dessiner(surface)  
            self.xp.dessiner(surface)
            self.sante.dessiner(surface)
            self.texte_informations.dessiner(surface)
            self.texte_inventaire.dessiner(surface)
          