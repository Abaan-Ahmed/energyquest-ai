from collections import deque
import heapq
import time
from config.settings import MOVE_COST, TRAP_COST, START_ENERGY
from ai.heuristics import manhattan

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# -----------------------------------------
# ENERGY UPDATE
# -----------------------------------------
def apply_energy(pos, energy, grid, collected):
    energy -= MOVE_COST

    if pos in grid.traps:
        energy -= TRAP_COST

    if pos in grid.gems and pos not in collected:
        energy += grid.gems[pos]
        collected = collected | {pos}

    return energy, collected


# -----------------------------------------
# BFS (Energy-Aware, Optimized)
# -----------------------------------------
def bfs(start, goal, grid):
    start_time = time.time()

    frontier = deque()
    frontier.append((start, START_ENERGY, frozenset(), []))

    visited = set()
    expanded = 0

    while frontier:
        pos, energy, collected, path = frontier.popleft()
        expanded += 1

        if energy <= 0:
            continue

        if pos == goal:
            return {
                "path": path,
                "energy": energy,
                "expanded": expanded,
                "time": time.time() - start_time,
            }

        state = (pos, energy, collected)
        if state in visited:
            continue
        visited.add(state)

        for dx, dy in MOVES:
            nxt = (pos[0] + dx, pos[1] + dy)

            if not grid.in_bounds(nxt):
                continue
            if not grid.is_walkable(nxt):
                continue

            new_energy, new_collected = apply_energy(nxt, energy, grid, collected)

            frontier.append((nxt, new_energy, new_collected, path + [nxt]))

    return None


# -----------------------------------------
# A* (Energy-Aware, Optimized)
# -----------------------------------------
def astar(start, goal, grid):
    start_time = time.time()

    pq = []
    counter = 0

    heapq.heappush(pq, (0, counter, start, START_ENERGY, frozenset(), []))

    visited = set()
    expanded = 0

    while pq:
        _, _, pos, energy, collected, path = heapq.heappop(pq)
        expanded += 1

        if energy <= 0:
            continue

        if pos == goal:
            return {
                "path": path,
                "energy": energy,
                "expanded": expanded,
                "time": time.time() - start_time,
            }

        state = (pos, energy, collected)
        if state in visited:
            continue
        visited.add(state)

        for dx, dy in MOVES:
            nxt = (pos[0] + dx, pos[1] + dy)

            if not grid.in_bounds(nxt):
                continue
            if not grid.is_walkable(nxt):
                continue

            new_energy, new_collected = apply_energy(nxt, energy, grid, collected)

            if new_energy <= 0:
                continue

            g = len(path) + 1
            h = manhattan(nxt, goal)
            f = g + h

            counter += 1
            heapq.heappush(
                pq, (f, counter, nxt, new_energy, new_collected, path + [nxt])
            )

    return None
