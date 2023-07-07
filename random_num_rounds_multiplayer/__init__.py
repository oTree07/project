from otree.api import *


doc = """
Random number of rounds for multiplayer (random stopping rule)
"""


class C(BaseConstants):
    NAME_IN_URL = 'random_num_rounds_multiplayer'
    PLAYERS_PER_GROUP = None
    # choose NUM_ROUNDS high enough that the chance of
    # maxing out is negligible
    NUM_ROUNDS = 50
    STOPPING_PROBABILITY = 0.2


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.participant.finished_rounds = False


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        import random

        if random.random() < C.STOPPING_PROBABILITY:
            print('ending game')
            for p in group.get_players():
                p.participant.finished_rounds = True

        # your usual after_all_players_arrive goes here...


class Results(Page):
    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.finished_rounds:
            return upcoming_apps[0]


page_sequence = [MyPage, ResultsWaitPage, Results]