# test_fighter.py
import unittest
from fighter import Fighter
from ai import GreatestThreatAI, LowestHealthAI, DefensiveAI, RandomAttackAI
from battle import Battle
from buff import BuffCreator
from map import Map, Position

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

    def test_fighter_movement(self):
        fighter = self.battle.fighters[0]
        original_position = fighter.position
        new_position = self.battle.map.get_position(2, 2)
        fighter.move_to(new_position)
        self.assertEqual(fighter.position, new_position)
        self.assertIsNone(original_position.fighter)
        self.assertEqual(fighter, new_position.fighter)

    def test_fighter_position_update(self):
        fighter = self.battle.fighters[1]
        original_position = fighter.position
        new_position = self.battle.map.get_position(3, 3)
        self.battle.map.occupy_position(fighter, new_position)
        self.assertEqual(fighter.position, new_position)
        self.assertEqual(self.battle.map.get_position(fighter.position.x, fighter.position.y), new_position)

    def test_position_occupancy(self):
        position = self.battle.map.get_position(4, 4)
        fighter = self.battle.fighters[2]
        self.battle.map.occupy_position(fighter, position)
        self.assertEqual(self.battle.map.get_position(fighter.position.x, fighter.position.y), position)
        self.assertEqual(fighter.position, position)

    def test_map_boundaries(self):
        fighter = self.battle.fighters[3]
        position_out_of_bounds = self.battle.map.get_position(-1, -1)  # Assuming -1 is out of bounds
        self.assertIsNone(position_out_of_bounds)
        self.battle.map.occupy_position(fighter, position_out_of_bounds) # assert raises exception?

    def test_multiple_fighters_same_position(self):
        position = self.battle.map.get_position(5, 5)
        fighter1 = self.battle.fighters[4]
        fighter2 = self.battle.fighters[5]
        self.battle.map.occupy_position(fighter1, position)
        self.battle.map.occupy_position(fighter2, position) # this should fail
        self.assertEqual(fighter1.position, position)
        self.assertEqual(self.battle.map.get_position(fighter1.position.x, fighter1.position.y), position)
        self.assertNotEqual(fighter2.position, position)
        self.assertNotEqual(self.battle.map.get_position(fighter2.position.x, fighter2.position.y), position)
        # is this the behavior we want? silent failure?

if __name__ == '__main__':
    unittest.main()
