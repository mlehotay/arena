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
        self.map = Map(5, 7)

    def test_initial_map_size(self):
        self.assertEqual(self.map.width, 5)
        self.assertEqual(self.map.height, 7)
        self.assertEqual(len(self.map.grid), 5)
        self.assertTrue(all(len(row) == 7 for row in self.map.grid))

    def test_set_terrain(self):
        self.map.set_terrain(1, 1, Terrain.FOREST)
        self.assertEqual(self.map.get_position(1, 1).terrain, Terrain.FOREST)

    def test_get_position(self):
        pos = self.map.get_position(2, 2)
        self.assertIsInstance(pos, Position)
        self.assertEqual(pos.x, 2)
        self.assertEqual(pos.y, 2)

        pos = self.map.get_position(10, 10)
        self.assertIsNone(pos)

    def test_occupy_position(self):
        fighter = Fighter('Test Fighter', 3, RandomAttackAI, "Odds")
        pos = self.map.get_position(3, 3)
        self.map.occupy_position(fighter, pos)

        self.assertEqual(pos.fighter, fighter)
        self.assertEqual(fighter.position, pos)

    def test_vacate_position(self):
        fighter = Fighter('Test Fighter', 3, RandomAttackAI, "Odds")
        pos = self.map.get_position(3, 3)
        self.map.occupy_position(fighter, pos)
        self.map.vacate_position(pos)

        self.assertIsNone(pos.fighter)
        self.assertIsNone(fighter.position)

    def test_move_fighter(self):
        fighter = Fighter('Test Fighter', 3, RandomAttackAI, "Odds")
        start_pos = self.map.get_position(2, 2)
        new_pos = self.map.get_position(3, 3)
        self.map.occupy_position(fighter, start_pos)
        self.map.move_fighter(fighter, new_pos)

        self.assertEqual(new_pos.fighter, fighter)
        self.assertEqual(fighter.position, new_pos)
        self.assertIsNone(start_pos.fighter)

    def test_calculate_distance(self):
        pos1 = self.map.get_position(1, 1)
        pos2 = self.map.get_position(4, 4)

        # Testing Manhattan distance for grid4
        self.map.map_type = 'grid4'
        self.assertEqual(self.map.calculate_distance(pos1, pos2), 6)

        # Testing Chebyshev distance for grid8
        self.map.map_type = 'grid8'
        self.assertEqual(self.map.calculate_distance(pos1, pos2), 3)

        # Testing Hex distance for hex
        self.map.map_type = 'hex'
        self.assertEqual(self.map.calculate_distance(pos1, pos2), 6)

    def test_is_within_range(self):
        start_pos = self.map.get_position(1, 1)
        end_pos = self.map.get_position(4, 4)

        self.assertTrue(self.map.is_within_range(start_pos, end_pos, 6))
        self.assertFalse(self.map.is_within_range(start_pos, end_pos, 5))

    def test_is_adjacent(self):
        pos1 = self.map.get_position(2, 2)
        pos2 = self.map.get_position(2, 3)

        self.assertTrue(self.map.is_adjacent(pos1, pos2))

        pos3 = self.map.get_position(3, 3)
        self.assertFalse(self.map.is_adjacent(pos1, pos3))

    def test_get_neighbors(self):
        pos = self.map.get_position(2, 2)
        neighbors = self.map.get_neighbors(pos)
        self.assertEqual(len(neighbors), 8)  # For grid8

        self.map.map_type = 'grid4'
        neighbors = self.map.get_neighbors(pos)
        self.assertEqual(len(neighbors), 4)  # For grid4

        self.map.map_type = 'hex'
        neighbors = self.map.get_neighbors(pos)
        self.assertEqual(len(neighbors), 6)  # For hex

    def test_move_towards(self):
        start_pos = self.map.get_position(1, 1)
        target_pos = self.map.get_position(3, 3)
        new_pos = self.map.move_towards(start_pos, target_pos)

        self.assertEqual(new_pos.x, 2)
        self.assertEqual(new_pos.y, 2)

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
