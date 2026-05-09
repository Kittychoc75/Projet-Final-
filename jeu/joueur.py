"""État du joueur : stats persistantes (vie, xp) + inventaire d'objets ramassés.

Source de vérité unique. L'Inventaire UI lit ces valeurs, le combat les modifie,
les quêtes ajoutent des objets, la sauvegarde les persiste.
"""


class Joueur:
    VIE_MAX = 100
    XP_MAX = 100

    def __init__(self):
        self.vie = self.VIE_MAX
        self.xp = 0
        self.objets = []  # liste d'ids (strings) — ordre = ordre de ramassage

    def perdre_vie(self, montant):
        self.vie = max(0, self.vie - montant)

    def gagner_xp(self, montant):
        self.xp = min(self.XP_MAX, self.xp + montant)

    def restaurer(self):
        """Recharge les HP au max (utilisé après défaite, checkpoint)."""
        self.vie = self.VIE_MAX

    def ramasser(self, objet_id):
        """Ajoute l'objet à l'inventaire (sans doublon)."""
        if objet_id not in self.objets:
            self.objets.append(objet_id)

    def consommer(self, objet_id):
        """Retire l'objet de l'inventaire. Silencieux si absent."""
        if objet_id in self.objets:
            self.objets.remove(objet_id)

    def etat(self):
        return {"vie": self.vie, "xp": self.xp, "objets": list(self.objets)}

    def appliquer_etat(self, etat):
        self.vie = int(etat.get("vie", self.VIE_MAX))
        self.xp = int(etat.get("xp", 0))
        self.objets = list(etat.get("objets") or [])
