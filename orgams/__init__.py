import random
from otree.api import *

doc = """
Juego de donación de órganos
"""

class C(BaseConstants):
    NAME_IN_URL = 'organ_donation'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20
    CHANGE_COST = 0.75


class Group(BaseGroup):
    donaciones = models.IntegerField(initial=0)


class Player(BasePlayer):
    caso = models.CharField()
    round_number = models.IntegerField(initial=0)
    periodos_en_lista = models.IntegerField(initial=0)
    organo_a_funcional = models.BooleanField(initial=True)
    organo_b_funcional = models.BooleanField(initial=True)
    es_donante = models.BooleanField(initial=False)
    donacion_previa = models.BooleanField(initial=False)
    en_lista_espera = models.BooleanField(initial=False)
    fuera_de_juego = models.BooleanField(initial=False)


class Subsession(BaseSubsession):
    pass


class Donacion(Page):
    timeout_seconds = 15
    form_model = 'player'
    form_fields = ['es_donante']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if player.es_donante:
            group.donaciones += 1
            if player.round_number <= 10 and not timeout_happened:
                player.payoff -= C.CHANGE_COST


class Espera(WaitPage):
    pass


class Simulacion(Page):
    timeout_seconds = 15

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        caso = random.choices(['A', 'B', 'C'], [0.10, 0.20, 0.70])[0]
        player.caso = caso

        if caso == 'A':
            player.organo_a_funcional = False
            player.fuera_de_juego = True
        elif caso == 'B':
            if player.donacion_previa:
                player.fuera_de_juego = True
            else:
                player.organo_b_funcional = False
                player.en_lista_espera = True
        else:
            #player.organo_a_funcional = True
            player.organo_b_funcional = True
            player.payoff += 3

    @staticmethod
    def is_displayed(player: Player):
        return not player.en_lista_espera and not player.fuera_de_juego


class ListaEspera(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group

        if group.donaciones > 0:
            group.donaciones -= 1
            player.donacion_previa = True
            player.periodos_en_lista = 0

        if player.periodos_en_lista >= 5:
            player.fuera_de_juego = True
        
        player.periodos_en_lista += 1

    @staticmethod
    def is_displayed(player: Player):
        return player.en_lista_espera and not player.fuera_de_juego


class FinRonda(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.fuera_de_juego


page_sequence = [
    Donacion,
    Espera,
    Simulacion,
    ListaEspera,
    FinRonda
]
