"""
Tests for dnd_agent.py — pure Python logic only, no API calls.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import dnd_agent
from dnd_agent import (
    ability_modifier,
    modifier_str,
    roll_stat,
    roll_dice,
    get_race_info,
    get_class_info,
    get_background_info,
    roll_quest_hook,
    detect_phase,
    save_result,
    VALID_DICE,
    MIN_ROLLS,
    MAX_ROLLS,
    RACES,
    CLASSES,
    BACKGROUNDS,
    QUEST_HOOKS,
)


# ── ability_modifier ────────────────────────────────────────────────────────────

class TestAbilityModifier:
    def test_score_10_is_zero(self):
        assert ability_modifier(10) == 0

    def test_score_11_is_zero(self):
        assert ability_modifier(11) == 0

    def test_score_8_is_minus_one(self):
        assert ability_modifier(8) == -1

    def test_score_9_is_minus_one(self):
        assert ability_modifier(9) == -1

    def test_score_12_is_plus_one(self):
        assert ability_modifier(12) == 1

    def test_score_20_is_plus_five(self):
        assert ability_modifier(20) == 5

    def test_score_1_is_minus_five(self):
        assert ability_modifier(1) == -5

    def test_score_18_is_plus_four(self):
        assert ability_modifier(18) == 4


# ── modifier_str ────────────────────────────────────────────────────────────────

class TestModifierStr:
    def test_positive_has_plus_sign(self):
        assert modifier_str(14) == "+2"

    def test_zero_has_plus_sign(self):
        assert modifier_str(10) == "+0"

    def test_negative_has_minus_sign(self):
        assert modifier_str(8) == "-1"


# ── roll_stat ───────────────────────────────────────────────────────────────────

class TestRollStat:
    def test_returns_string(self):
        result = roll_stat()
        assert isinstance(result, str)

    def test_contains_score_label(self):
        assert "score:" in roll_stat()

    def test_score_in_valid_range(self):
        # 4d6 drop lowest: min possible is 3 (1+1+1), max is 18 (6+6+6)
        for _ in range(50):
            result = roll_stat()
            score = int(result.split("score:")[-1].strip())
            assert 3 <= score <= 18


# ── roll_dice ───────────────────────────────────────────────────────────────────

class TestRollDice:
    def test_valid_die_returns_result(self):
        result = roll_dice(sides=6, count=1)
        assert "total:" in result

    def test_invalid_die_returns_error(self):
        result = roll_dice(sides=7)
        assert "Error" in result

    def test_invalid_die_57_returns_error(self):
        result = roll_dice(sides=57)
        assert "Error" in result

    def test_count_too_high_returns_error(self):
        result = roll_dice(sides=6, count=MAX_ROLLS + 1)
        assert "Error" in result

    def test_count_zero_returns_error(self):
        result = roll_dice(sides=6, count=0)
        assert "Error" in result

    def test_all_valid_dice_work(self):
        for sides in VALID_DICE:
            result = roll_dice(sides=sides, count=2)
            assert "total:" in result, f"d{sides} failed"

    def test_total_in_range(self):
        for _ in range(20):
            result = roll_dice(sides=6, count=2)
            total = int(result.split("total:")[-1].strip())
            assert 2 <= total <= 12


# ── get_race_info ───────────────────────────────────────────────────────────────

class TestGetRaceInfo:
    def test_valid_race_returns_data(self):
        result = get_race_info("Human")
        assert "Human" in result or "ability_bonuses" in result

    def test_invalid_race_returns_error(self):
        result = get_race_info("Klingon")
        assert "Unknown" in result or "not found" in result.lower() or "available" in result.lower()

    def test_all_races_return_data(self):
        for race in RACES:
            result = get_race_info(race)
            assert "Error" not in result, f"Race '{race}' returned an error"


# ── get_class_info ──────────────────────────────────────────────────────────────

class TestGetClassInfo:
    def test_valid_class_returns_data(self):
        result = get_class_info("Rogue")
        assert "Rogue" in result or "hit_die" in result

    def test_invalid_class_returns_error(self):
        result = get_class_info("Jedi")
        assert "Unknown" in result or "not found" in result.lower() or "available" in result.lower()

    def test_all_classes_return_data(self):
        for cls in CLASSES:
            result = get_class_info(cls)
            assert "Error" not in result, f"Class '{cls}' returned an error"


# ── get_background_info ─────────────────────────────────────────────────────────

class TestGetBackgroundInfo:
    def test_valid_background_returns_data(self):
        result = get_background_info("Urchin")
        assert "Urchin" in result or "skills" in result

    def test_invalid_background_returns_error(self):
        result = get_background_info("Astronaut")
        assert "Unknown" in result or "not found" in result.lower() or "available" in result.lower()

    def test_all_backgrounds_return_data(self):
        for bg in BACKGROUNDS:
            result = get_background_info(bg)
            assert "Error" not in result, f"Background '{bg}' returned an error"


# ── save_result ─────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Pip Underbough**\n*Rogue — light fingers, heavy conscience*"
        path = save_result(content, "full")
        assert "pip-underbough" in path.name

    def test_preamble_skipped_for_filename(self, tmp_path, monkeypatch):
        """Preamble before first ## heading must not end up in the filename."""
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "Now I have everything. Let me build her.\n\nHP = 8\n\n## **Iyari Sael**\n*Druid*"
        path = save_result(content, "full")
        assert "iyari-sael" in path.name
        assert "now" not in path.name
        assert "everything" not in path.name

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        """Second character with the same name gets -2 suffix, not a silent overwrite."""
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Aldric Vehr**\n*Fighter — wall of a man*"
        path1 = save_result(content, "full")
        path2 = save_result(content, "full")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()
        assert path2.name == "aldric-vehr-full-2.md"

    def test_collision_increments_beyond_two(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Aldric Vehr**\n*Fighter*"
        save_result(content, "full")
        save_result(content, "full")
        path3 = save_result(content, "full")
        assert path3.name == "aldric-vehr-full-3.md"

    def test_mode_used_as_suffix(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Rook Delmar**\n*Paladin*"
        assert save_result(content, "full").name.endswith("-full.md")
        content2 = "## **Siena Mott**\n*Warlock*"
        assert save_result(content2, "npc").name.endswith("-npc.md")
        content3 = "## **Halben Orriss**\n*Quest giver*"
        assert save_result(content3, "questgiver").name.endswith("-questgiver.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Test Character**\n*Cleric — keeps everyone alive, barely*"
        path = save_result(content, "full")
        assert path.read_text() == content

    def test_saves_to_correct_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Test**\n*Fighter*"
        path = save_result(content, "full")
        assert "characters" in str(path)
        assert "dnd" in str(path)

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "dnd_agent.py"))
        content = "## **Rook Delmar**\n*Fighter*"
        path = save_result(content, "full")
        assert "**" not in path.name
        assert "#" not in path.name


# ── roll_quest_hook ──────────────────────────────────────────────────────────────

class TestRollQuestHook:
    def test_returns_valid_json(self):
        result = roll_quest_hook()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(roll_quest_hook())
        assert "quest_type"   in data
        assert "description"  in data
        assert "complication" in data

    def test_quest_type_is_known(self):
        known_types = {h["type"] for h in QUEST_HOOKS}
        for _ in range(20):
            data = json.loads(roll_quest_hook())
            assert data["quest_type"] in known_types

    def test_returns_variety(self):
        # 30 rolls should yield at least 4 distinct quest types
        types = {json.loads(roll_quest_hook())["quest_type"] for _ in range(30)}
        assert len(types) >= 4

    def test_complication_is_non_empty_string(self):
        data = json.loads(roll_quest_hook())
        assert isinstance(data["complication"], str)
        assert len(data["complication"]) > 0

    def test_complication_belongs_to_quest_type(self):
        for _ in range(20):
            data = json.loads(roll_quest_hook())
            hook = next(h for h in QUEST_HOOKS if h["type"] == data["quest_type"])
            assert data["complication"] in hook["complications"]

    def test_at_least_twelve_quest_types(self):
        assert len(QUEST_HOOKS) >= 12

    def test_monster_hunt_and_heist_present(self):
        known_types = {h["type"] for h in QUEST_HOOKS}
        assert "Monster Hunt" in known_types
        assert "Heist"        in known_types


# ── detect_phase ─────────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_roll_stat_returns_stats(self):
        assert detect_phase("roll_stat", set()) == "stats"

    def test_get_race_info_returns_race(self):
        assert detect_phase("get_race_info", set()) == "race"

    def test_get_class_info_returns_class(self):
        assert detect_phase("get_class_info", set()) == "class"

    def test_get_background_info_returns_background(self):
        assert detect_phase("get_background_info", set()) == "background"

    def test_roll_name_suggestion_returns_name(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_roll_quest_hook_returns_quest(self):
        assert detect_phase("roll_quest_hook", set()) == "quest"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None

    def test_roll_dice_returns_none(self):
        assert detect_phase("roll_dice", set()) is None


# ── Constants sanity checks ─────────────────────────────────────────────────────

class TestConstants:
    def test_valid_dice_contains_standard_set(self):
        assert {4, 6, 8, 10, 12, 20}.issubset(VALID_DICE)

    def test_min_rolls_is_positive(self):
        assert MIN_ROLLS >= 1

    def test_max_rolls_is_reasonable(self):
        assert MAX_ROLLS <= 100
