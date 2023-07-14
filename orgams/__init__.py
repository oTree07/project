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


class Group(BaseGroup):
    ronda = models.IntegerField(initial=0)
    donaciones = models.IntegerField(initial=0)


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
    iteracion = models.IntegerField(initial=0)


# FUNCTIONS

def log(p: Player, fx):
    g = p.group

    print("Player {}: {} | Donante: {} | Donaciones: {} | Donacion Previa: {} | Caso: {} | Organo A: {} | Organo B: {} | Lista de Espera: {} | Periodos: {} | Fuera: {} | Payoff: {}".format(
        p.id_in_group, fx, p.es_donante, g.donaciones, p.donacion_previa, p.caso, p.organo_a_funcional, p.organo_b_funcional, p.en_lista_espera, p.periodos_en_lista, p.fuera_de_juego, p.pago))
    
def ResetearJugador(p: Player):
    subsession = p.subsession
    g = p.group

    for p in subsession.get_players():
        p.caso = ""
        p.periodos_en_lista = 0
        p.organo_a_funcional = True
        p.organo_b_funcional = True
        p.es_donante = False
        p.donacion_previa = False
        p.en_lista_espera = False
        p.fuera_de_juego = False
        p.pago = 0.0
        p.iteracion = 0
    
    g.donaciones = 0 

def GuardarJugador(p: Player):
    subsession = p.subsession
    g = p.group

    if subsession.round_number > 1:
        for p in subsession.get_players():
            jugador_anterior = p.in_round(subsession.round_number - 1)
            g.donaciones = jugador_anterior.group.donaciones
            g.ronda = jugador_anterior.group.ronda
            p.caso = jugador_anterior.caso
            p.periodos_en_lista = jugador_anterior.periodos_en_lista
            p.organo_a_funcional = jugador_anterior.organo_a_funcional
            p.organo_b_funcional = jugador_anterior.organo_b_funcional
            p.es_donante = jugador_anterior.es_donante
            p.donacion_previa = jugador_anterior.donacion_previa
            p.en_lista_espera = jugador_anterior.en_lista_espera
            p.fuera_de_juego = jugador_anterior.fuera_de_juego
            p.pago = jugador_anterior.pago


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
        p.en_lista_espera = False
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
        GuardarJugador(p)
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
    @staticmethod
    def is_displayed(p: Player):
        return not p.fuera_de_juego


class FinRonda(WaitPage):
    template_name = 'orgams/FinRonda.html'

    @staticmethod
    def is_displayed(p: Player):
        return p.fuera_de_juego

class Resultados(Page):
    @staticmethod
    def is_displayed(p: Player):
        g= p.group

        if all(p.fuera_de_juego == True for p in g.subsession.get_players()):
            print("FIN RONDA " + str(g.ronda))
            ResetearJugador(p)
            g.ronda += 1

        return g.ronda == 2

    @staticmethod
    def app_after_this_page(p: Player, upcoming_apps):
        return upcoming_apps[0]

page_sequence = [
    Donacion,
    Espera,
    Simulacion,
    ListaEspera,
    FinRonda,
    Resultados
]
