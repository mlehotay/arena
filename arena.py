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
        print(f'{attacker} attacks {self} for {damage} damage')
        self.health -= damage
        if(self.health < 1):
            self.die()

    def die(self):
        print(f'{self} dies!')
        self.arena.fighters.remove(self)
        self.arena = None

class Arena:
    def __init__(self):
        self.fighters = []
        self.turn = 0
        self.winner = None

    def __repr__(self):
        return f'Arena v{VERSION} ({len(self.fighters)} fighters, turn {self.turn})'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.arena = self
        print(f'{fighter} enters the arena')

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

class Game:
    def run(self, argv):
        print('Welcome to Arena version ' + VERSION)

        arena = Arena()
        arena.add_fighter(Fighter('Alice'))
        arena.add_fighter(Fighter('Bob'))
        arena.add_fighter(Fighter('Eve'))

        while arena.is_battle():
            arena.play_round()

        print(f'{arena.winner} is the winner!')
        print('Game Over')

if __name__ == '__main__':
    Game().run(sys.argv)
