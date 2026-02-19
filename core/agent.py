from config.settings import *

class Agent:
    def __init__(self):
        self.position = (0, 0)
        self.energy = START_ENERGY
        self.path = []

    def move(self, new_pos, grid):
        self.position = new_pos
        self.energy -= MOVE_COST

        if new_pos in grid.gems:
            self.energy += grid.gems.pop(new_pos)

        if new_pos in grid.traps:
            self.energy -= TRAP_COST
