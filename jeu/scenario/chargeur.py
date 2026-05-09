"""Lecture et validation du fichier scenario.yaml."""
from dataclasses import dataclass, field

import yaml

from jeu.scenario.modeles import (
    CombatData,
    DialogueData,
    MonstreData,
    ObjetData,
    PersonnageData,
    QueteData,
    TransitionData,
)


@dataclass
class DonneesScenario:
    niveau_initial: str = "depart"
    chaine: list = field(default_factory=list)
    flags_initiaux: list = field(default_factory=list)
    personnages: dict = field(default_factory=dict)   # id → PersonnageData
    dialogues: list = field(default_factory=list)     # list[DialogueData]
    transitions: list = field(default_factory=list)   # list[TransitionData]
    monstres: dict = field(default_factory=dict)      # id → MonstreData
    combats: list = field(default_factory=list)       # list[CombatData]
    objets: dict = field(default_factory=dict)        # id → ObjetData
    quetes: list = field(default_factory=list)        # list[QueteData]


class ScenarioInvalide(ValueError):
    pass


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        brut = yaml.safe_load(f) or {}
    donnees = _construire(brut)
    _valider(donnees)
    return donnees


def _construire(brut):
    personnages = {}
    for pid, p in (brut.get("personnages") or {}).items():
        personnages[pid] = PersonnageData(
            id=pid,
            nom=p["nom"],
            couleur_nom=tuple(p["couleur_nom"]),
            sprite_carte=p["sprite_carte"],
            sprite_dialogue_1=p["sprite_dialogue_1"],
            sprite_dialogue_2=p["sprite_dialogue_2"],
            facteur_taille_carte=float(p.get("facteur_taille_carte", 1.0)),
            toujours_visible=bool(p.get("toujours_visible", False)),
        )

    dialogues = []
    for d in brut.get("dialogues") or []:
        dialogues.append(DialogueData(
            id=d["id"],
            niveau=d["niveau"],
            couleur=d["couleur"],
            personnage=d["personnage"],
            messages=list(d.get("messages") or []),
            requiert=list(d.get("requiert") or []),
            interdit=list(d.get("interdit") or []),
            pose_flags=list(d.get("pose_flags") or []),
            couleurs_speciales={k: tuple(v) for k, v in (d.get("couleurs_speciales") or {}).items()},
        ))

    transitions = []
    for t in brut.get("transitions") or []:
        transitions.append(TransitionData(
            niveau=t["niveau"],
            requiert=list(t.get("requiert") or []),
            interdit=list(t.get("interdit") or []),
            indice_echec=t.get("indice_echec"),
            indices_par_flag=dict(t.get("indices_par_flag") or {}),
        ))

    monstres = {}
    for mid, m in (brut.get("monstres") or {}).items():
        monstres[mid] = MonstreData(
            id=mid,
            nom=m["nom"],
            sprites=list(m.get("sprites") or []),
            pv=int(m["pv"]),
            degats=int(m["degats"]),
            defense_duree=int(m["defense_duree"]),
            spawn_min=int(m["spawn_min"]),
            spawn_max=int(m["spawn_max"]),
            nb_min=int(m["nb_min"]),
            nb_max=int(m["nb_max"]),
            v_min=float(m["v_min"]),
            v_max=float(m["v_max"]),
            periode_anim=int(m.get("periode_anim", 60)),
        )

    combats = []
    for c in brut.get("combats") or []:
        monstre_id = c["monstre"]
        monstre_obj = monstres.get(monstre_id)
        combats.append(CombatData(
            id=c["id"],
            niveau=c["niveau"],
            couleur=c["couleur"],
            monstre=monstre_obj,  # résolu (ou None — détecté à la validation)
            requiert=list(c.get("requiert") or []),
            interdit=list(c.get("interdit") or []),
            pose_flags_victoire=list(c.get("pose_flags_victoire") or []),
            pose_flags_epargne=list(c.get("pose_flags_epargne") or []),
        ))
        # Stocke aussi l'id du monstre pour validation (le combat data lui-même tient l'objet)
        combats[-1]._monstre_id = monstre_id

    objets = {}
    for oid, o in (brut.get("objets") or {}).items():
        objets[oid] = ObjetData(
            id=oid,
            nom=o["nom"],
            sprite=o["sprite"],
            facteur_taille_carte=float(o.get("facteur_taille_carte", 1.0)),
            cache_sur_carte=bool(o.get("cache_sur_carte", False)),
        )

    quetes = []
    for q in brut.get("quetes") or []:
        objet_id = q["objet"]
        objet_obj = objets.get(objet_id)
        quetes.append(QueteData(
            id=q["id"],
            niveau=q["niveau"],
            couleur=q["couleur"],
            objet=objet_obj,
            message=q.get("message", ""),
            requiert=list(q.get("requiert") or []),
            interdit=list(q.get("interdit") or []),
            pose_flags=list(q.get("pose_flags") or []),
        ))
        quetes[-1]._objet_id = objet_id

    return DonneesScenario(
        niveau_initial=brut.get("niveau_initial", "depart"),
        chaine=list(brut.get("chaine") or []),
        flags_initiaux=list(brut.get("flags_initiaux") or []),
        personnages=personnages,
        dialogues=dialogues,
        transitions=transitions,
        monstres=monstres,
        combats=combats,
        objets=objets,
        quetes=quetes,
    )


def _valider(donnees):
    erreurs = []

    if donnees.chaine and donnees.niveau_initial not in donnees.chaine:
        erreurs.append(f"niveau_initial '{donnees.niveau_initial}' absent de chaine {donnees.chaine}")

    pids = set(donnees.personnages.keys())
    niveaux = set(donnees.chaine)
    monstres_ids = set(donnees.monstres.keys())

    ids_dialogues = set()
    for d in donnees.dialogues:
        if d.id in ids_dialogues:
            erreurs.append(f"dialogue id '{d.id}' en doublon")
        ids_dialogues.add(d.id)
        if d.personnage not in pids:
            erreurs.append(f"dialogue '{d.id}' référence personnage inconnu '{d.personnage}' (connus : {sorted(pids)})")
        if niveaux and d.niveau not in niveaux:
            erreurs.append(f"dialogue '{d.id}' référence niveau inconnu '{d.niveau}'")
        if not d.messages:
            erreurs.append(f"dialogue '{d.id}' n'a aucun message")

    for t in donnees.transitions:
        if niveaux and t.niveau not in niveaux:
            erreurs.append(f"transition pour niveau inconnu '{t.niveau}'")

    ids_combats = set()
    for c in donnees.combats:
        if c.id in ids_combats:
            erreurs.append(f"combat id '{c.id}' en doublon")
        ids_combats.add(c.id)
        if c.monstre is None:
            mid = getattr(c, "_monstre_id", "?")
            erreurs.append(f"combat '{c.id}' référence monstre inconnu '{mid}' (connus : {sorted(monstres_ids)})")
        if niveaux and c.niveau not in niveaux:
            erreurs.append(f"combat '{c.id}' référence niveau inconnu '{c.niveau}'")

    objets_ids = set(donnees.objets.keys())
    ids_quetes = set()
    for q in donnees.quetes:
        if q.id in ids_quetes:
            erreurs.append(f"quete id '{q.id}' en doublon")
        ids_quetes.add(q.id)
        if q.objet is None:
            oid = getattr(q, "_objet_id", "?")
            erreurs.append(f"quete '{q.id}' référence objet inconnu '{oid}' (connus : {sorted(objets_ids)})")
        if niveaux and q.niveau not in niveaux:
            erreurs.append(f"quete '{q.id}' référence niveau inconnu '{q.niveau}'")

    poses = (
        {f for d in donnees.dialogues for f in d.pose_flags}
        | {f for c in donnees.combats for f in c.pose_flags_victoire}
        | {f for c in donnees.combats for f in c.pose_flags_epargne}
        | {f for q in donnees.quetes for f in q.pose_flags}
    )
    lus = (
        {f for d in donnees.dialogues for f in d.requiert + d.interdit}
        | {f for c in donnees.combats for f in c.requiert + c.interdit}
        | {f for q in donnees.quetes for f in q.requiert + q.interdit}
        | {f for t in donnees.transitions for f in t.requiert + t.interdit}
        | set(donnees.flags_initiaux)
    )
    orphelins = poses - lus
    if orphelins:
        erreurs.append(f"AVERT : flags posés mais jamais lus : {sorted(orphelins)}")
    requis_jamais_poses = (lus - set(donnees.flags_initiaux)) - poses
    if requis_jamais_poses:
        erreurs.append(f"AVERT : flags requis/interdits mais jamais posés : {sorted(requis_jamais_poses)}")

    bloquants = [e for e in erreurs if not e.startswith("AVERT")]
    if bloquants:
        raise ScenarioInvalide("\n".join(erreurs))
    if erreurs:
        for e in erreurs:
            print(f"[scenario] {e}")
