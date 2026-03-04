import random
import time
from config.settings import START_ENERGY, MOVE_COST, TRAP_COST

# ----------------------------------------------------
# PARAMETERS (TUNEABLE)
# ----------------------------------------------------
POP_SIZE = 80
GENERATIONS = 60
CHROMOSOME_LENGTH = 50
MUTATION_RATE = 0.15
ELITE_COUNT = 10

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP  # DOWN  # LEFT  # RIGHT


# ----------------------------------------------------
# SIMULATION FUNCTION
# ----------------------------------------------------
def simulate(chromosome, start, goal, grid):

    pos = start
    energy = START_ENERGY
    collected = set()

    for gene in chromosome:

        dx, dy = MOVES[gene]
        nxt = (pos[0] + dx, pos[1] + dy)

        if not grid.in_bounds(nxt):
            continue
        if not grid.is_walkable(nxt):
            continue

        # Movement cost
        energy -= MOVE_COST

        # Trap penalty
        if nxt in grid.traps:
            energy -= TRAP_COST

        # Gem reward
        if nxt in grid.gems and nxt not in collected:
            energy += grid.gems[nxt]
            collected.add(nxt)

        pos = nxt

        if energy <= 0:
            break

    # FITNESS
    if pos == goal and energy > 0:
        return energy  # maximize remaining energy
    else:
        # Penalize not reaching goal
        dist = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        return -100 - dist


# ----------------------------------------------------
# GENETIC ALGORITHM
# ----------------------------------------------------
def genetic_algorithm(start, goal, grid):

    start_time = time.time()

    # Create initial population
    population = [
        [random.randint(0, 3) for _ in range(CHROMOSOME_LENGTH)]
        for _ in range(POP_SIZE)
    ]

    for _ in range(GENERATIONS):

        # Sort by fitness (descending)
        population.sort(
            key=lambda chromo: simulate(chromo, start, goal, grid), reverse=True
        )

        next_generation = population[:ELITE_COUNT]

        # Generate rest by crossover + mutation
        while len(next_generation) < POP_SIZE:

            parent1 = random.choice(population[:30])
            parent2 = random.choice(population[:30])

            cut = random.randint(0, CHROMOSOME_LENGTH - 1)
            child = parent1[:cut] + parent2[cut:]

            # Mutation
            if random.random() < MUTATION_RATE:
                idx = random.randint(0, CHROMOSOME_LENGTH - 1)
                child[idx] = random.randint(0, 3)

            next_generation.append(child)

        population = next_generation

    # Get best chromosome
    best = max(population, key=lambda chromo: simulate(chromo, start, goal, grid))

    # Convert chromosome to actual path
    path = []
    pos = start
    collected = set()
    energy = START_ENERGY

    for gene in best:
        dx, dy = MOVES[gene]
        nxt = (pos[0] + dx, pos[1] + dy)

        if not grid.in_bounds(nxt):
            continue
        if not grid.is_walkable(nxt):
            continue

        path.append(nxt)
        pos = nxt

        energy -= MOVE_COST

        if nxt in grid.traps:
            energy -= TRAP_COST

        if nxt in grid.gems and nxt not in collected:
            energy += grid.gems[nxt]
            collected.add(nxt)

        if energy <= 0:
            break

    return {
        "path": path,
        "energy": energy,
        "expanded": POP_SIZE * GENERATIONS,
        "time": time.time() - start_time,
    }
