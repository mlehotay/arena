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
    def __init__(self, x, y, map_type='grid', terrain=TerrainType.PLAIN):
        self.x = x
        self.y = y
        self.map_type = map_type
        self.terrain = terrain

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

def calculateDistance(pos1: Position, pos2: Position) -> int:
    if pos1 is None or pos2 is None:
        raise ValueError("Positions cannot be None.")
    if pos1.map_type != pos2.map_type:
        raise ValueError("Positions must be on the same type of map.")

    if pos1.map_type == 'grid':
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
    elif pos1.map_type == 'hex':
        return (abs(pos1.x - pos2.x) + abs(pos1.x + pos1.y - pos2.x - pos2.y) + abs(pos1.y - pos2.y)) // 2
    elif pos1.map_type == 'grid8':
        return max(abs(pos1.x - pos2.x), abs(pos1.y - pos2.y))
    else:
        raise ValueError(f"Unknown map type: {pos1.map_type}")

GRID_NEIGHBORS: List[Tuple[int, int]] = [(0, 1), (1, 0), (0, -1), (-1, 0)]
GRID8_NEIGHBORS: List[Tuple[int, int]] = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
HEX_NEIGHBORS: List[Tuple[int, int]] = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

class Map:
    def __init__(self, width: int, height: int, map_type: str = 'grid'):
        self.width = width
        self.height = height
        self.map_type = map_type
        self.grid = [[Position(x, y, map_type) for y in range(height)] for x in range(width)]

    def setTerrain(self, x: int, y: int, terrain: TerrainType):
        self.grid[x][y].terrain = terrain

    def getPosition(self, x: int, y: int) -> Position:
        return self.grid[x][y]

    def getNeighbors(self, position: Position) -> List[Position]:
        neighbors = []
        if position.map_type == 'grid':
            for dx, dy in GRID_NEIGHBORS:
                nx, ny = position.x + dx, position.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self.grid[nx][ny])
        elif position.map_type == 'hex':
            for dx, dy in HEX_NEIGHBORS:
                nx, ny = position.x + dx, position.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self.grid[nx][ny])
        elif position.map_type == 'grid8':
            for dx, dy in GRID8_NEIGHBORS:
                nx, ny = position.x + dx, position.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self.grid[nx][ny])
        return neighbors

def heuristic(a: Position, b: Position) -> int:
    return calculateDistance(a, b)

def astar(start: Position, goal: Position, game_map: Map) -> List[Position]:
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Position, Position] = {}
    g_score: Dict[Position, int] = {start: 0}
    f_score: Dict[Position, int] = {start: heuristic(start, goal)}

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

        for neighbor in game_map.getNeighbors(current):
            tentative_g_score = g_score[current] + TERRAIN_COSTS[neighbor.terrain]
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    return []

def isWithinRange(start: Position, end: Position, range_limit: int) -> bool:
    return calculateDistance(start, end) <= range_limit

# Example Usage with Hex Map

def run(self):
    # Create a 5x5 hex map
    game_map = Map(5, 5, 'hex')

    # Set some terrain types
    game_map.setTerrain(2, 2, TerrainType.FOREST)
    game_map.setTerrain(3, 3, TerrainType.MOUNTAIN)
    game_map.setTerrain(4, 4, TerrainType.WATER)

    # Define start and goal positions
    start = game_map.getPosition(0, 0)
    goal = game_map.getPosition(4, 4)

    # Find path using A* algorithm
    path = astar(start, goal, game_map)

    # Print the path
    print("Path found:", path)
