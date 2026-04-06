# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  ai/heuristics.py
# ─────────────────────────────────────────────────────────────
from config.settings import MOVE_COST


def manhattan(a, b):
    """Manhattan distance — admissible, consistent heuristic for grid search."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def energy_lower_bound(pos, goal):
    """
    Minimum energy that must be spent to reach goal from pos.
    = manhattan distance × move cost  (ignores traps and gems).
    This is admissible because:
      • every step costs at least MOVE_COST
      • the minimum steps is the Manhattan distance
      • gems may reduce actual cost further (heuristic under-estimates → safe)
    """
    return manhattan(pos, goal) * MOVE_COST
