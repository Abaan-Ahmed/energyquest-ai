# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  core/grid.py
# ─────────────────────────────────────────────────────────────
import random
import copy
from collections import deque
from config.settings import (
    GRID_ROWS, GRID_COLS, NUM_GEMS, MAX_GEM_ENERGY
)

EMPTY    = 0
WALL     = 1
GEM      = 2    # only human's gold gem remains on this tile
TRAP     = 3
GOAL     = 4
GEM_A    = 5    # only AI's purple gem remains on this tile
GEM_BOTH = 6    # both gold AND purple gem on this tile (start state)


class GridWorld:
    def __init__(self):
        self.grid       = [[EMPTY] * GRID_COLS for _ in range(GRID_ROWS)]
        self.human_gems = {}   # pos -> value  (only human can collect)
        self.ai_gems    = {}   # pos -> value  (only AI can collect)
        self.traps      = set()
        self.goal       = (GRID_ROWS - 1, GRID_COLS - 1)
        self._generate()

    # ── Generation ────────────────────────────────────────────
    def _generate(self):
        for _attempt in range(30):
            self.grid       = [[EMPTY] * GRID_COLS for _ in range(GRID_ROWS)]
            self.human_gems = {}
            self.ai_gems    = {}
            self.traps      = set()

            self.grid[self.goal[0]][self.goal[1]] = GOAL

            # Place walls
            placed = 0
            for _ in range(800):
                if placed >= 28:
                    break
                r = random.randint(0, GRID_ROWS - 1)
                c = random.randint(0, GRID_COLS - 1)
                if (r, c) not in ((0, 0), self.goal) and self.grid[r][c] == EMPTY:
                    self.grid[r][c] = WALL
                    placed += 1

            if not self._reachable((0, 0), self.goal):
                continue

            # ── Paired gem placement ───────────────────────────
            # Every tile gets BOTH a gold (human) and a purple (AI) gem.
            # This guarantees equal travel distances for equivalent rewards.
            n_pairs = NUM_GEMS // 2  # number of paired tiles

            attempts  = 0
            p_placed  = 0
            while p_placed < n_pairs and attempts < 2000:
                attempts += 1
                r = random.randint(0, GRID_ROWS - 1)
                c = random.randint(0, GRID_COLS - 1)
                if self.grid[r][c] != EMPTY:
                    continue
                val = random.randint(2, MAX_GEM_ENERGY)
                # Both agents get the same energy value from this tile
                self.grid[r][c]          = GEM_BOTH
                self.human_gems[(r, c)]  = val
                self.ai_gems[(r, c)]     = val
                p_placed += 1

            # Place traps
            placed_t = 0
            attempts = 0
            while placed_t < 10 and attempts < 1000:
                attempts += 1
                r = random.randint(0, GRID_ROWS - 1)
                c = random.randint(0, GRID_COLS - 1)
                if self.grid[r][c] == EMPTY:
                    self.grid[r][c] = TRAP
                    self.traps.add((r, c))
                    placed_t += 1

            return  # success

        self._fallback()

    def _fallback(self):
        self.grid       = [[EMPTY] * GRID_COLS for _ in range(GRID_ROWS)]
        self.human_gems = {}
        self.ai_gems    = {}
        self.traps      = set()
        self.grid[self.goal[0]][self.goal[1]] = GOAL
        interior = [
            (r, c) for r in range(2, 13) for c in range(2, 13)
            if (r, c) not in ((0, 0), self.goal)
        ]
        for r, c in random.sample(interior, 10):
            self.grid[r][c] = WALL
        n_pairs = NUM_GEMS // 2
        p_placed = 0
        attempts = 0
        while p_placed < n_pairs and attempts < 1000:
            attempts += 1
            r = random.randint(0, GRID_ROWS - 1)
            c = random.randint(0, GRID_COLS - 1)
            if self.grid[r][c] != EMPTY:
                continue
            val = random.randint(2, MAX_GEM_ENERGY)
            self.grid[r][c]         = GEM_BOTH
            self.human_gems[(r, c)] = val
            self.ai_gems[(r, c)]    = val
            p_placed += 1
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == EMPTY and len(self.traps) < 10:
                    if random.random() < 0.08:
                        self.grid[r][c] = TRAP
                        self.traps.add((r, c))

    def _reachable(self, start, goal):
        q   = deque([start])
        vis = {start}
        while q:
            r, c = q.popleft()
            if (r, c) == goal:
                return True
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS
                        and (nr, nc) not in vis
                        and self.grid[nr][nc] != WALL):
                    vis.add((nr, nc))
                    q.append((nr, nc))
        return False

    # ── Interface ─────────────────────────────────────────────
    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS

    def is_walkable(self, pos):
        r, c = pos
        return self.grid[r][c] != WALL

    def clone(self):
        n             = GridWorld.__new__(GridWorld)
        n.grid        = copy.deepcopy(self.grid)
        n.human_gems  = copy.deepcopy(self.human_gems)
        n.ai_gems     = copy.deepcopy(self.ai_gems)
        n.traps       = copy.deepcopy(self.traps)
        n.goal        = self.goal
        return n