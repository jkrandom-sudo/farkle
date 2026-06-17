import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import farkle as farkle_mod


class TestScoreDice(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(farkle_mod.score_dice([]), (0, True))

    def test_single_one(self):
        self.assertEqual(farkle_mod.score_dice([1]), (100, True))

    def test_single_five(self):
        self.assertEqual(farkle_mod.score_dice([5]), (50, True))

    def test_single_non_scoring(self):
        self.assertEqual(farkle_mod.score_dice([2]), (0, False))
        self.assertEqual(farkle_mod.score_dice([3]), (0, False))

    def test_two_ones(self):
        self.assertEqual(farkle_mod.score_dice([1, 1]), (200, True))

    def test_one_and_five(self):
        self.assertEqual(farkle_mod.score_dice([1, 5]), (150, True))

    def test_three_ones(self):
        self.assertEqual(farkle_mod.score_dice([1, 1, 1]), (1000, True))

    def test_three_twos(self):
        self.assertEqual(farkle_mod.score_dice([2, 2, 2]), (200, True))

    def test_three_sixes(self):
        self.assertEqual(farkle_mod.score_dice([6, 6, 6]), (600, True))

    def test_four_of_a_kind(self):
        self.assertEqual(farkle_mod.score_dice([3, 3, 3, 3]), (600, True))
        self.assertEqual(farkle_mod.score_dice([1, 1, 1, 1]), (2000, True))

    def test_five_of_a_kind(self):
        self.assertEqual(farkle_mod.score_dice([4, 4, 4, 4, 4]), (1600, True))
        self.assertEqual(farkle_mod.score_dice([1, 1, 1, 1, 1]), (4000, True))

    def test_six_of_a_kind(self):
        self.assertEqual(farkle_mod.score_dice([2, 2, 2, 2, 2, 2]), (1600, True))
        self.assertEqual(farkle_mod.score_dice([1, 1, 1, 1, 1, 1]), (8000, True))

    def test_straight(self):
        self.assertEqual(farkle_mod.score_dice([1, 2, 3, 4, 5, 6]), (1500, True))
        self.assertEqual(farkle_mod.score_dice([6, 5, 4, 3, 2, 1]), (1500, True))

    def test_three_pairs(self):
        self.assertEqual(farkle_mod.score_dice([2, 2, 4, 4, 6, 6]), (1500, True))
        self.assertEqual(farkle_mod.score_dice([1, 1, 5, 5, 3, 3]), (1500, True))

    def test_two_triplets(self):
        self.assertEqual(farkle_mod.score_dice([2, 2, 2, 3, 3, 3]), (2500, True))

    def test_three_kind_plus_singles(self):
        # 1,1,1 + 5 = 1000 + 50
        self.assertEqual(farkle_mod.score_dice([1, 1, 1, 5]), (1050, True))

    def test_leftover_die_invalidates(self):
        # 1,1,1 + 2 → leftover 2 is non-scoring, not a valid keep
        self.assertEqual(farkle_mod.score_dice([1, 1, 1, 2]), (0, False))

    def test_pair_plus_single_one(self):
        # 2,2,1 → only the 1 scores; the pair of 2s is leftover
        self.assertEqual(farkle_mod.score_dice([2, 2, 1]), (0, False))

    def test_two_fives(self):
        self.assertEqual(farkle_mod.score_dice([5, 5]), (100, True))

    def test_invalid_face(self):
        self.assertEqual(farkle_mod.score_dice([7]), (0, False))


class TestIsFarkle(unittest.TestCase):
    def test_farkle_2346(self):
        self.assertTrue(farkle_mod.is_farkle([2, 3, 4, 6]))

    def test_farkle_pair_only(self):
        self.assertTrue(farkle_mod.is_farkle([2, 2]))

    def test_not_farkle_with_one(self):
        self.assertFalse(farkle_mod.is_farkle([1, 2, 3]))

    def test_not_farkle_with_five(self):
        self.assertFalse(farkle_mod.is_farkle([5, 2, 3]))

    def test_not_farkle_with_three_kind(self):
        self.assertFalse(farkle_mod.is_farkle([3, 3, 3]))

    def test_not_farkle_with_straight(self):
        self.assertFalse(farkle_mod.is_farkle([1, 2, 3, 4, 5, 6]))

    def test_not_farkle_with_three_pairs(self):
        self.assertFalse(farkle_mod.is_farkle([2, 2, 4, 4, 6, 6]))


class TestBestSubset(unittest.TestCase):
    def test_picks_three_ones(self):
        score, keep = farkle_mod.best_score_subset([1, 1, 1, 2, 3])
        self.assertEqual(score, 1000)
        self.assertEqual(sorted(keep), [1, 1, 1])

    def test_picks_one_plus_five(self):
        score, keep = farkle_mod.best_score_subset([1, 5, 2, 3])
        self.assertEqual(score, 150)

    def test_picks_straight_when_present(self):
        score, _ = farkle_mod.best_score_subset([1, 2, 3, 4, 5, 6])
        self.assertEqual(score, 1500)

    def test_picks_three_pairs(self):
        score, _ = farkle_mod.best_score_subset([2, 2, 4, 4, 6, 6])
        self.assertEqual(score, 1500)

    def test_returns_zero_when_no_score(self):
        score, keep = farkle_mod.best_score_subset([2, 3, 4, 6])
        self.assertEqual(score, 0)
        self.assertEqual(keep, [])

    def test_picks_three_kind_plus_one(self):
        score, _ = farkle_mod.best_score_subset([3, 3, 3, 1, 2, 4])
        # 333=300, +1=100 -> 400
        self.assertEqual(score, 400)


class TestCanKeep(unittest.TestCase):
    def test_valid_keep(self):
        self.assertTrue(farkle_mod.can_keep([1, 2, 3, 5], [1, 5]))

    def test_keep_not_subset_of_roll(self):
        self.assertFalse(farkle_mod.can_keep([1, 2, 3], [1, 1]))

    def test_keep_with_leftover_invalid(self):
        # 2 is not a scoring die alone
        self.assertFalse(farkle_mod.can_keep([1, 2, 5], [1, 2]))

    def test_remove_dice(self):
        out = farkle_mod.remove_dice([1, 1, 5, 2], [1, 5])
        self.assertEqual(sorted(out), [1, 2])


if __name__ == "__main__":
    unittest.main()
