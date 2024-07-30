# ai.py
from fighter import *
import random

class BaseAI:
    @staticmethod
    def take_turn(fighter):
        raise NotImplementedError

    @staticmethod
    def move_towards(fighter, target_position):
        path = fighter.battle.map.astar(fighter.position, target_position)
        if path:
            next_position = path[1]  # The first position is the current position
            if not fighter.battle.map.is_position_occupied(next_position):
                fighter.move_to(next_position)
            else:
                print(f"{fighter.name} cannot move to {next_position}, position is occupied.")
        else:
            print(f"{fighter.name} cannot find a path to {target_position}.")

    @staticmethod
    def attack(fighter, target):
        distance = fighter.battle.map.calculate_distance(fighter.position, target.position)
        if distance <= 1:
            fighter.attack(target)
        elif fighter.ranged_weapon and distance <= fighter.ranged_weapon.range:
            fighter.attack_with_ranged_weapon(target)
        else:
            BaseAI.move_towards(fighter, target.position)

    @staticmethod
    def find_nearest_enemy(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if not opponents:
            return None
        closest_enemy = min(opponents, key=lambda f: fighter.battle.map.calculate_distance(fighter.position, f.position))
        return closest_enemy

class RandomAttackAI(BaseAI):
    @staticmethod
    def take_turn(fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        for neighbor in neighbors:
            if neighbor.fighter and neighbor.fighter.faction != fighter.faction:
                BaseAI.attack(fighter, neighbor.fighter)
                return

        target = BaseAI.find_nearest_enemy(fighter)
        if target:
            BaseAI.attack(fighter, target)

class LowestHealthAI(BaseAI):
    @staticmethod
    def take_turn(fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        for neighbor in neighbors:
            if neighbor.fighter and neighbor.fighter.faction != fighter.faction:
                BaseAI.attack(fighter, neighbor.fighter)
                return

        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = min(opponents, key=lambda x: x.health)
            BaseAI.attack(fighter, target)

class GreatestThreatAI(BaseAI):
    @staticmethod
    def take_turn(fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        for neighbor in neighbors:
            if neighbor.fighter and neighbor.fighter.faction != fighter.faction:
                BaseAI.attack(fighter, neighbor.fighter)
                return

        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = max(opponents, key=lambda x: GreatestThreatAI.calculate_threat(x))
            BaseAI.attack(fighter, target)

    @staticmethod
    def calculate_threat(opponent):
        if opponent.weapon in weapon_list:
            dice, sides, addend = weapon_list[opponent.weapon]
            average_roll = dice * (1 + sides) / 2
            return average_roll + addend + opponent.damage_bonus
        return 0

class DefensiveAI(BaseAI):
    deadlock_threshold = 5  # Number of turns to wait before breaking deadlock
    deadlock_counter = 0

    @staticmethod
    def take_turn(fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        for neighbor in neighbors:
            if neighbor.fighter and neighbor.fighter.faction != fighter.faction:
                BaseAI.attack(fighter, neighbor.fighter)
                return

        if fighter.health < fighter.max_health / 4:
            DefensiveAI.deadlock_counter += 1
            if DefensiveAI.deadlock_counter >= DefensiveAI.deadlock_threshold:
                DefensiveAI.deadlock_counter = 0  # Reset counter and force attack
                GreatestThreatAI.take_turn(fighter)
            else:
                fighter.take_defensive_action()
        else:
            DefensiveAI.deadlock_counter = 0  # Reset counter if not in defensive action
            GreatestThreatAI.take_turn(fighter)

class RangedAttackAI(BaseAI):
    @staticmethod
    def take_turn(fighter):
        neighbors = fighter.battle.map.get_neighbors(fighter.position)
        for neighbor in neighbors:
            if neighbor.fighter and neighbor.fighter.faction != fighter.faction:
                BaseAI.attack(fighter, neighbor.fighter)
                return

        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = random.choice(opponents)
            BaseAI.attack(fighter, target)
