"""Balloon burst probability, independent of desktop input and presentation."""

import random
import config


def burst_or_not(blow_num, *, capacity=None, rng=None):
    """Return 0/1 with the original conditional hazard 1/(capacity+1-pumps)."""
    capacity = config.bart_max_balloon_capacity if capacity is None else capacity
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
        raise ValueError("capacity must be a positive integer")
    if isinstance(blow_num, bool) or not isinstance(blow_num, int) or not 1 <= blow_num <= capacity:
        raise ValueError("pump number must be between 1 and capacity")
    probability = 1 / (capacity + 1 - blow_num)
    rng = random if rng is None else rng
    return rng.choices([0, 1], weights=(1 - probability, probability), k=1)[0]
