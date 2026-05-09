from jeu.debug import Debug
from jeu.entites import Perso
from jeu.joueur import Joueur
from jeu.monde import Monde
from jeu.monde.niveaux import PAR_NOM
from jeu.ui import UI


class Gameplay:
    """Gère la logique de jeu : transitions entre niveaux, interactions, dialogues, combats."""

    def __init__(self, surface, scenario, debug=False):
        self.scenario = scenario
        self.surface = surface
        self.joueur = Joueur()
        niveau_initial = PAR_NOM.get(scenario.niveau_initial, PAR_NOM["depart"])
        self.monde = Monde(surface, niveau_initial)
        self.ui = UI(self.joueur, scenario)
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
        """État sérialisable du jeu. Étendre ici quand on ajoutera l'inventaire d'objets, etc."""
        return {
            "niveau": self.monde.niveau.NOM,
            "perso": {
                "x": float(self.perso.position.x),
                "y": float(self.perso.position.y),
                "direction": self.perso.direction,
            },
            "joueur": self.joueur.etat(),
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
        self.joueur.appliquer_etat(etat.get("joueur") or {})
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

        self._verifier_zones()

    def _verifier_zones(self):
        """Détecte les collisions avec les zones meta et déclenche dialogue / combat selon la couleur."""
        niveau = self.monde.niveau
        for couleur, zones in niveau.zones_par_couleur.items():
            for i, zone in enumerate(zones):
                chevauche = self.perso.hitbox.colliderect(zone)
                key = (couleur, i)
                if chevauche and not self._zones_actives.get(key, False):
                    self._declencher_zone(niveau.NOM, couleur)
                self._zones_actives[key] = chevauche

    def _declencher_zone(self, nom_niveau, couleur):
        """Sans hardcode couleur→type : on demande au scenario quoi déclencher."""
        d = self.scenario.dialogue_a_declencher(nom_niveau, couleur)
        if d is not None:
            self.ui.declencher_dialogue(d)
            return
        c = self.scenario.combat_a_declencher(nom_niveau, couleur)
        if c is not None:
            self.ui.declencher_combat(
                c, on_termine=lambda res, cd=c: self._on_combat_termine(cd, res),
            )
            return
        q = self.scenario.quete_a_declencher(nom_niveau, couleur)
        if q is not None:
            self._ramasser_quete(q)

    def _ramasser_quete(self, quete):
        """Ramasse l'objet d'une quête : ajout inventaire, message, flags."""
        if quete.objet is not None:
            self.joueur.ramasser(quete.objet.id)
        if quete.message:
            self.ui.afficher_indice(quete.message)
        self.scenario.appliquer_resultat_quete(quete)

    def _on_combat_termine(self, combat_data, resultat):
        self.scenario.appliquer_resultat_combat(combat_data, resultat)
        if resultat == "defaite":
            # Checkpoint : HP rechargée + retour au spawn du niveau.
            self.joueur.restaurer()
            spawn = self.monde.niveau.spawn
            self.perso.position.update(spawn.x, spawn.y)
            self.perso.redimensionner(self.monde.echelle)
            self._sortie_active = False
            self._spawn_active = True
            self._zones_actives = self._init_zones_actives()
        else:
            # Si le joueur reste sur le blob du combat, on veut que la prochaine
            # action disponible (typiquement une quête au même endroit) puisse
            # se déclencher immédiatement sans qu'il sorte/rentre dans la zone.
            for key in list(self._zones_actives):
                if key[0] == combat_data.couleur:
                    self._zones_actives[key] = False

    def _effectuer_transition(self, classe, vers_avant):
        """Tente une transition. Retourne True si effectuée, False si bloquée par le scenario.

        Seule la progression forward est gated (impossible sinon d'aller chercher
        un objet de quête dans un niveau précédent). Le retour-arrière est libre.
        """
        if vers_avant:
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
