# Pixel Fall

Jeu 2D top-down développé en Python avec **pygame**.

---

## Sommaire

- [Prérequis](#prérequis)
- [Lancer le jeu](#lancer-le-jeu)
- [Contrôles](#contrôles)
- [Structure du projet](#structure-du-projet)
- [Fonctionnement](#fonctionnement)
  - [Boucle principale](#boucle-principale)
  - [Redimensionnement & ratio](#redimensionnement--ratio)
  - [Système de niveaux](#système-de-niveaux)
  - [Collisions](#collisions)
  - [Chaîne de niveaux & sortie](#chaîne-de-niveaux--sortie)
  - [Mode debug](#mode-debug)
- [Workflow éditeur d'images — calques d'un niveau](#workflow-éditeur-dimages--calques-dun-niveau)
- [Ajouter un niveau](#ajouter-un-niveau)
- [Commandes utiles](#commandes-utiles)

---

## Prérequis

- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets Python)

## Lancer le jeu

```bash
uv sync                  # installation initiale (crée .venv + Python 3.12 + pygame)
uv run main.py           # mode normal
uv run main.py --debug   # mode debug (overlay collisions/spawn/sortie)
```

## Contrôles

| Touche | Action |
|---|---|
| ← ↑ → ↓ | Déplacer le perso |

Le mode debug est activé via `--debug` au lancement (pas de toggle en jeu).

---

## Structure du projet

```
.
├── main.py                          # Entry point — boucle pygame + parsing CLI
├── pyproject.toml                   # Dépendances (pygame)
├── images/
│   ├── debut.png                    # Décor du niveau Depart
│   ├── debut_mur.png                # Masque collisions (alpha = mur)
│   ├── debut_meta.png               # Masque meta (1 px par marqueur)
│   └── perso_*.png                  # Sprites du perso (4 directions)
└── jeu/                             # Package principal
    ├── __init__.py                  # expose Gameplay, Ecran
    ├── config.py                    # constantes (LARGEUR, HAUTEUR, VITESSE_PERSO)
    ├── ecran.py                     # Gère la fenêtre + ratio au resize
    ├── gameplay.py                  # Orchestration (perso + monde + debug)
    ├── debug.py                     # Overlay debug (activé par --debug)
    ├── entites/
    │   ├── __init__.py
    │   └── perso.py                 # Perso + _Sprites (hitbox aux pieds)
    └── monde/
        ├── __init__.py
        ├── monde.py                 # Monde (niveau courant + redim + collision + changer_niveau)
        ├── niveau.py                # Classe abstraite Niveau (image + masque + meta)
        ├── couleurs_meta.py         # Constantes COULEUR_SPAWN, COULEUR_SORTIE
        ├── chaine.py                # CHAINE = [Depart, ...] (ordre des niveaux)
        └── niveaux/
            ├── __init__.py
            └── depart.py            # Niveau Depart
```

---

## Fonctionnement

### Boucle principale

`main.py` :

1. Parse les arguments CLI (`--debug`).
2. Crée la `surface` pygame en mode **redimensionnable**.
3. Instancie `Gameplay(surface, debug=...)` (qui charge le niveau et place le perso à son spawn).
4. Délègue le redimensionnement à `Ecran` (force le ratio du monde, voir ci-dessous).
5. Boucle d'événements : `QUIT`, `VIDEORESIZE`.
6. À chaque frame : `gameplay.mettre_a_jour(dt)` → `pygame.display.update()`.

### Redimensionnement & ratio

Le monde a un **ratio fixe** (largeur/hauteur de l'image décor). Sans correction, redimensionner la fenêtre déformerait l'image.

`Monde.taille_corrigee(taille)` calcule la plus grande taille **respectant le ratio** qui rentre dans la taille demandée. `Ecran.appliquer_taille(taille)` enchaîne :

1. `taille_corrigee` ramène la taille au ratio
2. `pygame.display.set_mode(taille_corrigee, RESIZABLE)` recrée la surface
3. `gameplay.redimensionner(surface)` propage à `Monde` (rescale décor) et `Perso` (rescale sprites)

Conséquence : `echelle.x == echelle.y` toujours → **aucune déformation**.

### Système de niveaux

Un **niveau** = 3 fichiers PNG dans `images/`, tous **mêmes dimensions** :

| Fichier | Rôle |
|---|---|
| `<nom>.png` | Décor visible |
| `<nom>_mur.png` | Masque alpha — pixel opaque = **mur** |
| `<nom>_meta.png` | Masque méta — 1 pixel par marqueur (spawn, sortie, …) |

La classe `Niveau` (dans `jeu/monde/niveau.py`) charge les 3 fichiers, vérifie que les dimensions matchent, construit le `pygame.mask.Mask` du masque mur et scanne le masque meta pour trouver les marqueurs (via `pygame.mask.from_threshold`).

Les sous-classes concrètes (`jeu/monde/niveaux/depart.py`) ne font que fournir les chemins de fichiers.

### Collisions

**Stockage** : tout est en **coordonnées du monde original** (jamais scalé), pour rester indépendant de la taille de la fenêtre.

- Le perso a une **hitbox réduite aux pieds** (30×20 px), pas le sprite entier — sinon le chapeau du perso bloquerait sur les murs.
- À chaque frame, `Perso.mouvement` :
  1. Calcule `dx`, `dy` à partir des touches.
  2. Applique `dx` → si `monde.collision(hitbox)` → annule.
  3. Applique `dy` → si `monde.collision(hitbox)` → annule.
  4. Cette **séparation par axe** permet de **glisser le long d'un mur** (ex: UP+RIGHT contre un mur droit, le mouvement vertical passe quand même).
- `Monde.collision(hitbox)` crée un masque rempli aux dimensions du rect et appelle `mask.overlap()` sur le masque du niveau.

### Chaîne de niveaux & sortie

L'ordre des niveaux est déclaré dans **`jeu/monde/chaine.py`** :

```python
from jeu.monde.niveaux import Depart, Foret, Boss

CHAINE = [Depart, Foret, Boss]
```

À chaque frame, `Gameplay._verifier_transitions` teste **deux directions** :

**Aller-avant** — la hitbox chevauche le `Rect` `niveau.sortie` :

1. Cherche le niveau suivant dans `CHAINE`.
2. `Monde.changer_niveau(suivant)` → recharge image + masque + meta + rescale au format courant.
3. Téléporte le perso au `spawn` du nouveau niveau.

**Retour-arrière** — la hitbox couvre le point `niveau.spawn` :

1. Cherche le niveau précédent dans `CHAINE`.
2. `Monde.changer_niveau(precedent)`.
3. Téléporte le perso au **centre de la sortie** du niveau précédent (la position où il était sorti). Si ce niveau n'a pas de sortie, fallback sur son spawn.

Dans les deux cas : sprites du perso re-rescalés à la nouvelle `echelle`, `fin_chaine` remis à `False`.

**Anti re-trigger** — deux flags `_sortie_active` / `_spawn_active` font de l'**edge-detection** : un trigger ne se déclenche qu'à la **frontière entrante** (frame précédente : pas sur le marqueur ; frame courante : sur le marqueur). Sans ça, après une transition le perso est posé sur le marqueur du niveau d'arrivée et déclencherait immédiatement la transition inverse en boucle.

**Si pas de niveau suivant** (`CHAINE` épuisée), `Gameplay.fin_chaine` passe à `True` et bloque les triggers `sortie`. Le retour-arrière reste possible.

⚠️ **Contrainte** : tous les niveaux d'une même chaîne **doivent avoir les mêmes dimensions** (image + masques). Sinon le ratio change entre niveaux et le perso est rescalé entre transitions, ce qui peut surprendre. Si besoin de tailles différentes, il faudra émettre un événement custom pour reforcer `Ecran.appliquer_taille` après chaque changement.

### Mode debug

Activé au lancement avec `uv run main.py --debug`. Pas de toggle en cours de jeu.

Affiche par-dessus le décor :
- **Murs** en fuchsia semi-transparent (#FF00FF α=128) — c'est le masque alpha rendu en couleur
- **Hitbox** du perso en cyan (cadre 2px)
- **Spawn** en cercle vert (2px)
- **Sortie** en cadre rouge (2px)

Tout est rescalé à la taille courante de la fenêtre.

---

## Workflow éditeur d'images — calques d'un niveau

Pour créer un nouveau niveau, ouvrir l'éditeur d'images de ton choix (Photopea, GIMP, Aseprite, Krita, Affinity Photo, …) avec **3 calques** (un fichier PNG exporté par calque) :

### Calque 1 — décor (`<nom>.png`)

- Le visuel du niveau.
- Aucune contrainte de couleur ou de format.
- Sauvegarder en PNG.

### Calque 2 — masque mur (`<nom>_mur.png`)

- **Mêmes dimensions** que le décor.
- Peindre les murs en **noir opaque** sur un fond **transparent**.
- ⚠️ **Pinceau dur, alpha binaire 0/255, AUCUN anti-aliasing**. Sinon les bords ont des pixels semi-transparents → collisions imprévisibles.
- Sauvegarder en PNG avec transparence.

### Calque 3 — masque meta (`<nom>_meta.png`)

- **Mêmes dimensions** que le décor.
- 1 pixel par marqueur, sur fond transparent. Couleurs définies dans `jeu/monde/couleurs_meta.py` :

| Couleur | Hex | Marqueur |
|---|---|---|
| Vert | `#00FF00` | **Spawn perso** (obligatoire) |
| Rouge | `#FF0000` | Sortie vers niveau suivant (optionnel) |

- Pour ajouter un type de marqueur : déclarer une nouvelle constante dans `couleurs_meta.py` et l'utiliser dans `Niveau`.
- ⚠️ **Pinceau dur, couleur exacte, pas d'AA**. Tolérance de chargement : ±5 par canal RGB.
- Si tu peins un blob au lieu d'un pixel : pour le **spawn** le code prend le **centre** du blob ; pour la **sortie** le code prend la **bounding box** (pratique pour définir une zone de trigger plus large).

### Vérification

Lancer le jeu en mode debug : `uv run main.py --debug`. Tu vois en fuchsia tes murs, en vert ton spawn, en rouge ta sortie → tu valides visuellement avant de jouer.

---

## Ajouter un niveau

1. Créer `images/<nom>.png`, `images/<nom>_mur.png`, `images/<nom>_meta.png` (voir [calques](#workflow-éditeur-dimages--calques-dun-niveau)).
2. Créer `jeu/monde/niveaux/<nom>.py` :
   ```python
   from jeu.monde.niveau import Niveau

   class Foret(Niveau):
       def __init__(self):
           super().__init__(
               chemin_image="images/foret.png",
               chemin_mur="images/foret_mur.png",
               chemin_meta="images/foret_meta.png",
           )
   ```
3. Exposer dans `jeu/monde/niveaux/__init__.py` :
   ```python
   from jeu.monde.niveaux.foret import Foret
   __all__ = ["Depart", "Foret"]
   ```
4. Ajouter à la chaîne dans `jeu/monde/chaine.py` :
   ```python
   from jeu.monde.niveaux import Depart, Foret
   CHAINE = [Depart, Foret]
   ```

---

## Commandes utiles

```bash
uv run main.py            # lancer le jeu
uv run main.py --debug    # lancer en mode debug
uv add <package>          # ajouter une dépendance
uv remove <package>       # retirer une dépendance
uv sync                   # réinstaller depuis le lockfile
```
