"""Four IGT decks with independently shuffled, replenished loss blocks."""

import random
import config

_remaining_losses = {deck: [] for deck in range(1, 5)}


def reset_decks():
    """Discard partial loss blocks before starting another participant session."""
    for losses in _remaining_losses.values():
        losses.clear()


def gain_loss(decknumber, *, rng=None):
    """Return the configured gain and next loss for deck 1–4.

    Each complete block contains exactly the configured losses, in random order.
    The optional random generator supports reproducible tests without changing
    the application's default randomness.
    """
    if (
        isinstance(decknumber, bool)
        or not isinstance(decknumber, int)
        or decknumber not in _remaining_losses
    ):
        raise ValueError("decknumber must be an integer from 1 to 4")
    losses = _remaining_losses[decknumber]
    if not losses:
        configured = getattr(config, f"igt_deck{decknumber}_all_losses")
        if not configured:
            raise ValueError("each deck must contain at least one loss")
        rng = random if rng is None else rng
        losses.extend(rng.sample(configured, len(configured)))
    return getattr(config, f"igt_deck{decknumber}_gain"), losses.pop()
