from config.settings import *


class Agent:
    def __init__(self):
        self.position = (0, 0)
        self.energy = START_ENERGY
        self.path = []
        self.collected_gems = set()

    def move(self, new_pos, grid):
        self.position = new_pos
        self.energy -= MOVE_COST

        # Trap penalty
        if new_pos in grid.traps:
            self.energy -= TRAP_COST

        # Gem reward (agent-specific)
        if new_pos in grid.gems and new_pos not in self.collected_gems:
            self.energy += grid.gems[new_pos]
            self.collected_gems.add(new_pos)
