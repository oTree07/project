import random
from otree.api import *

doc = """
Juego de donación de órganos
"""

# Definición de variables globales
INICIO = True
TURNO = 1
RONDA = 1

class C(BaseConstants):
    NAME_IN_URL = 'organ_donation'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20 # Número de rondas máximas
    CHANGE_COST = 0.75

# Subclases del juego
class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    ronda = models.IntegerField(initial=1)
    turno = models.IntegerField(initial=1)
    donaciones = models.IntegerField(initial=0)

class Player(BasePlayer):
    caso = models.CharField(initial="")
    turnos_en_espera = models.IntegerField(initial=0)
    organo_a_funcional = models.BooleanField(initial=True)
    organo_b_funcional = models.BooleanField(initial=True)
    es_donante = models.BooleanField(initial=False)
    donacion_previa = models.BooleanField(initial=False)
    en_lista_espera = models.BooleanField(initial=False)
    fuera_de_juego = models.BooleanField(initial=False)
    fin_turno = models.BooleanField(initial=False)
    pago = models.FloatField(initial=0.0)

# FUNCIONES

# Función para imprimir información del jugador
def log(p: Player, fx):
    g = p.group
    print("Player {}: {} | Donante: {} | Donaciones: {} | Donacion Previa: {} | Caso: {} | Organo A: {} | Organo B: {} | Lista de Espera: {} | Turnos en lista: {} | Fin Turno: {} | Pago: {}".format(
        p.id_in_group, fx, p.es_donante, g.donaciones, p.donacion_previa, p.caso, p.organo_a_funcional, p.organo_b_funcional, p.en_lista_espera, p.turnos_en_espera, p.fuera_de_juego, p.pago))

# Función para resetear los campos del jugador
def ResetearJugador(p: Player):
    subsession = p.subsession
    g = p.group

    for p in subsession.get_players():
        p.caso = ""
        p.turnos_en_espera = 0
        p.organo_a_funcional = True
        p.organo_b_funcional = True
        p.es_donante = False
        p.donacion_previa = False
        p.en_lista_espera = False
        p.fuera_de_juego = False
        p.pago = 0.0
    
    g.donaciones = 0 
    g.turno = 1
    g.ronda = 1

# Función para guardar el estado del jugador y el grupo
def GuardarJugador(p: Player):
    global INICIO, TURNO, RONDA
    subsession = p.subsession
    g = p.group

    try:
        if TURNO > 1:
            for p in subsession.get_players():
                anterior = p.in_round(p.round_number - 1)
                g.donaciones = anterior.group.donaciones
                g.turno = anterior.group.turno
                g.ronda = anterior.group.ronda
                p.caso = anterior.caso
                p.turnos_en_espera = anterior.turnos_en_espera
                p.organo_a_funcional = anterior.organo_a_funcional
                p.organo_b_funcional = anterior.organo_b_funcional
                p.es_donante = anterior.es_donante
                p.donacion_previa = anterior.donacion_previa
                p.en_lista_espera = anterior.en_lista_espera
                p.fuera_de_juego = anterior.fuera_de_juego
                p.pago = anterior.pago
    except:
        INICIO = True
        TURNO = 1
        RONDA = 1

# Función para verificar si el juego está en su etapa de inicio
def Inicio():
    global INICIO
    return INICIO

# Función para obtener el número de ronda actual
def Ronda():
    global RONDA
    return RONDA

# Función para evaluar el estado del juego y tomar decisiones
def Evaluar(p: Player):
    global INICIO, TURNO, RONDA
    g = p.group

    # Verificar si todos los jugadores han finalizado su turno
    if all(not p.fin_turno for p in g.subsession.get_players()):
        if not INICIO:
            g.turno += 1
            TURNO += 1

        INICIO = False
        p.fin_turno = True

    # Verificar si todos los jugadores están fuera del juego
    if all(p.fuera_de_juego for p in g.subsession.get_players()):
        ResetearJugador(p)
        g.ronda += 1
        INICIO = True
        TURNO = 1
        RONDA += 1

# Función para procesar la elección de donar del jugador
def ElegirDonar(p: Player):
    global RONDA, INICIO
    INICIO = False

    if p.es_donante:
        if RONDA <= 10:
            p.pago -= C.CHANGE_COST # Si es donante y la ronda es menor o igual a 10, se resta el costo del cambio de p.pago
    
    log(p, "ElegirDonar")

# Función para simular un caso para el jugador
def SimularCaso(p: Player):
    g = p.group
    caso = random.choices(['A', 'B', 'C'], [0.10, 0.20, 0.70])[0]
    p.caso = caso

    # Caso A: El órgano A no es funcional
    if caso == 'A':
        p.organo_a_funcional = False
        p.fuera_de_juego = True  # El jugador queda fuera del juego
        if p.es_donante:
            g.donaciones += 1  # Si el jugador es donante, se registra una donación en el grupo

    # Caso B: El órgano B no es funcional
    elif caso == 'B':
        if p.donacion_previa:
            p.fuera_de_juego = True  # Si el jugador ya realizó una donación previa, queda fuera del juego
        else:
            p.organo_b_funcional = False
            p.en_lista_espera = True  # El jugador entra en la lista de espera

    # Caso C: Ambos órganos son funcionales
    else:
        #p.organo_a_funcional = True
        #p.organo_b_funcional = True
        p.pago += 3.0  # Se incrementa el pago del jugador en 3.0 unidades


    
    log(p, "SimularCaso")

# Función para evaluar la lista de espera del jugador
def EvaluarLista(p: Player):
    g = p.group

    # Verificar si el grupo tiene donaciones disponibles
    if g.donaciones > 0:
        g.donaciones -= 1  # Decrementar el contador de donaciones del grupo
        p.en_lista_espera = False  # El jugador ya no está en lista de espera
        p.donacion_previa = True  # Indicar que el jugador ha realizado una donación previa
        p.turnos_en_espera = 0  # Reiniciar el contador de turnos en espera

    if p.turnos_en_espera >= 5:
        p.fuera_de_juego = True  # El jugador está fuera del juego si ha estado en espera durante 5 turnos o más
    
    p.turnos_en_espera += 1  # Incrementar el contador de turnos en espera del jugador


    log(p, "EvaluarLista")

# PÁGINAS

class Donacion(Page):
    timeout_seconds = 15
    form_model = 'player'
    form_fields = ['es_donante']

    @staticmethod
    def is_displayed(p: Player):
        if not Inicio():
            GuardarJugador(p)

        return Inicio()
    
    @staticmethod
    def vars_for_template(p: Player):
        image_data = {
        'imagen1': 2,  # El número indica hasta que ronda se mostrá como máximo
        'imagen2': 4,  # Modificar de acuerdo a las imagenes de la carpeta _static/images y según rondas
        }

        for imagen, ronda in image_data.items():
            if Ronda() <= ronda:
                image = 'images/{}.png'.format(imagen)
                break
        
        return dict(
            image_path = image
        )

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

class FinTurno(WaitPage):
    template_name = 'orgams/FinTurno.html'

    @staticmethod
    def is_displayed(p: Player):
        return p.fuera_de_juego

class FinRonda(Page):
    @staticmethod
    def is_displayed(p: Player):
        Evaluar(p)
        return Ronda() == 4 # Aquí colocar C.NUM_ROUNDS sino se están haciendo pruebas

    @staticmethod
    def app_after_this_page(p: Player, upcoming_apps):
        return upcoming_apps[0]

page_sequence = [
    Donacion,
    Espera,
    Simulacion,
    ListaEspera,
    FinTurno,
    FinRonda,
    Espera
]
