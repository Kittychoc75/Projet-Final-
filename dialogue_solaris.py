import os,pygame

pygame.init()

W,H=800,600

NOIR=(0,0,0)
BLANC=(255,255,255)
ROUGE=(255,80,80)

couleur_bouton=(50,120,220)
couleur_bouton_survol=(70,150,255)
couleur_texte_bouton=(255,255,255)

ecran=pygame.display.set_mode((W,H))
pygame.display.set_caption("Boss")

clock=pygame.time.Clock()

def charge(nom,taille):
    if os.path.exists(nom):
        image=pygame.image.load(nom)
        image=image.convert_alpha() if image.get_alpha() else image.convert()
        return pygame.transform.scale(image,taille)

    image=pygame.Surface(taille)
    image.fill((80,80,80))

    return image

def coupe(txt,police,largeur):

    mots=txt.split(" ")
    lignes=[]
    ligne=""

    for mot in mots:

        test=mot if ligne=="" else ligne+" "+mot

        if police.size(test)[0]<=largeur:
            ligne=test

        else:
            lignes.append(ligne)
            ligne=mot

    lignes.append(ligne)

    return lignes

def dessiner_bouton(surface,rect,texte,survol):

    couleur=couleur_bouton_survol if survol else couleur_bouton

    pygame.draw.rect(surface,couleur,rect,border_radius=12)

    label=police_bouton.render(
        texte,
        True,
        couleur_texte_bouton
    )

    label_rect=label.get_rect(center=rect.center)

    surface.blit(label,label_rect)

police=pygame.font.Font("PIXELADE.TTF",26)
petite=pygame.font.Font("PIXELADE.TTF",18)
police_bouton=pygame.font.Font("PIXELADE.TTF",28)

boss=charge("solaris.jpg",(420,420))
fond=charge("zone_texte.PNG",(740,150))

dialogues=[

"Comment est-ce possible ?",
"Un humain ici ?!",
"Comment oses-tu pénétrer dans mon royaume !",
"Ne sais-tu pas qui je suis ?",
"Moi, Maitre de ces lieux.",
"Tu ne rentreras jamais chez toi.",
"Ton sort est scellé.",
"Choisir ne servira à rien.",
"Mais... Mais... Je ne comprends pas...",
"J'ai pourtant tout fait pour te provoquer et détériorer ta santé mentale.",
"Et toi, tu ne cèdes pas à la violence ?",
"Personne n'avait été si gentil avec moi.",
"Tu es donc libre de partir.",
"Pauvre fou...",
"Tu viens de commettre une grave erreur !",
"Tu es tombé dans mon piège !",
"Tu es devenu comme moi...",
"Ne trouves-tu pas cela ironique ?",
"Penser délivrer un monde de la misère en la semant toi-meme.",
"Tu viens de me libérer de ce monde maudit en prenant ma place.",
"Tu resteras à jamais bloqué."

]

i=0
lettres=0
jeu=True

rect_bouton=pygame.Rect(0,0,200,50)
rect_bouton.bottomright=(760,400)

while jeu:

    clock.tick(60)

    texte=dialogues[i]

    fini=lettres>=len(texte)

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            jeu=False

        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:

            if rect_bouton.collidepoint(event.pos):

                if not fini:

                    lettres=len(texte)

                else:

                    i+=1
                    lettres=0

                    if i>=len(dialogues):
                        jeu=False

    if not fini:

        lettres=min(len(texte),lettres+2)

    ecran.fill(NOIR)

    ecran.blit(
        boss,
        boss.get_rect(center=(W//2,220))
    )

    x,y=30,420

    ecran.blit(fond,(x,y))

    pygame.draw.rect(
        ecran,
        BLANC,
        (x,y,740,150),
        3
    )

    nom=petite.render("LE MAITRE",1,ROUGE)

    ecran.blit(nom,(x+20,y+10))

    visible=texte[:lettres]

    lignes=coupe(visible,police,700)

    for n,ligne in enumerate(lignes[:4]):

        rendu=police.render(ligne,1,BLANC)

        ecran.blit(
            rendu,
            (x+20,y+40+n*23)
        )

    pos_souris=pygame.mouse.get_pos()

    survol=rect_bouton.collidepoint(pos_souris)

    texte_bouton="Continuer"

    if i==len(dialogues)-1:
        texte_bouton="Terminer"

    dessiner_bouton(
        ecran,
        rect_bouton,
        texte_bouton,
        survol
    )

    pygame.display.flip()

pygame.quit()