# test_map.py
import unittest
from ai import *
from fighter import Fighter
from map import Map, Position, Terrain

class TestPosition(unittest.TestCase):

    def test_position_equality(self):
        pos1 = Position(1, 2, 'grid8', Terrain.PLAIN)
        pos2 = Position(1, 2, 'grid8', Terrain.PLAIN)
        pos3 = Position(2, 3, 'grid8', Terrain.FOREST)

        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)

    def test_position_hash(self):
        pos1 = Position(1, 2, 'grid8', Terrain.PLAIN)
        pos2 = Position(1, 2, 'grid8', Terrain.PLAIN)
        pos3 = Position(2, 3, 'grid8', Terrain.FOREST)

        self.assertEqual(hash(pos1), hash(pos2))
        self.assertNotEqual(hash(pos1), hash(pos3))

class TestMap(unittest.TestCase):

    def setUp(self):
        self.width = 5
        self.height = 7
        self.map = Map(self.width, self.height, 'grid4')

    def create_map(self, map_type):
        return Map(self.width, self.height, map_type)

    def test_initial_map_size(self):
        map = self.create_map('grid4')
        self.assertEqual(map.width, self.width)
        self.assertEqual(map.height, self.height)
        self.assertEqual(len(map.grid), self.width)
        self.assertTrue(all(len(row) == self.height for row in map.grid))

    def test_set_terrain(self):
        map = self.create_map('grid4')
        map.set_terrain(1, 1, Terrain.FOREST)
        self.assertEqual(map.get_position(1, 1).terrain, Terrain.FOREST)

    def test_get_position(self):
        map = self.create_map('grid4')
        pos = map.get_position(2, 2)
        self.assertIsInstance(pos, Position)
        self.assertEqual(pos.x, 2)
        self.assertEqual(pos.y, 2)

        pos = map.get_position(10, 10)
        self.assertIsNone(pos)

    def test_occupy_position(self):
        map = self.create_map('grid4')
        fighter = Fighter('Test Fighter', 3, RandomAttackAI, "Odds")
        pos = map.get_position(3, 3)
        map.occupy_position(fighter, pos)

        self.assertEqual(pos.fighter, fighter)
        self.assertEqual(fighter.position, pos)

    def test_vacate_position(self):
        map = self.create_map('grid4')
        fighter = Fighter('Test Fighter', 3, RandomAttackAI, "Odds")
        pos = map.get_position(3, 3)
        map.occupy_position(fighter, pos)
        map.vacate_position(pos)

        self.assertIsNone(pos.fighter)
        self.assertIsNone(fighter.position)

    def test_move_fighter(self):
        map = self.create_map('grid4')
        fighter = Fighter('Test Fighter', 3, RandomAttackAI, "Odds")
        start_pos = map.get_position(2, 2)
        new_pos = map.get_position(3, 3)
        map.occupy_position(fighter, start_pos)
        map.move_fighter(fighter, new_pos)

        self.assertEqual(new_pos.fighter, fighter)
        self.assertEqual(fighter.position, new_pos)
        self.assertIsNone(start_pos.fighter)

    def test_calculate_distance(self):
        pos1 = self.create_map('grid4').get_position(1, 1)
        pos2 = self.create_map('grid4').get_position(4, 4)

        # Testing Manhattan distance for grid4
        map = self.create_map('grid4')
        self.assertEqual(map.calculate_distance(pos1, pos2), 6)

        # Testing Chebyshev distance for grid8
        map = self.create_map('grid8')
        self.assertEqual(map.calculate_distance(pos1, pos2), 3)

        # Testing Hex distance for hex
        map = self.create_map('hex')
        self.assertEqual(map.calculate_distance(pos1, pos2), 6)

    def test_is_within_range(self):
        start_pos = self.create_map('grid4').get_position(1, 1)
        end_pos = self.create_map('grid4').get_position(4, 4)

        # Test for grid4
        map = self.create_map('grid4')
        self.assertTrue(map.is_within_range(start_pos, end_pos, 6))
        self.assertFalse(map.is_within_range(start_pos, end_pos, 5))

        # Test for grid8
        map = self.create_map('grid8')
        self.assertTrue(map.is_within_range(start_pos, end_pos, 3))
        self.assertFalse(map.is_within_range(start_pos, end_pos, 2))

        # Test for hex
        map = self.create_map('hex')
        self.assertTrue(map.is_within_range(start_pos, end_pos, 6))
        self.assertFalse(map.is_within_range(start_pos, end_pos, 5))

    def test_is_adjacent(self):
        pos1 = self.create_map('grid4').get_position(2, 2)
        pos2 = self.create_map('grid4').get_position(2, 3)

        # Test for grid4
        map = self.create_map('grid4')
        self.assertTrue(map.is_adjacent(pos1, pos2))
        pos3 = map.get_position(3, 3)
        self.assertFalse(map.is_adjacent(pos1, pos3))

        # Test for grid8
        map = self.create_map('grid8')
        self.assertTrue(map.is_adjacent(pos1, pos2))
        self.assertTrue(map.is_adjacent(pos1, pos3))

        # Test for hex
        map = self.create_map('hex')
        self.assertTrue(map.is_adjacent(pos1, pos2))
        pos3_hex = map.get_position(3, 1)
        self.assertTrue(map.is_adjacent(pos1, pos3_hex))
        pos4 = map.get_position(3, 2)
        self.assertTrue(map.is_adjacent(pos1, pos4))

    def test_get_neighbors(self):
        pos = self.create_map('grid4').get_position(2, 2)

        # Test for grid8
        map = self.create_map('grid8')
        neighbors = map.get_neighbors(pos)
        self.assertEqual(len(neighbors), 8)  # For grid8

        # Test for grid4
        map = self.create_map('grid4')
        neighbors = map.get_neighbors(pos)
        self.assertEqual(len(neighbors), 4)  # For grid4

        # Test for hex
        map = self.create_map('hex')
        neighbors = map.get_neighbors(pos)
        self.assertEqual(len(neighbors), 6)  # For hex

    def test_move_towards(self):
        start_pos = self.map.get_position(1, 1)
        target_pos = self.map.get_position(3, 3)

        # Test for grid4
        self.map.map_type = 'grid4'
        new_pos = self.map.move_towards(start_pos, target_pos)
        possible_positions = [(2, 1), (1, 2)]
        self.assertIn((new_pos.x, new_pos.y), possible_positions)

        # Test for grid8
        self.map.map_type = 'grid8'
        new_pos = self.map.move_towards(start_pos, target_pos)
        possible_positions = [(2, 1), (1, 2), (2, 2)]
        self.assertIn((new_pos.x, new_pos.y), possible_positions)

        # Test for hex
        self.map.map_type = 'hex'
        new_pos = self.map.move_towards(start_pos, target_pos)
        # In a hex grid, moving towards (3, 3) from (1, 1) could be (2, 2) or (2, 1) or (1, 2)
        possible_positions_hex = [(2, 2), (2, 1), (1, 2)]
        self.assertIn((new_pos.x, new_pos.y), possible_positions_hex)

    def test_terrain_cost(self):
        map = self.create_map('grid4')
        pos = map.get_position(2, 2)
        map.set_terrain(2, 2, Terrain.FOREST)
        self.assertEqual(pos.terrain, Terrain.FOREST)

    def test_astar(self):
        # Simple test with a known path
        self.map.set_terrain(2, 2, Terrain.WATER)  # Block path
        start = self.map.get_position(0, 0)
        goal = self.map.get_position(4, 4)
        path = self.map.astar(start, goal)

        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

if __name__ == '__main__':
    unittest.main()
