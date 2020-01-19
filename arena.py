#!/usr/bin/env python

VERSION = '0.1'
VERBOSE = False

import random
import sys

def roll(dice, sides):
    total = 0
    for _ in range(0, dice):
        total += random.randint(1, sides)
    return total

class Fighter:
    def __init__(self, name):
        self.name = name
        self.max_health = roll(2,4)
        self.health = self.max_health
        self.arena = None
        self.team = None

    def __repr__(self):
        return f'{self.name} ({self.health}/{self.max_health})'

    def take_turn(self):
        opponents = self.arena.fighters[:]
        opponents.remove(self)
        target = random.choice(opponents)
        self.attack(target)

    def attack(self, opponent):
        damage = roll(1,2)
        opponent.take_damage(damage, self)

    def take_damage(self, damage, attacker):
        if VERBOSE:
            print(f'  {attacker} attacks {self} for {damage} damage')
        self.health -= damage
        if(self.health < 1):
            self.die()

    def die(self):
        if VERBOSE:
            print(f'  {self} dies!')
        self.arena.fighters.remove(self)
        self.arena = None

class ToughFighter(Fighter):
    def __init__(self, name):
        super().__init__(name)
        self.max_health += roll(1, 8)
        self.health = self.max_health

class Arena:
    def __init__(self, fighters=[]):
        self.fighters = []
        self.winner = None
        self.turn = 0
        for f in fighters:
            self.add_fighter(f)

    def __repr__(self):
        return f'Arena {hex(hash(self))} ({len(self.fighters)} fighters, turn {self.turn})'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.arena = self

    # bug: Why didn't Eve attack?
    # Arena 0x7f6a7056535 (3 fighters, turn 3):
    # Alice (1/4) attacks Eve (2/4) for 1 damage
    # Bob (5/8) attacks Alice (1/4) for 2 damage
    # Alice (-1/4) dies!

    # Arena 0x7fa12f13fc5 (3 fighters, turn 3):
    #   Fighter4 (1/5) attacks Fighter28 (3/4) for 2 damage
    #   Fighter81 (4/8) attacks Fighter4 (1/5) for 1 damage
    #   Fighter4 (0/5) dies!
    # Arena 0x7fa12f13fc5 (2 fighters, turn 4):
    def play_round(self):
        self.turn += 1
        if VERBOSE:
            print(f'{self}:')
        for f in self.fighters:
            f.take_turn()
        if len(self.fighters) == 1:
            self.winner = self.fighters[0]

class Team:
    def __init__(self, name, fighter_type):
        self.name = name
        self.fighter_type = fighter_type
        self.type_name = fighter_type.__name__

    def __repr__(self):
        return f'Team {self.name} ({self.type_name})'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.team = self


class Tournament:
    def __init__(self, teams):
        self.teams = teams
        self.wins = {team:0 for team in teams}

    def __repr__(self):
        return f'Tournament {hex(hash(self))} {[team.type_name for team in self.teams]}'

    def fight_battle(self, title, teams):
        fighters = []
        for team in self.teams:
            name = f'{team.type_name}{random.randint(1,99)}'
            fighter = team.fighter_type(name)
            fighter.team = team
            fighters.append(fighter)
        if VERBOSE:
            print(f'{self} {title}:')
        arena = Arena(fighters)
        while arena.winner == None:
            arena.play_round()
        if VERBOSE:
            print(f'{arena.winner} wins {title}!')
        return arena.winner.team

    def compete(self, num_battles):
        for i in range(0, num_battles):
            winning_team = self.fight_battle(f'Battle {i+1}', self.teams)
            self.wins[winning_team] += 1

        most_wins = max([self.wins[team] for team in self.teams])
        winning_teams = [team for team in self.teams if self.wins[team]==most_wins]
        if len(winning_teams)>1:
            winning_team = self.fight_battle('Tiebreaker Battle', winning_teams)
            self.wins[winning_team] += 1
            self.winner = winning_team
        else:
            self.winner = winning_teams[0]

        if VERBOSE:
            print(f'{self.winner.name} wins the tournament!')

    def print_standings(self):
        print('Final Standings:')
        for team in self.teams:
            print(f'  {team.name} ({team.type_name}): {self.wins[team]}')


class Game:
    def run(self, argv):
        print('Arena version ' + VERSION)

        teams = [
            Team('Flying Gryphons', Fighter),
            Team('Mob Riot', ToughFighter),
            Team('Dungeon Explorers', Fighter),
        ]

        t = Tournament(teams)
        t.compete(2)
        t.print_standings()

if __name__ == '__main__':
    Game().run(sys.argv)
