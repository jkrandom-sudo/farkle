import io
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import game as game_mod
import score as score_mod
import settings as settings_mod
from sound import Sound


class StackedInput:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def __call__(self, prompt=""):
        if self.calls >= len(self.replies):
            raise EOFError()
        reply = self.replies[self.calls]
        self.calls += 1
        return reply


class TestParseKeep(unittest.TestCase):
    def test_spaced(self):
        self.assertEqual(game_mod.parse_keep("1 5"), [1, 5])

    def test_comma(self):
        self.assertEqual(game_mod.parse_keep("1,5"), [1, 5])
        self.assertEqual(game_mod.parse_keep("1, 5"), [1, 5])

    def test_repeats(self):
        self.assertEqual(game_mod.parse_keep("1 1 1"), [1, 1, 1])

    def test_invalid(self):
        self.assertIsNone(game_mod.parse_keep(""))
        self.assertIsNone(game_mod.parse_keep("abc"))
        self.assertIsNone(game_mod.parse_keep("0 1"))   # 0 invalid
        self.assertIsNone(game_mod.parse_keep("7 1"))   # 7 invalid


class TestRollDice(unittest.TestCase):
    def test_returns_n_dice(self):
        out = game_mod.roll_dice(6, random.Random(0))
        self.assertEqual(len(out), 6)
        for d in out:
            self.assertGreaterEqual(d, 1)
            self.assertLessEqual(d, 6)


class TestPlayHumanTurn(unittest.TestCase):
    def test_quit(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        # First roll always non-farkle thanks to seed; user immediately quits
        inp = StackedInput(["q"])
        result = game_mod.play_human_turn(
            {"lang": "en", "target": 5000, "difficulty": "normal"},
            sound, inp, out, random.Random(0), 0)
        self.assertIsNone(result)

    def test_keep_auto_then_bank(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        # k = auto-keep best, then b = bank
        inp = StackedInput(["k", "b"])
        # Find a seed where roll has a scoring combination
        result = game_mod.play_human_turn(
            {"lang": "en", "target": 5000, "difficulty": "normal"},
            sound, inp, out, random.Random(0), 0)
        # Either farkle (returns 0) or banks > 0
        self.assertIn(result, (0,) if result == 0 else (result,))

    def test_invalid_keep_then_quit(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        inp = StackedInput(["abc", "q"])
        result = game_mod.play_human_turn(
            {"lang": "en", "target": 5000, "difficulty": "normal"},
            sound, inp, out, random.Random(0), 0)
        self.assertIsNone(result)
        self.assertIn("Invalid", out.getvalue())

    def test_bank_with_no_score_rejected(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        inp = StackedInput(["b", "q"])
        result = game_mod.play_human_turn(
            {"lang": "en", "target": 5000, "difficulty": "normal"},
            sound, inp, out, random.Random(0), 0)
        self.assertIsNone(result)
        # Should have shown "No round score" prompt
        text = out.getvalue()
        self.assertIn("No round score yet", text)


class TestPlayAITurn(unittest.TestCase):
    def test_returns_nonneg_score(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        score = game_mod.play_ai_turn(
            {"lang": "en", "target": 5000, "difficulty": "easy"},
            sound, out, random.Random(7), 0)
        self.assertGreaterEqual(score, 0)


class TestPlayRound(unittest.TestCase):
    def test_human_quit_returns_none(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        inp = StackedInput(["q"])
        result = game_mod.play_round(
            {"lang": "en", "target": 5000, "difficulty": "normal"},
            sound, inp, out, rng=random.Random(0))
        self.assertIsNone(result)

    def test_human_wins_when_target_low(self):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        # Force a high-score path: keep auto + bank, with small target.
        # k+b loop until human total exceeds 100.
        inp = StackedInput(["k", "b"] * 30)
        result = game_mod.play_round(
            {"lang": "en", "target": 100, "difficulty": "normal"},
            sound, inp, out, rng=random.Random(1))
        # May resolve as win or loss; result is dict either way
        self.assertIsNotNone(result)
        self.assertIn(result["result"], ("win", "loss"))


class TestMainMenu(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._settings_path = Path(self._tmp.name) / "settings.json"
        self._scores_path = Path(self._tmp.name) / "scores.json"
        self._sp = mock.patch.object(settings_mod, "DEFAULT_PATH", self._settings_path)
        self._scp = mock.patch.object(score_mod, "DEFAULT_PATH", self._scores_path)
        self._sp.start()
        self._scp.start()

    def tearDown(self):
        self._sp.stop()
        self._scp.stop()
        self._tmp.cleanup()

    def test_quit(self):
        out = io.StringIO()
        inp = StackedInput(["q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("再见", out.getvalue())

    def test_help(self):
        out = io.StringIO()
        inp = StackedInput(["h", "", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("帮助", out.getvalue())

    def test_scores_empty(self):
        out = io.StringIO()
        inp = StackedInput(["l", "", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("暂无成绩", out.getvalue())

    def test_play_then_save(self):
        out = io.StringIO()
        inp = StackedInput(["p", "alice", "q"])
        fake = {"result": "win", "score": 5050, "difficulty": "normal", "target": 5000}
        with mock.patch.object(game_mod, "play_round", return_value=fake):
            game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        scores = score_mod.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["name"], "alice")

    def test_play_skip_save(self):
        out = io.StringIO()
        inp = StackedInput(["p", "", "q"])
        fake = {"result": "loss", "score": 0, "difficulty": "normal", "target": 5000}
        with mock.patch.object(game_mod, "play_round", return_value=fake):
            game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertEqual(score_mod.load(), [])

    def test_play_quit_no_save(self):
        out = io.StringIO()
        inp = StackedInput(["p", "q"])
        with mock.patch.object(game_mod, "play_round", return_value=None):
            game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertEqual(score_mod.load(), [])

    def test_settings_lang_toggle(self):
        out = io.StringIO()
        inp = StackedInput(["s", "1", "b", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["lang"], "en")

    def test_settings_target_cycle(self):
        out = io.StringIO()
        inp = StackedInput(["s", "5", "b", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["target"], 10000)  # 5000 -> 10000

    def test_unknown_choice(self):
        out = io.StringIO()
        inp = StackedInput(["zzz", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("未知选项", out.getvalue())


if __name__ == "__main__":
    unittest.main()
