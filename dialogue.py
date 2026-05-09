import sys
import pygame

pygame.init()

village = "village.png"

Atticus = {
    "parle1": "atticus1.PNG",
    "parle2": "atticus2.PNG",
}

zone_texte = "zone_texte.PNG"

background = pygame.image.load(village)
bubble = pygame.image.load(zone_texte)

# Atticus

atticus_images = {}

for etat, chemin in Atticus.items():

    img = pygame.image.load(chemin)

    echelle = 0.20

    img = pygame.transform.smoothscale(
        img,
        (
            int(img.get_width() * echelle),
            int(img.get_height() * echelle),
        ),
    )

    atticus_images[etat] = img

atticus = atticus_images["parle1"]

# Fenetre

LARGEUR, HAUTEUR = background.get_width(), background.get_height()

ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))

pygame.display.set_caption("Dialogue Atticus")

# Police

police_bouton = pygame.font.Font("PIXELADE.TTF", 28)

# Couleurs

couleur_texte = (255, 255, 255)
couleur_atticus = (39, 163, 245)
couleur_IL = (255, 0, 0)
couleur_champimagic = (0, 255, 120)
couleur_code = (180, 80, 255)

couleur_bouton = (50, 120, 220)
couleur_bouton_survol = (70, 150, 255)
couleur_texte_bouton = (255, 255, 255)

# Dialogues

messages = [
    "Holà l'ami ! T'es nouveau toi nan ? Moi c'est Atticus. Ça faisait longtemps que personne n'était passé par ici. D'où viens-tu ?",

    "...",

    "Ça me dit vaguement quelque chose.",

    "...",

    "...",

    "Désolé j'étais dans mes pensées. Que cherches-tu ?",

    "...",

    "Rentrer chez toi ? Cela semble compliqué. Mais tu peux toujours aller LE voir. IL te laissera surement partir si tu restes fidèle à tes principes. Pour cela tu dois te rendre dans le temple qui se trouve après les ruines.",

    "...",

    "C'est vrai j'oubliai : les portes vers les ruines puis vers le temple ne s'ouvriront que si tu réponds aux attentes des habitants de ce monde.",

    "...",

    "J'aurais alors une requete à te faire. En ce moment, c'est pas la fete. Le village tombe en ruine et j'ai vraiment très faim. Est-ce que tu pourrais me rapporter un ChampiMagic dans la (0110) (0001 0101) (0001 1000) (0101) (0010 0000) ?",

    "...",

    "Tu ne comprends pas ? Je ne peux pas t'en dire plus car IL ne le tolèrerait pas mais je peux te donner cet indice: chaque parenthèse correspond à un nombre qui lui-meme correspond à une lettre de l'alphabet. À toi de traduire ces nombres écrits en BCG.",

    "...",

    "T'as oublié ce que je t'ai dit ? Va dans la (0110) (0001 0101) (0001 1000) (0101) (0010 0000).",
]

# Variables dialogue

index_courant = 0
chars_visibles = 0 #Nombre de caractères du message actuel qui sont affichés à l'écran
en_frappe = True
delai_frappe = 10
last_tick = pygame.time.get_ticks() #Gère le délai entre l'affichage de chaque caractère pour l'effet machine à écrire
dialogue_termine = False
timer_animation_parole = 0
delai_animation_parole = 100

#Bouton

rect_bouton = pygame.Rect(0, 0, 180, 50)

#Redimensionnement bulle,pour que le texte puisse tenir dedans

bulle_max_largeur = min(760, LARGEUR - 80)
bulle_max_hauteur = min(220, HAUTEUR - 180)

bulle_echelle = min(
    bulle_max_largeur / bubble.get_width(),
    bulle_max_hauteur / bubble.get_height(),
    1.0
)

bubble = pygame.transform.smoothscale(
    bubble,
    (
        int(bubble.get_width() * bulle_echelle),
        int(bubble.get_height() * bulle_echelle),
    ),
)

#Positions

rect_atticus = atticus.get_rect()
rect_atticus.midbottom = (LARGEUR // 2, HAUTEUR - 170)

rect_bulle = bubble.get_rect()
rect_bulle.midbottom = (LARGEUR // 2, HAUTEUR - 10)

rect_texte_bulle = rect_bulle.inflate(-40, -60)

rect_bouton.bottomright = (LARGEUR - 40, rect_bulle.top - 20)

#Fonction texte

def dessiner_texte_couleur(
    surface,
    texte,
    couleur_normale,
    pos_debut,
    max_largeur,
    max_hauteur,
    espacement_ligne=4
):

    taille_police = 26

    while taille_police >= 14:

        police = pygame.font.Font("PIXELADE.TTF", taille_police)

        mots = texte.split(" ")

        lignes = []

        ligne_actuelle = ""

        for mot in mots:

            test_ligne = ligne_actuelle + mot + " "

            largeur_test = police.size(test_ligne)[0]

            if largeur_test <= max_largeur:

                ligne_actuelle = test_ligne

            else:

                lignes.append(ligne_actuelle)

                ligne_actuelle = mot + " "

        lignes.append(ligne_actuelle)

        hauteur_ligne = police.get_height() + espacement_ligne

        hauteur_totale = len(lignes) * hauteur_ligne

        if hauteur_totale <= max_hauteur:
            break

        taille_police -= 2

    x_start, y_start = pos_debut

    dans_code = False

    for i, ligne in enumerate(lignes):

        mots_ligne = ligne.split(" ")

        x = x_start

        y = y_start + i * hauteur_ligne

        for mot in mots_ligne:

            if mot == "":
                continue

            couleur = couleur_normale

            # IL et LE
            if mot == "IL" or mot == "LE":

                couleur = couleur_IL

            # Atticus
            elif "Atticus" in mot:

                couleur = couleur_atticus

            # ChampiMagic
            elif "ChampiMagic" in mot:

                couleur = couleur_champimagic

            #Code de la foret en violet
            if "(" in mot:
                dans_code = True

            if dans_code:
                couleur = couleur_code

            if ")" in mot:

                couleur = couleur_code
                dans_code = False

            rendu = police.render(mot, True, couleur)

            surface.blit(rendu, (x, y))

            x += rendu.get_width() + police.size(" ")[0]

#Dessin bouton

def dessiner_bouton(surface, rect, texte, survol):

    couleur = couleur_bouton_survol if survol else couleur_bouton

    pygame.draw.rect(surface, couleur, rect, border_radius=12)

    label = police_bouton.render(
        texte,
        True,
        couleur_texte_bouton
    )

    label_rect = label.get_rect(center=rect.center)

    surface.blit(label, label_rect)

#Animation Atticus

def mettre_a_jour_sprite_atticus():

    global atticus
    global timer_animation_parole

    if dialogue_termine:

        atticus = atticus_images["parle1"]

    elif en_frappe:

        now = pygame.time.get_ticks()

        if now - timer_animation_parole >= delai_animation_parole:

            timer_animation_parole = now

            if atticus == atticus_images["parle1"]:

                atticus = atticus_images["parle2"]

            else:

                atticus = atticus_images["parle1"]

    else:

        atticus = atticus_images["parle1"]


#Dessin scène

def dessiner_scene():

    ecran.blit(background, (0, 0))

    mettre_a_jour_sprite_atticus()

    ecran.blit(atticus, rect_atticus)

    if not dialogue_termine:

        ecran.blit(bubble, rect_bulle)

        message = messages[index_courant][:chars_visibles]

        pos_texte = (
            rect_texte_bulle.left + 15,
            rect_texte_bulle.top + 6
        )

        clip_precedent = ecran.get_clip()

        ecran.set_clip(rect_texte_bulle)

        dessiner_texte_couleur(
            ecran,
            message,
            couleur_texte,
            pos_texte,
            rect_texte_bulle.width - 30,
            rect_texte_bulle.height - 20
        )

        ecran.set_clip(clip_precedent)

        #Bouton

        pos_souris = pygame.mouse.get_pos()

        survol = rect_bouton.collidepoint(pos_souris)

        label_bouton = "Continuer"

        if index_courant == len(messages) - 1:
            label_bouton = "Terminer"

        dessiner_bouton(
            ecran,
            rect_bouton,
            label_bouton,
            survol
        )

#Avancer dialogue, cad bouton continuer

def avancer_dialogue():

    global index_courant
    global chars_visibles
    global en_frappe
    global dialogue_termine

    if en_frappe:

        chars_visibles = len(messages[index_courant])

        en_frappe = False

    else:

        if index_courant < len(messages) - 1:

            index_courant += 1

            chars_visibles = 0

            en_frappe = True

        else:

            dialogue_termine = True

#boucle principale

horloge = pygame.time.Clock()

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()

            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if rect_bouton.collidepoint(event.pos):

                    avancer_dialogue()

        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_RETURN, pygame.K_SPACE):

                avancer_dialogue()

    # Effet machine à écrire

    if en_frappe:

        now = pygame.time.get_ticks()

        if now - last_tick >= delai_frappe:

            last_tick = now

            chars_visibles = min(
                chars_visibles + 1,
                len(messages[index_courant])
            )

            if chars_visibles >= len(messages[index_courant]):

                en_frappe = False

    dessiner_scene()

    pygame.display.flip()

    horloge.tick(60)