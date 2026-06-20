"""Farkle — main menu and game loop."""
import random
import sys
from typing import List, Optional

import ai as ai_mod
import farkle as farkle_mod
import score as score_mod
import settings as settings_mod
from i18n import t
from sound import Sound


class QuitGame(Exception):
    pass


def parse_keep(text: str) -> Optional[List[int]]:
    """Parse a keep input. Returns list of dice values, or None on bad input.

    Accepted: '1 5', '1,5', '1, 5', '1 1 1', etc. Empty -> None.
    """
    if not text:
        return None
    s = text.strip()
    if not s:
        return None
    for ch in ",;":
        s = s.replace(ch, " ")
    tokens = s.split()
    if not tokens or not all(tok.isdigit() for tok in tokens):
        return None
    vals = [int(tok) for tok in tokens]
    if not all(1 <= v <= 6 for v in vals):
        return None
    return vals


def roll_dice(n: int, rng: random.Random) -> List[int]:
    return [rng.randint(1, 6) for _ in range(n)]


def play_human_turn(s: dict, sound: Sound, input_func, output,
                    rng: random.Random, total_score: int) -> Optional[int]:
    """Play one human turn. Returns the points to bank (>=0), or None if quit."""
    lang = s.get("lang", "zh")
    target = int(s.get("target", 5000))

    def write(msg=""):
        output.write(msg + "\n")

    round_score = 0
    dice_left = farkle_mod.DICE_PER_ROLL
    write(t(lang, "your_turn"))

    while True:
        # Roll
        roll = roll_dice(dice_left, rng)
        sound.roll()
        write(t(lang, "rolled", dice=" ".join(str(d) for d in roll)))
        if farkle_mod.is_farkle(roll):
            write(t(lang, "farkle_msg"))
            sound.farkle()
            return 0
        # Selection sub-loop within this roll: keep at least one scoring die
        kept_this_roll: List[int] = []
        remaining = list(roll)
        invalid_attempts = 0
        max_invalid_attempts = 10
        while True:
            try:
                line = input_func(t(lang, "input_keep"))
            except EOFError:
                raise QuitGame()
            cmd = line.strip().lower()
            if cmd == "q":
                return None
            if cmd == "b":
                if round_score == 0 and not kept_this_roll:
                    write(t(lang, "no_score_yet"))
                    continue
                # Must keep at least one scoring die before banking THIS roll
                if not kept_this_roll:
                    write(t(lang, "must_keep_at_least_one"))
                    continue
                sound.bank()
                write(t(lang, "banked", score=round_score,
                        total=total_score + round_score))
                return round_score
            if cmd == "r":
                if not kept_this_roll:
                    write(t(lang, "must_keep_at_least_one"))
                    continue
                # Roll remaining dice
                if not remaining:
                    # hot dice
                    write(t(lang, "hot_dice_msg"))
                    sound.hot_dice()
                    dice_left = farkle_mod.DICE_PER_ROLL
                else:
                    dice_left = len(remaining)
                break
            if cmd == "k":
                # Auto-pick best subset from `remaining`
                best_score, best_keep = farkle_mod.best_score_subset(remaining)
                if best_score == 0:
                    write(t(lang, "must_keep_at_least_one"))
                    continue
                kept_this_roll.extend(best_keep)
                round_score += best_score
                remaining = farkle_mod.remove_dice(remaining, best_keep)
                sound.keep()
                write(t(lang, "kept", dice=" ".join(str(d) for d in best_keep),
                        score=best_score))
                write(t(lang, "round_score", score=round_score))
                continue
            keep = parse_keep(line)
            if keep is None:
                invalid_attempts += 1
                write(t(lang, "invalid_keep"))
                if invalid_attempts >= max_invalid_attempts:
                    write(t(lang, "too_many_invalid"))
                    sound.farkle()
                    return 0
                continue
            if not farkle_mod.can_keep(remaining, keep):
                invalid_attempts += 1
                write(t(lang, "invalid_keep"))
                if invalid_attempts >= max_invalid_attempts:
                    write(t(lang, "too_many_invalid"))
                    sound.farkle()
                    return 0
                continue
            invalid_attempts = 0
            sc, _ = farkle_mod.score_dice(keep)
            kept_this_roll.extend(keep)
            round_score += sc
            remaining = farkle_mod.remove_dice(remaining, keep)
            sound.keep()
            write(t(lang, "kept", dice=" ".join(str(d) for d in keep), score=sc))
            write(t(lang, "round_score", score=round_score))


def play_ai_turn(s: dict, sound: Sound, output, rng: random.Random,
                 total_score: int) -> int:
    lang = s.get("lang", "zh")
    target = int(s.get("target", 5000))
    difficulty = s.get("difficulty", "normal")

    def write(msg=""):
        output.write(msg + "\n")

    write(t(lang, "ai_turn"))
    round_score = 0
    dice_left = farkle_mod.DICE_PER_ROLL
    while True:
        roll = roll_dice(dice_left, rng)
        sound.roll()
        write(t(lang, "rolled", dice=" ".join(str(d) for d in roll)))
        if farkle_mod.is_farkle(roll):
            write(t(lang, "ai_farkle"))
            sound.farkle()
            return 0
        keep = ai_mod.best_keep(roll)
        sc, _ = farkle_mod.score_dice(keep)
        round_score += sc
        remaining_count = len(roll) - len(keep)
        sound.keep()
        write(t(lang, "ai_keeps", dice=" ".join(str(d) for d in keep), score=sc))
        write(t(lang, "round_score", score=round_score))
        if ai_mod.should_bank(round_score, remaining_count, total_score,
                              target, difficulty):
            sound.bank()
            write(t(lang, "ai_banks", score=round_score,
                    total=total_score + round_score))
            return round_score
        if remaining_count == 0:
            write(t(lang, "ai_hot_dice"))
            sound.hot_dice()
            dice_left = farkle_mod.DICE_PER_ROLL
        else:
            write(t(lang, "ai_pushes"))
            dice_left = remaining_count


def play_round(s: dict, sound: Sound, input_func, output,
               rng=None) -> Optional[dict]:
    if rng is None:
        rng = random.Random()
    lang = s.get("lang", "zh")
    target = int(s.get("target", 5000))
    p1 = 0
    p2 = 0
    while True:
        output.write(t(lang, "totals", p1=p1, p2=p2, target=target) + "\n")
        gained = play_human_turn(s, sound, input_func, output, rng, p1)
        if gained is None:
            return None
        p1 += gained
        if p1 >= target:
            output.write(t(lang, "win_msg", score=p1) + "\n")
            sound.win()
            return {"result": "win", "score": p1, "difficulty": s.get("difficulty", "normal"),
                    "target": target}
        output.write(t(lang, "totals", p1=p1, p2=p2, target=target) + "\n")
        ai_gained = play_ai_turn(s, sound, output, rng, p2)
        p2 += ai_gained
        if p2 >= target:
            output.write(t(lang, "lose_msg", score=p2) + "\n")
            return {"result": "loss", "score": p1,
                    "difficulty": s.get("difficulty", "normal"), "target": target}


def show_help(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    output.write("\n=== " + t(lang, "help_title") + " ===\n")
    output.write(t(lang, "help_body") + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def show_scores(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    scores = score_mod.load()
    output.write("\n=== " + t(lang, "scores_title") + " ===\n")
    if not scores:
        output.write(t(lang, "scores_empty") + "\n")
    else:
        for i, e in enumerate(scores, 1):
            output.write(t(
                lang, "scores_row",
                rank=i, name=e.get("name", "")[:12],
                score=e.get("score", 0),
                difficulty=t(lang, f"diff_{e.get('difficulty', 'normal')}"),
                target=e.get("target", 5000),
            ) + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def settings_menu(s: dict, input_func, output) -> dict:
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "settings_title") + " ===\n")
        output.write(t(lang, "settings_lang", value=t(lang, f"lang_{lang}")) + "\n")
        output.write(t(lang, "settings_sound",
                       value=t(lang, "on" if s.get("sound") else "off")) + "\n")
        output.write(t(lang, "settings_volume", value=s.get("volume", 1)) + "\n")
        output.write(t(lang, "settings_difficulty",
                       value=t(lang, f"diff_{s.get('difficulty', 'normal')}")) + "\n")
        output.write(t(lang, "settings_target", value=s.get("target", 5000)) + "\n")
        output.write(t(lang, "settings_back") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            break
        if choice == "1":
            settings_mod.cycle_lang(s)
        elif choice == "2":
            settings_mod.toggle_sound(s)
        elif choice == "3":
            settings_mod.cycle_volume(s)
        elif choice == "4":
            settings_mod.cycle_difficulty(s)
        elif choice == "5":
            settings_mod.cycle_target(s)
        elif choice == "b":
            break
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")
    settings_mod.save(s)
    return s


def main_menu(input_func=None, output=None, rng=None) -> None:
    if input_func is None:
        input_func = input
    if output is None:
        output = sys.stdout
    if rng is None:
        rng = random.Random()
    s = settings_mod.load()
    settings_mod.save(s)
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "title") + " ===\n")
        output.write(t(lang, "menu_play") + "\n")
        output.write(t(lang, "menu_help") + "\n")
        output.write(t(lang, "menu_scores") + "\n")
        output.write(t(lang, "menu_settings") + "\n")
        output.write(t(lang, "menu_quit") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "q":
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "p":
            sound = Sound(enabled=bool(s.get("sound", True)),
                          volume=int(s.get("volume", 1)),
                          output=output)
            try:
                result = play_round(s, sound, input_func, output, rng=rng)
            except QuitGame:
                output.write(t(lang, "bye") + "\n")
                return
            if result is None:
                continue
            try:
                name = input_func(t(lang, "name_prompt")).strip()
            except EOFError:
                name = ""
            if name:
                score_mod.add(name, result["score"], result["difficulty"],
                              result["target"])
        elif choice == "h":
            show_help(s, input_func, output)
        elif choice == "l":
            show_scores(s, input_func, output)
        elif choice == "s":
            settings_menu(s, input_func, output)
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
