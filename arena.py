#!/usr/bin/env python

VERSION = '0.1'

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
        self.arena = None
        self.heal()

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
        print(f'  {attacker} attacks {self} for {damage} damage')
        self.health -= damage
        if(self.health < 1):
            self.die()

    def heal(self):
        self.health = self.max_health

    def die(self):
        print(f'  {self} dies!')
        self.arena.fighters.remove(self)
        self.arena = None


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
        fighter.heal()
        print(f'{fighter} enters the arena')

    # bug: Why didn't Eve attack?
    # Arena 0x7f6a7056535 (3 fighters, turn 3):
    # Alice (1/4) attacks Eve (2/4) for 1 damage
    # Bob (5/8) attacks Alice (1/4) for 2 damage
    # Alice (-1/4) dies!
    def play_round(self):
        self.turn += 1
        print(f'{self}:')
        for f in self.fighters:
            f.take_turn()
        self.select_winner()

    def is_battle(self):
        return self.winner == None

    def select_winner(self):
        if len(self.fighters) > 1:
            self.winner = None
        else:
            self.winner = self.fighters[0]

class Tournament:
    def __init__(self, fighters):
        self.fighters = fighters
        self.wins = {f:0 for f in fighters}

    def __repr__(self):
        return f'Tournament {hex(hash(self))} ({len(self.fighters)} fighters)'

    def compete(self, num_battles):
        for i in range(0, num_battles):
            print(f'{self} Battle {i}:')
            arena = Arena(self.fighters)
            while arena.is_battle():
                arena.play_round()
            self.wins[arena.winner] += 1
            print(f'{arena.winner} wins battle {i}!')

    def print_standings(self):
        print('Final Standings:')
        for f in self.fighters:
            print(f'  {f.name}: {self.wins[f]}')


class Game:
    def run(self, argv):
        print('Welcome to Arena version ' + VERSION)

        contestants = [
            Fighter('Alice'),
            Fighter('Bob'),
            Fighter('Eve')
        ]

        t = Tournament(contestants)
        t.compete(3);
        t.print_standings()


if __name__ == '__main__':
    Game().run(sys.argv)
