from otree.api import *

doc = """
Multiplayer Organ Donation Game
"""

import random

class C(BaseConstants):
    NAME_IN_URL = 'organ_donation'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20
    CHANGE_COST = 0.75


class Group(BaseGroup):
    donations = models.IntegerField(initial=0)

class Player(BasePlayer):
    round_number = models.IntegerField(initial=0)
    is_donor = models.BooleanField(initial=False)
    scenario = models.CharField()
    organ_a_functional = models.BooleanField(initial=True)
    organ_b_functional = models.BooleanField(initial=True)
    on_waiting_list = models.BooleanField(initial=False)
    periods_on_list = models.IntegerField(initial=0)

    def update_organs(self):
        self.organ_a_functional = True
        self.organ_b_functional = True

    def join_waiting_list(self):
        self.on_waiting_list = True

    def leave_waiting_list(self):
        self.on_waiting_list = False
        self.periods_on_list = 0

    def increment_periods_on_list(self):
        self.periods_on_list += 1


class Subsession(BaseSubsession):
    pass

class Splash(Page):
    timeout_seconds = 15

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class WaitingTime(WaitPage):
    pass

class Donation(Page):
    timeout_seconds = 15
    form_model = 'player'
    form_fields = ['is_donor']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_donor

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number <= 10 and not timeout_happened:
            if player.is_donor:
                player.payoff -= C.CHANGE_COST

class Status(Page):
    timeout_seconds = 15

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        scenario = random.choices(['A', 'B', 'C'], [0.10, 0.20, 0.70])[0]
        player.scenario = scenario

        if scenario == 'A':
            player.organ_a_functional = False
        elif scenario == 'B':
            if player.organ_b_functional:
                player.organ_b_functional = False
                player.join_waiting_list()
                if player.periods_on_list == 5:
                    player.leave_waiting_list()
                elif group.donations > 0:
                    group.decrement_donations()
        else:
            player.update_organs()
            player.payoff += 3

    @staticmethod
    def is_displayed(player: Player):
        return not player.on_waiting_list

class WaitList(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.on_waiting_list:
            player.increment_periods_on_list()

    @staticmethod
    def is_displayed(player: Player):
        return player.on_waiting_list

class GameOver(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.organ_a_functional

page_sequence = [
    Splash,
    WaitingTime,
    Donation,
    Status,
    WaitList,
    GameOver
]
