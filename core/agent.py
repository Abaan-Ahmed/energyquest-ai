# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  core/agent.py
# ─────────────────────────────────────────────────────────────
from config.settings import START_ENERGY, MOVE_COST, TRAP_COST
from core.grid import EMPTY, GEM, GEM_A


class Agent:
    def __init__(self):
        self.position       = (0, 0)
        self.energy         = START_ENERGY
        self.steps          = 0
        self.collected_gems = set()

    def move(self, new_pos, grid, own_gems: dict):
        """
        Move to new_pos, apply costs/rewards, return event string or None.

        own_gems  – the gem dict this agent is allowed to collect
                    (grid.human_gems for human, grid.ai_gems for AI).

        Paired-tile behaviour
        ─────────────────────
        Every gem tile starts with BOTH a gold and a purple gem (GEM_BOTH).
        When an agent collects their gem the cell is updated to reflect what
        remains:
          • partner gem still present  → show GEM (gold) or GEM_A (purple)
          • no gems left               → EMPTY
        This means the other agent can still visit and collect their gem later.
        """
        self.position = new_pos
        self.energy  -= MOVE_COST
        self.steps   += 1
        event = None

        if new_pos in grid.traps:
            self.energy -= TRAP_COST
            event = "trap"

        if new_pos in own_gems and new_pos not in self.collected_gems:
            self.energy += own_gems[new_pos]
            self.collected_gems.add(new_pos)
            del own_gems[new_pos]

            # Determine what remains on this tile for the partner agent.
            r, c = new_pos
            if new_pos in grid.human_gems:
                # AI just collected its purple gem; gold gem still here
                grid.grid[r][c] = GEM
            elif new_pos in grid.ai_gems:
                # Human just collected its gold gem; purple gem still here
                grid.grid[r][c] = GEM_A
            else:
                # Both gems collected – tile is now empty
                grid.grid[r][c] = EMPTY

            event = "gem"

        return event
