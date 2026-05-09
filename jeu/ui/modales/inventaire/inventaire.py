# jeu/ui/modales/inventaire/inventaire.py
import pygame
from pygame.math import Vector2

from jeu.joueur import Joueur
from jeu.ui.element import ElementUI
from jeu.ui.jauge import Jauge
from jeu.ui.label import Label
from jeu.ui.modales.modale import Modale


class Inventaire(Modale):
    # Coordonnées logiques de la grille d'objets (repère config.LARGEUR×config.HAUTEUR)
    GRILLE_X = 285
    GRILLE_Y = 200
    TAILLE_CASE = 60
    ESPACE_CASE = 8
    COLONNES = 3
    LIGNES = 4

    def __init__(self, joueur, scenario):
        super().__init__(
            icone=ElementUI("images/icon.png", (15, 15)),
            panneau=ElementUI("images/inventaire.png", (350, 130)),
            centree=True,
        )
        self.joueur = joueur
        self.scenario = scenario
        self.vie = Jauge(joueur.vie, 0, Joueur.VIE_MAX, (508, 250), 200, 30, (94, 199, 118), "VIE")
        self.xp = Jauge(joueur.xp, 0, Joueur.XP_MAX, (508, 300), 200, 30, (255, 230, 123), "XP")
        self.texte_informations = Label((505, 100), "INFORMATIONS")
        self.texte_inventaire = Label((275, 100), "INVENTAIRE")
        self._echelle = Vector2(1, 1)
        # Cache des sprites d'objets scalés à la taille de case
        self._cache_sprites = {}

    def mettre_a_jour(self, dt):
        self.vie.mettre_a_jour(self.joueur.vie)
        self.xp.mettre_a_jour(self.joueur.xp)

    def redimensionner_contenu(self, echelle):
        self._echelle = Vector2(echelle)
        self.vie.redimensionner(echelle)
        self.xp.redimensionner(echelle)
        self.texte_informations.redimensionner(echelle)
        self.texte_inventaire.redimensionner(echelle)
        self._cache_sprites = {}  # invalidation au resize

    def dessiner_contenu(self, surface):
        self.vie.dessiner(surface)
        self.xp.dessiner(surface)
        self.texte_informations.dessiner(surface)
        self.texte_inventaire.dessiner(surface)
        self._dessiner_objets(surface)

    def _dessiner_objets(self, surface):
        if not self.joueur.objets:
            return
        sx, sy = self._echelle.x, self._echelle.y
        case = max(1, int(self.TAILLE_CASE * sy))
        espace = max(1, int(self.ESPACE_CASE * sy))
        x0 = int(self.GRILLE_X * sx)
        y0 = int(self.GRILLE_Y * sy)
        capacite = self.COLONNES * self.LIGNES
        for i, objet_id in enumerate(self.joueur.objets[:capacite]):
            col = i % self.COLONNES
            row = i // self.COLONNES
            cx = x0 + col * (case + espace)
            cy = y0 + row * (case + espace)
            sprite = self._sprite_pour_case(objet_id, case)
            if sprite is None:
                continue
            rect = sprite.get_rect(center=(cx + case // 2, cy + case // 2))
            surface.blit(sprite, rect.topleft)

    def _sprite_pour_case(self, objet_id, case_px):
        cle = (objet_id, case_px)
        if cle in self._cache_sprites:
            return self._cache_sprites[cle]
        objet = self.scenario.objets.get(objet_id)
        if objet is None:
            return None
        src = objet.sprite_origine
        sw, sh = src.get_size()
        ratio = min(case_px / sw, case_px / sh)
        target = (max(1, int(sw * ratio)), max(1, int(sh * ratio)))
        scaled = pygame.transform.smoothscale(src, target)
        self._cache_sprites[cle] = scaled
        return scaled
