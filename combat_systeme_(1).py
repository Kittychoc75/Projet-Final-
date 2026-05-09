# combat_systeme.py
import os
import math
import random
import pygame

FPS = 60

# couleurs de base
NOIR  = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT  = (0, 180, 0)
BLEU  = (0, 120, 255)

# stats globales du joueur
XP_MAX      = 100
SANTE_MAX   = 100
GAIN_XP     = 20
PERTE_SANTE = 20

# paramètres de combat
DEGATS_BON    = 40
ZONE_CIBLE_PX = 20   # largeur de la zone "BON" au centre de la jauge
VITESSE_JAUGE = 3    # plus c'est petit, plus c'est lent

TAILLE_COEUR  = 24
TAILLE_ENNEMI = 150


def dossier_projet():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()


def charger_image(nom, taille, police):
    # on cherche d'abord dans images/, sinon directement à côté du script
    dossier = dossier_projet()
    variants = [nom]
    base, ext = os.path.splitext(nom)
    if ext.lower() in (".jpg", ".jpeg", ".png"):
        for alt in (".jpeg", ".jpg", ".png"):
            variante = base + alt
            if variante not in variants:
                variants.append(variante)

    chemins = []
    for dossier_candidat in (os.path.join(dossier, "images"), dossier):
        for variante in variants:
            chemins.append(os.path.join(dossier_candidat, variante))

    for chemin in chemins:
        if os.path.exists(chemin):
            img = pygame.image.load(chemin)
            # les jpg n'ont pas d'alpha en général
            if img.get_alpha() is None:
                img = img.convert()
            else:
                img = img.convert_alpha()
            return pygame.transform.scale(img, taille)

    # image manquante → carré gris avec le nom dedans
    surf = pygame.Surface(taille, pygame.SRCALPHA)
    surf.fill((80, 80, 80))
    surf.blit(police.render(nom, True, BLANC), (5, taille[1] // 2 - 10))
    return surf


def dessiner_barre(ecran, police, x, y, w, h, val, val_max, titre, droite=False):
    pygame.draw.rect(ecran, (70, 0, 0), (x, y, w, h))
    ratio = 0 if val_max == 0 else max(0.0, min(1.0, val / val_max))
    pygame.draw.rect(ecran, VERT, (x, y, int(w * ratio), h))
    pygame.draw.rect(ecran, BLANC, (x, y, w, h), 2)
    label = police.render(f"{titre}: {max(0, int(val))}/{val_max}", True, BLANC)
    lx = (x + w - label.get_width()) if droite else x
    ecran.blit(label, (lx, y - 18))


def vitesse_vers(x0, y0, x1, y1, v):
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0.0, 0.0
    return (dx / dist) * v, (dy / dist) * v


def point_bord(rect):
    # on choisit un côté au hasard puis un point dessus
    cote = random.choice(("g", "d", "h", "b"))
    if cote == "g":
        return rect.left,  random.randint(rect.top, rect.bottom)
    if cote == "d":
        return rect.right, random.randint(rect.top, rect.bottom)
    if cote == "h":
        return random.randint(rect.left, rect.right), rect.top
    return     random.randint(rect.left, rect.right), rect.bottom


class Bouton:
    def __init__(self, rect, texte, police):
        self.rect   = rect
        self.texte  = texte
        self.police = police

    def afficher(self, ecran):
        pygame.draw.rect(ecran, BLANC, self.rect, 2)
        t = self.police.render(self.texte, True, BLANC)
        ecran.blit(t, t.get_rect(center=self.rect.center))

    def clique(self, pos):
        return self.rect.collidepoint(pos)


class Jauge:
    def __init__(self, rect):
        self.rect = rect
        self.reset()

    def reset(self):
        self.x  = self.rect.left
        self.vx = VITESSE_JAUGE

    def update(self):
        self.x += self.vx
        if self.x <= self.rect.left:
            self.x  = self.rect.left
            self.vx = abs(self.vx)
        if self.x >= self.rect.right:
            self.x  = self.rect.right
            self.vx = -abs(self.vx)

    def reussi(self):
        return abs(self.x - self.rect.centerx) <= ZONE_CIBLE_PX // 2

    def afficher(self, ecran):
        pygame.draw.rect(ecran, BLANC, self.rect, 2)

        # zone cible au centre
        demi = ZONE_CIBLE_PX // 2
        zone = pygame.Rect(self.rect.centerx - demi, self.rect.top, ZONE_CIBLE_PX, self.rect.height)
        pygame.draw.rect(ecran, BLANC, zone, 1)

        # ligne centrale + curseur
        pygame.draw.line(ecran, BLANC,
                         (self.rect.centerx, self.rect.top),
                         (self.rect.centerx, self.rect.bottom), 1)
        pygame.draw.circle(ecran, BLANC, (int(self.x), self.rect.centery), 6)


class Projectile:
    def __init__(self, x, y, vx, vy, r, couleur):
        self.x       = float(x)
        self.y       = float(y)
        self.vx      = float(vx)
        self.vy      = float(vy)
        self.r       = int(r)
        self.couleur = couleur
        self.vivant  = True

    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r * 2, self.r * 2)

    def update_ennemi(self, zone_sortie):
        self.x += self.vx
        self.y += self.vy
        if not zone_sortie.collidepoint(int(self.x), int(self.y)):
            self.vivant = False

    def update_tir(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < -80:
            self.vivant = False

    def afficher(self, ecran):
        pygame.draw.circle(ecran, self.couleur, (int(self.x), int(self.y)), self.r)


class Ennemi:
    def __init__(self, nom, images, pv, periode, centre):
        self.nom     = nom
        self.images  = images
        self.pv_max  = pv
        self.pv      = pv
        self.periode = periode
        self.centre  = centre
        self.temps   = 0
        self.frame   = 0
        self.rect    = images[0].get_rect(center=centre)

    def update(self):
        if len(self.images) > 1:
            self.temps += 1
            if self.temps % self.periode == 0:
                self.frame = 1 - self.frame
        self.rect = self.images[self.frame].get_rect(center=self.centre)

    def afficher(self, ecran):
        ecran.blit(self.images[self.frame], self.rect)


class Coeur:
    def __init__(self, image, zone):
        self.image      = image
        self.zone       = zone
        self.rect       = image.get_rect(center=zone.center)
        self.vitesse    = 4
        self.invincible = 0

    def reset(self):
        self.rect.center = self.zone.center
        self.invincible  = 0

    def update(self):
        if self.invincible > 0:
            self.invincible -= 1

    def bouger(self, touches):
        dx = dy = 0
        if touches[pygame.K_LEFT]:  dx = -self.vitesse
        if touches[pygame.K_RIGHT]: dx =  self.vitesse
        if touches[pygame.K_UP]:    dy = -self.vitesse
        if touches[pygame.K_DOWN]:  dy =  self.vitesse
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(self.zone)

    def afficher(self, ecran):
        # clignote quand invincible
        if self.invincible == 0 or (self.invincible // 4) % 2 == 0:
            ecran.blit(self.image, self.rect)


POKEMONS = {
    "rondoudou": {
        "nom": "Rondoudou",
        "images": ["rondoudou1.jpg", "rondoudou2.jpg"],
        "pv": 120,
        "degats": 4,
        "defense_duree": 260,
        "spawn_min": 65, "spawn_max": 95,
        "nb_min": 1, "nb_max": 1,
        "v_min": 1.1, "v_max": 1.7,
        "periode_anim": 60,
    },
    "tiplouf": {
        "nom": "Tiplouf",
        # IMPORTANT : il faut bien 2 fichiers différents
        "images": ["tiplouf1.jpeg", "tiplouf2.jpeg"],
        "pv": 150,
        "degats": 5,
        "defense_duree": 280,
        "spawn_min": 60, "spawn_max": 90,
        "nb_min": 1, "nb_max": 2,
        "v_min": 1.2, "v_max": 1.9,
        "periode_anim": 60,
    },
    "dracofeu": {
        "nom": "Dracofeu",
        "images": ["dracofeu1.jpeg", "dracofeu2.jpeg"],
        "pv": 220,
        "degats": 7,
        "defense_duree": 320,
        "spawn_min": 40, "spawn_max": 65,
        "nb_min": 2, "nb_max": 3,
        "v_min": 1.5, "v_max": 2.5,
        "periode_anim": 60,
    },
    "reshizekrom": {
        "nom": "ReshiZekrom",
        "images": ["reshizekrom1.jpeg", "reshizekrom2.jpeg"],
        "pv": 320,
        "degats": 9,
        "defense_duree": 360,
        "spawn_min": 30, "spawn_max": 50,
        "nb_min": 2, "nb_max": 4,
        "v_min": 1.9, "v_max": 3.0,
        "periode_anim": 60,
    },
}


def page_choix(ecran, pokemon_id):
    police  = pygame.font.Font(None, 44)
    petite  = pygame.font.Font(None, 24)
    horloge = pygame.time.Clock()
    w, h    = ecran.get_size()

    cfg      = POKEMONS[pokemon_id]
    img      = charger_image(cfg["images"][0], (140, 140), petite)
    rect_img = img.get_rect(center=(w // 2, h // 2 - 60))

    b_attaquer = Bouton(pygame.Rect(w // 2 - 220, h // 2 + 90, 180, 55), "ATTAQUER", petite)
    b_epargner = Bouton(pygame.Rect(w // 2 + 40,  h // 2 + 90, 180, 55), "EPARGNER", petite)

    while True:
        horloge.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quitter"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quitter"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if b_attaquer.clique(event.pos): return "attaquer"
                if b_epargner.clique(event.pos): return "epargner"

        ecran.fill(NOIR)
        ecran.blit(img, rect_img)

        t1 = police.render(cfg["nom"], True, BLANC)
        ecran.blit(t1, t1.get_rect(center=(w // 2, 70)))
        t2 = petite.render("Attaquer ou epargner ?", True, BLANC)
        ecran.blit(t2, t2.get_rect(center=(w // 2, h // 2 + 50)))

        b_attaquer.afficher(ecran)
        b_epargner.afficher(ecran)
        pygame.display.flip()


def animation_fin(ecran, xp, sante):
    # montre d'abord le gain XP, puis la perte de santé
    petite  = pygame.font.Font(None, 24)
    grande  = pygame.font.Font(None, 44)
    horloge = pygame.time.Clock()
    w, h    = ecran.get_size()

    b_suivant = Bouton(pygame.Rect(w // 2 - 90, h // 2 + 120, 180, 55), "SUIVANT", petite)

    xp2 = min(XP_MAX, xp + GAIN_XP)
    s2  = max(0, sante - PERTE_SANTE)

    etape = "XP"
    cur   = xp

    while True:
        horloge.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return xp, sante
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return xp, sante
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if etape == "XP":
                    if cur < xp2:
                        cur = xp2   # skip l'animation
                    elif b_suivant.clique(event.pos):
                        etape = "SANTE"
                        cur   = sante
                else:
                    if cur > s2:
                        cur = s2
                    elif b_suivant.clique(event.pos):
                        return xp2, s2

        if etape == "XP"    and cur < xp2: cur += 1
        if etape == "SANTE" and cur > s2:  cur -= 1

        ecran.fill(NOIR)

        if etape == "XP":
            t = grande.render("Victoire", True, BLANC)
            ecran.blit(t, t.get_rect(center=(w // 2, 120)))
            dessiner_barre(ecran, petite, 200, h // 2, 400, 20, cur, XP_MAX, "XP")
            if cur >= xp2:
                b_suivant.afficher(ecran)
        else:
            t = grande.render("Sante", True, BLANC)
            ecran.blit(t, t.get_rect(center=(w // 2, 120)))
            dessiner_barre(ecran, petite, 200, h // 2, 400, 20, cur, SANTE_MAX, "SANTE")
            if cur <= s2:
                b_suivant.afficher(ecran)

        pygame.display.flip()


def combat(ecran, pokemon_id, xp, sante):
    petite  = pygame.font.Font(None, 24)
    horloge = pygame.time.Clock()
    w, h    = ecran.get_size()

    centre_ennemi = (w // 2, 80)
    arene         = pygame.Rect(w // 2 - 150, 160, 300, 300)

    zone_coeur  = arene.inflate(-20, -20)
    zone_sortie = arene.inflate(60, 60)

    y_barres = arene.bottom + 10

    # jauge d'attaque — positionnée clairement sous les barres, pas de chevauchement
    jauge_rect = pygame.Rect(w // 2 - 200, h - 40, 400, 22)

    cfg = POKEMONS[pokemon_id]

    img_coeur = charger_image("coeur.png", (TAILLE_COEUR, TAILLE_COEUR), petite)
    coeur     = Coeur(img_coeur, zone_coeur)

    images_ennemi = [charger_image(n, (TAILLE_ENNEMI, TAILLE_ENNEMI), petite) for n in cfg["images"]]
    ennemi        = Ennemi(cfg["nom"], images_ennemi, cfg["pv"], cfg["periode_anim"], centre_ennemi)

    pv_joueur     = 100
    pv_joueur_max = 100

    jauge = Jauge(jauge_rect)

    etat       = "JAUGE"
    balles     = []
    tir        = None
    degats_tir = 0

    prochain_spawn = 0
    temps          = 0
    temps_defense  = 0

    while True:
        horloge.tick(FPS)
        temps += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quitter", xp, sante
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quitter", xp, sante

            if etat == "JAUGE":
                espace_ou_clic = (
                    event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)
                ) or (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                )
                if espace_ou_clic:
                    ok         = jauge.reussi()
                    degats_tir = DEGATS_BON if ok else 0
                    tir        = Projectile(jauge_rect.centerx, jauge_rect.top, 0.0, -11.0, 4, BLEU)
                    etat       = "TIR"

        touches = pygame.key.get_pressed()
        ennemi.update()
        coeur.update()

        if etat == "JAUGE":
            jauge.update()

        if etat == "TIR" and tir is not None:
            tir.update_tir()
            if tir.vivant and tir.rect().colliderect(ennemi.rect):
                if degats_tir > 0:
                    ennemi.pv -= degats_tir
                tir.vivant = False

            if not tir.vivant:
                tir = None
                if ennemi.pv <= 0:
                    xp, sante = animation_fin(ecran, xp, sante)
                    return "victoire", xp, sante
                # sinon on passe en phase défense
                balles        = []
                temps_defense = cfg["defense_duree"]
                prochain_spawn = temps + 10
                etat          = "DEFENSE"

        if etat == "DEFENSE":
            coeur.bouger(touches)

            if temps >= prochain_spawn:
                nb = random.randint(cfg["nb_min"], cfg["nb_max"])
                for _ in range(nb):
                    sx, sy = point_bord(arene)
                    tx = coeur.rect.centerx + random.randint(-35, 35)
                    ty = coeur.rect.centery + random.randint(-35, 35)
                    v  = random.uniform(cfg["v_min"], cfg["v_max"])
                    vx, vy = vitesse_vers(sx, sy, tx, ty, v)
                    balles.append(Projectile(sx, sy, vx, vy, 4, BLANC))
                prochain_spawn = temps + random.randint(cfg["spawn_min"], cfg["spawn_max"])

            for b in balles[:]:
                b.update_ennemi(zone_sortie)
                if b.vivant and coeur.invincible == 0 and b.rect().colliderect(coeur.rect):
                    pv_joueur       -= cfg["degats"]
                    coeur.invincible = 22
                    b.vivant         = False
                if not b.vivant:
                    balles.remove(b)

            temps_defense -= 1
            if pv_joueur <= 0:
                return "defaite", xp, sante
            if temps_defense <= 0:
                balles = []
                jauge.reset()
                etat = "JAUGE"

        # --- rendu ---
        ecran.fill(NOIR)
        ennemi.afficher(ecran)
        pygame.draw.rect(ecran, BLANC, arene, 5)

        for b in balles:
            b.afficher(ecran)
        if tir is not None:
            tir.afficher(ecran)

        coeur.afficher(ecran)

        # barre ennemie à gauche, label à gauche
        dessiner_barre(ecran, petite, 80,  y_barres, 300, 18, ennemi.pv, ennemi.pv_max, ennemi.nom)
        # barre joueur à droite, label aligné à droite
        dessiner_barre(ecran, petite, 420, y_barres, 300, 18, pv_joueur, pv_joueur_max, "Toi", droite=True)

        if etat == "JAUGE":
            jauge.afficher(ecran)
            info = petite.render("Clique ou Espace pour attaquer", True, BLANC)
            ecran.blit(info, (w // 2 - 120, jauge_rect.top - 30))
        else:
            info = petite.render("Defense: esquive", True, BLANC)
            ecran.blit(info, (w // 2 - 70, jauge_rect.top - 30))

        pygame.display.flip()


def lancer_rencontre(ecran, pokemon_id, xp, sante):
    if pokemon_id not in POKEMONS:
        raise ValueError("pokemon_id inconnu: " + str(pokemon_id))

    choix = page_choix(ecran, pokemon_id)
    if choix == "quitter": return "quitter", xp, sante
    if choix == "epargner": return "epargne", xp, sante

    return combat(ecran, pokemon_id, xp, sante)


if __name__ == "__main__":
    pygame.init()
    fenetre = pygame.display.set_mode((800, 600))
    res, xp, sante = lancer_rencontre(fenetre, "tiplouf", 0, 100)
    print(res, xp, sante)
    pygame.quit()
