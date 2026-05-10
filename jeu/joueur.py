"""État du joueur : stats persistantes (vie, xp) + inventaire d'objets ramassés.

Source de vérité unique. L'Inventaire UI lit ces valeurs, le combat les modifie,
les quêtes ajoutent des objets, la sauvegarde les persiste.
"""


class Joueur:
    """Stats persistantes (vie, xp) et inventaire d'ids d'objets ramassés."""

    VIE_MAX = 100
    XP_MAX = 100

    def __init__(self):
        """Initialise vie=VIE_MAX, xp=0 et inventaire vide."""
        self.vie = self.VIE_MAX
        self.xp = 0
        self.objets = []  # liste d'ids (strings) — ordre = ordre de ramassage

    def perdre_vie(self, montant):
        """Retire `montant` PV (planché à 0).

        Parameters
        ----------
        montant : int
                  Nombre de PV à retirer.
        """
        self.vie = max(0, self.vie - montant)

    def gagner_xp(self, montant):
        """Ajoute `montant` XP (plafonné à XP_MAX).

        Parameters
        ----------
        montant : int
                  Nombre d'XP à ajouter.
        """
        self.xp = min(self.XP_MAX, self.xp + montant)

    def restaurer(self):
        """Recharge les HP au max (utilisé après défaite, checkpoint)."""
        self.vie = self.VIE_MAX

    def ramasser(self, objet_id):
        """Ajoute l'objet à l'inventaire (sans doublon).

        Parameters
        ----------
        objet_id : str
                   Identifiant de l'objet à ajouter.
        """
        if objet_id not in self.objets:
            self.objets.append(objet_id)

    def consommer(self, objet_id):
        """Retire l'objet de l'inventaire. Silencieux si absent.

        Parameters
        ----------
        objet_id : str
                   Identifiant de l'objet à retirer.
        """
        if objet_id in self.objets:
            self.objets.remove(objet_id)

    def etat(self):
        """État sérialisable (vie, xp, liste d'ids d'objets) pour la sauvegarde.

        Parameters
        ----------

        Returns
        ----------
        dict
             Dictionnaire {vie, xp, objets} prêt à être écrit en JSON.
        """
        return {"vie": self.vie, "xp": self.xp, "objets": list(self.objets)}

    def appliquer_etat(self, etat):
        """Restaure vie/xp/objets depuis un dict produit par `etat()`.

        Parameters
        ----------
        etat : dict
               Dictionnaire {vie, xp, objets} lu depuis la sauvegarde.
        """
        self.vie = int(etat.get("vie", self.VIE_MAX))
        self.xp = int(etat.get("xp", 0))
        self.objets = list(etat.get("objets") or [])
