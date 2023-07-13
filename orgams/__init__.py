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

class Subsession(BaseSubsession):
    pass
    #def creating_session(self):
    #    self.group_randomly(fixed_id_in_group=True)
    #    self.group_by_arrival_time()

class Group(BaseGroup):
    donaciones = models.IntegerField(initial=0)

    def before_session_starts(self):
        for player in self.get_players():
            player.donacion_previa = False
            player.en_lista_espera = False
            player.fuera_de_juego = False
            player.pago = 0.0

class Player(BasePlayer):
    caso = models.CharField(initial="")
    periodos_en_lista = models.IntegerField(initial=0)
    organo_a_funcional = models.BooleanField(initial=True)
    organo_b_funcional = models.BooleanField(initial=True)
    es_donante = models.BooleanField(initial=False)
    donacion_previa = models.BooleanField(initial=False)
    en_lista_espera = models.BooleanField(initial=False)
    fuera_de_juego = models.BooleanField(initial=False)
    pago = models.FloatField(initial=0.0)


# FUNCTIONS

def guardar_valores_jugadores(subsession):
    if subsession.round_number > 1:
        for player in subsession.get_players():
            jugador_anterior = player.in_round(subsession.round_number - 1)
            #player.jugador_anterior_id = jugador_anterior.id_in_group
            player.caso = jugador_anterior.caso
            player.periodos_en_lista = jugador_anterior.periodos_en_lista
            player.organo_a_funcional = jugador_anterior.organo_a_funcional
            player.organo_b_funcional = jugador_anterior.organo_b_funcional
            player.es_donante = jugador_anterior.es_donante
            player.donacion_previa = jugador_anterior.donacion_previa
            player.en_lista_espera = jugador_anterior.en_lista_espera
            player.fuera_de_juego = jugador_anterior.fuera_de_juego
            player.pago = jugador_anterior.pago


def log(p: Player, fx):
    g = p.group

    print("Player {}: {} | Donante: {} | Donaciones: {} | Donacion Previa: {} | Caso: {} | Organo A: {} | Organo B: {} | Lista de Espera: {} | Periodos: {} | Fuera: {} | Payoff: {}".format(
        p.id_in_group, fx, p.es_donante, g.donaciones, p.donacion_previa, p.caso, p.organo_a_funcional, p.organo_b_funcional, p.en_lista_espera, p.periodos_en_lista, p.fuera_de_juego, p.pago))
    

def ElegirDonar(p: Player):
    g = p.group
    if p.es_donante:
        if p.round_number <= 10:
            p.pago -= C.CHANGE_COST
    
    log(p, "ElegirDonar")


def SimularCaso(p: Player):
    g = p.group
    caso = random.choices(['A', 'B', 'C'], [0.10, 0.20, 0.70])[0]
    p.caso = caso

    if caso == 'A':
        p.organo_a_funcional = False
        p.fuera_de_juego = True
        if p.es_donante:
            g.donaciones += 1
    elif caso == 'B':
        if p.donacion_previa:
            p.fuera_de_juego = True
        else:
            p.organo_b_funcional = False
            p.en_lista_espera = True
    else:
        #p.organo_a_funcional = True
        #p.organo_b_funcional = True
        p.pago += 3.0
    
    log(p, "SimularCaso")


def EvaluarLista(p: Player):
    g = p.group

    if g.donaciones > 0:
        g.donaciones -= 1
        p.donacion_previa = True
        p.periodos_en_lista = 0

    if p.periodos_en_lista >= 5:
        p.fuera_de_juego = True
    
    p.periodos_en_lista += 1

    log(p, "EvaluarLista")


# PAGES

class Donacion(Page):
    timeout_seconds = 15
    form_model = 'player'
    form_fields = ['es_donante']

    @staticmethod
    def is_displayed(p: Player):
        guardar_valores_jugadores(p.subsession)
        return p.round_number == 1

    @staticmethod
    def before_next_page(p: Player, timeout_happened):
        ElegirDonar(p)


class Simulacion(Page):
    timeout_seconds = 5

    @staticmethod
    def is_displayed(p: Player):
        return not p.en_lista_espera and not p.fuera_de_juego
    
    @staticmethod
    def before_next_page(p: Player, timeout_happened):
        SimularCaso(p)


class ListaEspera(Page):
    timeout_seconds = 5

    @staticmethod
    def is_displayed(p: Player):
        return p.en_lista_espera and not p.fuera_de_juego
    
    @staticmethod
    def before_next_page(p: Player, timeout_happened):
        EvaluarLista(p)


class Espera(WaitPage):
    pass


class FinRonda(WaitPage):
    @staticmethod
    def is_displayed(p: Player):
        return p.fuera_de_juego


page_sequence = [
    Donacion,
    Espera,
    Simulacion,
    ListaEspera,
    FinRonda
]
