"""Simple AI for Farkle.

Decision: each turn, after a successful keep, the AI must decide whether
to bank the round score or push for more. Strategy: bank when the round
score crosses a difficulty-dependent threshold, OR when remaining dice
count is too risky for the current round score.
"""
from typing import List

import farkle as farkle_mod


# (bank_threshold, fewer-dice-bank-multiplier)
DIFFICULTY = {
    "easy":   (200, 1.0),    # easy AI banks early, often loses
    "normal": (350, 1.2),    # solid play
    "hard":   (500, 1.4),    # pushes harder, banks high
}


def best_keep(roll: List[int]) -> List[int]:
    """Pick the highest-scoring full-keep from a roll."""
    _, keep = farkle_mod.best_score_subset(roll)
    return keep


def should_bank(round_score: int, dice_left: int, total_score: int,
                target: int, difficulty: str = "normal") -> bool:
    """Decide whether to bank the round score (vs roll the remaining dice).

    `dice_left` is the number of dice that would be rolled next if we don't
    bank. If 0, hot dice → roll all 6 (don't bank).
    """
    if dice_left == 0:
        return False  # hot dice, free reroll
    cfg = DIFFICULTY.get(difficulty, DIFFICULTY["normal"])
    threshold, multiplier = cfg
    # If banking wins the game, always bank.
    if total_score + round_score >= target:
        return True
    # Adjust threshold by remaining dice — fewer dice = more risk.
    risk_factor = {1: 0.4, 2: 0.6, 3: 0.85, 4: 1.0, 5: 1.1, 6: 1.2}.get(
        dice_left, 1.0)
    effective = threshold * risk_factor / multiplier
    return round_score >= effective
