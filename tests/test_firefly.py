"""
Tests for firefly_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from firefly_agent import (
    roll_cortex_attributes,
    get_role_info,
    get_location_info,
    roll_dice,
    roll_war_history,
    save_result,
    detect_phase,
    VALID_DICE_SIZES,
    CORTEX_LADDER,
    ROLES,
    VERSE_LOCATIONS,
    WAR_HISTORY,
)


# ── roll_cortex_attributes ──────────────────────────────────────────────────────

class TestRollCortexAttributes:
    def test_returns_valid_json(self):
        result = roll_cortex_attributes()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_all_six_attributes(self):
        data = json.loads(roll_cortex_attributes())
        expected = {"Agility", "Alertness", "Intelligence", "Strength", "Vitality", "Willpower"}
        assert set(data.keys()) == expected

    def test_all_values_are_valid_die_strings(self):
        data = json.loads(roll_cortex_attributes())
        valid = {f"d{s}" for s in CORTEX_LADDER}
        for attr, die in data.items():
            assert die in valid, f"{attr}: unexpected die '{die}'"

    def test_uses_standard_spread(self):
        # Standard spread: [4,6,6,8,8,10] — sizes should sum to the same total
        data = json.loads(roll_cortex_attributes())
        sizes = sorted([int(v[1:]) for v in data.values()])
        assert sizes == sorted([4, 6, 6, 8, 8, 10])

    def test_no_d12_in_starting_spread(self):
        # Starting characters don't get d12
        for _ in range(20):
            data = json.loads(roll_cortex_attributes())
            assert "d12" not in data.values()


# ── get_role_info ───────────────────────────────────────────────────────────────

class TestGetRoleInfo:
    def test_valid_role_returns_json(self):
        result = get_role_info("Captain")
        data = json.loads(result)
        assert "description" in data

    def test_invalid_role_returns_error(self):
        result = get_role_info("Jedi Knight")
        assert "Unknown" in result or "Available" in result

    def test_all_roles_have_required_keys(self):
        required = {"description", "key_attributes", "key_skills", "flavor", "distinction_seeds"}
        for role in ROLES:
            data = json.loads(get_role_info(role))
            missing = required - data.keys()
            assert not missing, f"Role '{role}' missing keys: {missing}"

    def test_all_roles_have_three_distinction_seeds(self):
        for role in ROLES:
            data = json.loads(get_role_info(role))
            assert len(data["distinction_seeds"]) == 3, f"Role '{role}' should have 3 seeds"

    def test_all_roles_have_key_attributes(self):
        for role in ROLES:
            data = json.loads(get_role_info(role))
            assert len(data["key_attributes"]) >= 1, f"Role '{role}' has no key attributes"

    def test_key_attributes_are_valid(self):
        valid = {"Agility", "Alertness", "Intelligence", "Strength", "Vitality", "Willpower"}
        for role in ROLES:
            data = json.loads(get_role_info(role))
            for attr in data["key_attributes"]:
                assert attr in valid, f"Role '{role}' has unknown attribute '{attr}'"


# ── get_location_info ────────────────────────────────────────────────────────────

class TestGetLocationInfo:
    def test_valid_region_returns_json(self):
        result = get_location_info("Core")
        data = json.loads(result)
        assert "worlds" in data

    def test_invalid_region_returns_error(self):
        result = get_location_info("Outer Rim")
        assert "Unknown" in result or "Available" in result

    def test_all_regions_return_data(self):
        for region in VERSE_LOCATIONS:
            data = json.loads(get_location_info(region))
            assert "worlds" in data
            assert "flavor" in data
            assert "background" in data

    def test_each_region_has_worlds(self):
        for region in VERSE_LOCATIONS:
            data = json.loads(get_location_info(region))
            assert len(data["worlds"]) >= 1, f"Region '{region}' has no worlds"

    def test_three_known_regions(self):
        for region in ("Core", "Border", "Rim"):
            result = get_location_info(region)
            data = json.loads(result)
            assert "worlds" in data


# ── roll_dice ───────────────────────────────────────────────────────────────────

class TestRollDice:
    def test_valid_die_returns_result(self):
        result = roll_dice(sides=6, count=1)
        assert "total:" in result

    def test_invalid_die_returns_error(self):
        result = roll_dice(sides=7)
        assert "Error" in result

    def test_all_valid_dice_work(self):
        for sides in VALID_DICE_SIZES:
            result = roll_dice(sides=sides)
            assert "Error" not in result, f"d{sides} returned an error"

    def test_total_in_range_2d6(self):
        for _ in range(30):
            result = roll_dice(sides=6, count=2)
            total = int(result.split("total:")[-1].strip())
            assert 2 <= total <= 12

    def test_total_in_range_1d8(self):
        for _ in range(30):
            result = roll_dice(sides=8, count=1)
            total = int(result.split("total:")[-1].strip())
            assert 1 <= total <= 8


# ── roll_war_history ─────────────────────────────────────────────────────────────

class TestRollWarHistory:
    def test_returns_valid_json(self):
        result = roll_war_history()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_history_and_flavor(self):
        data = json.loads(roll_war_history())
        assert "history" in data
        assert "flavor" in data

    def test_history_is_known_option(self):
        for _ in range(20):
            data = json.loads(roll_war_history())
            assert data["history"] in WAR_HISTORY, f"Unknown history: {data['history']}"

    def test_flavor_is_non_empty_string(self):
        data = json.loads(roll_war_history())
        assert isinstance(data["flavor"], str)
        assert len(data["flavor"]) > 0


# ── detect_phase ─────────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_role_info_returns_role(self):
        assert detect_phase("get_role_info", set()) == "role"

    def test_location_info_returns_homeworld(self):
        assert detect_phase("get_location_info", set()) == "homeworld"

    def test_war_history_returns_war(self):
        assert detect_phase("roll_war_history", set()) == "war"

    def test_cortex_attributes_returns_attributes(self):
        assert detect_phase("roll_cortex_attributes", set()) == "attributes"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("roll_dice", set()) is None

    def test_unrelated_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None


# ── save_result ──────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Cassidy Vane**\n*Pilot — flies like she was born in the black*\n..."
        path = save_result(content, "character")
        assert "cassidy-vane" in path.name

    def test_mode_used_as_suffix(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Rook Delmar**\n*Muscle — professional about it*"
        assert save_result(content, "character").name.endswith("-character.md")
        content2 = "## **Siena Mott**\n*Fence — you didn't get it from her*"
        assert save_result(content2, "npc").name.endswith("-npc.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Test Character**\n*Mechanic — keeps the lights on*"
        path = save_result(content, "character")
        assert path.read_text() == content

    def test_saves_to_firefly_characters_dir(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Test**\n*Role*"
        path = save_result(content, "character")
        assert "firefly_characters" in str(path)

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Rook Delmar**\n*Muscle*"
        path = save_result(content, "character")
        assert "**" not in path.name
        assert "#" not in path.name


# ── Constants ────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_valid_dice_sizes_are_cortex_dice(self):
        assert VALID_DICE_SIZES == {4, 6, 8, 10, 12}

    def test_cortex_ladder_is_ascending(self):
        assert CORTEX_LADDER == sorted(CORTEX_LADDER)

    def test_cortex_ladder_starts_at_d4(self):
        assert CORTEX_LADDER[0] == 4

    def test_cortex_ladder_ends_at_d12(self):
        assert CORTEX_LADDER[-1] == 12

    def test_nine_roles_defined(self):
        assert len(ROLES) == 9

    def test_three_verse_regions(self):
        assert len(VERSE_LOCATIONS) == 3
        assert set(VERSE_LOCATIONS.keys()) == {"Core", "Border", "Rim"}

    def test_six_war_history_options(self):
        assert len(WAR_HISTORY) == 6
