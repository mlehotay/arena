import unittest
import random

from arena import Fighter, Battle, RandomAttackAI, GreatestThreatAI, LowestHealthAI, DefensiveAI, weapon_list, armor_list, shield_list

class TestFighter(unittest.TestCase):

    def setUp(self):
        self.fighter1 = Fighter('Alice', 5, 'Order', RandomAttackAI, 'long sword', 'chain mail', 'small shield')
        self.fighter2 = Fighter('Bob', 4, 'Order', GreatestThreatAI, 'two-handed sword', 'leather armor')
        self.fighter3 = Fighter('Eve', 5, 'Chaos', LowestHealthAI, 'flail', 'padded armor', 'large shield')
        self.fighter4 = Fighter('Mallory', 3, 'Chaos', RandomAttackAI, 'mace', 'banded mail', )

        self.battle = Battle('Test Battle', [], verbose=False)
        self.battle.add_fighter(self.fighter1)
        self.battle.add_fighter(self.fighter2)
        self.battle.add_fighter(self.fighter3)
        self.battle.add_fighter(self.fighter4)

    def test_initial_health(self):
        self.assertGreaterEqual(self.fighter1.health, 5)
        self.assertGreaterEqual(self.fighter2.health, 4)
        self.assertGreaterEqual(self.fighter3.health, 5)
        self.assertGreaterEqual(self.fighter4.health, 3)

    def test_armor_class(self):
        self.assertEqual(self.fighter1.armor_class, 4)  # chain mail (5) + small shield (1)
        self.assertEqual(self.fighter2.armor_class, 8)  # leather armor (2)
        self.assertEqual(self.fighter3.armor_class, 6)  # padded armor (2) + large shield (2)
        self.assertEqual(self.fighter4.armor_class, 4)  # banded mail (6)

    def test_calculate_threat(self):
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.fighter1), 4.5)  # long sword 1d8
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.fighter2), 5.5)  # two-handed sword 1d10
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.fighter3), 4.5)  # flail 1d6+1
        self.assertAlmostEqual(GreatestThreatAI.calculate_threat(self.fighter4), 4.5)  # mace 1d6+1

    def test_take_damage(self):
        self.fighter1.take_damage(5, self.fighter2)
        self.assertEqual(self.fighter1.health, self.fighter1.max_health - 5)

    def test_die(self):
        self.fighter1.take_damage(self.fighter1.health, self.fighter2)
        self.assertIsNone(self.fighter1.battle)
        self.assertNotIn(self.fighter1, self.battle.fighters)
        self.assertNotIn(self.fighter1, self.fighter2.battle.fighters)

    def test_repr(self):
        self.assertIn('Alice', repr(self.fighter1))
        self.assertIn('long sword', repr(self.fighter1))
        self.assertIn('RandomAttackAI', repr(self.fighter1))

class TestBattle(unittest.TestCase):

    def setUp(self):
        roles = [
            {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
            {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': GreatestThreatAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
            {'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'ai': LowestHealthAI, 'weapon': 'flail', 'armor': 'padded armor', 'shield': 'large shield'},
            {'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'mace', 'armor': 'banded mail', 'shield': None}
        ]
        self.battle = Battle('Test Battle', roles, verbose=False)
        for fighter in self.battle.fighters:
            fighter.battle = self.battle

    def test_battle_initialization(self):
        self.assertEqual(len(self.battle.fighters), 4)

    def test_fighter_factions(self):
        factions = {fighter.faction for fighter in self.battle.fighters}
        self.assertEqual(factions, {'Order', 'Chaos'})

    def test_play_round(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.play_round()
        self.assertLessEqual(len(self.battle.fighters), initial_fighters_count)

class TestAI(unittest.TestCase):

    def setUp(self):
        roles = [
            {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
            {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': GreatestThreatAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
            {'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'ai': LowestHealthAI, 'weapon': 'flail', 'armor': 'padded armor', 'shield': 'large shield'},
            {'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'mace', 'armor': 'banded mail', 'shield': None}
        ]
        self.battle = Battle('Test Battle', roles, verbose=False)
        for fighter in self.battle.fighters:
            fighter.battle = self.battle

        self.fighter1 = self.battle.fighters[0]
        self.fighter2 = self.battle.fighters[1]
        self.fighter3 = self.battle.fighters[2]
        self.fighter4 = self.battle.fighters[3]

    def test_random_attack_ai(self):
        pass

    def test_lowest_health_attack_ai(self):
        pass

    def test_greatest_threat_ai(self):
        pass

    def test_defensive_ai(self):
        pass

class TestBuff(unittest.TestCase):
    pass

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()
