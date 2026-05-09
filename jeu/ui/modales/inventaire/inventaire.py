# jeu/ui/modales/inventaire/inventaire.py
from jeu.ui.element import ElementUI
from jeu.ui.modales.modale import Modale
from jeu.ui.jauge import Jauge
from jeu.ui.label import Label


class Inventaire(Modale):
    def __init__(self):
        super().__init__(
            icone=ElementUI("images/icon.png", (15, 15)),
            panneau=ElementUI("images/inventaire.png", (350, 130)),
            centree=True,
        )
        self.vie = Jauge(100, 0, 100, (508, 250), 200, 30, (94, 199, 118), "VIE")
        self.xp = Jauge(0, 0, 100, (508, 300), 200, 30, (255, 230, 123), "XP")
        self.sante = Jauge(0, -100, 100, (508, 350), 200, 30, (245, 121, 158), "SANTÉ")
        self.texte_informations = Label((505, 100), "INFORMATIONS")
        self.texte_inventaire = Label((275, 100), "INVENTAIRE")

    def redimensionner_contenu(self, echelle):
        self.vie.redimensionner(echelle)
        self.xp.redimensionner(echelle)
        self.sante.redimensionner(echelle)
        self.texte_informations.redimensionner(echelle)
        self.texte_inventaire.redimensionner(echelle)

    def dessiner_contenu(self, surface):
        self.vie.dessiner(surface)
        self.xp.dessiner(surface)
        self.sante.dessiner(surface)
        self.texte_informations.dessiner(surface)
        self.texte_inventaire.dessiner(surface)
