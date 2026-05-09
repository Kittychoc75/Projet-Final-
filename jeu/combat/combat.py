"""ModaleCombat : machine à 3 phases (jauge → tir → défense) en boucle.

Avant le combat, une phase "choix" demande Attaquer / Épargner.
À la fin : victoire (xp+), épargne (sortie sans combat), ou défaite.
Le résultat est notifié via le callback `on_termine`.
"""
import os
import random

import pygame
from pygame.math import Vector2

from jeu import config
from jeu.combat.barre_timing import BarreTiming
from jeu.combat.entites import Coeur, EnnemiCombat, Projectile, point_bord, vitesse_vers
from jeu.combat.sprites import charger_avec_fallback
from jeu.ui import polices
from jeu.ui.bouton import Bouton
from jeu.ui.modales.modale import Modale


# --- Constantes de gameplay ---
DEGATS_BON = 40
GAIN_XP = 20

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 180, 0)
BLEU = (0, 120, 255)

# Tailles logiques (référence config.LARGEUR × config.HAUTEUR)
TAILLE_COEUR = 24
TAILLE_ENNEMI = 150


class ModaleCombat(Modale):
    OPACITE_OVERLAY = 160  # 0 = transparent, 255 = opaque

    def __init__(self, joueur):
        super().__init__(panneau=_PanneauNoir(), icone=None, centree=False)
        self.joueur = joueur
        self.combat_data = None
        self._on_termine = None
        self._echelle = Vector2(1, 1)
        self._phase = None  # state machine : "choix" | "jauge" | "tir" | "defense" | "victoire" | "defaite"
        # Sprites + entités initialisés à declencher()
        self._ennemi = None
        self._coeur = None
        self._barre = None
        self._tir = None
        self._tir_degats = 0
        self._balles = []
        self._temps = 0
        self._temps_defense = 0
        self._prochain_spawn = 0
        self._pv_combat_max = 100
        self._pv_combat = 100  # HP locaux à ce combat (séparés de joueur.vie)
        # UI sub-objets
        self._bouton_attaquer = None
        self._bouton_epargner = None
        self._bouton_continuer = None
        self._layout = {}
        self._overlay = None

    @property
    def bloque_jeu(self):
        return self.ouvert

    # ---------------------------------------------------------------- declencher
    def declencher(self, combat_data, on_termine):
        """combat_data porte le monstre + flags. on_termine(resultat: str) callback."""
        self.combat_data = combat_data
        self._on_termine = on_termine
        # PV combat partent du PV courant du joueur (persistant entre combats)
        self._pv_combat_max = self.joueur.VIE_MAX
        self._pv_combat = max(1, self.joueur.vie)
        # Réinitialise les états
        self._tir = None
        self._tir_degats = 0
        self._balles = []
        self._temps = 0
        self._temps_defense = 0
        self._prochain_spawn = 0
        self._construire_entites()
        self._phase = "choix"
        self.ouvert = True

    def _construire_entites(self):
        cfg = self.combat_data.monstre
        # Sprites ennemi
        sprites = [charger_avec_fallback(c, self._taille_ennemi()) for c in cfg.sprites]
        if not sprites:
            sprites = [charger_avec_fallback("?.png", self._taille_ennemi())]
        self._ennemi = EnnemiCombat(
            nom=cfg.nom,
            sprites=sprites,
            pv=cfg.pv,
            periode_anim=cfg.periode_anim,
            centre=self._layout.get("centre_ennemi", (480, 100)),
        )
        # Cœur
        img_coeur = charger_avec_fallback("images/coeur.png", self._taille_coeur())
        zone_coeur = self._layout.get("zone_coeur", pygame.Rect(0, 0, 1, 1))
        self._coeur = Coeur(img_coeur, zone_coeur)
        # Barre de visée
        self._barre = BarreTiming(self._layout.get("barre_rect", pygame.Rect(0, 0, 1, 1)))
        # Boutons (recalculés à chaque resize)
        self._construire_boutons()

    # ---------------------------------------------------------------- layout
    def redimensionner_contenu(self, echelle):
        self._echelle = Vector2(echelle)
        self._calculer_layout()
        self._overlay = None  # taille a pu changer → force recréation
        # Si combat actif, regénère les entités liées au layout
        if self.ouvert:
            self._reappliquer_layout()
            self._construire_boutons()

    def _ensurer_overlay(self, surface):
        taille = surface.get_size()
        if self._overlay is None or self._overlay.get_size() != taille:
            self._overlay = pygame.Surface(taille, pygame.SRCALPHA)
            self._overlay.fill((0, 0, 0, self.OPACITE_OVERLAY))

    def _calculer_layout(self):
        sx, sy = self._echelle.x, self._echelle.y
        w = int(config.LARGEUR * sx)
        h = int(config.HAUTEUR * sy)
        # Position de l'ennemi (haut, centré)
        centre_ennemi = (w // 2, int(120 * sy))
        # Arène (zone où vit le cœur en phase défense)
        arene_w = int(300 * sx)
        arene_h = int(280 * sy)
        arene = pygame.Rect((w - arene_w) // 2, int(200 * sy), arene_w, arene_h)
        zone_coeur = arene.inflate(-20, -20)
        zone_sortie = arene.inflate(60, 60)
        # Barres PV juste sous l'arène
        y_barres = arene.bottom + int(10 * sy)
        # Jauge de visée tout en bas
        barre_w = int(400 * sx)
        barre_h = int(22 * sy)
        barre_rect = pygame.Rect((w - barre_w) // 2, h - int(40 * sy), barre_w, barre_h)
        self._layout = {
            "ecran": (w, h),
            "centre_ennemi": centre_ennemi,
            "arene": arene,
            "zone_coeur": zone_coeur,
            "zone_sortie": zone_sortie,
            "y_barres": y_barres,
            "barre_rect": barre_rect,
        }

    def _reappliquer_layout(self):
        self._ennemi.centre = self._layout["centre_ennemi"]
        # Re-scale ennemi
        sprites = [pygame.transform.smoothscale(s, self._taille_ennemi()) for s in self._sprites_origine_ennemi()]
        self._ennemi.sprites = sprites
        self._ennemi.rect = sprites[0].get_rect(center=self._ennemi.centre)
        # Cœur
        img_coeur = charger_avec_fallback("images/coeur.png", self._taille_coeur())
        self._coeur = Coeur(img_coeur, self._layout["zone_coeur"])
        # Barre
        self._barre = BarreTiming(self._layout["barre_rect"])

    def _sprites_origine_ennemi(self):
        # On recharge depuis disque pour garder la qualité au resize
        cfg = self.combat_data.monstre
        return [charger_avec_fallback(c, self._taille_ennemi()) for c in cfg.sprites]

    def _taille_ennemi(self):
        s = max(1, int(TAILLE_ENNEMI * self._echelle.y))
        return (s, s)

    def _taille_coeur(self):
        s = max(1, int(TAILLE_COEUR * self._echelle.y))
        return (s, s)

    def _construire_boutons(self):
        sx, sy = self._echelle.x, self._echelle.y
        w, h = self._layout.get("ecran", (config.LARGEUR, config.HAUTEUR))
        # Largeur/hauteur logique 180×55 pour les boutons
        bw = int(180 * sx)
        bh = int(55 * sy)
        # Choix : 2 boutons côte à côte au centre-bas
        self._bouton_attaquer = Bouton(
            position=(int(config.LARGEUR / 2) - 220, int(config.HAUTEUR / 2) + 90),
            largeur=180, hauteur=55, texte="ATTAQUER",
        )
        self._bouton_attaquer.redimensionner(self._echelle)
        self._bouton_epargner = Bouton(
            position=(int(config.LARGEUR / 2) + 40, int(config.HAUTEUR / 2) + 90),
            largeur=180, hauteur=55, texte="EPARGNER",
        )
        self._bouton_epargner.redimensionner(self._echelle)
        # Continuer (fin de combat)
        self._bouton_continuer = Bouton(
            position=(int(config.LARGEUR / 2) - 90, int(config.HAUTEUR / 2) + 120),
            largeur=180, hauteur=55, texte="CONTINUER",
        )
        self._bouton_continuer.redimensionner(self._echelle)

    # ---------------------------------------------------------------- événements
    def gerer_evenement(self, evenement):
        if not self.ouvert:
            return
        if self._phase == "choix":
            self._gerer_choix(evenement)
        elif self._phase == "jauge":
            self._gerer_jauge(evenement)
        elif self._phase in ("victoire", "defaite", "epargne"):
            self._gerer_fin(evenement)
        # phase "tir" et "defense" : pas d'event direct (gestion auto dans mettre_a_jour)

    def _gerer_choix(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self._bouton_attaquer.contient(e.pos):
                self._barre.reset()
                self._phase = "jauge"
            elif self._bouton_epargner.contient(e.pos):
                self._phase = "epargne"

    def _gerer_jauge(self, e):
        clic = (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1)
        espace = (e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN))
        if not (clic or espace):
            return
        ok = self._barre.reussi()
        self._tir_degats = DEGATS_BON if ok else 0
        sx = self._echelle.x
        self._tir = Projectile(
            self._barre.rect.centerx, self._barre.rect.top,
            0.0, -11.0 * sx, max(2, int(4 * self._echelle.y)), BLEU,
        )
        self._phase = "tir"

    def _gerer_fin(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self._bouton_continuer.contient(e.pos):
                self._terminer(self._phase)

    # ---------------------------------------------------------------- update
    def mettre_a_jour(self, dt):
        if not self.ouvert:
            return
        self._temps += 1
        self._ennemi.mettre_a_jour()
        self._coeur.mettre_a_jour()
        if self._phase == "jauge":
            self._barre.mettre_a_jour()
        elif self._phase == "tir":
            self._update_tir()
        elif self._phase == "defense":
            self._update_defense()

    def _update_tir(self):
        if self._tir is None:
            return
        self._tir.mettre_a_jour_haut()
        if self._tir.vivant and self._tir.rect().colliderect(self._ennemi.rect):
            if self._tir_degats > 0:
                self._ennemi.pv -= self._tir_degats
            self._tir.vivant = False
        if not self._tir.vivant:
            self._tir = None
            if self._ennemi.pv <= 0:
                self.joueur.gagner_xp(GAIN_XP)
                self._phase = "victoire"
                return
            # passe en défense
            self._balles = []
            cfg = self.combat_data.monstre
            self._temps_defense = cfg.defense_duree
            self._prochain_spawn = self._temps + 10
            self._phase = "defense"

    def _update_defense(self):
        cfg = self.combat_data.monstre
        touches = pygame.key.get_pressed()
        self._coeur.bouger(touches)
        # Spawn de nouvelles balles
        if self._temps >= self._prochain_spawn:
            arene = self._layout["arene"]
            nb = random.randint(cfg.nb_min, cfg.nb_max)
            for _ in range(nb):
                sx, sy = point_bord(arene)
                tx = self._coeur.rect.centerx + random.randint(-35, 35)
                ty = self._coeur.rect.centery + random.randint(-35, 35)
                v = random.uniform(cfg.v_min, cfg.v_max) * self._echelle.x
                vx, vy = vitesse_vers(sx, sy, tx, ty, v)
                rayon = max(2, int(4 * self._echelle.y))
                self._balles.append(Projectile(sx, sy, vx, vy, rayon, BLANC))
            self._prochain_spawn = self._temps + random.randint(cfg.spawn_min, cfg.spawn_max)
        # Mouvement + collisions
        zone_sortie = self._layout["zone_sortie"]
        for b in self._balles[:]:
            b.mettre_a_jour_sortie(zone_sortie)
            if b.vivant and self._coeur.invincible == 0 and b.rect().colliderect(self._coeur.rect):
                self._pv_combat -= cfg.degats
                self._coeur.encaisser()
                b.vivant = False
            if not b.vivant:
                self._balles.remove(b)
        self._temps_defense -= 1
        if self._pv_combat <= 0:
            self._phase = "defaite"
            return
        if self._temps_defense <= 0:
            self._balles = []
            self._barre.reset()
            self._phase = "jauge"

    # ---------------------------------------------------------------- terminer
    def _terminer(self, resultat):
        cb = self._on_termine
        self.ouvert = False
        self.combat_data = None
        self._on_termine = None
        # Note : on persiste la vie courante du combat sur joueur.vie (sauf défaite, gérée par gameplay).
        if resultat == "victoire":
            self.joueur.vie = max(1, int(self._pv_combat))
        if cb:
            cb(resultat)

    # ---------------------------------------------------------------- rendu
    def dessiner(self, surface):
        if not self.ouvert:
            return
        surface.fill(NOIR)
        self.dessiner_contenu(surface)

    def dessiner_contenu(self, surface):
        if self._phase == "choix":
            self._dessiner_choix(surface)
        elif self._phase in ("jauge", "tir", "defense"):
            self._dessiner_combat(surface)
        elif self._phase in ("victoire", "epargne"):
            self._dessiner_fin(surface, "Victoire" if self._phase == "victoire" else "Tu l'as épargné")
        elif self._phase == "defaite":
            self._dessiner_fin(surface, "Défaite")

    def _dessiner_choix(self, surface):
        sy = self._echelle.y
        w = surface.get_width()
        h = surface.get_height()
        nom = self.combat_data.monstre.nom
        police_titre = polices.pixelade(max(20, int(44 * sy)))
        police = polices.pixelade(max(14, int(24 * sy)))
        # Sprite centré
        sprite = self._ennemi.sprites[0]
        small = pygame.transform.smoothscale(sprite, (int(140 * sy), int(140 * sy)))
        rect_img = small.get_rect(center=(w // 2, h // 2 - int(60 * sy)))
        surface.blit(small, rect_img)
        # Nom du monstre
        t1 = police_titre.render(nom, True, BLANC)
        surface.blit(t1, t1.get_rect(center=(w // 2, int(70 * sy))))
        # Question
        t2 = police.render("Attaquer ou épargner ?", True, BLANC)
        surface.blit(t2, t2.get_rect(center=(w // 2, h // 2 + int(50 * sy))))
        self._bouton_attaquer.dessiner(surface)
        self._bouton_epargner.dessiner(surface)

    def _dessiner_combat(self, surface):
        sx, sy = self._echelle.x, self._echelle.y
        arene = self._layout["arene"]
        # Ennemi en haut
        self._ennemi.dessiner(surface)
        # Arène
        pygame.draw.rect(surface, BLANC, arene, max(2, int(5 * sy)))
        # Projectiles (défense) + tir (montée vers ennemi)
        for b in self._balles:
            b.dessiner(surface)
        if self._tir is not None:
            self._tir.dessiner(surface)
        # Cœur (défense ou jauge — toujours visible)
        self._coeur.dessiner(surface)
        # Barres PV
        police = polices.pixelade(max(12, int(18 * sy)))
        y_barres = self._layout["y_barres"]
        w = surface.get_width()
        _dessiner_barre(surface, police,
                        int(80 * sx), y_barres, int(300 * sx), int(18 * sy),
                        self._ennemi.pv, self._ennemi.pv_max, self._ennemi.nom, droite=False)
        _dessiner_barre(surface, police,
                        w - int(380 * sx), y_barres, int(300 * sx), int(18 * sy),
                        self._pv_combat, self._pv_combat_max, "Toi", droite=True)
        # Phase-specifique
        if self._phase == "jauge":
            self._barre.dessiner(surface)
            t = police.render("Clique ou Espace pour attaquer", True, BLANC)
            surface.blit(t, (w // 2 - t.get_width() // 2, self._barre.rect.top - int(28 * sy)))
        elif self._phase == "defense":
            t = police.render("Esquive !", True, BLANC)
            surface.blit(t, (w // 2 - t.get_width() // 2, self._barre.rect.top - int(28 * sy)))

    def _dessiner_fin(self, surface, titre):
        sy = self._echelle.y
        w = surface.get_width()
        h = surface.get_height()
        police_titre = polices.pixelade(max(20, int(44 * sy)))
        t = police_titre.render(titre, True, BLANC)
        surface.blit(t, t.get_rect(center=(w // 2, h // 2 - int(40 * sy))))
        self._bouton_continuer.dessiner(surface)


def _dessiner_barre(surface, police, x, y, w, h, val, val_max, titre, droite=False):
    pygame.draw.rect(surface, (70, 0, 0), (x, y, w, h))
    ratio = 0 if val_max == 0 else max(0.0, min(1.0, val / val_max))
    pygame.draw.rect(surface, VERT, (x, y, int(w * ratio), h))
    pygame.draw.rect(surface, BLANC, (x, y, w, h), 2)
    label = police.render(f"{titre}: {max(0, int(val))}/{val_max}", True, BLANC)
    lx = (x + w - label.get_width()) if droite else x
    surface.blit(label, (lx, y - int(label.get_height() * 0.9)))


class _PanneauNoir:
    """Panneau dummy : Modale exige un panneau, mais ModaleCombat surcharge dessiner()
    et fait sa propre composition (fond noir + entités). Ce panneau ne fait rien."""

    def redimensionner(self, echelle):
        pass

    def dessiner(self, surface):
        pass
