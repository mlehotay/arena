# test_ai.py
import unittest
from ai import RandomAttackAI, LowestHealthAI, GreatestThreatAI, DefensiveAI, RangedAttackAI
from fighter import Fighter
from map import Map, Position


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


class TestAI2(unittest.TestCase):

    def setUp(self):
        self.map = Map(10, 10, 'grid8')
        self.position1 = Position(1, 1, 'grass')
        self.position2 = Position(2, 2, 'grass')
        self.position3 = Position(3, 3, 'grass')
        self.map.occupy_position(None, self.position1)
        self.map.occupy_position(None, self.position2)
        self.map.occupy_position(None, self.position3)

        self.fighter1 = Fighter(
            name='Fighter1', level=5, ai=RandomAttackAI, faction='Red',
            weapon='long sword', armor='chain mail', shield='small shield'
        )
        self.fighter2 = Fighter(
            name='Fighter2', level=3, ai=LowestHealthAI, faction='Blue',
            weapon='short sword', armor='leather armor', shield=None
        )
        self.fighter3 = Fighter(
            name='Fighter3', level=4, ai=GreatestThreatAI, faction='Green',
            weapon='axe', armor='studded leather', shield=None
        )
        self.fighter4 = Fighter(
            name='Fighter4', level=2, ai=DefensiveAI, faction='Yellow',
            weapon='dagger', armor='padded armor', shield='small shield'
        )
        self.fighter5 = Fighter(
            name='Fighter5', level=3, ai=RangedAttackAI, faction='Purple',
            weapon='short sword', armor='leather armor', shield=None
        )

        # Set up positions and maps
        self.fighter1.position = self.position1
        self.fighter2.position = self.position2
        self.fighter3.position = self.position3
        self.map.occupy_position(self.fighter1, self.position1)
        self.map.occupy_position(self.fighter2, self.position2)
        self.map.occupy_position(self.fighter3, self.position3)
        self.map.occupy_position(self.fighter4, self.position3)

        self.fighter1.battle = self.fighter2.battle = self.fighter3.battle = self.fighter4.battle = self.fighter5.battle = self.map

    def test_random_attack_ai(self):
        self.fighter1.ai.take_turn(self.fighter1)
        # Since the RandomAttackAI targets random enemies, we check if the attack happened correctly
        self.assertTrue(self.fighter2.health < self.fighter2.max_health or self.fighter3.health < self.fighter3.max_health)

    def test_lowest_health_ai(self):
        # Set fighter2's health to low
        self.fighter2.health = 1
        self.fighter3.health = 10
        self.fighter2.ai.take_turn(self.fighter2)
        # LowestHealthAI should prioritize attacking fighter2
        self.assertTrue(self.fighter2.health < 1)

    def test_greatest_threat_ai(self):
        # The fighter3 with GreatestThreatAI should consider the weapon's threat
        self.fighter1.attack(self.fighter2)  # This makes fighter2 less healthy
        self.fighter3.ai.take_turn(self.fighter3)
        # Assuming weapon_list[weapon] gives higher threat value, fighter3 should attack fighter1
        self.assertTrue(self.fighter1.health < self.fighter1.max_health or self.fighter2.health < self.fighter2.max_health)

    def test_defensive_ai(self):
        self.fighter4.health = self.fighter4.max_health / 4 - 1  # Set health to be low
        self.fighter4.ai.take_turn(self.fighter4)
        # DefensiveAI should apply defensive actions when health is low
        defensive_buff = next((buff for buff in self.fighter4.buffs if buff.name == 'Defensive Stance'), None)
        self.assertIsNotNone(defensive_buff)

    def test_ranged_attack_ai(self):
        self.fighter5.equip_ranged_weapon('short sword')  # Assuming the range is tied to the weapon
        self.fighter5.ai.take_turn(self.fighter5)
        # If fighter5's ranged attack is implemented correctly, it should attack if in range
        self.assertTrue(self.fighter2.health < self.fighter2.max_health or self.fighter3.health < self.fighter3.max_health)

    def tearDown(self):
        # Clean up after each test
        self.map.vacate_position(self.fighter1)
        self.map.vacate_position(self.fighter2)
        self.map.vacate_position(self.fighter3)
        self.map.vacate_position(self.fighter4)
        self.map.vacate_position(self.fighter5)
        self.fighter1 = None
        self.fighter2 = None
        self.fighter3 = None
        self.fighter4 = None
        self.fighter5 = None
        self.map = None
        self.position1 = None
        self.position2 = None
        self.position3 = None

if __name__ == '__main__':
    unittest.main()
