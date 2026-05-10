"""PNJ : sprite affiché sur la carte + deux sprites de portrait (bouche fermée/ouverte)."""
import pygame
from pygame.math import Vector2


class Personnage:
    """Personnage non-joueur : sprite carte + sprites dialogue (bouche fermée/ouverte)."""

    def __init__(self, nom, couleur_nom, sprite_carte, sprite_dialogue_1, sprite_dialogue_2, facteur_taille_carte=1.0, toujours_visible=False):
        """Charge les 3 sprites (carte + 2 portraits). `toujours_visible` force la présence sur la map.

        Parameters
        ----------
        nom : str
              Nom du personnage (affiché dans les dialogues).
        couleur_nom : tuple[int, int, int]
                      Couleur RGB du nom du personnage.
        sprite_carte : str
                       Chemin du PNG du sprite affiché sur la carte.
        sprite_dialogue_1 : str
                            Chemin du PNG portrait bouche fermée.
        sprite_dialogue_2 : str
                            Chemin du PNG portrait bouche ouverte.
        facteur_taille_carte : float
                               Multiplicateur de taille du sprite carte.
        toujours_visible : bool
                           True pour rester affiché même si plus aucun dialogue.
        """
        self.nom = nom
        self.couleur_nom = couleur_nom
        self.toujours_visible = toujours_visible
        origine = pygame.image.load(sprite_carte).convert_alpha()
        if facteur_taille_carte != 1.0:
            w = max(1, int(origine.get_width() * facteur_taille_carte))
            h = max(1, int(origine.get_height() * facteur_taille_carte))
            origine = pygame.transform.scale(origine, (w, h))
        self._sprite_carte_origine = origine
        self.sprite_dialogue_1 = pygame.image.load(sprite_dialogue_1).convert_alpha()
        self.sprite_dialogue_2 = pygame.image.load(sprite_dialogue_2).convert_alpha()
        self._sprite_carte_echelle = None
        self._sprite_carte = self._sprite_carte_origine

    def redimensionner_carte(self, echelle):
        """Met à jour le sprite carte selon `echelle` (no-op si inchangée).

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer.
        """
        echelle = Vector2(echelle)
        if echelle == self._sprite_carte_echelle:
            return
        self._sprite_carte_echelle = echelle
        l = max(1, int(self._sprite_carte_origine.get_width() * echelle.x))
        h = max(1, int(self._sprite_carte_origine.get_height() * echelle.y))
        self._sprite_carte = pygame.transform.scale(self._sprite_carte_origine, (l, h))

    def dessiner_sur_carte(self, surface, position_monde, echelle):
        """Blitte le sprite carte ancré midbottom à `position_monde * echelle`.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        position_monde : pygame.math.Vector2
                         Position cible en coordonnées monde original.
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) de conversion vers la fenêtre.
        """
        self.redimensionner_carte(echelle)
        rect = self._sprite_carte.get_rect()
        rect.midbottom = (
            int(position_monde.x * echelle.x),
            int(position_monde.y * echelle.y),
        )
        surface.blit(self._sprite_carte, rect.topleft)

    def sprite_dialogue(self, bouche_ouverte):
        """Retourne le portrait bouche-ouverte ou bouche-fermée selon le flag.

        Parameters
        ----------
        bouche_ouverte : bool
                         True pour retourner le portrait bouche ouverte.

        Returns
        ----------
        pygame.Surface
               Sprite portrait correspondant.
        """
        return self.sprite_dialogue_2 if bouche_ouverte else self.sprite_dialogue_1
