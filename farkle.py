"""Farkle scoring engine.

Standard scoring used here:
  Each 1 (not in 3+ of a kind):  100
  Each 5 (not in 3+ of a kind):   50
  Three 1s:                     1000
  Three Ns (N=2..6):            N * 100
  Four of a kind:                2 * three of a kind
  Five of a kind:                4 * three of a kind
  Six of a kind:                 8 * three of a kind
  Straight 1-2-3-4-5-6:         1500
  Three pairs:                  1500
  Two triplets (e.g. 222 333):  2500

A "valid keep" is a set of dice from a roll where every die contributes to a
scoring combination (no leftover non-scoring dice).
"""
from collections import Counter
from typing import List, Optional, Tuple


DICE_PER_ROLL = 6


def _three_kind_value(face: int) -> int:
    return 1000 if face == 1 else face * 100


def score_dice(dice: List[int]) -> Tuple[int, bool]:
    """Score a *complete* set of dice as the player wants them counted.

    Returns (points, all_dice_used). all_dice_used is True iff every die in
    `dice` contributes to a scoring combination — i.e. this is a valid
    "keep" set. If any die is leftover, returns (0, False).
    """
    if not dice:
        return (0, True)
    if not all(1 <= d <= 6 for d in dice):
        return (0, False)
    counts = Counter(dice)
    n = len(dice)

    # Straight 1-2-3-4-5-6
    if n == 6 and all(counts[f] == 1 for f in range(1, 7)):
        return (1500, True)

    # Three pairs (exactly 6 dice in three pairs)
    if n == 6 and len(counts) == 3 and all(v == 2 for v in counts.values()):
        return (1500, True)

    # Two triplets (exactly 6 dice in two triplets)
    if n == 6 and len(counts) == 2 and all(v == 3 for v in counts.values()):
        return (2500, True)

    # General case: walk faces and accumulate
    score = 0
    used = 0
    for face in range(1, 7):
        c = counts.get(face, 0)
        if c == 0:
            continue
        if c >= 3:
            base = _three_kind_value(face)
            mult = {3: 1, 4: 2, 5: 4, 6: 8}[c]
            score += base * mult
            used += c
        else:
            if face == 1:
                score += 100 * c
                used += c
            elif face == 5:
                score += 50 * c
                used += c
            # else: leftover, contributes nothing
    if used != n:
        return (0, False)
    return (score, True)


def is_farkle(dice: List[int]) -> bool:
    """Return True if no scoring combination exists in the rolled dice."""
    return best_score_subset(dice)[0] == 0


def best_score_subset(dice: List[int]) -> Tuple[int, List[int]]:
    """Find the highest-scoring valid subset of the given roll.

    Returns (best_score, best_keep_list). If no scoring subset exists,
    returns (0, []).
    """
    n = len(dice)
    best_score = 0
    best_keep: List[int] = []
    # Enumerate all non-empty subsets via bitmask (n <= 6)
    for mask in range(1, 1 << n):
        subset = [dice[i] for i in range(n) if mask & (1 << i)]
        sc, ok = score_dice(subset)
        if ok and sc > best_score:
            best_score = sc
            best_keep = subset
    return (best_score, best_keep)


def can_keep(roll: List[int], keep: List[int]) -> bool:
    """Check `keep` is a multiset-subset of `roll` and forms a valid scoring set."""
    rc = Counter(roll)
    kc = Counter(keep)
    for face, count in kc.items():
        if rc.get(face, 0) < count:
            return False
    _, ok = score_dice(keep)
    return ok


def remove_dice(roll: List[int], keep: List[int]) -> List[int]:
    """Return roll with `keep` dice removed (multiset)."""
    remaining = list(roll)
    for d in keep:
        remaining.remove(d)
    return remaining
