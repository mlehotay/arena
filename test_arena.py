# test_arena.py
import unittest
from arena import *

test_roles = [
    {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
    {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': GreatestThreatAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
    {'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'ai': LowestHealthAI, 'weapon': 'flail', 'armor': 'padded armor', 'shield': 'large shield'},
    {'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'morning star', 'armor': 'banded mail', 'shield': None},
    {'name': 'Carol', 'faction': 'Order', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'spear', 'armor': 'leather armor', 'shield': 'small shield'},
    {'name': 'Dave', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'quarterstaff', 'armor': 'ring mail', 'shield': None},
]

class TestFighter(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('TestFighter Battle', test_roles, verbose=False)

    def test_initial_health(self):
        for fighter in self.battle.fighters:
            self.assertGreaterEqual(fighter.health, fighter.level)
            self.assertLessEqual(fighter.health, fighter.level * 10)

    def test_armor_class(self):
        self.assertEqual(self.battle.fighters[0].armor_class, 4)  # chain mail (5) + small shield (1)
        self.assertEqual(self.battle.fighters[1].armor_class, 8)  # leather armor (2)
        self.assertEqual(self.battle.fighters[2].armor_class, 6)  # padded armor (2) + large shield (2)
        self.assertEqual(self.battle.fighters[3].armor_class, 4)  # banded mail (6)
        self.assertEqual(self.battle.fighters[4].armor_class, 7)  # leather armor (2) + small shield (1)
        self.assertEqual(self.battle.fighters[5].armor_class, 7)  # ring mail (3)

    def test_calculate_threat(self):
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[0]), 4.5)  # long sword 1d8
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[1]), 5.5)  # two-handed sword 1d10
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[2]), 4.5)  # flail 1d6+1
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[3]), 5.0)  # morning star 2d4
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[4]), 3.5)  # spear 1d6
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.battle.fighters[5]), 3.5)  # quarterstaff 1d6

    def test_take_damage(self):
        self.battle.fighters[0].take_damage(5, self.battle.fighters[1])
        self.assertEqual(self.battle.fighters[0].health, self.battle.fighters[0].max_health - 5)

    def test_die(self):
        fighter = self.battle.fighters[0];
        self.battle.fighters[0].take_damage(fighter.health, self.battle.fighters[1])
        self.assertIsNone(fighter.battle)
        self.assertNotIn(fighter, self.battle.fighters)
        self.assertNotIn(fighter, self.battle.fighters[1].battle.fighters)

    def test_repr(self):
        self.assertIn('Alice', repr(self.battle.fighters[0]))
        self.assertIn('long sword', repr(self.battle.fighters[0]))
        self.assertIn('RandomAttackAI', repr(self.battle.fighters[0]))

class TestBattle(unittest.TestCase):

    def setUp(self):
        self.battle = Battle('Test Battle', test_roles, verbose=False)

    def test_battle_initialization(self):
        self.assertEqual(len(self.battle.fighters), 6)

    def test_fighter_factions(self):
        factions = {fighter.faction for fighter in self.battle.fighters}
        self.assertEqual(factions, {'Order', 'Chaos'})

    def test_play_round(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.play_round()
        self.assertLessEqual(len(self.battle.fighters), initial_fighters_count)

    def test_fight_battle(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.fight_battle()
        self.assertLess(len(self.battle.fighters), initial_fighters_count)

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

class TestBuffs(unittest.TestCase):
    def setUp(self):
        test_roles = [
            {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
            {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
        ]
        self.battle = Battle('Test Buffs Battle', test_roles, verbose=False)

    def test_defensive_stance_application(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_armor_class = test_fighter.armor_class
        test_fighter.apply_buff(BuffCreator.create_defensive_stance())
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 4, "Armor class did not increase correctly after applying Defensive Stance")

    def test_shield_wall_application(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_armor_class = test_fighter.armor_class
        test_fighter.apply_buff(BuffCreator.create_shield_wall())
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 6, "Armor class did not increase correctly after applying Shield Wall")

    def test_defensive_action_buff_with_shield(self):
        test_fighter = next(fighter for fighter in self.battle.fighters if fighter.shield is not None)
        initial_armor_class = test_fighter.armor_class
        test_fighter.take_defensive_action()
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 6, "Defensive Action with shield did not apply Shield Wall buff")

    def test_defensive_action_buff_with_no_shield(self):
        test_fighter = next(fighter for fighter in self.battle.fighters if fighter.shield is None)
        initial_armor_class = test_fighter.armor_class
        test_fighter.take_defensive_action()
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 4, "Defensive Action without shield did not apply Defensive Stance buff")

    def test_buff_duration(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_armor_class = test_fighter.armor_class
        test_fighter.apply_buff(BuffCreator.create_defensive_stance())
        self.assertEqual(test_fighter.armor_class, initial_armor_class - 4, "Buff was not applied correctly")
        for _ in range(test_fighter.buffs[0].remaining_duration):
            test_fighter.take_turn()
        self.assertEqual(test_fighter.armor_class, initial_armor_class, "Buff should have expired")

    def test_buff_cooldown(self):
        test_fighter = random.choice(self.battle.fighters)
        buff = BuffCreator.create_shield_wall()
        test_fighter.apply_buff(buff)

        self.assertEqual(buff.remaining_cooldown, buff.cooldown, "Buff cooldown was not set correctly")

        # Process turns equal to the duration of the buff
        for _ in range(buff.duration):
            test_fighter.take_turn()

        # Cooldown should start only after the buff has expired
        self.assertEqual(buff.remaining_cooldown, buff.cooldown, "Buff cooldown should start after buff expires")

        for _ in range(buff.cooldown):
            test_fighter.take_turn()

        self.assertEqual(buff.remaining_cooldown, 0, "Buff cooldown did not decrease correctly")

    def test_berserk_rage_last_teammate(self):
        test_fighter = random.choice(self.battle.fighters)
        team_mate = next(fighter for fighter in self.battle.fighters if fighter != test_fighter)
        team_mate.die()  # Simulate teammate death
        self.assertIn('Berserk Rage', [buff.name for buff in test_fighter.buffs], "Berserk Rage buff was not applied correctly")

        # Check attack bonus progression
        expected_attack_bonus = 5
        for _ in range(5):
            self.assertEqual(test_fighter.attack_bonus, expected_attack_bonus, f"Attack bonus did not increase correctly after applying Berserk Rage")
            test_fighter.take_turn()
            expected_attack_bonus -= 1

    def test_heal_over_time_application(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_health = test_fighter.health
        test_fighter.health -= 10  # Simulate damage
        test_fighter.apply_buff(BuffCreator.create_heal_over_time())
        for _ in range(2):  # Healing over two turns
            test_fighter.take_turn()
        self.assertGreater(test_fighter.health, initial_health - 10, "Health did not increase correctly after applying Heal Over Time")

    def test_heal_over_time_duration(self):
        test_fighter = random.choice(self.battle.fighters)
        initial_health = test_fighter.health
        test_fighter.health -= 10  # Simulate damage
        test_fighter.apply_buff(BuffCreator.create_heal_over_time())
        for _ in range(3):  # Healing over three turns
            test_fighter.take_turn()
        self.assertGreater(test_fighter.health, initial_health - 10, "Health should have increased over time")

    def test_heal_over_time_cooldown(self):
        test_fighter = random.choice(self.battle.fighters)
        buff = BuffCreator.create_heal_over_time()
        test_fighter.apply_buff(buff)
        for _ in range(buff.remaining_duration + buff.remaining_cooldown):  # Full duration plus cooldown
            test_fighter.take_turn()
        self.assertEqual(buff.remaining_cooldown, 0, "Buff cooldown did not decrease correctly")

if __name__ == '__main__':
    unittest.main()
