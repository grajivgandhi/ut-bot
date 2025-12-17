import math


def round_step(qty: float, step: float) -> float:
    """Round a quantity down to the nearest step size."""
    if step <= 0:
        return qty
    return math.floor(qty / step) * step
