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
    roll_homeworld,
    roll_job_hook,
    save_result,
    detect_phase,
    VALID_DICE_SIZES,
    CORTEX_LADDER,
    ROLES,
    VERSE_LOCATIONS,
    VERSE_WORLDS,
    JOB_HOOKS,
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

    def test_roll_homeworld_returns_homeworld(self):
        assert detect_phase("roll_homeworld", set()) == "homeworld"

    def test_roll_job_hook_returns_job(self):
        assert detect_phase("roll_job_hook", set()) == "job"

    def test_roll_name_suggestion_returns_name(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_roll_ship_name_returns_ship(self):
        assert detect_phase("roll_ship_name", set()) == "ship"

    def test_roll_firefly_gear_returns_gear(self):
        assert detect_phase("roll_firefly_gear", set()) == "gear"


# ── Gear wiring ──────────────────────────────────────────────────────────────────

class TestGearWiring:
    def test_gear_phase_message_present(self):
        import firefly_agent
        assert "gear" in firefly_agent.PHASE_MESSAGES

    def test_gear_phase_message_is_string(self):
        import firefly_agent
        assert isinstance(firefly_agent.PHASE_MESSAGES["gear"], str)
        assert len(firefly_agent.PHASE_MESSAGES["gear"]) > 0

    def test_firefly_gear_schema_in_tools(self):
        import firefly_agent
        tool_names = [t["name"] for t in firefly_agent.TOOLS]
        assert "roll_firefly_gear" in tool_names

    def test_run_tool_returns_gear_json(self):
        import firefly_agent
        result = firefly_agent.run_tool("roll_firefly_gear", {"role": "Pilot"})
        data = json.loads(result)
        assert "gear" in data
        assert "note" in data
        assert len(data["gear"]) == 4

    def test_run_tool_gear_works_for_mechanic(self):
        import firefly_agent
        result = firefly_agent.run_tool("roll_firefly_gear", {"role": "Mechanic"})
        data = json.loads(result)
        assert "gear" in data

    def test_system_prompt_mentions_roll_firefly_gear(self):
        import firefly_agent
        assert "roll_firefly_gear" in firefly_agent.SYSTEM_PROMPT


# ── save_result ──────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Cassidy Vane**\n*Pilot — flies like she was born in the black*\n..."
        path = save_result(content, "full")
        assert "cassidy-vane" in path.name

    def test_mode_used_as_suffix(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Rook Delmar**\n*Muscle — professional about it*"
        assert save_result(content, "full").name.endswith("-full.md")
        content2 = "## **Siena Mott**\n*Fence — you didn't get it from her*"
        assert save_result(content2, "npc").name.endswith("-npc.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Test Character**\n*Mechanic — keeps the lights on*"
        path = save_result(content, "full")
        assert path.read_text() == content

    def test_saves_to_firefly_characters_dir(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Test**\n*Role*"
        path = save_result(content, "full")
        assert "characters" in str(path)
        assert "firefly" in str(path)

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        """Second character with the same name gets -2 suffix, not a silent overwrite."""
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Cassidy Vane**\n*Pilot — flies like she was born in the black*"
        path1 = save_result(content, "full")
        path2 = save_result(content, "full")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()
        assert path2.name == "cassidy-vane-full-2.md"

    def test_collision_increments_beyond_two(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Cassidy Vane**\n*Pilot*"
        save_result(content, "full")
        save_result(content, "full")
        path3 = save_result(content, "full")
        assert path3.name == "cassidy-vane-full-3.md"

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        import firefly_agent
        monkeypatch.setattr(firefly_agent, "__file__", str(tmp_path / "firefly_agent.py"))
        content = "## **Rook Delmar**\n*Muscle*"
        path = save_result(content, "full")
        assert "**" not in path.name
        assert "#" not in path.name


# ── roll_homeworld ───────────────────────────────────────────────────────────────

class TestRollHomeworld:
    def test_returns_valid_json(self):
        result = roll_homeworld("Core")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_world_region_and_flavor(self):
        for region in ("Core", "Border", "Rim"):
            data = json.loads(roll_homeworld(region))
            assert "world" in data
            assert "region" in data
            assert "flavor" in data

    def test_world_is_in_known_list(self):
        for region in ("Core", "Border", "Rim"):
            data = json.loads(roll_homeworld(region))
            world_names = [w for w, _ in VERSE_WORLDS[region]]
            assert data["world"] in world_names, f"Unknown world '{data['world']}' for {region}"

    def test_region_matches_input(self):
        for region in ("Core", "Border", "Rim"):
            data = json.loads(roll_homeworld(region))
            assert data["region"] == region

    def test_invalid_region_returns_error(self):
        result = roll_homeworld("Deep Space")
        assert "Unknown" in result

    def test_flavor_is_non_empty_string(self):
        data = json.loads(roll_homeworld("Rim"))
        assert isinstance(data["flavor"], str)
        assert len(data["flavor"]) > 0

    def test_returns_variety_across_calls(self):
        # 50 rolls on the Rim (15 worlds) should yield more than one distinct world
        worlds = {json.loads(roll_homeworld("Rim"))["world"] for _ in range(50)}
        assert len(worlds) > 1

    def test_border_worlds_expanded(self):
        # Border should have well more worlds than the old VERSE_LOCATIONS list
        assert len(VERSE_WORLDS["Border"]) > len(VERSE_LOCATIONS["Border"]["worlds"])

    def test_rim_worlds_expanded(self):
        assert len(VERSE_WORLDS["Rim"]) > len(VERSE_LOCATIONS["Rim"]["worlds"])


# ── roll_job_hook ────────────────────────────────────────────────────────────────

class TestRollJobHook:
    def test_returns_valid_json(self):
        result = roll_job_hook()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(roll_job_hook())
        assert "job_type" in data
        assert "description" in data
        assert "complication" in data

    def test_job_type_is_known(self):
        known_types = {h["type"] for h in JOB_HOOKS}
        for _ in range(20):
            data = json.loads(roll_job_hook())
            assert data["job_type"] in known_types

    def test_returns_variety(self):
        # 30 rolls should produce at least 3 distinct job types (14 options)
        types = {json.loads(roll_job_hook())["job_type"] for _ in range(30)}
        assert len(types) >= 3

    def test_complication_is_non_empty_string(self):
        data = json.loads(roll_job_hook())
        assert isinstance(data["complication"], str)
        assert len(data["complication"]) > 0

    def test_complication_belongs_to_job(self):
        for _ in range(20):
            data = json.loads(roll_job_hook())
            hook = next(h for h in JOB_HOOKS if h["type"] == data["job_type"])
            assert data["complication"] in hook["complications"]

    def test_no_pharmaceutical_default_type(self):
        # Pharmaceutical/medical cargo should not be a standalone job type
        known_types = {h["type"] for h in JOB_HOOKS}
        assert "Pharmaceutical Run" not in known_types
        assert "Medical Cargo" not in known_types

    def test_at_least_ten_job_types(self):
        assert len(JOB_HOOKS) >= 10


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
