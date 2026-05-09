"""Dataclasses du scénario — strictement les données telles que décrites en YAML."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PersonnageData:
    id: str
    nom: str
    couleur_nom: tuple
    sprite_carte: str
    sprite_dialogue_1: str
    sprite_dialogue_2: str
    facteur_taille_carte: float = 1.0
    toujours_visible: bool = False  # True = sprite affiché même si plus aucun dialogue ne triggerable


@dataclass
class DialogueData:
    id: str
    niveau: str
    couleur: str
    personnage: str
    messages: list = field(default_factory=list)
    requiert: list = field(default_factory=list)
    interdit: list = field(default_factory=list)
    pose_flags: list = field(default_factory=list)
    couleurs_speciales: dict = field(default_factory=dict)


@dataclass
class TransitionData:
    niveau: str
    requiert: list = field(default_factory=list)
    interdit: list = field(default_factory=list)
    indice_echec: Optional[str] = None
    indices_par_flag: dict = field(default_factory=dict)  # flag manquant → message ciblé


@dataclass
class MonstreData:
    id: str
    nom: str
    sprites: list                   # liste de chemins
    pv: int
    degats: int
    defense_duree: int              # frames pendant lesquelles on encaisse
    spawn_min: int                  # frames mini entre 2 spawns de balles
    spawn_max: int
    nb_min: int                     # nb mini de balles par spawn
    nb_max: int
    v_min: float                    # vitesse mini d'une balle
    v_max: float
    periode_anim: int = 60


@dataclass
class ObjetData:
    id: str
    nom: str
    sprite: str
    facteur_taille_carte: float = 1.0
    cache_sur_carte: bool = False   # True = invisible sur le décor, déclenchable seulement à l'aveugle


@dataclass
class QueteData:
    id: str
    niveau: str
    couleur: str
    objet: object                  # ObjetData (résolu au chargement)
    message: str = ""
    requiert: list = field(default_factory=list)
    interdit: list = field(default_factory=list)
    pose_flags: list = field(default_factory=list)


@dataclass
class CombatData:
    id: str
    niveau: str
    couleur: str
    monstre: object                 # MonstreData (résolu au chargement)
    requiert: list = field(default_factory=list)
    interdit: list = field(default_factory=list)
    pose_flags_victoire: list = field(default_factory=list)
    pose_flags_epargne: list = field(default_factory=list)
