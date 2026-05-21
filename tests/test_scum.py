"""
Tests for scum_villainy_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from scum_villainy_agent import (
    get_playbook_info,
    assign_action_dots,
    roll_heritage,
    roll_background,
    roll_vice,
    roll_dice,
    save_result,
    detect_phase,
    PLAYBOOKS,
    HERITAGE,
    BACKGROUND,
    VICE,
    ACTIONS,
)


# ── get_playbook_info ────────────────────────────────────────────────────────────

class TestGetPlaybookInfo:
    def test_valid_playbook_returns_json(self):
        result = get_playbook_info("Muscle")
        data = json.loads(result)
        assert "description" in data

    def test_invalid_playbook_returns_error(self):
        result = get_playbook_info("Wizard")
        assert "Unknown" in result or "Available" in result

    def test_all_playbooks_have_required_keys(self):
        required = {"description", "starting_actions", "key_actions",
                    "special_abilities", "xp_triggers", "load"}
        for pb in PLAYBOOKS:
            data = json.loads(get_playbook_info(pb))
            missing = required - data.keys()
            assert not missing, f"Playbook '{pb}' missing keys: {missing}"

    def test_each_playbook_has_two_xp_triggers(self):
        for pb in PLAYBOOKS:
            data = json.loads(get_playbook_info(pb))
            assert len(data["xp_triggers"]) == 2, f"Playbook '{pb}' should have 2 XP triggers"

    def test_each_playbook_has_special_abilities(self):
        for pb in PLAYBOOKS:
            data = json.loads(get_playbook_info(pb))
            assert len(data["special_abilities"]) >= 6, f"Playbook '{pb}' needs ≥6 abilities"

    def test_load_is_valid_weight(self):
        valid_loads = {"Light", "Medium", "Heavy"}
        for pb in PLAYBOOKS:
            data = json.loads(get_playbook_info(pb))
            assert data["load"] in valid_loads, f"Playbook '{pb}' has invalid load '{data['load']}'"


# ── assign_action_dots ───────────────────────────────────────────────────────────

class TestAssignActionDots:
    def test_returns_valid_json(self):
        result = assign_action_dots("Muscle")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_grouped_by_three_attributes(self):
        data = json.loads(assign_action_dots("Muscle"))
        assert set(data.keys()) == {"Insight", "Prowess", "Resolve"}

    def test_muscle_has_skirmish_at_two(self):
        # Muscle starting actions: Skirmish 2, Command 1
        data = json.loads(assign_action_dots("Muscle"))
        assert data["Prowess"]["Skirmish"] >= 2

    def test_no_action_exceeds_two_dots(self):
        # Bonus allocation is capped at 2 per action
        for pb in PLAYBOOKS:
            data = json.loads(assign_action_dots(pb))
            for attr, actions in data.items():
                for action, dots in actions.items():
                    assert dots <= 2, f"{pb}/{action} has {dots} dots — expected max 2"

    def test_pilot_uses_helm_not_skirmish(self):
        data = json.loads(assign_action_dots("Pilot"))
        all_actions = [a for actions in data.values() for a in actions]
        assert "Helm" in all_actions
        assert "Skirmish" not in all_actions

    def test_stitch_uses_patch_not_tinker(self):
        data = json.loads(assign_action_dots("Stitch"))
        all_actions = [a for actions in data.values() for a in actions]
        assert "Patch" in all_actions
        assert "Tinker" not in all_actions

    def test_invalid_playbook_returns_error(self):
        result = assign_action_dots("Warlock")
        assert "Unknown" in result

    def test_each_attribute_group_has_four_actions(self):
        for pb in PLAYBOOKS:
            data = json.loads(assign_action_dots(pb))
            for attr, actions in data.items():
                assert len(actions) == 4, f"{pb}/{attr} should have 4 actions"

    def test_all_dots_are_non_negative(self):
        for pb in PLAYBOOKS:
            data = json.loads(assign_action_dots(pb))
            for attr, actions in data.items():
                for action, dots in actions.items():
                    assert dots >= 0, f"{pb}/{action} has negative dots"


# ── roll_heritage ────────────────────────────────────────────────────────────────

class TestRollHeritage:
    def test_returns_valid_json(self):
        result = roll_heritage()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_heritage_key(self):
        data = json.loads(roll_heritage())
        assert "heritage" in data

    def test_heritage_is_known_option(self):
        for _ in range(20):
            data = json.loads(roll_heritage())
            assert data["heritage"] in HERITAGE, f"Unknown heritage: {data['heritage']}"

    def test_has_description_and_flavor(self):
        data = json.loads(roll_heritage())
        assert "description" in data
        assert "flavor" in data


# ── roll_background ──────────────────────────────────────────────────────────────

class TestRollBackground:
    def test_returns_valid_json(self):
        data = json.loads(roll_background())
        assert isinstance(data, dict)

    def test_has_background_key(self):
        data = json.loads(roll_background())
        assert "background" in data

    def test_background_is_known_option(self):
        for _ in range(20):
            data = json.loads(roll_background())
            assert data["background"] in BACKGROUND, f"Unknown background: {data['background']}"

    def test_has_flavor(self):
        data = json.loads(roll_background())
        assert "flavor" in data


# ── roll_vice ────────────────────────────────────────────────────────────────────

class TestRollVice:
    def test_returns_valid_json(self):
        data = json.loads(roll_vice())
        assert isinstance(data, dict)

    def test_has_vice_key(self):
        data = json.loads(roll_vice())
        assert "vice" in data

    def test_vice_is_known_option(self):
        for _ in range(20):
            data = json.loads(roll_vice())
            assert data["vice"] in VICE, f"Unknown vice: {data['vice']}"

    def test_has_flavor(self):
        data = json.loads(roll_vice())
        assert "flavor" in data


# ── roll_dice ────────────────────────────────────────────────────────────────────

class TestRollDice:
    def test_returns_valid_json(self):
        result = roll_dice(count=2)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_rolls_and_outcome(self):
        data = json.loads(roll_dice(count=2))
        assert "rolls" in data
        assert "outcome" in data
        assert "best" in data

    def test_count_two_returns_two_rolls(self):
        data = json.loads(roll_dice(count=2))
        assert len(data["rolls"]) == 2

    def test_count_clamped_to_minimum_one(self):
        data = json.loads(roll_dice(count=0))
        assert len(data["rolls"]) >= 1

    def test_count_clamped_to_maximum_six(self):
        data = json.loads(roll_dice(count=100))
        assert len(data["rolls"]) <= 6

    def test_rolls_are_d6_values(self):
        for _ in range(20):
            data = json.loads(roll_dice(count=3))
            for roll in data["rolls"]:
                assert 1 <= roll <= 6, f"Roll {roll} out of d6 range"

    def test_double_six_is_critical(self):
        import random
        import unittest.mock as mock
        with mock.patch.object(random, "randint", return_value=6):
            data = json.loads(roll_dice(count=2))
            assert "Critical" in data["outcome"] or "6/6" in data["outcome"]

    def test_outcome_describes_result(self):
        data = json.loads(roll_dice(count=2))
        assert any(word in data["outcome"] for word in ("success", "Failure", "Critical", "Partial", "Full"))


# ── detect_phase ─────────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_playbook_phase(self):
        assert detect_phase("get_playbook_info") == "playbook"

    def test_heritage_phase(self):
        assert detect_phase("roll_heritage") == "heritage"

    def test_background_phase(self):
        assert detect_phase("roll_background") == "background"

    def test_vice_phase(self):
        assert detect_phase("roll_vice") == "vice"

    def test_actions_phase(self):
        assert detect_phase("assign_action_dots") == "actions"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("roll_dice") is None

    def test_unrelated_tool_returns_none(self):
        assert detect_phase("flip_coin") is None


# ── save_result ──────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Reva Marsh**\n*Scoundrel — three fake IDs and a real grudge*\n..."
        path = save_result(content, "full")
        assert "reva-marsh" in path.name

    def test_character_suffix(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Test**\n*Muscle*"
        assert save_result(content, "full").name.endswith("-full.md")

    def test_npc_suffix(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Tess Varo**\n*Fixer*"
        assert save_result(content, "npc").name.endswith("-npc.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Test Character**\n*Muscle — hits things professionally*"
        path = save_result(content, "full")
        assert path.read_text() == content

    def test_saves_to_scum_villainy_characters_dir(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Test**\n*Role*"
        path = save_result(content, "full")
        assert "characters" in str(path)
        assert "scum_villainy" in str(path)

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        """Second character with the same name gets -2 suffix, not a silent overwrite."""
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Reva Marsh**\n*Scoundrel — three fake IDs and a real grudge*"
        path1 = save_result(content, "full")
        path2 = save_result(content, "full")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()
        assert path2.name == "reva-marsh-full-2.md"

    def test_collision_increments_beyond_two(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Reva Marsh**\n*Scoundrel*"
        save_result(content, "full")
        save_result(content, "full")
        path3 = save_result(content, "full")
        assert path3.name == "reva-marsh-full-3.md"

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        import scum_villainy_agent
        monkeypatch.setattr(scum_villainy_agent, "__file__", str(tmp_path / "scum_villainy_agent.py"))
        content = "## **Reva Marsh**\n*Scoundrel*"
        path = save_result(content, "full")
        assert "**" not in path.name
        assert "#" not in path.name


# ── Constants ────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_six_playbooks(self):
        assert len(PLAYBOOKS) == 6
        assert set(PLAYBOOKS.keys()) == {"Muscle", "Pilot", "Scoundrel", "Mystic", "Speaker", "Stitch"}

    def test_five_heritages(self):
        assert len(HERITAGE) == 5

    def test_six_backgrounds(self):
        assert len(BACKGROUND) == 6

    def test_seven_vices(self):
        assert len(VICE) == 7

    def test_three_attribute_groups(self):
        assert len(ACTIONS) == 3
        assert set(ACTIONS.keys()) == {"Insight", "Prowess", "Resolve"}

    def test_four_actions_per_attribute(self):
        for attr, actions in ACTIONS.items():
            assert len(actions) == 4, f"Attribute '{attr}' should have 4 actions, has {len(actions)}"

    def test_standard_actions_present(self):
        all_actions = [a for actions in ACTIONS.values() for a in actions]
        for action in ("Hunt", "Skirmish", "Sway"):
            assert action in all_actions, f"Standard action '{action}' missing"
