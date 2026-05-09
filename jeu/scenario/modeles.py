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


@dataclass
class DialogueData:
    id: str
    niveau: str
    couleur: str          # nom de la couleur ('cyan', 'magenta', …)
    personnage: str       # id du personnage
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
