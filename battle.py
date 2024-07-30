# battle.py
import random
from ai import *
from fighter import Fighter
from map import Map

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
                break

    def remove_fighter(self, fighter):
        self.fighters.remove(fighter)
        fighter.battle = None
        self.map.vacate_position(fighter.position)

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
        if self.map.refresh_needed:
            map_grid = [['.' for _ in range(self.map.width)] for _ in range(self.map.height)]
            for fighter in self.fighters:
                if fighter.is_alive():
                    x, y = fighter.position.x, fighter.position.y
                    if 0 <= x < self.map.width and 0 <= y < self.map.height:
                        map_grid[y][x] = fighter.name[0]
            map_display = '\n'.join([' '.join(row) for row in map_grid])
            self.log(map_display)
            self.map.refresh_needed = False
