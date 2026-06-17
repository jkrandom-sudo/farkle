import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import i18n as i18n_mod
import score as score_mod
import settings as settings_mod
from sound import Sound


class TestI18n(unittest.TestCase):
    def test_zh_and_en_keys_match(self):
        zh_keys = set(i18n_mod.STRINGS["zh"].keys())
        en_keys = set(i18n_mod.STRINGS["en"].keys())
        self.assertEqual(zh_keys, en_keys, msg=f"missing: {zh_keys ^ en_keys}")

    def test_t_basic(self):
        self.assertEqual(i18n_mod.t("zh", "on"), "开")
        self.assertEqual(i18n_mod.t("en", "on"), "on")

    def test_t_format(self):
        s = i18n_mod.t("en", "round_score", score=400)
        self.assertIn("400", s)

    def test_t_missing_key_falls_back(self):
        self.assertEqual(i18n_mod.t("zh", "no_such_key_xyz"), "no_such_key_xyz")


class TestSettings(unittest.TestCase):
    def test_load_returns_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            s = settings_mod.load(path)
            for k, v in settings_mod.DEFAULTS.items():
                self.assertEqual(s[k], v)

    def test_save_then_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            s = settings_mod.load(path)
            s["lang"] = "en"
            s["sound"] = False
            s["volume"] = 2
            s["difficulty"] = "hard"
            s["target"] = 10000
            settings_mod.save(s, path)
            s2 = settings_mod.load(path)
            self.assertEqual(s2["lang"], "en")
            self.assertEqual(s2["target"], 10000)
            self.assertEqual(s2["difficulty"], "hard")

    def test_load_repairs_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "settings.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"lang": "fr", "target": 999, "difficulty": "extreme",
                           "sound": "yes"}, f)
            s = settings_mod.load(path)
            self.assertEqual(s["lang"], "zh")
            self.assertEqual(s["target"], 5000)
            self.assertEqual(s["difficulty"], "normal")
            self.assertTrue(s["sound"])

    def test_cycle_difficulty(self):
        s = {"difficulty": "easy"}
        settings_mod.cycle_difficulty(s)
        self.assertEqual(s["difficulty"], "normal")

    def test_cycle_target(self):
        s = {"target": 3000}
        settings_mod.cycle_target(s)
        self.assertEqual(s["target"], 5000)
        settings_mod.cycle_target(s)
        self.assertEqual(s["target"], 10000)
        settings_mod.cycle_target(s)
        self.assertEqual(s["target"], 3000)


class TestScore(unittest.TestCase):
    def test_load_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "scores.json"
            self.assertEqual(score_mod.load(path), [])
            score_mod.add("alice", 5000, "normal", 5000, path=path)
            score_mod.add("bob", 10000, "hard", 10000, path=path)
            scores = score_mod.load(path)
            self.assertEqual(len(scores), 2)
            self.assertEqual(scores[0]["name"], "bob")

    def test_truncated(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "scores.json"
            for i in range(20):
                score_mod.add(f"p{i}", i * 100, "normal", 5000, path=path)
            self.assertEqual(len(score_mod.load(path)), score_mod.MAX_ENTRIES)


class TestSound(unittest.TestCase):
    def test_disabled(self):
        out = io.StringIO()
        s = Sound(enabled=False, volume=2, output=out)
        s.roll()
        s.win()
        self.assertEqual(out.getvalue(), "")

    def test_zero_volume(self):
        out = io.StringIO()
        s = Sound(enabled=True, volume=0, output=out)
        s.roll()
        self.assertEqual(out.getvalue(), "")

    def test_emits_bells(self):
        out = io.StringIO()
        s = Sound(enabled=True, volume=2, output=out)
        s.roll()       # 1*2 = 2
        s.farkle()     # 2*2 = 4
        s.hot_dice()   # 3*2 = 6
        self.assertEqual(out.getvalue().count("\a"), 12)

    def test_volume_clamped(self):
        self.assertEqual(Sound(volume=99).volume, 3)
        self.assertEqual(Sound(volume=-5).volume, 0)


if __name__ == "__main__":
    unittest.main()
