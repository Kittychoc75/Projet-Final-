"""Lance une passe de validation sur scenario.yaml et affiche les erreurs/avertissements.

Usage : uv run python verifier_scenario.py [chemin]
"""
import sys

from jeu.scenario.chargeur import ScenarioInvalide, charger


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else "scenario.yaml"
    try:
        donnees = charger(chemin)
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {chemin}")
        sys.exit(1)
    except ScenarioInvalide as e:
        print(f"[INVALIDE] {chemin} :\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERREUR DE PARSING] {chemin} : {type(e).__name__} : {e}")
        sys.exit(1)

    print(f"[OK] {chemin} valide")
    print(f"  niveau initial : {donnees.niveau_initial}")
    print(f"  chaîne         : {donnees.chaine}")
    print(f"  personnages    : {sorted(donnees.personnages.keys())}")
    print(f"  dialogues      : {[d.id for d in donnees.dialogues]}")
    print(f"  transitions    : {[t.niveau for t in donnees.transitions]}")


if __name__ == "__main__":
    main()
