# ai.py
from fighter import *
import random

class BaseAI:
    def take_turn(self, fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        enemies_in_range = [neighbor.fighter for neighbor in neighbors if neighbor.fighter and neighbor.fighter.faction != fighter.faction]

        if enemies_in_range:
            target = self.select_target(fighter, enemies_in_range)
            self.attack(fighter, target)
            return

        target = self.select_target(fighter)
        if target:
            self.attack(fighter, target)

    def move_towards(self, fighter, target_position):
        path = fighter.battle.map.astar(fighter.position, target_position)
        if path:
            next_position = path[1]  # The first position is the current position
            if not fighter.battle.map.is_position_occupied(next_position):
                fighter.move_to(next_position)
            else:
                print(f"{fighter.name} cannot move to {next_position}, position is occupied.")
        else:
            print(f"{fighter.name} cannot find a path to {target_position}.")

    def attack(self, fighter, target):
        distance = fighter.battle.map.calculate_distance(fighter.position, target.position)
        if fighter.weapon.range >= distance:
            fighter.attack(target)
        else:
            self.move_towards(fighter, target.position)

    def find_nearest_enemy(self, fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if not opponents:
            return None
        closest_enemy = min(opponents, key=lambda f: fighter.battle.map.calculate_distance(fighter.position, f.position))
        return closest_enemy

    def select_target(self, fighter, opponents=None):
        raise NotImplementedError("Subclasses must implement this method")

class RandomAttackAI(BaseAI):
    def select_target(self, fighter, opponents=None):
        if not opponents:
            opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            return random.choice(opponents)
        return None

class LowestHealthAI(BaseAI):
    def select_target(self, fighter, opponents=None):
        if not opponents:
            opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            return min(opponents, key=lambda x: x.health)
        return None

class GreatestThreatAI(BaseAI):
    def select_target(self, fighter, opponents=None):
        if not opponents:
            opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            return max(opponents, key=lambda x: self.calculate_threat(x))
        return None

    def calculate_threat(self, opponent):
        if opponent.weapon and opponent.weapon.name in weapon_list:
            dice, sides, addend, range = weapon_list[opponent.weapon.name]
            average_roll = dice * (1 + sides) / 2
            return average_roll + addend + opponent.damage_bonus
        return 0

class DefensiveAI(BaseAI):
    deadlock_threshold = 5  # Number of turns to wait before breaking deadlock
    deadlock_counter = 0

    def take_turn(self, fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        enemies_in_range = [neighbor.fighter for neighbor in neighbors if neighbor.fighter and neighbor.fighter.faction != fighter.faction]

        if enemies_in_range:
            target = self.select_target(fighter, enemies_in_range)
            self.attack(fighter, target)
            return

        if fighter.health < fighter.max_health / 4:
            DefensiveAI.deadlock_counter += 1
            if DefensiveAI.deadlock_counter >= DefensiveAI.deadlock_threshold:
                DefensiveAI.deadlock_counter = 0  # Reset counter and force attack
                GreatestThreatAI().take_turn(fighter)
            else:
                fighter.take_defensive_action()
        else:
            DefensiveAI.deadlock_counter = 0  # Reset counter if not in defensive action
            GreatestThreatAI().take_turn(fighter)

    def select_target(self, fighter, opponents=None):
        if not opponents:
            opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            return random.choice(opponents)
        return None
