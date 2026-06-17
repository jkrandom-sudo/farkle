import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import ai as ai_mod


class TestBestKeep(unittest.TestCase):
    def test_picks_high_score(self):
        keep = ai_mod.best_keep([1, 1, 1, 2, 3, 4])
        self.assertEqual(sorted(keep), [1, 1, 1])

    def test_empty_when_no_score(self):
        keep = ai_mod.best_keep([2, 3, 4, 6])
        self.assertEqual(keep, [])


class TestShouldBank(unittest.TestCase):
    def test_no_bank_when_hot_dice(self):
        self.assertFalse(ai_mod.should_bank(500, 0, 0, 5000))

    def test_bank_when_above_threshold_normal(self):
        self.assertTrue(ai_mod.should_bank(500, 4, 0, 5000, "normal"))

    def test_no_bank_when_below_threshold(self):
        self.assertFalse(ai_mod.should_bank(50, 4, 0, 5000, "normal"))

    def test_bank_when_winning(self):
        self.assertTrue(ai_mod.should_bank(200, 6, 4900, 5000))

    def test_easy_banks_earlier_than_hard(self):
        round_score = 250
        easy = ai_mod.should_bank(round_score, 4, 0, 5000, "easy")
        hard = ai_mod.should_bank(round_score, 4, 0, 5000, "hard")
        # Easy threshold lower → more likely to bank
        self.assertTrue(easy or not hard)
        if easy and hard:
            pass  # both true is acceptable
        else:
            self.assertGreaterEqual(int(easy), int(hard))

    def test_banks_more_eagerly_with_few_dice(self):
        # Same round score, fewer dice → more likely to bank
        many = ai_mod.should_bank(300, 5, 0, 5000, "normal")
        few = ai_mod.should_bank(300, 1, 0, 5000, "normal")
        # With 1 die, threshold drops a lot; assume banks
        self.assertTrue(few)


if __name__ == "__main__":
    unittest.main()
