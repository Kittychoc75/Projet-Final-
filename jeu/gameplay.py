from jeu.debug import Debug
from jeu.entites import Perso
from jeu.monde import Monde
from jeu.monde.niveaux import PAR_NOM
from jeu.ui import UI


class Gameplay:
    """Gère la logique de jeu : transitions entre niveaux, interactions, dialogues."""

    def __init__(self, surface, scenario, debug=False):
        self.scenario = scenario
        self.surface = surface
        # Le monde démarre sur le niveau initial du scenario (ou Depart par défaut).
        niveau_initial = PAR_NOM.get(scenario.niveau_initial, PAR_NOM["depart"])
        self.monde = Monde(surface, niveau_initial)
        self.ui = UI()
        self.perso = Perso(self.monde.niveau.spawn.x, self.monde.niveau.spawn.y)
        self.perso.redimensionner(self.monde.echelle)
        self.debug = Debug(actif=debug)
        self.fin_chaine = False
        # Edge-detection : True si la frame précédente le perso était déjà sur le marqueur.
        # Au démarrage le perso est sur le spawn → on bloque le retour-arrière auto.
        self._sortie_active = False
        self._spawn_active = True
        self._zones_actives = self._init_zones_actives()

    def _init_zones_actives(self):
        """Map (couleur_nom, blob_index) → bool (True = perso dessus la frame précédente)."""
        return {
            (couleur, i): False
            for couleur, zones in self.monde.niveau.zones_par_couleur.items()
            for i, _ in enumerate(zones)
        }

    # --- Sauvegarde / chargement ---

    def etat(self):
        """État sérialisable du jeu. Étendre ici quand on ajoutera l'inventaire, etc."""
        return {
            "niveau": self.monde.niveau.NOM,
            "perso": {
                "x": float(self.perso.position.x),
                "y": float(self.perso.position.y),
                "direction": self.perso.direction,
            },
            "flags": sorted(self.scenario.flags),
        }

    def restaurer(self, etat):
        """Applique un état chargé (issu de `etat()`) sur le gameplay."""
        nom_niveau = etat.get("niveau")
        classe = PAR_NOM.get(nom_niveau)
        if classe is not None and not isinstance(self.monde.niveau, classe):
            self.monde.changer_niveau(classe)
        perso = etat.get("perso") or {}
        if "x" in perso and "y" in perso:
            self.perso.position.update(float(perso["x"]), float(perso["y"]))
        if "direction" in perso:
            self.perso.direction = perso["direction"]
        self.perso.redimensionner(self.monde.echelle)
        self.scenario.flags = set(etat.get("flags") or [])
        # Edge-detection : on considère le perso comme "déjà sur" tout marqueur,
        # pour ne pas re-déclencher de transition à la première frame post-load.
        self._sortie_active = True
        self._spawn_active = True
        self._zones_actives = self._init_zones_actives()
        self.fin_chaine = False

    def redimensionner(self, surface):
        self.surface = surface
        self.monde.redimensionner(surface.get_size())
        self.perso.redimensionner(self.monde.echelle)
        self.ui.redimensionner(self.monde.echelle)

    def mettre_a_jour(self, dt):
        if not self.ui.bloque_jeu():
            self.perso.mouvement(dt, self.monde)
            self._verifier_transitions()
        self.ui.mettre_a_jour(dt)
        self.monde.dessiner(self.surface, self.scenario)
        self.perso.dessiner(self.surface)
        self.debug.dessiner(self.surface, self.monde, self.perso)
        self.ui.dessiner(self.surface)

    def gerer_evenements(self, evenement):
        self.ui.gerer_evenement(evenement)

    # --- Transitions de niveau ---

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
                if self._effectuer_transition(suivant, vers_avant=True):
                    return
            else:
                self.fin_chaine = True

        # Spawn → niveau précédent
        elif on_spawn and not self._spawn_active:
            precedent = self._niveau_precedent()
            if precedent is not None:
                if self._effectuer_transition(precedent, vers_avant=False):
                    return

        self._sortie_active = on_sortie
        self._spawn_active = on_spawn

        self._verifier_dialogues()

    def _verifier_dialogues(self):
        niveau = self.monde.niveau
        for couleur, zones in niveau.zones_par_couleur.items():
            for i, zone in enumerate(zones):
                chevauche = self.perso.hitbox.colliderect(zone)
                key = (couleur, i)
                if chevauche and not self._zones_actives.get(key, False):
                    dialogue = self.scenario.dialogue_a_declencher(niveau.NOM, couleur)
                    if dialogue is not None:
                        self.ui.declencher_dialogue(dialogue)
                self._zones_actives[key] = chevauche

    def _effectuer_transition(self, classe, vers_avant):
        """Tente une transition. Retourne True si effectuée, False si bloquée par le scenario."""
        autorise, indice = self.scenario.transition_autorisee(self.monde.niveau.NOM)
        if not autorise:
            self.ui.afficher_indice(indice or "Quelque chose te retient ici.")
            return False

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
        self._zones_actives = self._init_zones_actives()
        self.perso.position.update(cible)
        self.perso.redimensionner(self.monde.echelle)
        self.fin_chaine = False
        return True

    def _niveau_suivant(self):
        nom_suivant = self.scenario.niveau_suivant(self.monde.niveau.NOM)
        return PAR_NOM.get(nom_suivant) if nom_suivant else None

    def _niveau_precedent(self):
        nom_precedent = self.scenario.niveau_precedent(self.monde.niveau.NOM)
        return PAR_NOM.get(nom_precedent) if nom_precedent else None
