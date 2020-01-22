#!/usr/bin/env python

VERSION = '0.2'

import random
import sys

weapon_list = {
    None: (1,2,0),    # 1d2
    'sword': (1,8,0), # 1d8
    'mace': (1,6,1),  # 1d6+1
    'dagger': (1,4,0) # 1d4
}

armor_list = {
    None: 0,
    'leather armor': 1,
    'chain mail': 3,
    'plate mail': 5
}

def roll(dice, sides):
    total = 0
    for _ in range(0, dice):
        total += random.randint(1, sides)
    return total

class Fighter:
    def __init__(self, name, faction, weapon, armor):
        self.name = name
        self.max_health = roll(2,4)
        self.health = self.max_health
        self.faction = faction
        self.weapon = weapon
        self.armor = armor
        self.battle = None

    def __repr__(self):
        return f'{self.name} ({self.health}/{self.max_health}) [{self.faction}, {self.__class__.__name__}, {self.weapon}, {self.armor}]'

    def take_turn(self):
        opponents = [f for f in self.battle.fighters if f.faction!=self.faction]
        if(opponents != []):
            target = random.choice(opponents)
            self.attack(target)

    def attack(self, opponent):
        (dice, sides, plus) = weapon_list[self.weapon]
        damage = roll(dice, sides) + plus
        opponent.take_damage(damage, self)

    def take_damage(self, damage, attacker):
        protection = armor_list[self.armor]
        damage = max(0, damage-protection)

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

class ToughFighter(Fighter):
    def __init__(self, name, faction, weapon, armor):
        super().__init__(name, faction, weapon, armor)
        self.max_health += roll(1, 10)
        self.health = self.max_health

class Battle:
    def __init__(self, title, roles, verbose):
        self.title = title
        self.verbose = verbose
        self.fighters = []
        self.winner = None
        self.turn = 0
        for role in roles:
            fighter = role['class'](role['name'], role['faction'], role['weapon'], role['armor'])
            self.add_fighter(fighter)

    def __repr__(self):
        return f'{self.title}, Turn {self.turn}'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.battle = self

    def fight_battle(self):
        if self.verbose:
            print(f'{self.title} fighters:')
            for fighter in self.fighters:
                print(f'  {fighter}')
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
            print(f'  {faction}: {self.wins[faction]/self.iterations}')

class Game:
    def run(self, argv):
        print('Arena version ' + VERSION)

        roles = [
            {'name': 'Alice', 'faction': 'Order',
                'class':Fighter, 'weapon':'sword', 'armor':'chain mail'},
            {'name': 'Bob', 'faction': 'Order',
                'class':ToughFighter, 'weapon':None, 'armor':'leather armor'},
            {'name': 'Eve', 'faction': 'Chaos',
                'class':Fighter, 'weapon':'dagger', 'armor':None},
            {'name': 'Mallory', 'faction': 'Chaos',
                'class':ToughFighter, 'weapon':'mace', 'armor':'leather armor'}
        ]

        battle = Arena(roles, iterations=2, verbose=True)
        battle.simulate_battle()
        battle.print_probabilities()

if __name__ == '__main__':
    Game().run(sys.argv)
