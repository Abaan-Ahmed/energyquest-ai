def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def energy_aware(state, goal, energy):
    """
    Innovative heuristic:
    distance + penalty if energy is low
    """
    base = manhattan(state, goal)
    if energy < base:
        return base + 10
    return base

def risk_aware(state, goal, nearby_traps):
    """
    Penalizes paths near traps
    """
    return manhattan(state, goal) + nearby_traps * 2
