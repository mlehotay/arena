# test_arena.py
import unittest
from arena import Battle, Arena
from fighter import Fighter
from ai import GreatestThreatAI, LowestHealthAI, DefensiveAI, RandomAttackAI

test_roles = [
    {'name': 'Alice', 'faction': 'Order', 'level': 5, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': 'small shield'},
    {'name': 'Bob', 'faction': 'Order', 'level': 4, 'class': Fighter, 'ai': GreatestThreatAI, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None},
    {'name': 'Eve', 'faction': 'Chaos', 'level': 5, 'class': Fighter, 'ai': LowestHealthAI, 'weapon': 'flail', 'armor': 'padded armor', 'shield': 'large shield'},
    {'name': 'Mallory', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': RandomAttackAI, 'weapon': 'morning star', 'armor': 'banded mail', 'shield': None},
    {'name': 'Carol', 'faction': 'Order', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'spear', 'armor': 'leather armor', 'shield': 'small shield'},
    {'name': 'Dave', 'faction': 'Chaos', 'level': 3, 'class': Fighter, 'ai': DefensiveAI, 'weapon': 'quarterstaff', 'armor': 'ring mail', 'shield': None},
]

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

class TestBattle2(unittest.TestCase):
    def setUp(self):
        roles = [
            {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI},
            {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI},
            {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI},
        ]
        self.battle = Battle('Test Battle', roles, verbose=False)

    def test_initial_fighters_placement(self):
        for fighter in self.battle.fighters:
            self.assertIsNotNone(fighter.position)
            self.assertFalse(self.battle.map.get_position(fighter.position.x, fighter.position.y).fighter)

    def test_fight_battle(self):
        winner = self.battle.fight_battle()
        self.assertIn(winner, ['Red', 'Blue'])
        if winner:
            self.assertGreaterEqual(self.battle.turn, 1)

    def test_move_fighter(self):
        fighter = self.battle.fighters[0]
        old_position = fighter.position
        new_position = self.battle.map.get_position(1, 1)
        self.battle.move_fighter(fighter, new_position)
        self.assertEqual(fighter.position, new_position)
        self.assertIsNone(self.battle.map.get_position(old_position.x, old_position.y).fighter)
        self.assertEqual(self.battle.map.get_position(new_position.x, new_position.y).fighter, fighter)

    def test_resolve_ranged_attack(self):
        attacker = self.battle.fighters[0]
        target = self.battle.fighters[1]
        attacker.ranged_weapon = MockRangedWeapon(range=5, damage=10, ammunition=['arrow'])
        attacker.position = self.battle.map.get_position(0, 0)
        target.position = self.battle.map.get_position(3, 3)
        self.battle.resolve_ranged_attack(attacker, target)
        self.assertIn('arrow', attacker.ranged_weapon.ammunition)

    def test_resolve_throw(self):
        attacker = self.battle.fighters[0]
        target = self.battle.fighters[1]
        attacker.wielded_weapon = MockWeapon(name='axe', damage=15)
        self.battle.resolve_throw(attacker, target)
        self.assertIsNone(attacker.wielded_weapon)

class TestArena(unittest.TestCase):
    def setUp(self):
        roles = [
            {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI},
            {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI},
            {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI},
        ]
        self.arena = Arena(roles, iterations=10, verbose=False)

    def test_simulate_battle(self):
        self.arena.simulate_battle()
        self.assertGreaterEqual(sum(self.arena.wins.values()), self.arena.iterations)

    def test_print_probabilities(self):
        self.arena.simulate_battle()
        with self.assertLogs('root', level='INFO') as log:
            self.arena.print_probabilities()
            self.assertTrue(any(f'Blue: ' in message for message in log.output))
            self.assertTrue(any(f'Red: ' in message for message in log.output))

if __name__ == '__main__':
    unittest.main()
