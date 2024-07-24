# ai.py
from fighter import *

class AI:
    @staticmethod
    def take_turn(fighter):
        raise NotImplementedError

class RandomAttackAI(AI):
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = random.choice(opponents)
            fighter.attack(target)

class LowestHealthAI(AI):
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = min(opponents, key=lambda x: x.health)
            fighter.attack(target)

class GreatestThreatAI(AI):
    @staticmethod
    def take_turn(fighter):
        opponents = [f for f in fighter.battle.fighters if f.faction != fighter.faction]
        if opponents:
            target = max(opponents, key=lambda x: GreatestThreatAI.calculate_threat(x))
            fighter.attack(target)

    @staticmethod
    def calculate_threat(opponent):
        if opponent.weapon in weapon_list:
            dice, sides, addend = weapon_list[opponent.weapon]
            average_roll = dice * (1 + sides) / 2
            return average_roll + addend + opponent.damage_bonus
        return 0

class DefensiveAI(AI):
    deadlock_threshold = 5  # Number of turns to wait before breaking deadlock
    deadlock_counter = 0

    @staticmethod
    def take_turn(fighter):
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

class RangedAttackAI:
    @staticmethod
    def take_turn(fighter):
        # Attempt to attack if an enemy is in range, otherwise move closer
        target = random.choice([f for f in fighter.battle.fighters if f.faction != fighter.faction])
        distance = calculate_distance(fighter.position, target.position)
        if distance <= fighter.weapon.range:
            fighter.attack(target)
        else:
            # Implement movement logic towards the target
            pass
