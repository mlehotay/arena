# test_arena.py
import unittest
from arena import Arena
from ai import GreatestThreatAI, LowestHealthAI, DefensiveAI, RandomAttackAI
from fighter import Fighter

test_roles = [
            {'name': 'Glenda', 'faction': 'Red', 'level': 6, 'class': Fighter, 'weapon': 'long sword', 'armor': 'chain mail', 'shield': None, 'ai': GreatestThreatAI},
            {'name': 'Hiro', 'faction': 'Blue', 'level': 3, 'class': Fighter, 'weapon': 'two-handed sword', 'armor': 'leather armor', 'shield': None, 'ai': LowestHealthAI},
            {'name': 'Alice', 'faction': 'Blue', 'level': 4, 'class': Fighter, 'weapon': 'trident', 'armor': 'ring mail', 'shield': 'small shield', 'ai': DefensiveAI},
]

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
