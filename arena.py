#!/usr/bin/env python

VERSION = '0.1'
VERBOSE = False

import random
import sys

name_list = ['Adalee', 'Amos', 'Berit', 'Bergen', 'Cavery', 'Cullan', 'Disa',
    'Dawson', 'Edeline', 'Elias', 'Fallon', 'Fergus', 'Gemma', 'Garret',
    'Hazel', 'Heath', 'Idelle', 'Ira', 'Jillian', 'Jasper', 'Kaia', 'Keagan',
    'Lark', 'Landry', 'Morrin', 'Miles', 'Nella', 'Nixon', 'Odin', 'Ophelia',
    'Patia', 'Pearce', 'Quinevere', 'Qorbin', 'Rowen', 'Reaves', 'Sabel',
    'Soren', 'Taryn', 'Thatcher', 'Umina', 'Uri', 'Vika', 'Vance', 'Wila',
    'Walker', 'Xenia', 'Xander', 'Yates', 'Yumi', 'Zane', 'Zinia']

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
    def __init__(self, name):
        self.name = name
        self.max_health = roll(2,4)
        self.health = self.max_health
        self.weapon = None
        self.armor = None
        self.arena = None
        self.team = None

    def __repr__(self):
        return f'{self.name} ({self.health}/{self.max_health}) [{self.team}]'

    def take_turn(self):
        opponents = self.arena.fighters[:]
        opponents.remove(self)
        target = random.choice(opponents)
        self.attack(target)

    def attack(self, opponent):
        (dice, sides, plus) = weapon_list[self.weapon]
        damage = roll(dice, sides) + plus
        opponent.take_damage(damage, self)

    def take_damage(self, damage, attacker):
        protection = armor_list[self.armor]
        damage = max(0, damage-protection)

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

    def play_round(self):
        self.turn += 1
        if VERBOSE:
            print(f'{self}:')
        for f in self.fighters:
            f.take_turn()
        if len(self.fighters) == 1:
            self.winner = self.fighters[0]

class Team:
    def __init__(self, name, fighter_type, weapon, armor):
        self.name = name
        self.fighter_type = fighter_type
        self.type_name = fighter_type.__name__
        self.weapon = weapon
        self.armor = armor

    def __repr__(self):
        return f'{self.name} ({self.type_name}, {self.weapon}, {self.armor})'

    def add_fighter(self, fighter):
        fighter.team = self
        fighter.weapon = self.weapon
        fighter.armor = self.armor

class Tournament:
    def __init__(self, teams):
        self.teams = teams
        self.wins = {team:0 for team in teams}

    def __repr__(self):
        return f'Tournament {hex(hash(self))} {[team.type_name for team in self.teams]}'

    def fight_battle(self, title, teams):
        fighters = []
        for team in self.teams:
            name = random.choice(name_list)
            fighter = team.fighter_type(name)
            team.add_fighter(fighter)
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
            print(f'{self.winner} wins the tournament!')

    def print_standings(self):
        print('Final Standings:')
        for team in self.teams:
            print(f'  {team}: {self.wins[team]}')

class Game:
    def run(self, argv):
        print('Arena version ' + VERSION)

        teams = [
            Team('Flying Gryphons', Fighter, 'sword', 'chain mail'),
            Team('Mob Riot', ToughFighter, None, 'leather armor'),
            Team('Dungeon Explorers', Fighter, None, None),
            Team('Pointy Things', Fighter, 'dagger', 'leather armor'),
            Team('Bludgeoners', ToughFighter, 'mace', None)
        ]

        t = Tournament(teams)
        t.compete(1000)
        t.print_standings()

if __name__ == '__main__':
    Game().run(sys.argv)
