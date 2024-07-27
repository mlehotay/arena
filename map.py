# map.py
from enum import Enum
import heapq
from typing import List, Tuple, Dict

# Position and Terrain classes for spatial mechanics
class TerrainType(Enum):
    PLAIN = 1
    FOREST = 2
    MOUNTAIN = 3
    WATER = 4

TERRAIN_COSTS = {
    TerrainType.PLAIN: 1,
    TerrainType.FOREST: 2,
    TerrainType.MOUNTAIN: 3,
    TerrainType.WATER: float('inf')  # Impassable
}

class Position:
    def __init__(self, x, y, map_type='grid8', terrain=TerrainType.PLAIN):
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

GRID4_NEIGHBORS: List[Tuple[int, int]] = [(0, 1), (1, 0), (0, -1), (-1, 0)]
GRID8_NEIGHBORS: List[Tuple[int, int]] = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
HEX_NEIGHBORS: List[Tuple[int, int]] = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

class Map:
    def __init__(self, width: int, height: int, map_type: str = 'grid8'):
        self.width = width
        self.height = height
        self.map_type = map_type
        self.grid = [[Position(x, y, map_type) for y in range(height)] for x in range(width)]

    def set_terrain(self, x: int, y: int, terrain: TerrainType):
        self.grid[x][y].terrain = terrain

    def get_position(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        else:
            return None

    def occupy_position(self, fighter: 'Fighter', position: Position):
        if self.is_valid_position(position) and position.fighter is None:
            position.fighter = fighter
            fighter.position = position
        else:
            raise ValueError("Position is invalid or already occupied.")

    def vacate_position(self, position: Position):
        if self.is_valid_position(position) and self.is_position_occupied(position):
            position.fighter.position = None
            position.fighter = None
        else:
            raise ValueError("Position is invalid or not occupied.")

    def move_fighter(self, fighter: 'Fighter', new_position: Position):
        if self.is_valid_position(new_position) and new_position.fighter is None:
            self.vacate_position(fighter.position)
            self.occupy_position(fighter, new_position)
        else:
            raise ValueError("New position is invalid or occupied.")

    def is_position_occupied(self, position):
        return position and position.fighter is not None

    def is_valid_position(self, position: Position) -> bool:
        return position is not None and 0 <= position.x < self.width and 0 <= position.y < self.height

    def calculate_distance(self, pos1: Position, pos2: Position) -> int:
        if pos1 is None or pos2 is None:
            raise ValueError("Positions cannot be None.")
        if pos1.map_type != pos2.map_type:
            raise ValueError("Positions must be on the same type of map.")

        if pos1.map_type == 'grid4': # Manhattan distance
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
        elif pos1.map_type == 'hex': # axial distance
            return (abs(pos1.x - pos2.x) + abs(pos1.x + pos1.y - pos2.x - pos2.y) + abs(pos1.y - pos2.y)) // 2
        elif pos1.map_type == 'grid8': # Chebyshev distance
            return max(abs(pos1.x - pos2.x), abs(pos1.y - pos2.y))
        else:
            raise ValueError(f"Unknown map type: {pos1.map_type}")

    def is_within_range(self, start: Position, end: Position, range_limit: int) -> bool:
        return self.calculate_distance(start, end) <= range_limit

    def is_adjacent(self, pos1: Position, pos2: Position) -> bool:
        return self.calculate_distance(pos1, pos2) <= 1

    def get_neighbors(self, position: Position) -> List[Position]:
        neighbors = []
        if position.map_type == 'grid4':
            for dx, dy in GRID4_NEIGHBORS:
                nx, ny = position.x + dx, position.y + dy
                if self.is_valid_position(self.get_position(nx, ny)):
                    neighbors.append(self.get_position(nx, ny))
        elif position.map_type == 'hex':
            for dx, dy in HEX_NEIGHBORS:
                nx, ny = position.x + dx, position.y + dy
                if self.is_valid_position(self.get_position(nx, ny)):
                    neighbors.append(self.get_position(nx, ny))
        elif position.map_type == 'grid8':
            for dx, dy in GRID8_NEIGHBORS:
                nx, ny = position.x + dx, position.y + dy
                if self.is_valid_position(self.get_position(nx, ny)):
                    neighbors.append(self.get_position(nx, ny))
        return neighbors

    def move_towards(self, start_pos: Position, target_pos: Position) -> Position:
        x1, y1 = start_pos.x, start_pos.y
        x2, y2 = target_pos.x, target_pos.y

        if x1 < x2:
            new_x = x1 + 1
        elif x1 > x2:
            new_x = x1 - 1
        else:
            new_x = x1

        if y1 < y2:
            new_y = y1 + 1
        elif y1 > y2:
            new_y = y1 - 1
        else:
            new_y = y1

        new_pos = self.get_position(new_x, new_y)
        return new_pos if self.is_valid_position(new_pos) else start_pos

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
