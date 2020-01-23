#!/usr/bin/env python

VERSION = '0.2'

import random
import sys

weapon_list = {
    None: (1,2,0),  # 1d2
    'axe': (1,6,0), # 1d6
    'battle axe': (1,8,0), # 1d8
    'club': (1,6,0),
    'dagger': (1,4,0),
    'flail': (1,6,1), # 1d6+1
    'hammer': (1,4,1),
    'mace': (1,6,1),
    'morning star': (2,4,0), # 2d4
    'scimitar': (1,8,0),
    'spear': (1,6,0),
    'quarterstaff': (1,6,0),
    'broad sword': (2,4,0),
    'long sword': (1,8,0),
    'short sword': (1,6,0),
    'trident': (1,6,1),
    'two-handed sword': (1,10,0)
}

armor_list = {
    None: 0,
    'shield': 1,
    'padded armor': 2,
    'leather armor': 2,
    'studded leather': 3,
    'ring mail': 3,
    'scale mail': 4,
    'chain mail': 5,
    'splint mail': 6,
    'banded mail': 6,
    'plate mail': 7
}

def roll(dice, sides):
    total = 0
    for _ in range(0, dice):
        total += random.randint(1, sides)
    return total

class Fighter:
    def __init__(self, name, level, faction, weapon, armor):
        self.name = name
        self.level = level
        self.max_health = sum(roll(1,10) for _ in range(0,level))
        self.health = self.max_health
        self.faction = faction
        self.weapon = weapon
        self.armor = armor
        self.armor_class = 10 - armor_list[self.armor]
        self.battle = None

    def __repr__(self):
        return f'{self.name} ({self.health}/{self.max_health}) [Level {self.level} {self.__class__.__name__}, {self.weapon}, {self.armor}, {self.faction}]'

    def take_turn(self):
        opponents = [f for f in self.battle.fighters if f.faction!=self.faction]
        if(opponents != []):
            target = random.choice(opponents)
            self.attack(target)

    def attack(self, opponent):
        if (roll(1,20) >= (22 - opponent.armor_class - self.level)):
            (dice, sides, plus) = weapon_list[self.weapon]
            damage = roll(dice, sides) + plus
            opponent.take_damage(damage, self)
        elif(self.battle.verbose):
            print(f'  {self.name} swings at {opponent.name} and misses')

    def take_damage(self, damage, attacker):
        if self.battle.verbose:
            print(f'  {attacker.name} attacks {self.name} for {damage} damage')
        self.health -= damage
        if(self.health < 1):
            self.die()

    def die(self):
        if self.battle.verbose:
            print(f'  {self.name} dies!')
        self.battle.fighters.remove(self)
        self.battle = None

class Battle:
    def __init__(self, title, roles, verbose):
        self.title = title
        self.verbose = verbose
        self.fighters = []
        self.winner = None
        self.turn = 0
        for role in roles:
            fighter = role['class'](role['name'], role['level'], role['faction'], role['weapon'], role['armor'])
            self.add_fighter(fighter)

    def __repr__(self):
        return f'{self.title} turn {self.turn}'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.battle = self

    def fight_battle(self):
        if self.verbose:
            print(f'{self.title} fighters:')
            for fighter in self.fighters:
                print(fighter)
        while self.winner == None:
            self.play_round()
        if self.verbose:
            print(f'{self.winner} wins {self.title}!')
        return self.winner

    def play_round(self):
        self.turn += 1
        if self.verbose:
            print(f'{self}:')
        for f in self.fighters:
            f.take_turn()
        if len({f.faction for f in self.fighters}) == 1:
            self.winner = self.fighters[0].faction

class Arena:
    def __init__(self, roles, iterations=1000, verbose=False):
        self.roles = roles
        self.iterations = iterations
        self.verbose = verbose
        self.factions = {role['faction'] for role in roles}
        self.wins = {faction:0 for faction in self.factions}
        self.winner = None

    def simulate_battle(self):
        for i in range(0, self.iterations):
            winner = Battle(f'Battle {i+1}', self.roles, self.verbose).fight_battle()
            self.wins[winner] += 1

    def print_probabilities(self):
        print('Estimated Probabilities of Victory:')
        for faction in self.factions:
            print(f'{faction}: {self.wins[faction]/self.iterations}')

class Game:
    def run(self, argv):
        print('Arena version ' + VERSION)

        roles = [
            {'name': 'Alice', 'faction': 'Order', 'level': 1,
                'class':Fighter, 'weapon':'long sword', 'armor':'chain mail'},
            {'name': 'Bob', 'faction': 'Order', 'level': 2,
                'class':Fighter, 'weapon':None, 'armor':'leather armor'},
            {'name': 'Eve', 'faction': 'Chaos', 'level': 1,
                'class':Fighter, 'weapon':'flail', 'armor':'shield'},
            {'name': 'Mallory', 'faction': 'Chaos', 'level': 2,
                'class':Fighter, 'weapon':'mace', 'armor':'leather armor'}
        ]

        battle = Arena(roles, iterations=1000, verbose=False)
        battle.simulate_battle()
        battle.print_probabilities()

if __name__ == '__main__':
    Game().run(sys.argv)
