# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  ai/search.py
#
#  BFS  – uninformed baseline; finds shortest path (fewest steps)
#  A*   – energy-aware informed search; maximises remaining energy
#         g(n) = energy consumed = START_ENERGY - current_energy
#         h(n) = manhattan_dist x MOVE_COST  (admissible lower bound)
#         Minimising f = g + h  equivalent to maximising remaining energy
# ─────────────────────────────────────────────────────────────
from collections import deque
import heapq
import time
from config.settings import MOVE_COST, TRAP_COST, START_ENERGY
from ai.heuristics import manhattan

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def _apply(pos, energy, grid, collected):
    """
    Return (new_energy, new_collected) after the AI steps onto pos.
    Only grid.ai_gems are considered — AI cannot collect human gems.
    """
    energy -= MOVE_COST
    if pos in grid.traps:
        energy -= TRAP_COST
    if pos in grid.ai_gems and pos not in collected:
        energy += grid.ai_gems[pos]
        collected = collected | {pos}
    return energy, collected


# ─────────────────────────────────────────────────────────────
#  BFS  –  shortest-path uninformed baseline
# ─────────────────────────────────────────────────────────────
def bfs(start, goal, grid):
    t0       = time.perf_counter()
    frontier = deque([(start, [])])
    visited  = {start}
    expanded = 0

    while frontier:
        pos, path = frontier.popleft()
        expanded += 1

        if pos == goal:
            # Simulate energy along the found path using only AI gems
            energy    = START_ENERGY
            collected = frozenset()
            for p in path:
                energy, collected = _apply(p, energy, grid, collected)
                if energy <= 0:
                    energy = 0
                    break
            return {
                "path":     path,
                "energy":   energy,
                "expanded": expanded,
                "time":     time.perf_counter() - t0,
            }

        for dr, dc in MOVES:
            nxt = (pos[0] + dr, pos[1] + dc)
            if (grid.in_bounds(nxt) and grid.is_walkable(nxt)
                    and nxt not in visited):
                visited.add(nxt)
                frontier.append((nxt, path + [nxt]))

    return None


# ─────────────────────────────────────────────────────────────
#  A*  –  energy-aware informed search
# ─────────────────────────────────────────────────────────────
def astar(start, goal, grid):
    t0      = time.perf_counter()
    counter = 0
    h0      = manhattan(start, goal) * MOVE_COST
    heap    = [(h0, counter, start, START_ENERGY, frozenset(), [])]
    best    = {}
    expanded = 0

    while heap:
        f, _, pos, energy, collected, path = heapq.heappop(heap)
        expanded += 1

        if energy <= 0:
            continue

        if pos == goal:
            return {
                "path":     path,
                "energy":   energy,
                "expanded": expanded,
                "time":     time.perf_counter() - t0,
            }

        state  = (pos, collected)
        g_here = START_ENERGY - energy

        if state in best and best[state] <= g_here:
            continue
        best[state] = g_here

        for dr, dc in MOVES:
            nxt = (pos[0] + dr, pos[1] + dc)
            if not grid.in_bounds(nxt) or not grid.is_walkable(nxt):
                continue

            new_e, new_col = _apply(nxt, energy, grid, collected)
            if new_e <= 0:
                continue

            new_g = START_ENERGY - new_e
            h     = manhattan(nxt, goal) * MOVE_COST
            new_f = new_g + h

            counter += 1
            heapq.heappush(heap,
                (new_f, counter, nxt, new_e, new_col, path + [nxt]))

    return None
