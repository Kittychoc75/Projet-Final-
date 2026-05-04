from jeu.debug import Debug
from jeu.entites import Perso
from jeu.monde import Monde
from jeu.monde.chaine import CHAINE
from jeu.ui import UI 

class Gameplay:
    """ Gère la logique de jeu : transitions entre niveaux, interactions, etc"""
    def __init__(self, surface, debug=False):
        self.surface = surface
        self.monde = Monde(surface)
        self.ui = UI()
        self.perso = Perso(self.monde.niveau.spawn.x, self.monde.niveau.spawn.y)
        self.perso.redimensionner(self.monde.echelle)
        self.debug = Debug(actif=debug)
        self.fin_chaine = False
        # Edge-detection: True si la frame précédente le perso était déjà sur le marqueur.
        # Initialement le perso est sur le spawn → on bloque le retour-arrière auto.
        self._sortie_active = False
        self._spawn_active = True

    def redimensionner(self, surface):
        self.surface = surface
        self.monde.redimensionner(surface.get_size())
        self.perso.redimensionner(self.monde.echelle)

    def mettre_a_jour(self, dt):
        self.perso.mouvement(dt, self.monde)
        self._verifier_transitions()
        self.monde.dessiner(self.surface)
        self.perso.dessiner(self.surface)
        self.debug.dessiner(self.surface, self.monde, self.perso)
        self.ui.dessiner(self.surface)

    def gerer_evenements(self, evenement):
        self.ui.gerer_clic(evenement)

    def _verifier_transitions(self):
        sortie = self.monde.niveau.sortie
        spawn = self.monde.niveau.spawn
        on_sortie = sortie is not None and self.perso.hitbox.colliderect(sortie)
        on_spawn = spawn is not None and self.perso.hitbox.collidepoint(
            (int(spawn.x), int(spawn.y))
        )

        # Sortie → niveau suivant
        if on_sortie and not self._sortie_active and not self.fin_chaine:
            suivant = self._niveau_suivant()
            if suivant is not None:
                self._effectuer_transition(suivant, vers_avant=True)
                return
            self.fin_chaine = True

        # Spawn → niveau précédent
        elif on_spawn and not self._spawn_active:
            precedent = self._niveau_precedent()
            if precedent is not None:
                self._effectuer_transition(precedent, vers_avant=False)
                return

        self._sortie_active = on_sortie
        self._spawn_active = on_spawn

    def _effectuer_transition(self, classe, vers_avant):
        self.monde.changer_niveau(classe)
        if vers_avant:
            cible = self.monde.niveau.spawn
            self._spawn_active = True
            self._sortie_active = False
        else:
            sortie = self.monde.niveau.sortie
            cible = sortie.center if sortie is not None else self.monde.niveau.spawn
            self._sortie_active = True
            self._spawn_active = False
        self.perso.position.update(cible)
        self.perso.redimensionner(self.monde.echelle)
        self.fin_chaine = False

    def _niveau_suivant(self):
        idx = CHAINE.index(type(self.monde.niveau))
        return CHAINE[idx + 1] if idx + 1 < len(CHAINE) else None

    def _niveau_precedent(self):
        idx = CHAINE.index(type(self.monde.niveau))
        return CHAINE[idx - 1] if idx > 0 else None
