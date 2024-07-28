# test_arena.py
import unittest
from arena import Battle, Arena
from ai import GreatestThreatAI, LowestHealthAI, DefensiveAI, RandomAttackAI
from fighter import Fighter

test_roles = [
            {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI},
            {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI},
            {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI},
]

class TestBattle(unittest.TestCase):
    def setUp(self):
        self.battle = Battle('Test Battle', test_roles, verbose=False)

    def test_battle_initialization(self):
        self.assertEqual(len(self.battle.fighters), 3)

    def test_fighter_factions(self):
        factions = {fighter.faction for fighter in self.battle.fighters}
        self.assertEqual(factions, {'Red', 'Blue'})

    def test_initial_fighters_placement(self):
        for fighter in self.battle.fighters:
            self.assertIsNotNone(fighter.position)
            self.assertFalse(self.battle.map.get_position(fighter.position.x, fighter.position.y).fighter)

    def test_play_round(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.play_round()
        self.assertLessEqual(len(self.battle.fighters), initial_fighters_count)

    def test_fight_battle(self):
        initial_fighters_count = len(self.battle.fighters)
        self.battle.fight_battle()
        self.assertLess(len(self.battle.fighters), initial_fighters_count)

    def test_winner(self):
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

class TestArena(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(test_roles, iterations=10, verbose=False)

    def test_simulate_battle(self):
        self.arena.simulate_battle()
        self.assertGreaterEqual(sum(self.arena.wins.values()), self.arena.iterations)

    def test_print_probabilities(self):
        self.arena.simulate_battle()
        with self.assertLogs('root', level='INFO') as log:
            # self.arena.print_probabilities()
            self.assertTrue(any(f'Blue: ' in message for message in log.output))
            self.assertTrue(any(f'Red: ' in message for message in log.output))

if __name__ == '__main__':
    unittest.main()
