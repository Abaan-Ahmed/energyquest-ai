# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  ai/genetic.py
# ─────────────────────────────────────────────────────────────
import random
import time
from config.settings import START_ENERGY, MOVE_COST, TRAP_COST

POP_SIZE          = 100
GENERATIONS       = 80
CHROMOSOME_LENGTH = 55
MUTATION_RATE     = 0.12
ELITE_COUNT       = 12
TOURNAMENT_K      = 5

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def _simulate(chromosome, start, goal, grid):
    """
    Run chromosome through grid; return fitness.
    Only grid.ai_gems are counted — AI cannot collect human gems.
    """
    pos       = start
    energy    = START_ENERGY
    collected = set()

    for gene in chromosome:
        dr, dc = MOVES[gene]
        nxt = (pos[0] + dr, pos[1] + dc)

        if not grid.in_bounds(nxt) or not grid.is_walkable(nxt):
            continue

        energy -= MOVE_COST
        if nxt in grid.traps:
            energy -= TRAP_COST
        if nxt in grid.ai_gems and nxt not in collected:
            energy += grid.ai_gems[nxt]
            collected.add(nxt)

        pos = nxt

        if energy <= 0:
            break

    if pos == goal and energy > 0:
        return float(energy)
    dist = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    return -100.0 - dist * 2.0


def _tournament(pop, fitnesses):
    candidates = random.sample(range(len(pop)), TOURNAMENT_K)
    best_idx   = max(candidates, key=lambda i: fitnesses[i])
    return pop[best_idx]


def _crossover(p1, p2):
    a, b = sorted(random.sample(range(CHROMOSOME_LENGTH), 2))
    return p1[:a] + p2[a:b] + p1[b:]


def _mutate(chromo):
    if random.random() < MUTATION_RATE:
        idx         = random.randint(0, CHROMOSOME_LENGTH - 1)
        chromo[idx] = random.randint(0, 3)
    return chromo


def genetic_algorithm(start, goal, grid):
    t0 = time.perf_counter()

    pop = [[random.randint(0, 3) for _ in range(CHROMOSOME_LENGTH)]
           for _ in range(POP_SIZE)]

    best_chromo = pop[0]
    best_fit    = _simulate(best_chromo, start, goal, grid)

    for _gen in range(GENERATIONS):
        fitnesses = [_simulate(c, start, goal, grid) for c in pop]

        gen_best = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best] > best_fit:
            best_fit    = fitnesses[gen_best]
            best_chromo = pop[gen_best][:]

        sorted_idx = sorted(range(len(pop)), key=lambda i: -fitnesses[i])
        next_gen   = [pop[i][:] for i in sorted_idx[:ELITE_COUNT]]

        while len(next_gen) < POP_SIZE:
            p1    = _tournament(pop, fitnesses)
            p2    = _tournament(pop, fitnesses)
            child = _mutate(_crossover(p1, p2))
            next_gen.append(child)

        pop = next_gen

    # Convert best chromosome to path
    path      = []
    pos       = start
    energy    = START_ENERGY
    collected = set()

    for gene in best_chromo:
        dr, dc = MOVES[gene]
        nxt = (pos[0] + dr, pos[1] + dc)

        if not grid.in_bounds(nxt) or not grid.is_walkable(nxt):
            continue

        energy -= MOVE_COST
        if nxt in grid.traps:
            energy -= TRAP_COST
        if nxt in grid.ai_gems and nxt not in collected:
            energy += grid.ai_gems[nxt]
            collected.add(nxt)

        path.append(nxt)
        pos = nxt

        if energy <= 0:
            break

    return {
        "path":     path,
        "energy":   max(0, energy),
        "expanded": POP_SIZE * GENERATIONS,
        "time":     time.perf_counter() - t0,
    }
