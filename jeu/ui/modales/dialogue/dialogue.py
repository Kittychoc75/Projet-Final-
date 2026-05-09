# jeu/ui/modales/dialogue/dialogue.py
import pygame
from pygame.math import Vector2

from jeu.ui import polices
from jeu.ui.modales.modale import Modale
from jeu.ui.texte_colore import calculer_layout, dessiner_layout


class _PanneauBas:
    """Panneau scalable ancré en bas-centre (pour les dialogues)."""

    LARGEUR_LOGIQUE = 700
    HAUTEUR_LOGIQUE = 160
    MARGE_BAS = 20

    def __init__(self, chemin_image):
        origine = pygame.image.load(chemin_image).convert_alpha()
        self._base = pygame.transform.smoothscale(
            origine, (self.LARGEUR_LOGIQUE, self.HAUTEUR_LOGIQUE)
        )
        self.image = self._base
        self.rect = self._base.get_rect()
        self.echelle = Vector2(1, 1)

    def redimensionner(self, echelle):
        self.echelle = Vector2(echelle)
        l = max(1, int(self.LARGEUR_LOGIQUE * self.echelle.x))
        h = max(1, int(self.HAUTEUR_LOGIQUE * self.echelle.y))
        self.image = pygame.transform.smoothscale(self._base, (l, h))
        self.rect = self.image.get_rect()

    def dessiner(self, surface):
        marge = int(self.MARGE_BAS * self.echelle.y)
        self.rect.midbottom = (surface.get_width() // 2, surface.get_height() - marge)
        surface.blit(self.image, self.rect.topleft)


class ModaleDialogue(Modale):
    DELAI_FRAPPE = 25.0     # ms par caractère (effet machine à écrire)
    DELAI_BOUCHE = 100.0    # ms entre changements de sprite (anim bouche)
    LARGEUR_PORTRAIT = 0.30  # part horizontale réservée au portrait
    PADDING = 18             # padding interne (logique, multiplié par échelle.y)
    TAILLE_POLICE = 22
    COULEUR_TEXTE = (255, 255, 255)

    def __init__(self):
        super().__init__(
            panneau=_PanneauBas("images/zone_texte.png"),
            icone=None,
            centree=False,
        )
        self.dialogue = None
        self._chars_visibles = 0
        self._timer_frappe = 0.0
        self._timer_bouche = 0.0
        self._bouche_ouverte = False
        self._echelle = Vector2(1, 1)
        self._invalider_caches()

    def _invalider_caches(self):
        self._layout = None
        self._hauteur_ligne = 0
        self._police = None
        self._sprite_1_scaled = None
        self._sprite_2_scaled = None
        self._portrait_dim = (0, 0)

    @property
    def bloque_jeu(self):
        return self.ouvert

    def declencher(self, dialogue):
        dialogue.reinitialiser()
        self.dialogue = dialogue
        self._chars_visibles = 0
        self._timer_frappe = 0.0
        self._timer_bouche = 0.0
        self._bouche_ouverte = False
        self._invalider_caches()
        self.ouvert = True

    def gerer_evenement(self, evenement):
        if not self.ouvert or self.dialogue is None:
            return
        avancer = (
            (evenement.type == pygame.KEYDOWN
             and evenement.key in (pygame.K_SPACE, pygame.K_RETURN))
            or (evenement.type == pygame.MOUSEBUTTONDOWN
                and evenement.button == 1)
        )
        if avancer:
            self._avancer()

    def _avancer(self):
        message = self.dialogue.message_courant()
        if self._chars_visibles < len(message):
            # 1er clic : on saute le streaming, on affiche tout le message
            self._chars_visibles = len(message)
            return
        if self.dialogue.suivant():
            self._chars_visibles = 0
            self._timer_frappe = 0.0
            self._layout = None
        else:
            if self.dialogue.on_termine:
                self.dialogue.on_termine()
            self.ouvert = False
            self.dialogue = None

    def mettre_a_jour(self, dt):
        if not self.ouvert or self.dialogue is None:
            return
        message = self.dialogue.message_courant()
        if self._chars_visibles < len(message):
            self._timer_frappe += dt
            while self._timer_frappe >= self.DELAI_FRAPPE and self._chars_visibles < len(message):
                self._timer_frappe -= self.DELAI_FRAPPE
                self._chars_visibles += 1
        en_frappe = self._chars_visibles < len(message)
        self._timer_bouche += dt
        if self._timer_bouche >= self.DELAI_BOUCHE:
            self._timer_bouche -= self.DELAI_BOUCHE
            self._bouche_ouverte = (not self._bouche_ouverte) if en_frappe else False

    def redimensionner_contenu(self, echelle):
        self._echelle = Vector2(echelle)
        self._invalider_caches()

    def dessiner_contenu(self, surface):
        if self.dialogue is None:
            return
        rect = self.panneau.rect
        padding = max(1, int(self.PADDING * self._echelle.y))

        # Portrait à gauche
        portrait_w = int(rect.width * self.LARGEUR_PORTRAIT)
        portrait_h = rect.height
        sprite = self._sprite_courant(portrait_w, portrait_h)
        sprite_rect = sprite.get_rect()
        sprite_rect.midbottom = (rect.left + portrait_w // 2, rect.bottom)
        surface.blit(sprite, sprite_rect.topleft)

        # Texte à droite
        zone_texte = pygame.Rect(
            rect.left + portrait_w,
            rect.top + padding,
            rect.width - portrait_w - padding,
            rect.height - 2 * padding,
        )
        self._ensurer_layout(zone_texte.width)
        dessiner_layout(
            surface,
            self._layout,
            self._police,
            zone_texte,
            self._chars_visibles,
            self._hauteur_ligne,
        )

    def _ensurer_layout(self, largeur_max):
        if self._layout is not None and self._layout_largeur == largeur_max:
            return
        taille_police = max(1, int(self.TAILLE_POLICE * self._echelle.y))
        self._police = polices.pixelade(taille_police)
        self._layout, self._hauteur_ligne = calculer_layout(
            self.dialogue.message_courant(),
            self._police,
            largeur_max,
            self.dialogue.couleurs_speciales,
            self.COULEUR_TEXTE,
        )
        self._layout_largeur = largeur_max

    def _sprite_courant(self, max_w, max_h):
        target = (max_w, max_h)
        if self._sprite_1_scaled is None or target != self._portrait_dim:
            self._portrait_dim = target
            personnage = self.dialogue.personnage
            self._sprite_1_scaled = self._fit(personnage.sprite_dialogue_1, max_w, max_h)
            self._sprite_2_scaled = self._fit(personnage.sprite_dialogue_2, max_w, max_h)
        return self._sprite_2_scaled if self._bouche_ouverte else self._sprite_1_scaled

    @staticmethod
    def _fit(sprite, max_w, max_h):
        sw, sh = sprite.get_size()
        ratio = min(max_w / sw, max_h / sh)
        return pygame.transform.smoothscale(
            sprite, (max(1, int(sw * ratio)), max(1, int(sh * ratio)))
        )
