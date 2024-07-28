# map.py
from enum import Enum
import heapq
from typing import List, Tuple, Dict

# Position and Terrain classes for spatial mechanics
class Terrain(Enum):
    PLAIN = 1
    FOREST = 2
    MOUNTAIN = 3
    WATER = 4

TERRAIN_COSTS = {
    Terrain.PLAIN: 1,
    Terrain.FOREST: 2,
    Terrain.MOUNTAIN: 3,
    Terrain.WATER: float('inf')  # Impassable
}

class Position:
    def __init__(self, x, y, map_type, terrain=Terrain.PLAIN):
        self.x = x
        self.y = y
        self.map_type = map_type
        self.terrain = terrain
        self.fighter = None

    def __repr__(self):
        return f"({self.x}, {self.y}, {self.map_type}, {self.terrain})"

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y and self.map_type == other.map_type and self.terrain == other.terrain
        return False

    def __hash__(self):
        return hash((self.x, self.y, self.map_type, self.terrain))

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

class Map:
    def __init__(self, width, height, map_type='grid8'):
        self.width = width
        self.height = height
        self.map_type = map_type
        self.grid = [[Position(x, y, map_type, Terrain.PLAIN) for y in range(height)] for x in range(width)]

    def get_position(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None

    def set_terrain(self, x, y, terrain):
        pos = self.get_position(x, y)
        if pos:
            pos.terrain = terrain

    def occupy_position(self, fighter, pos):
        if pos and pos.fighter is None:
            pos.fighter = fighter
            fighter.position = pos

    def vacate_position(self, pos):
        if pos and pos.fighter:
            pos.fighter.position = None
            pos.fighter = None

    def move_fighter(self, fighter, new_pos):
        if fighter.position:
            self.vacate_position(fighter.position)
        self.occupy_position(fighter, new_pos)

    def calculate_distance(self, pos1, pos2):
        if self.map_type == 'grid4':
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
        elif self.map_type == 'grid8':
            return max(abs(pos1.x - pos2.x), abs(pos1.y - pos2.y))
        elif self.map_type == 'hex':
            return (abs(pos1.x - pos2.x) + abs(pos1.x + pos1.y - pos2.x - pos2.y) + abs(pos1.y - pos2.y)) // 2

    def is_within_range(self, start_pos, end_pos, range):
        return self.calculate_distance(start_pos, end_pos) <= range

    def is_adjacent(self, pos1, pos2):
        if self.map_type == 'grid8':
            return max(abs(pos1.x - pos2.x), abs(pos1.y - pos2.y)) == 1
        elif self.map_type == 'grid4':
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y) == 1
        elif self.map_type == 'hex':
            return (abs(pos1.x - pos2.x) + abs(pos1.x + pos1.y - pos2.x - pos2.y) + abs(pos1.y - pos2.y)) // 2 == 1

    def get_neighbors(self, pos):
        neighbors = []
        if self.map_type == 'grid8':
            deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        elif self.map_type == 'grid4':
            deltas = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        elif self.map_type == 'hex':
            deltas = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]

        for dx, dy in deltas:
            neighbor = self.get_position(pos.x + dx, pos.y + dy)
            if neighbor:
                neighbors.append(neighbor)

        return neighbors

    def move_towards(self, start_pos, target_pos):
        dx = target_pos.x - start_pos.x
        dy = target_pos.y - start_pos.y

        if self.map_type in ['grid4', 'grid8']:
            if abs(dx) > abs(dy):
                new_x = start_pos.x + (1 if dx > 0 else -1)
                new_y = start_pos.y
            elif abs(dx) < abs(dy):
                new_x = start_pos.x
                new_y = start_pos.y + (1 if dy > 0 else -1)
            else:
                new_x = start_pos.x + (1 if dx > 0 else -1)
                new_y = start_pos.y + (1 if dy > 0 else -1)
        elif self.map_type == 'hex':
            if abs(dx) >= abs(dy):
                new_x = start_pos.x + (1 if dx > 0 else -1)
                new_y = start_pos.y + (1 if dy > 0 else -1)
            else:
                new_x = start_pos.x + (1 if dx > 0 else -1)
                new_y = start_pos.y + (1 if dy > 0 else -1)

        return self.get_position(new_x, new_y)

    def is_position_occupied(self, position):
        return position and position.fighter is not None

    def is_valid_position(self, position: Position) -> bool:
        return position is not None and 0 <= position.x < self.width and 0 <= position.y < self.height

    def heuristic(self, a: Position, b: Position) -> int:
        return self.calculate_distance(a, b)

    def astar(self, start: Position, goal: Position) -> List[Position]:
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from: Dict[Position, Position] = {}
        g_score: Dict[Position, int] = {start: 0}
        f_score: Dict[Position, int] = {start: self.heuristic(start, goal)}

        open_set_hash = {start}

        while open_set:
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                # Calculate terrain cost
                terrain_cost = TERRAIN_COSTS.get(neighbor.terrain, float('inf'))

                # If the neighbor is occupied by a fighter, increase the cost significantly
                if neighbor.fighter:
                    terrain_cost = float('inf')

                tentative_g_score = g_score[current] + terrain_cost
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

        return []
