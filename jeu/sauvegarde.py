"""Sauvegarde / chargement de la partie en cours.

Format simple, JSON, un seul slot. Extensible (ajouter des champs n'invalide
rien tant que la version reste la même)."""
import json
import time
from pathlib import Path

_RACINE = Path(__file__).resolve().parent.parent
_DOSSIER = _RACINE / "sauvegardes"
_FICHIER = _DOSSIER / "partie.json"

VERSION = 1


def existe():
    return _FICHIER.exists()


def sauvegarder(etat):
    """Écrit l'état dans le fichier de sauvegarde (créé si absent)."""
    _DOSSIER.mkdir(exist_ok=True)
    data = {
        "version": VERSION,
        "timestamp": int(time.time()),
        **etat,
    }
    with open(_FICHIER, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def charger():
    """Lit le fichier de sauvegarde. Retourne le dict d'état, ou None si absent/corrompu/incompatible."""
    if not _FICHIER.exists():
        return None
    try:
        with open(_FICHIER, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[sauvegarde] fichier illisible, ignoré : {e}")
        return None
    if data.get("version") != VERSION:
        print(f"[sauvegarde] version {data.get('version')} incompatible (attendu {VERSION}), ignorée")
        return None
    data.pop("version", None)
    data.pop("timestamp", None)
    return data
