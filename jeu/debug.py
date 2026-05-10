import pygame

class Debug:
    """Affichage debug : overlay fuchsia des murs + hitbox du perso + spawn + sortie.

    Activé via le flag CLI `--debug` au lancement. Pas togglable en jeu.
    """

    COULEUR_MUR = (255, 0, 255, 128)
    COULEUR_HITBOX = (0, 255, 255)
    COULEUR_SPAWN = (0, 255, 0)
    COULEUR_SORTIE = (255, 0, 0)

    def __init__(self, actif=False):
        self.actif = actif

    def dessiner(self, surface, monde, perso):
        if not self.actif:
            return

        echelle = monde.echelle
        taille_fenetre = (int(monde.taille_fenetre.x), int(monde.taille_fenetre.y))

        overlay = pygame.mask.from_surface(monde.niveau.masque_image).to_surface(
            setcolor=self.COULEUR_MUR,
            unsetcolor=(0, 0, 0, 0),
        )
        if overlay.get_size() != taille_fenetre:
            overlay = pygame.transform.scale(overlay, taille_fenetre)
        surface.blit(overlay, (0, 0))

        hitbox = perso.hitbox
        rect_scale = pygame.Rect(
            int(hitbox.left * echelle.x),
            int(hitbox.top * echelle.y),
            int(hitbox.width * echelle.x),
            int(hitbox.height * echelle.y),
        )
        pygame.draw.rect(surface, self.COULEUR_HITBOX, rect_scale, width=2)

        spawn = monde.niveau.spawn
        if spawn is not None:
            pygame.draw.circle(
                surface,
                self.COULEUR_SPAWN,
                (int(spawn.x * echelle.x), int(spawn.y * echelle.y)),
                radius=6,
                width=2,
            )

        sortie = monde.niveau.sortie
        if sortie is not None:
            sortie_scale = pygame.Rect(
                int(sortie.left * echelle.x),
                int(sortie.top * echelle.y),
                int(sortie.width * echelle.x),
                int(sortie.height * echelle.y),
            )
            pygame.draw.rect(surface, self.COULEUR_SORTIE, sortie_scale, width=2)

