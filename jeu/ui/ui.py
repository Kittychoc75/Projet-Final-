# jeu/ui/ui.py
"""Façade UI : regroupe inventaire, dialogue, combat et indices flottants."""
from jeu.combat import ModaleCombat
from jeu.ui.indice import IndiceFlottant
from jeu.ui.modales.dialogue import ModaleDialogue
from jeu.ui.modales.inventaire import Inventaire


class UI:
    """Regroupe toutes les modales et le bandeau d'indice ; route resize/events/update/draw."""

    def __init__(self, joueur, scenario):
        """Instancie inventaire, dialogue, combat et indice (référencent `joueur` et `scenario`).

        Parameters
        ----------
        joueur : Joueur
                 Source de vérité des stats (vie, xp) et de l'inventaire.
        scenario : Scenario
                   Scénario chargé (catalogue d'objets, déclencheurs).
        """
        self.joueur = joueur
        self.scenario = scenario
        self.inventaire = Inventaire(joueur, scenario)
        self.dialogue = ModaleDialogue()
        self.combat = ModaleCombat(joueur)
        self.indice = IndiceFlottant()
        self.modales = [self.inventaire, self.dialogue, self.combat]

    def declencher_dialogue(self, dialogue):
        """Ouvre la modale de dialogue avec le `Dialogue` runtime fourni.

        Parameters
        ----------
        dialogue : Dialogue
                   Dialogue runtime (personnage + messages + callback fin).
        """
        self.dialogue.declencher(dialogue)

    def declencher_combat(self, combat_data, on_termine):
        """Ouvre la modale combat ; `on_termine(resultat)` est appelé à la fin.

        Parameters
        ----------
        combat_data : CombatData
                      Définition du combat à jouer.
        on_termine : callable
                     Callback `(resultat: str) -> None` appelé à la fin.
        """
        self.combat.declencher(combat_data, on_termine)

    def afficher_indice(self, message):
        """Affiche un bandeau temporaire en haut de l'écran.

        Parameters
        ----------
        message : str
                  Texte à afficher.
        """
        self.indice.afficher(message)

    def bloque_jeu(self):
        """True si une modale ouverte doit bloquer le déplacement du perso.

        Parameters
        ----------

        Returns
        ----------
        bool
             True si une modale bloquante est ouverte.
        """
        return any(m.bloque_jeu for m in self.modales)

    def redimensionner(self, echelle):
        """Propage le resize à toutes les modales et au bandeau d'indice.

        Parameters
        ----------
        echelle : pygame.math.Vector2
                  Facteur (sx, sy) à appliquer à tous les éléments UI.
        """
        for m in self.modales:
            m.redimensionner(echelle)
        self.indice.redimensionner(echelle)

    def gerer_evenement(self, evenement):
        """Route un événement pygame vers chaque modale.

        Parameters
        ----------
        evenement : pygame.event.Event
                    Événement pygame courant.
        """
        for m in self.modales:
            m.gerer_evenement(evenement)

    def mettre_a_jour(self, dt):
        """Tick toutes les modales et le bandeau d'indice.

        Parameters
        ----------
        dt : int
             Durée écoulée depuis la dernière frame en millisecondes.
        """
        for m in self.modales:
            m.mettre_a_jour(dt)
        self.indice.mettre_a_jour(dt)

    def dessiner(self, surface):
        """Dessine modales (dans l'ordre) puis l'indice par-dessus.

        Parameters
        ----------
        surface : pygame.Surface
                  Surface d'affichage sur laquelle dessiner.
        """
        for m in self.modales:
            m.dessiner(surface)
        self.indice.dessiner(surface)
