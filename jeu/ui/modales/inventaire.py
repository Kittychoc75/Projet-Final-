# jeu/ui/modales/inventaire.py
from jeu.ui.element import ElementUI
from jeu.ui.modales.modale import Modale


class Inventaire(Modale):
    def __init__(self):
        super().__init__(
            icone=ElementUI("images/icon.png", (15, 15)),
            panneau=ElementUI("images/inventaire.png", (350, 130)),
            centree=True
        )