# test_ai.py
import unittest
import random
from ai import RandomAttackAI, LowestHealthAI, GreatestThreatAI, DefensiveAI, RangedAttackAI
from arena import Battle, Arena
from fighter import Fighter
from map import Map, Position

test_roles = [
    {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
    {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': GreatestThreatAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
    {'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'ai': LowestHealthAI, 'weapon': 'flail', 'armor': 'padded armor', 'shield': 'large shield'},
    {'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'morning star', 'armor': 'banded mail', 'shield': None},
    {'name': 'Carol', 'faction': 'Order', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'spear', 'armor': 'leather armor', 'shield': 'small shield'},
    {'name': 'Dave', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'quarterstaff', 'armor': 'ring mail', 'shield': None},
]

class TestAI(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('Test Battle', test_roles, verbose=False)

    def test_random_attack_ai(self):
        # randomly select a RandomAttackAI fighter for testing
        fighters_with_random_attack_ai = [fighter for fighter in self.battle.fighters if fighter.ai == RandomAttackAI]
        self.assertGreater(len(fighters_with_random_attack_ai), 0, "No fighters with RandomAttackAI found")
        test_fighter = random.choice(fighters_with_random_attack_ai)

        # Take multiple turns to ensure the fighter targets multiple opponents
        targeted_opponents = set()
        for _ in range(10):  # Number of turns to check randomness
            self.battle.logs.clear()
            test_fighter.take_turn()
            for log in self.battle.logs:
                if 'attacks' in log or 'misses' in log:
                    attacker_name = log.split()[0]
                    if attacker_name == test_fighter.name:
                        target = log.split()[2]
                        targeted_opponents.add(target)

        # Check that multiple opponents were targeted
        self.assertGreater(len(targeted_opponents), 1, f"{test_fighter.name} did not target multiple opponents")

    def test_random_attack_ai_movement(self):
        # Randomly select a RandomAttackAI fighter for testing
        fighters_with_random_attack_ai = [fighter for fighter in self.battle.fighters if fighter.ai == RandomAttackAI]
        self.assertGreater(len(fighters_with_random_attack_ai), 0, "No fighters with RandomAttackAI found")
        test_fighter = random.choice(fighters_with_random_attack_ai)

        # Take multiple turns to ensure the fighter moves if needed
        moved = False
        for _ in range(10):  # Number of turns to check movement
            self.battle.logs.clear()
            test_fighter.take_turn()
            for log in self.battle.logs:
                if 'moves towards' in log:
                    moved = True
                    break
            if moved:
                break

        self.assertTrue(moved, f"{test_fighter.name} did not move towards an opponent when necessary")

    def test_lowest_health_attack_ai(self):
        # randomly select a LowestHealthAI fighter for testing
        fighters_with_lowest_health_ai = [fighter for fighter in self.battle.fighters if fighter.ai == LowestHealthAI]
        self.assertGreater(len(fighters_with_lowest_health_ai), 0, "No fighters with LowestHealthAI found")
        test_fighter = random.choice(fighters_with_lowest_health_ai)

        # Determine opponents with the lowest health
        min_health = min(fighter.health for fighter in self.battle.fighters if fighter.faction != test_fighter.faction)
        lowest_health_fighters = [fighter.name for fighter in self.battle.fighters if fighter.health == min_health and fighter.faction != test_fighter.faction]

        # Have the fighter take their turn
        test_fighter.take_turn()

        # verify the fighter's target is in lowest_health_fighters
        attacked = False
        for log in self.battle.logs:
            if 'attacks' in log or 'misses' in log:
                attacker_name = log.split()[0]
                if attacker_name == test_fighter.name:
                    target = log.split()[2]
                    self.assertIn(target, lowest_health_fighters, f"{test_fighter.name} did not target one of the lowest health opponents")
                    attacked = True

        self.assertTrue(attacked, f"{test_fighter.name} did not perform any attacks or misses")

    def test_lowest_health_ai_movement(self):
        # Randomly select a LowestHealthAI fighter for testing
        fighters_with_lowest_health_ai = [fighter for fighter in self.battle.fighters if fighter.ai == LowestHealthAI]
        self.assertGreater(len(fighters_with_lowest_health_ai), 0, "No fighters with LowestHealthAI found")
        test_fighter = random.choice(fighters_with_lowest_health_ai)

        # Determine opponents with the lowest health
        min_health = min(fighter.health for fighter in self.battle.fighters if fighter.faction != test_fighter.faction)
        lowest_health_fighters = [fighter for fighter in self.battle.fighters if fighter.health == min_health and fighter.faction != test_fighter.faction]

        # Simulate multiple turns to check for movement
        moved_to_target = False
        for _ in range(10):
            self.battle.logs.clear()
            test_fighter.take_turn()
            for log in self.battle.logs:
                if 'moves towards' in log:
                    target_name = log.split()[2]
                    if target_name in [fighter.name for fighter in lowest_health_fighters]:
                        moved_to_target = True
                        break
            if moved_to_target:
                break

        self.assertTrue(moved_to_target, f"{test_fighter.name} did not move towards a lowest health opponent when necessary")

    def test_greatest_threat_ai(self):
        # randomly select a GreatestThreatAI fighter for testing
        fighters_with_greatest_threat_ai = [fighter for fighter in self.battle.fighters if fighter.ai == GreatestThreatAI]
        self.assertGreater(len(fighters_with_greatest_threat_ai), 0, "No fighters with GreatestThreatAI found")
        test_fighter = random.choice(fighters_with_greatest_threat_ai)

        # Determine opponents with the greatest threat
        opponents = [fighter for fighter in self.battle.fighters if fighter.faction != test_fighter.faction]
        max_threat = max(GreatestThreatAI.calculate_threat(opponent) for opponent in opponents)
        greatest_threat_fighters = [fighter.name for fighter in opponents if GreatestThreatAI.calculate_threat(fighter) == max_threat]

        # Have the fighter take their turn
        test_fighter.take_turn()

        # verify the fighter's target is in greatest_threat_fighters
        attacked = False
        for log in self.battle.logs:
            if 'attacks' in log or 'misses' in log:
                attacker_name = log.split()[0]
                if attacker_name == test_fighter.name:
                    target = log.split()[2]
                    self.assertIn(target, greatest_threat_fighters, f"{test_fighter.name} did not target one of the greatest threat opponents")
                    attacked = True

        self.assertTrue(attacked, f"{test_fighter.name} did not perform any attacks or misses")

    def test_greatest_threat_ai_movement(self):
        # Randomly select a GreatestThreatAI fighter for testing
        fighters_with_greatest_threat_ai = [fighter for fighter in self.battle.fighters if fighter.ai == GreatestThreatAI]
        self.assertGreater(len(fighters_with_greatest_threat_ai), 0, "No fighters with GreatestThreatAI found")
        test_fighter = random.choice(fighters_with_greatest_threat_ai)

        # Determine the opponent with the greatest threat
        opponents = [fighter for fighter in self.battle.fighters if fighter.faction != test_fighter.faction]
        max_threat = max(GreatestThreatAI.calculate_threat(opponent) for opponent in opponents)
        greatest_threat_fighters = [fighter for fighter in opponents if GreatestThreatAI.calculate_threat(fighter) == max_threat]

        # Simulate multiple turns to check for movement
        moved_to_target = False
        for _ in range(10):
            self.battle.logs.clear()
            test_fighter.take_turn()
            for log in self.battle.logs:
                if 'moves towards' in log:
                    target_name = log.split()[2]
                    if target_name in [fighter.name for fighter in greatest_threat_fighters]:
                        moved_to_target = True
                        break
            if moved_to_target:
                break

        self.assertTrue(moved_to_target, f"{test_fighter.name} did not move towards the greatest threat when necessary")

    def test_ai_map_boundaries(self):
        # Ensure that AI does not move outside the map
        for ai_class in [RandomAttackAI, LowestHealthAI, GreatestThreatAI, DefensiveAI]:
            fighters_with_ai = [fighter for fighter in self.battle.fighters if fighter.ai == ai_class]
            for fighter in fighters_with_ai:
                original_position = fighter.position
                for _ in range(10):  # Number of turns to test
                    self.battle.logs.clear()
                    fighter.take_turn()
                    # Assuming you have a method to check if the position is within map bounds
                    self.assertTrue(self.battle.map.is_valid_position(fighter.position), f"{fighter.name} moved out of bounds")
                    if 'moves towards' in [log for log in self.battle.logs]:
                        # Check that movements are valid
                        self.assertTrue(self.battle.map.is_valid_position(fighter.position), f"{fighter.name} moved out of bounds during movement")

class TestDefensiveAI(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('Test Battle', test_roles, verbose=False)

    def test_defensive_ai_low_health(self):
        # Set the DefensiveAI fighter's health to low
        defender = next(fighter for fighter in self.battle.fighters if fighter.ai == DefensiveAI)
        defender.health = defender.max_health / 4 - 1  # Trigger defensive behavior

        # Clear logs and take turn
        self.battle.logs.clear()
        defender.take_turn()

        # Check that a defensive action was taken
        defensive_action_taken = any('gains buff' in log and defender.name in log for log in self.battle.logs)
        self.assertTrue(defensive_action_taken, f"{defender.name} did not take a defensive action")

    def test_defensive_ai_high_health(self):
        # Set the DefensiveAI fighter's health to high
        defender = next(fighter for fighter in self.battle.fighters if fighter.ai == DefensiveAI)
        defender.health = defender.max_health  # Set to full health

        # Clear logs and take turn
        self.battle.logs.clear()
        defender.take_turn()

        # Check that the fighter attacked an opponent
        attack_action_taken = any('attacks' in log or 'misses' in log for log in self.battle.logs if log.split()[0] == defender.name)
        self.assertTrue(attack_action_taken, f"{defender.name} did not attack an opponent")

    def test_defensive_ai_switching_behaviors(self):
        # Set the DefensiveAI fighter's health to low and then high to check switching behaviors
        defender = next(fighter for fighter in self.battle.fighters if fighter.ai == DefensiveAI)

        # Set health to low and take turn
        defender.health = defender.max_health / 4 - 1
        self.battle.logs.clear()
        defender.take_turn()
        defensive_action_taken = any('gains buff' in log and defender.name in log for log in self.battle.logs)
        self.assertTrue(defensive_action_taken, f"{defender.name} did not take a defensive action when health was low")

        # Set health to high and take turn
        defender.health = defender.max_health
        self.battle.logs.clear()
        defender.take_turn()
        attack_action_taken = any('attacks' in log or 'misses' in log for log in self.battle.logs if log.split()[0] == defender.name)
        self.assertTrue(attack_action_taken, f"{defender.name} did not attack an opponent when health was high")

    def test_defensive_ai_movement(self):
        # Set the DefensiveAI fighter's health to low
        defender = next(fighter for fighter in self.battle.fighters if fighter.ai == DefensiveAI)
        defender.health = defender.max_health / 4 - 1  # Trigger defensive behavior

        # Clear logs and take turn
        self.battle.logs.clear()
        defender.take_turn()

        # Check for defensive actions and potential movement
        defensive_action_taken = any('gains buff' in log and defender.name in log for log in self.battle.logs)
        movement_action_taken = any('moves towards' in log for log in self.battle.logs)
        self.assertTrue(defensive_action_taken, f"{defender.name} did not take a defensive action")
        self.assertTrue(movement_action_taken, f"{defender.name} did not move towards a safer position if necessary")


if __name__ == '__main__':
    unittest.main()
