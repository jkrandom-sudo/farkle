"""Bilingual strings."""

STRINGS = {
    "zh": {
        "title": "Farkle / 掷骰子",
        "menu_play": "p) 开始游戏",
        "menu_help": "h) 帮助",
        "menu_scores": "l) 排行榜",
        "menu_settings": "s) 设置",
        "menu_quit": "q) 退出",
        "menu_choice": "请选择 > ",
        "bye": "再见!",
        "unknown": "未知选项: {choice}",
        "help_title": "帮助",
        "help_body": (
            "Farkle: 推骰子游戏, 先达到目标分数(默认 5000)者胜。\n"
            "回合规则:\n"
            "  - 每回合从 6 颗骰子开始, 投掷得到一组点数。\n"
            "  - 至少要保留一颗计分骰子, 然后可选择继续投剩余骰子或'落袋'。\n"
            "  - 若投出无任何计分组合 -> Farkle, 本回合分数清零。\n"
            "  - 若 6 颗骰子全部计入, 即'热骰', 可继续投全部 6 颗。\n"
            "计分:\n"
            "  单 1 = 100, 单 5 = 50\n"
            "  三 1 = 1000, 三 N = N×100\n"
            "  四同 = 2× 三同, 五同 = 4× 三同, 六同 = 8× 三同\n"
            "  顺子 1-2-3-4-5-6 = 1500\n"
            "  三对 = 1500, 两个三同 = 2500\n"
            "操作:\n"
            "  输入要保留的骰子点数, 例如 '1 5' 或 '1,5'\n"
            "  k = 自动选择最高得分组合\n"
            "  b = 落袋, 计入总分\n"
            "  r = 投剩余骰子\n"
            "  q = 放弃本局\n"
        ),
        "press_enter": "按回车继续...",
        "settings_title": "设置",
        "settings_lang": "1) 语言: {value}",
        "settings_sound": "2) 声音: {value}",
        "settings_volume": "3) 音量: {value}",
        "settings_difficulty": "4) AI 难度: {value}",
        "settings_target": "5) 目标分: {value}",
        "settings_back": "b) 返回",
        "scores_title": "排行榜 (Top 10)",
        "scores_empty": "暂无成绩",
        "scores_row": "{rank:>2}. {name:<12} {score:>5}  ({difficulty}, 目标 {target})",
        "name_prompt": "姓名(空= 不保存): ",
        "your_turn": "==== 你的回合 ====",
        "ai_turn": "==== AI 回合 ====",
        "totals": "总分: 你 {p1} | AI {p2}  (目标 {target})",
        "rolled": "投出: {dice}",
        "round_score": "本回合分数: {score}",
        "farkle_msg": "Farkle! 本回合归零.",
        "hot_dice_msg": "热骰! 重新投全部 6 颗.",
        "input_keep": "保留 (空格分隔点数, k=自动, b=落袋, r=继续投, q=退出) > ",
        "kept": "已保留: {dice} (+{score})",
        "invalid_keep": "无效的保留 — 必须是有效计分组合, 且每颗骰子均计入",
        "too_many_invalid": "输入错误过多, 本回合归零.",
        "must_keep_at_least_one": "必须至少保留一颗计分骰子",
        "banked": "落袋 +{score}, 总分 {total}",
        "no_score_yet": "本回合还没有分数, 不能落袋",
        "win_msg": "恭喜! 你赢了 {score} 分",
        "lose_msg": "AI 赢了 {score} 分, 再接再厉",
        "ai_keeps": "AI 保留 {dice} (+{score})",
        "ai_banks": "AI 落袋 +{score}, 总分 {total}",
        "ai_pushes": "AI 选择继续投",
        "ai_farkle": "AI 投出 Farkle!",
        "ai_hot_dice": "AI 热骰, 全部 6 颗重投",
        "score_label": "得分: {score}",
        "diff_easy": "简单",
        "diff_normal": "普通",
        "diff_hard": "困难",
        "lang_zh": "中文",
        "lang_en": "英文",
        "on": "开",
        "off": "关",
    },
    "en": {
        "title": "Farkle",
        "menu_play": "p) Play",
        "menu_help": "h) Help",
        "menu_scores": "l) Leaderboard",
        "menu_settings": "s) Settings",
        "menu_quit": "q) Quit",
        "menu_choice": "Choose > ",
        "bye": "Bye!",
        "unknown": "Unknown option: {choice}",
        "help_title": "Help",
        "help_body": (
            "Farkle: a press-your-luck dice game. First to the target\n"
            "score (default 5000) wins.\n"
            "Turn:\n"
            "  - Start with 6 dice; roll them.\n"
            "  - Set aside at least one scoring die, then choose to roll\n"
            "    the remaining dice or bank.\n"
            "  - If a roll has no scoring combination → Farkle, lose round.\n"
            "  - If you set aside all 6 dice (hot dice), reroll all 6.\n"
            "Scoring:\n"
            "  Each 1 = 100, each 5 = 50\n"
            "  Three 1s = 1000, three Ns = N x 100\n"
            "  Four of a kind = 2x three, five = 4x, six = 8x\n"
            "  Straight 1-2-3-4-5-6 = 1500\n"
            "  Three pairs = 1500, two triplets = 2500\n"
            "Commands:\n"
            "  Enter dice values to keep, e.g. '1 5' or '1,5'\n"
            "  k = auto-pick the highest scoring set\n"
            "  b = bank (add round to total)\n"
            "  r = roll remaining dice\n"
            "  q = quit this round\n"
        ),
        "press_enter": "Press Enter to continue...",
        "settings_title": "Settings",
        "settings_lang": "1) Language: {value}",
        "settings_sound": "2) Sound: {value}",
        "settings_volume": "3) Volume: {value}",
        "settings_difficulty": "4) AI difficulty: {value}",
        "settings_target": "5) Target score: {value}",
        "settings_back": "b) Back",
        "scores_title": "Leaderboard (Top 10)",
        "scores_empty": "No scores yet",
        "scores_row": "{rank:>2}. {name:<12} {score:>5}  ({difficulty}, target {target})",
        "name_prompt": "Name (empty = skip save): ",
        "your_turn": "==== Your turn ====",
        "ai_turn": "==== AI turn ====",
        "totals": "Totals: You {p1} | AI {p2}  (target {target})",
        "rolled": "Rolled: {dice}",
        "round_score": "Round score: {score}",
        "farkle_msg": "Farkle! Round score lost.",
        "hot_dice_msg": "Hot dice! Reroll all 6.",
        "input_keep": "Keep (space-separated, k=auto, b=bank, r=roll, q=quit) > ",
        "kept": "Kept: {dice} (+{score})",
        "invalid_keep": "Invalid keep — must be a valid scoring set with no leftovers",
        "too_many_invalid": "Too many invalid attempts, round score lost.",
        "must_keep_at_least_one": "You must keep at least one scoring die",
        "banked": "Banked +{score}, total {total}",
        "no_score_yet": "No round score yet — cannot bank",
        "win_msg": "You win with {score}!",
        "lose_msg": "AI wins with {score}. Better luck next time.",
        "ai_keeps": "AI keeps {dice} (+{score})",
        "ai_banks": "AI banks +{score}, total {total}",
        "ai_pushes": "AI rolls on",
        "ai_farkle": "AI rolled Farkle!",
        "ai_hot_dice": "AI hot dice — reroll all 6",
        "score_label": "Score: {score}",
        "diff_easy": "easy",
        "diff_normal": "normal",
        "diff_hard": "hard",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "on": "on",
        "off": "off",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang) or STRINGS["en"]
    s = table.get(key)
    if s is None:
        s = STRINGS["en"].get(key, key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s
