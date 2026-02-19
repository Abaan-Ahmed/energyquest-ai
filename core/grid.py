import random
import copy
from config.settings import *

EMPTY = 0
WALL = 1
GEM = 2
TRAP = 3
GOAL = 4

class GridWorld:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.gems = {}
        self.traps = set()
        self.goal = (GRID_ROWS - 1, GRID_COLS - 1)
        self._generate()

    def _generate(self):
        self.grid[self.goal[0]][self.goal[1]] = GOAL

        # Walls
        for _ in range(30):
            r = random.randint(0, GRID_ROWS - 1)
            c = random.randint(0, GRID_COLS - 1)
            if (r, c) != (0, 0) and (r, c) != self.goal:
                self.grid[r][c] = WALL

        # Gems
        while len(self.gems) < NUM_GEMS:
            r = random.randint(0, GRID_ROWS - 1)
            c = random.randint(0, GRID_COLS - 1)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = GEM
                self.gems[(r, c)] = random.randint(2, MAX_GEM_ENERGY)

        # Traps
        for _ in range(10):
            r = random.randint(0, GRID_ROWS - 1)
            c = random.randint(0, GRID_COLS - 1)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = TRAP
                self.traps.add((r, c))

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS

    def is_walkable(self, pos):
        r, c = pos
        return self.grid[r][c] != WALL

    def clone(self):
        new = GridWorld.__new__(GridWorld)
        new.grid = copy.deepcopy(self.grid)
        new.gems = copy.deepcopy(self.gems)
        new.traps = copy.deepcopy(self.traps)
        new.goal = self.goal
        return new
