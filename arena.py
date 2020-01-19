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

    def compete(self, num_battles):
        for i in range(0, num_battles):
            if VERBOSE:
                print(f'{self} Battle {i+1}:')
            fighters = []
            for team in self.teams:
                name = f'{team.type_name}{random.randint(1,99)}'
                fighter = team.fighter_type(name)
                fighter.team = team
                fighters.append(fighter)
            arena = Arena(fighters)
            while arena.winner == None:
                arena.play_round()
            self.wins[arena.winner.team] += 1
            if VERBOSE:
                print(f'{arena.winner} wins battle {i+1}!')

        most_wins = max([self.wins[team] for team in self.teams])
        winning_teams = [team for team in self.teams if self.wins[team]==most_wins]
        if len(winning_teams)>1:
            if VERBOSE:
                print(f'{self} Tiebreaker Battle:')
            fighters = []
            for team in self.teams:
                name = f'{team.type_name}{random.randint(1,99)}'
                fighter = team.fighter_type(name)
                fighter.team = team
                fighters.append(fighter)
            arena = Arena(fighters)
            while arena.winner == None:
                arena.play_round()
            self.wins[arena.winner.team] += 1
            if VERBOSE:
                print(f'{arena.winner} wins the tiebreaker battle!')
            self.winner = arena.winner.team
        else:
            self.winner = fighters[0].team

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
            Team('Team A', ToughFighter),
            Team('Team B', Fighter),
            Team('Team C', ToughFighter),
            Team('Team D', Fighter)
        ]
        t = Tournament(teams)
        t.compete(1000)
        t.print_standings()


if __name__ == '__main__':
    Game().run(sys.argv)
