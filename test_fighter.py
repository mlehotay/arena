# test_fighter.py
import unittest
from fighter import Fighter
from ai import GreatestThreatAI, LowestHealthAI, DefensiveAI, RandomAttackAI
from arena import Battle, Arena
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


class TestFighter2(unittest.TestCase):

    def setUp(self):
        self.map = Map(10, 10, 'grid8')
        self.position1 = Position(1, 1, 'grass')
        self.position2 = Position(2, 2, 'grass')
        self.map.occupy_position(None, self.position1)
        self.map.occupy_position(None, self.position2)

        self.fighter1 = Fighter(
            name='Fighter1', level=5, ai=RandomAttackAI, faction='Red',
            weapon='long sword', armor='chain mail', shield='small shield'
        )
        self.fighter2 = Fighter(
            name='Fighter2', level=3, ai=RandomAttackAI, faction='Blue',
            weapon='short sword', armor='leather armor', shield=None
        )
        self.fighter1.position = self.position1
        self.fighter2.position = self.position2
        self.map.occupy_position(self.fighter1, self.position1)
        self.map.occupy_position(self.fighter2, self.position2)

    def test_initialization(self):
        self.assertEqual(self.fighter1.name, 'Fighter1')
        self.assertEqual(self.fighter1.level, 5)
        self.assertEqual(self.fighter1.weapon, 'long sword')
        self.assertEqual(self.fighter1.armor, 'chain mail')
        self.assertEqual(self.fighter1.shield, 'small shield')
        self.assertEqual(self.fighter1.armor_class, 10 - 5 - 1)

    def test_attack_success(self):
        self.fighter1.attack(self.fighter2)
        self.assertGreater(self.fighter2.health, 0)

    def test_attack_fail(self):
        # Assuming fighter2 has high armor class or fighter1's attack roll is low
        self.fighter1.attack(self.fighter2)
        self.assertEqual(self.fighter2.health, self.fighter2.max_health)

    def test_move(self):
        new_position = Position(3, 3, 'grass')
        self.map.occupy_position(None, new_position)
        self.fighter1.move_to(new_position)
        self.assertEqual(self.fighter1.position, new_position)

    def test_apply_buff(self):
        # Create a mock buff
        mock_buff = BuffCreator.create_defensive_stance()
        self.fighter1.apply_buff(mock_buff)
        self.assertIn(mock_buff, self.fighter1.buffs)

    def test_take_damage(self):
        initial_health = self.fighter2.health
        self.fighter1.attack(self.fighter2)
        self.assertLess(self.fighter2.health, initial_health)

    def test_die(self):
        self.fighter2.health = 1  # Set health to 1 for testing
        self.fighter2.take_damage(2, self.fighter1)
        self.assertIsNone(self.fighter2.battle)

    def test_take_defensive_action(self):
        self.fighter1.take_defensive_action()
        # Assuming the defensive actions modify buffs
        defensive_stance_buff = next(
            (buff for buff in self.fighter1.buffs if buff.name == 'Defensive Stance'), None
        )
        self.assertIsNotNone(defensive_stance_buff)

    def tearDown(self):
        # Clean up after each test
        self.map.vacate_position(self.fighter1)
        self.map.vacate_position(self.fighter2)
        self.fighter1 = None
        self.fighter2 = None
        self.map = None
        self.position1 = None
        self.position2 = None

if __name__ == '__main__':
    unittest.main()
