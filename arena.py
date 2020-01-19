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

class Tournament:
    def __init__(self, teams):
        self.teams = teams
        self.wins = {team:0 for team in teams}

    def __repr__(self):
        return f'Tournament {hex(hash(self))} {[team.__name__ for team in self.teams]}'

    def compete(self, num_battles):
        for i in range(0, num_battles):
            if VERBOSE:
                print(f'{self} Battle {i}:')
            fighters = []
            for team in self.teams:
                fighters.append(team(f'{team.__name__}{random.randint(1,99)}'))
            arena = Arena(fighters)
            while arena.winner == None:
                arena.play_round()
            self.wins[arena.winner.__class__] += 1
            if VERBOSE:
                print(f'{arena.winner} wins battle {i}!')

        most_wins = max([self.wins[team] for team in self.teams])
        champions = [team(f'{team.__name__}{random.randint(1,99)}') for team in self.teams if self.wins[team]==most_wins]
        if len(champions)>1:
            if VERBOSE:
                print(f'{self} Tiebreaker Battle:')
            arena = Arena(champions)
            while arena.winner == None:
                arena.play_round()
            self.wins[arena.winner.__class__] += 1
            if VERBOSE:
                print(f'{arena.winner} wins the tiebreaker battle!')
            self.winner = arena.winner.__class__
        else:
            self.winner = champions[0].__class__

        if VERBOSE:
            print(f'Team {self.winner.__name__} wins the tournament!')

    def print_standings(self):
        print('Final Standings:')
        for team in self.teams:
            print(f'  {team.__name__}: {self.wins[team]}')


class Game:
    def run(self, argv):
        print('Arena version ' + VERSION)

        #t = Tournament([ Fighter, Fighter, ToughFighter ])
        t = Tournament([ Fighter, ToughFighter ])
        t.compete(1000)
        t.print_standings()


if __name__ == '__main__':
    Game().run(sys.argv)
