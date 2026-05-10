"""Moteur runtime du scénario : charge le YAML, gère l'état (flags), répond aux requêtes."""
from jeu.dialogues.dialogue import Dialogue
from jeu.dialogues.personnage import Personnage
from jeu.objet import Objet
from jeu.scenario.chargeur import charger


class Scenario:
    """Charge `scenario.yaml` une fois et expose les déclencheurs runtime + les flags."""

    def __init__(self, chemin_yaml):
        """Charge et matérialise personnages/objets ; les autres données restent en dataclass.

        Parameters
        ----------
        chemin_yaml : str
                      Chemin du fichier scenario.yaml à charger.
        """
        donnees = charger(chemin_yaml)
        self.niveau_initial = donnees.niveau_initial
        self.chaine = list(donnees.chaine)
        self.flags = set(donnees.flags_initiaux)
        # Personnages : runtime objects (sprites chargés une fois)
        self.personnages = {
            pid: Personnage(
                nom=p.nom,
                couleur_nom=p.couleur_nom,
                sprite_carte=p.sprite_carte,
                sprite_dialogue_1=p.sprite_dialogue_1,
                sprite_dialogue_2=p.sprite_dialogue_2,
                facteur_taille_carte=p.facteur_taille_carte,
                toujours_visible=p.toujours_visible,
            )
            for pid, p in donnees.personnages.items()
        }
        self._dialogues = donnees.dialogues
        self._transitions = {t.niveau: t for t in donnees.transitions}
        self._combats = donnees.combats
        # Objets : runtime (sprites chargés une fois)
        self.objets = {
            oid: Objet(
                id=oid,
                nom=o.nom,
                sprite=o.sprite,
                facteur_taille_carte=o.facteur_taille_carte,
                cache_sur_carte=o.cache_sur_carte,
            )
            for oid, o in donnees.objets.items()
        }
        self._quetes = donnees.quetes

    # --- Niveau / chaîne ---

    def niveau_suivant(self, nom):
        """Nom du niveau suivant `nom` dans la chaîne, ou None si dernier/inconnu.

        Parameters
        ----------
        nom : str
              Nom du niveau courant.

        Returns
        ----------
        str | None
             Nom du niveau suivant, ou None.
        """
        if nom not in self.chaine:
            return None
        i = self.chaine.index(nom)
        return self.chaine[i + 1] if i + 1 < len(self.chaine) else None

    def niveau_precedent(self, nom):
        """Nom du niveau précédent `nom` dans la chaîne, ou None si premier/inconnu.

        Parameters
        ----------
        nom : str
              Nom du niveau courant.

        Returns
        ----------
        str | None
             Nom du niveau précédent, ou None.
        """
        if nom not in self.chaine:
            return None
        i = self.chaine.index(nom)
        return self.chaine[i - 1] if i > 0 else None

    # --- Dialogues ---

    def dialogue_a_declencher(self, nom_niveau, couleur):
        """Retourne le runtime Dialogue à jouer à (niveau, couleur), ou None.

        Parameters
        ----------
        nom_niveau : str
                     Nom du niveau courant.
        couleur : str
                  Nom de couleur du marqueur (cyan, magenta, …).

        Returns
        ----------
        Dialogue | None
               Dialogue runtime à jouer, ou None si aucun n'est triggerable.
        """
        for d in self._dialogues:
            if d.niveau == nom_niveau and d.couleur == couleur and self._conditions_ok(d):
                return self._materialiser(d)
        return None

    def personnage_present(self, nom_niveau, couleur):
        """Retourne le Personnage à dessiner sur la carte à (niveau, couleur), ou None.

        Visible si au moins un dialogue est triggerable, OU si le personnage a
        `toujours_visible=True` (il reste alors présent même quand inactif).

        Parameters
        ----------
        nom_niveau : str
                     Nom du niveau courant.
        couleur : str
                  Nom de couleur du marqueur.

        Returns
        ----------
        Personnage | None
               Personnage à dessiner, ou None.
        """
        perso_associe = None
        for d in self._dialogues:
            if d.niveau == nom_niveau and d.couleur == couleur:
                perso = self.personnages.get(d.personnage)
                if perso is None:
                    continue
                perso_associe = perso
                if self._conditions_ok(d):
                    return perso
        if perso_associe is not None and perso_associe.toujours_visible:
            return perso_associe
        return None

    def _materialiser(self, data):
        """Convertit un `DialogueData` en runtime `Dialogue` avec callback pose-flags.

        Parameters
        ----------
        data : DialogueData
               Dataclass du dialogue à matérialiser.

        Returns
        ----------
        Dialogue
               Dialogue runtime prêt à être joué.
        """
        return Dialogue(
            personnage=self.personnages[data.personnage],
            messages=data.messages,
            couleurs_speciales=data.couleurs_speciales,
            on_termine=lambda: self._poser_flags(data.pose_flags),
        )

    def _poser_flags(self, flags):
        """Ajoute chaque flag à l'ensemble courant (idempotent).

        Parameters
        ----------
        flags : list[str]
                Flags à ajouter à l'ensemble courant.
        """
        for f in flags:
            self.flags.add(f)

    # --- Quêtes ---

    def quete_a_declencher(self, nom_niveau, couleur):
        """Retourne la QueteData à déclencher à (niveau, couleur), ou None.

        Parameters
        ----------
        nom_niveau : str
                     Nom du niveau courant.
        couleur : str
                  Nom de couleur du marqueur.

        Returns
        ----------
        QueteData | None
               Quête à déclencher, ou None.
        """
        for q in self._quetes:
            if q.niveau == nom_niveau and q.couleur == couleur and self._conditions_ok(q):
                return q
        return None

    def objet_present(self, nom_niveau, couleur):
        """Retourne l'Objet runtime à dessiner sur la carte, ou None.

        Renvoie None aussi si l'objet est marqué `cache_sur_carte` : il reste
        ramassable (la quête se déclenche en marchant dessus) mais pas visible.

        Parameters
        ----------
        nom_niveau : str
                     Nom du niveau courant.
        couleur : str
                  Nom de couleur du marqueur.

        Returns
        ----------
        Objet | None
               Objet à dessiner sur la carte, ou None.
        """
        q = self.quete_a_declencher(nom_niveau, couleur)
        if q is None or q.objet is None:
            return None
        objet = self.objets.get(q.objet.id)
        if objet is None or objet.cache_sur_carte:
            return None
        return objet

    def appliquer_resultat_quete(self, quete_data):
        """Pose les flags de la quête une fois ramassée.

        Parameters
        ----------
        quete_data : QueteData
                     Quête venant d'être ramassée.
        """
        self._poser_flags(quete_data.pose_flags)

    # --- Combats ---

    def combat_a_declencher(self, nom_niveau, couleur):
        """Retourne le CombatData à déclencher à (niveau, couleur), ou None.

        Parameters
        ----------
        nom_niveau : str
                     Nom du niveau courant.
        couleur : str
                  Nom de couleur du marqueur.

        Returns
        ----------
        CombatData | None
               Combat à déclencher, ou None.
        """
        for c in self._combats:
            if c.niveau == nom_niveau and c.couleur == couleur and self._conditions_ok(c):
                return c
        return None

    def appliquer_resultat_combat(self, combat_data, resultat):
        """resultat ∈ {'victoire', 'epargne', 'defaite'}. Pose les bons flags.

        Parameters
        ----------
        combat_data : CombatData
                      Combat qui vient de se terminer.
        resultat : str
                   Résultat parmi 'victoire', 'epargne', 'defaite'.
        """
        if resultat == "victoire":
            self._poser_flags(combat_data.pose_flags_victoire)
        elif resultat == "epargne":
            self._poser_flags(combat_data.pose_flags_epargne)
        # defaite : pas de flag → le combat reste rejouable

    # --- Transitions ---

    def transition_autorisee(self, nom_niveau):
        """Retourne (autorise: bool, indice: str | None).

        Si bloqué, renvoie l'indice ciblé du PREMIER flag manquant (via
        `indices_par_flag`), sinon le générique `indice_echec`.

        Parameters
        ----------
        nom_niveau : str
                     Nom du niveau qu'on veut quitter.

        Returns
        ----------
        tuple[bool, str | None]
               (True, None) si autorisé, (False, message) sinon.
        """
        t = self._transitions.get(nom_niveau)
        if t is None:
            return True, None
        if any(f in self.flags for f in t.interdit):
            return False, t.indice_echec
        for f in t.requiert:
            if f not in self.flags:
                return False, t.indices_par_flag.get(f, t.indice_echec)
        return True, None

    # --- Conditions ---

    def _conditions_ok(self, item):
        """True si aucun flag interdit n'est posé ET tous les flags requis le sont.

        Parameters
        ----------
        item : DialogueData | QueteData | CombatData
               Élément portant des listes `requiert` et `interdit`.

        Returns
        ----------
        bool
             True si l'élément est triggerable dans l'état courant.
        """
        if any(f in self.flags for f in item.interdit):
            return False
        if not all(f in self.flags for f in item.requiert):
            return False
        return True
