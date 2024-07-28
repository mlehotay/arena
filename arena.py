# arena.py
import random
from ai import *
from fighter import Fighter
from map import Map

VERSION = '0.6'

class Battle:
    def __init__(self, title, roles, verbose=False, map_width=10, map_height=10, turn_limit=100):
        self.title = title
        self.verbose = verbose
        self.fighters = []
        self.winner = None
        self.turn = 0
        self.logs = []
        self.map = Map(map_width, map_height, 'grid8')
        self.turn_limit = turn_limit

        for role in roles:
            fighter = role['class'](role['name'], role['level'], role['ai'], role['faction'], role['weapon'], role['armor'], role['shield'])
            self.add_fighter(fighter)

    def __repr__(self):
        return f'{self.title} turn {self.turn}'

    def add_fighter(self, fighter):
        self.fighters.append(fighter)
        fighter.battle = self  # Ensure fighter knows which battle they are part of
        while True:
            x = random.randint(0, self.map.width - 1)
            y = random.randint(0, self.map.height - 1)
            position = self.map.get_position(x, y)
            if position and not position.fighter:  # Check if position is valid and unoccupied
                self.map.occupy_position(fighter, position)
                fighter.move_to(position)
                break

    def remove_fighter(self, fighter):
        self.fighters.remove(fighter)
        fighter.battle = None
        self.map.vacate_position(fighter)

    def move_fighter(self, fighter, new_position):
        self.map.move_fighter(fighter, new_position)

    def fight_battle(self):
        self.log(f'{self.title} fighters:')
        for fighter in self.fighters:
            self.log(fighter)
        while self.winner is None and self.turn < self.turn_limit:
            self.play_round()
        if self.winner:
            self.log(f'{self.winner} wins {self.title}!')
        else:
            self.log(f'{self.title} ends in a draw after {self.turn_limit} turns!')
        return self.winner

    def play_round(self):
        self.turn += 1
        self.log(f'{self}:')
        self.display_map()
        for fighter in sorted(self.fighters, key=lambda x: x.health, reverse=True):
            if self.winner:
                break
            fighter.take_turn()
            factions = set(f.faction for f in self.fighters if f.is_alive())
            if len(factions) == 1:
                self.winner = factions.pop()

    def log(self, message):
        if self.verbose:
            print(message)
        self.logs.append(message)

    def display_map(self):
        map_grid = [['.' for _ in range(self.map.width)] for _ in range(self.map.height)]
        for fighter in self.fighters:
            if fighter.is_alive():
                x, y = fighter.position.x, fighter.position.y
                if 0 <= x < self.map.width and 0 <= y < self.map.height:
                    map_grid[y][x] = fighter.name[0]
        map_display = '\n'.join([' '.join(row) for row in map_grid])
        self.log(map_display)

    def resolve_ranged_attack(self, attacker, target):
        distance = self.map.calculate_distance(attacker.position, target.position)
        if attacker.ranged_weapon and attacker.ranged_weapon.ammunition:
            if distance <= attacker.ranged_weapon.range:
                ammo = attacker.ranged_weapon.ammunition.pop()
                # Implement attack logic here, e.g., reduce target's health
                print(f"{attacker.name} hits {target.name} with {ammo.name} for {attacker.ranged_weapon.damage} damage")

    def resolve_throw(self, attacker, target):
        if attacker.wielded_weapon:
            attacker.throw_weapon(target)
            # Implement throw logic here, e.g., reduce target's health
            print(f"{attacker.name} throws {attacker.wielded_weapon.name} at {target.name} for {attacker.wielded_weapon.damage} damage")

    def resolve_turn(self):
        for fighter in self.fighters:
            fighter.update_buffs()

class Arena:
    def __init__(self, roles, iterations=1000, verbose=False):
        self.roles = roles
        self.iterations = iterations
        self.verbose = verbose
        self.factions = {role['faction'] for role in roles}
        self.wins = {faction: 0 for faction in self.factions}
        self.winner = None

    def simulate_battle(self):
        for i in range(self.iterations):
            winner = Battle(f'Battle {i + 1}', self.roles, self.verbose).fight_battle()
            if winner:
                self.wins[winner] += 1

    def print_probabilities(self):
        print('Estimated Probabilities of Victory:')
        for faction in sorted(self.factions):
            print(f'{faction}: {self.wins[faction] / self.iterations:.2%}')


#############################################################################
# start here

class Game:
    def run(self):
        print('Arena version ' + VERSION)

        roles = [
            {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI},
            {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI},
            {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI},
        ]

        battle = Arena(roles, iterations=1, verbose=True)
        battle.simulate_battle()
        battle.print_probabilities()

# Game().run()
