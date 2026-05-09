"""Lecture et validation du fichier scenario.yaml.

Lève des erreurs explicites quand le YAML référence des entités inconnues.
"""
from dataclasses import dataclass, field

import yaml

from jeu.scenario.modeles import DialogueData, PersonnageData, TransitionData


@dataclass
class DonneesScenario:
    niveau_initial: str = "depart"
    chaine: list = field(default_factory=list)
    flags_initiaux: list = field(default_factory=list)
    personnages: dict = field(default_factory=dict)   # id → PersonnageData
    dialogues: list = field(default_factory=list)     # list[DialogueData]
    transitions: list = field(default_factory=list)   # list[TransitionData]


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
        ))

    return DonneesScenario(
        niveau_initial=brut.get("niveau_initial", "depart"),
        chaine=list(brut.get("chaine") or []),
        flags_initiaux=list(brut.get("flags_initiaux") or []),
        personnages=personnages,
        dialogues=dialogues,
        transitions=transitions,
    )


def _valider(donnees):
    """Lève ScenarioInvalide si une référence est cassée."""
    erreurs = []

    # Niveau initial doit être dans la chaîne
    if donnees.chaine and donnees.niveau_initial not in donnees.chaine:
        erreurs.append(f"niveau_initial '{donnees.niveau_initial}' absent de chaine {donnees.chaine}")

    # Chaque dialogue référence un personnage et un niveau connus
    pids = set(donnees.personnages.keys())
    niveaux = set(donnees.chaine)
    ids_dialogues = set()
    for d in donnees.dialogues:
        if d.id in ids_dialogues:
            erreurs.append(f"dialogue id '{d.id}' en doublon")
        ids_dialogues.add(d.id)
        if d.personnage not in pids:
            erreurs.append(f"dialogue '{d.id}' référence personnage inconnu '{d.personnage}' (connus : {sorted(pids)})")
        if niveaux and d.niveau not in niveaux:
            erreurs.append(f"dialogue '{d.id}' référence niveau inconnu '{d.niveau}' (connus : {sorted(niveaux)})")
        if not d.messages:
            erreurs.append(f"dialogue '{d.id}' n'a aucun message")

    # Transitions : niveau doit être dans la chaîne
    for t in donnees.transitions:
        if niveaux and t.niveau not in niveaux:
            erreurs.append(f"transition pour niveau inconnu '{t.niveau}' (connus : {sorted(niveaux)})")

    # Flags posés vs flags lus — détection de flags morts (juste un avertissement, pas bloquant)
    poses = {f for d in donnees.dialogues for f in d.pose_flags}
    lus = (
        {f for d in donnees.dialogues for f in d.requiert + d.interdit}
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
        # Que des avertissements : on les imprime mais on continue.
        for e in erreurs:
            print(f"[scenario] {e}")
