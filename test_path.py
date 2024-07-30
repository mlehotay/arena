import unittest
from map import Map, Position, Terrain

class TestPathfinding(unittest.TestCase):
    def setUp(self):
        self.map = Map(width=5, height=5, map_type='grid8')
        # Set some terrain types manually
        self.map.set_terrain(1, 1, Terrain.FOREST)
        self.map.set_terrain(2, 1, Terrain.FOREST)
        self.map.set_terrain(3, 1, Terrain.FOREST)
        self.map.set_terrain(1, 2, Terrain.MOUNTAIN)
        self.map.set_terrain(2, 2, Terrain.MOUNTAIN)
        self.map.set_terrain(3, 2, Terrain.MOUNTAIN)
        # Ensure terrain is set correctly
        for x in range(5):
            for y in range(5):
                pos = self.map.get_position(x, y)
                if pos.terrain == Terrain.PLAIN:
                    continue
                self.map.set_terrain(x, y, Terrain.PLAIN)

    def test_clear_path(self):
        start = Position(0, 0, 'grid8')
        end = Position(4, 4, 'grid8')
        path = self.map.astar(start, end)
        print(f"Clear path test - Path found: {path}")
        expected_path = [
            Position(0, 0, 'grid8', Terrain.PLAIN),
            Position(1, 1, 'grid8', Terrain.PLAIN),
            Position(2, 2, 'grid8', Terrain.PLAIN),
            Position(3, 3, 'grid8', Terrain.PLAIN),
            Position(4, 4, 'grid8', Terrain.PLAIN)
        ]
        self.assertEqual(path, expected_path)

    def test_blocked_path(self):
        start = Position(0, 0, 'grid8')
        end = Position(4, 4, 'grid8')
        # Block the path by setting some terrain as impassable
        self.map.set_terrain(2, 0, Terrain.WATER)
        self.map.set_terrain(2, 1, Terrain.WATER)
        self.map.set_terrain(2, 2, Terrain.WATER)
        self.map.set_terrain(2, 3, Terrain.WATER)
        path = self.map.astar(start, end)
        print(f"Blocked path test - Path found: {path}")
        self.assertEqual(path, [])  # Expecting no path due to blocking terrain

    def test_same_start_end(self):
        start = Position(1, 1, 'grid8')
        end = Position(1, 1, 'grid8')
        path = self.map.astar(start, end)
        print(f"Same start/end test - Path found: {path}")
        self.assertEqual(path, [start])  # The path should be just the starting position

    def test_complex_path(self):
        start = Position(0, 0, 'grid8')
        end = Position(4, 4, 'grid8')
        self.map.set_terrain(1, 2, Terrain.FOREST)
        self.map.set_terrain(2, 2, Terrain.FOREST)
        self.map.set_terrain(3, 2, Terrain.FOREST)
        self.map.set_terrain(2, 1, Terrain.FOREST)
        path = self.map.astar(start, end)
        print(f"Complex path test - Path found: {path}")
        expected_path = [
            Position(0, 0, 'grid8', Terrain.PLAIN),
            Position(1, 1, 'grid8', Terrain.PLAIN),
            Position(2, 2, 'grid8', Terrain.FOREST),
            Position(3, 3, 'grid8', Terrain.PLAIN),
            Position(4, 4, 'grid8', Terrain.PLAIN)
        ]
        self.assertEqual(path, expected_path)


    def test_out_of_bounds(self):
        start = Position(-1, -1, 'grid8')
        end = Position(6, 6, 'grid8')
        path = self.map.astar(start, end)
        print(f"Out of bounds test - Path found: {path}")
        self.assertEqual(path, [])  # Expecting no path due to invalid start/end

if __name__ == '__main__':
    unittest.main()
