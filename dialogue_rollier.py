import os,pygame

pygame.init()

W,H=800,600

NOIR=(0,0,0)
BLANC=(255,255,255)
JAUNE=(255,230,80)

BLEU=(80,220,255)
VERT=(120,255,180)

couleur_bouton=(50,120,220)
couleur_bouton_survol=(70,150,255)
couleur_texte_bouton=(255,255,255)

ecran=pygame.display.set_mode((W,H))

clock=pygame.time.Clock()

def img(nom,t):

    if os.path.exists(nom):

        i=pygame.image.load(nom)

        i=i.convert_alpha() if i.get_alpha() else i.convert()

        return pygame.transform.scale(i,t)

    s=pygame.Surface(t)

    s.fill((80,80,80))

    return s

def lignes(txt,p,l):

    mots=txt.split(" ")

    res=[]

    li=""

    for mot in mots:

        test=mot if li=="" else li+" "+mot

        if p.size(test)[0]<=l:

            li=test

        else:

            if li:
                res.append(li)

            li=mot

    if li:
        res.append(li)

    return res

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

p=pygame.font.Font("PIXELADE.TTF",26)
pp=pygame.font.Font("PIXELADE.TTF",18)
police_bouton=pygame.font.Font("PIXELADE.TTF",28)
rollier=img("monsieur rollier.jpg",(340,340))
rollier_cafe=img("monsieur rollier1.jpg",(340,340))
fond=img("zone_texte.PNG",(740,150))

dialogues=[

"*SOUPIRE* Oh la la... La matrice inversée ne fonctionne que sur l'algorithme cubique du tableau de Karnaugh sucré au sucre.",

"J'ai mélangé le tasty crousty de la fonction quadratique en concaténation logarithmique. Je suis fichu.",

"La porte ne s'ouvrira jamais.",

"...",

"Ah, toi aussi tu veux rentrer dans le temple, petit toutou ? Ha Ha Ha...",

"...",

"HA HA HAAAAAAAAAAAAAAAAAAAAAAA !!!",

"...",

"Ummmh. Je ne peux rien faire depuis que j'ai perdu ma PUFF préférée.",

"J'en ai besoin, c'est VITAAAAAAAAAAAAL. Va chercher !",

"...",

"C'est une blague ?! Tu ne sais pas ce que c'est qu'une PUFF ?!",

"C'est pourtant évident, tout est dans le nom : Psychose Ultraviolette Formaldéshydrogénation Fractoluminescente.",

"Stupide chien ! Va chercher ma PUFF.",

"MA PUFF.",

"Ah ! Ma PUFF ! MA PUUUUUUUUUUFF !",

"Ma Psychose Ultraviolette Formaldéshydrogénation Fractoluminescente !",

"Merci ! Merci ! MERCIIIIIIIIIIIIIII !",

"Je peux enfin résoudre mon problème !",

"...",

"Pause café.",

"...",

"Ok, c'est bon ! La porte du temple est ouverte.",

"MA PUFF !",

"MA PUUUUUUUFF !"

]

couleurs={

"PUFF":VERT,

"Psychose":VERT,
"Ultraviolette":VERT,
"Formaldéshydrogénation":VERT,
"Fractoluminescente":VERT,
"PUUUUUUUUUUFF":VERT

}

i=0
lettres=0
run=True
rect_bouton=pygame.Rect(0,0,200,50)
rect_bouton.bottomright=(760,400)

while run:

    clock.tick(60)

    txt=dialogues[i]

    fini=lettres>=len(txt)

    for e in pygame.event.get():

        if e.type==pygame.QUIT:
            run=False

        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
            run=False

        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:

            if rect_bouton.collidepoint(e.pos):

                if not fini:

                    lettres=len(txt)

                else:

                    i+=1

                    lettres=0

                    if i>=len(dialogues):
                        run=False

    if not fini:

        lettres=min(len(txt),lettres+2)

    ecran.fill(NOIR)

    perso=rollier_cafe if txt=="Pause café." else rollier

    ecran.blit(
        perso,
        perso.get_rect(center=(W//2,220))
    )

    x,y=30,420

    ecran.blit(fond,(x,y))

    pygame.draw.rect(
        ecran,
        BLANC,
        (x,y,740,150),
        3
    )

    ecran.blit(
        pp.render("MONSIEUR ROLLIER",1,JAUNE),
        (x+20,y+10)
    )

    for n,li in enumerate(lignes(txt[:lettres],p,700)[:4]):

        px=x+20

        py=y+40+n*23

        for mot in li.split(" "):

            propre=mot.strip(".,!?:;")

            col=couleurs.get(propre,BLANC)

            rendu=p.render(mot+" ",1,col)

            ecran.blit(rendu,(px,py))

            px+=rendu.get_width()

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