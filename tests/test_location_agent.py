"""
Tests for location_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from location_agent import (
    roll_dnd_location_seed,
    roll_traveller_location_seed,
    roll_firefly_location_seed,
    roll_scum_location_seed,
    save_location,
    detect_phase,
    LOCATION_POOLS,
    GAME_SUBDIRS,
    DND_LOCATION_SEED_SCHEMA,
    TRAVELLER_LOCATION_SEED_SCHEMA,
    FIREFLY_LOCATION_SEED_SCHEMA,
    SCUM_LOCATION_SEED_SCHEMA,
    GAME_TOOLS,
    GAME_SYSTEM_PROMPTS,
)


GAMES = ["dnd", "traveller", "firefly", "scum"]
ROLLERS = {
    "dnd":       roll_dnd_location_seed,
    "traveller": roll_traveller_location_seed,
    "firefly":   roll_firefly_location_seed,
    "scum":      roll_scum_location_seed,
}


# ── LOCATION_POOLS structure ──────────────────────────────────────────────────

class TestLocationPools:
    def test_all_four_games_present(self):
        assert set(LOCATION_POOLS.keys()) == {"dnd", "traveller", "firefly", "scum"}

    def test_each_game_has_four_categories(self):
        required = {"types", "conditions", "complications", "hooks"}
        for game in GAMES:
            assert set(LOCATION_POOLS[game].keys()) == required, \
                f"{game} missing seed categories"

    def test_types_has_at_least_fifteen_entries(self):
        for game in GAMES:
            entries = LOCATION_POOLS[game]["types"]
            assert len(entries) >= 15, f"{game}/types has only {len(entries)} entries"

    def test_conditions_has_at_least_fifteen_entries(self):
        for game in GAMES:
            entries = LOCATION_POOLS[game]["conditions"]
            assert len(entries) >= 15, f"{game}/conditions has only {len(entries)} entries"

    def test_complications_has_at_least_fifteen_entries(self):
        for game in GAMES:
            entries = LOCATION_POOLS[game]["complications"]
            assert len(entries) >= 15, f"{game}/complications has only {len(entries)} entries"

    def test_hooks_has_at_least_ten_entries(self):
        for game in GAMES:
            entries = LOCATION_POOLS[game]["hooks"]
            assert len(entries) >= 10, f"{game}/hooks has only {len(entries)} entries"

    def test_all_entries_are_non_empty_strings(self):
        for game in GAMES:
            for category, entries in LOCATION_POOLS[game].items():
                for entry in entries:
                    assert isinstance(entry, str) and len(entry) > 5, \
                        f"{game}/{category} has an invalid entry: {entry!r}"

    def test_game_specific_content_present(self):
        # Each game's types should reference game-appropriate things
        assert any("tavern" in t.lower() or "inn" in t.lower() or "market" in t.lower()
                   for t in LOCATION_POOLS["dnd"]["types"])
        assert any("starport" in t.lower() or "station" in t.lower()
                   for t in LOCATION_POOLS["traveller"]["types"])
        assert any("rim" in t.lower() or "alliance" in t.lower() or "firefly" in t.lower()
                   or "border" in t.lower()
                   for t in LOCATION_POOLS["firefly"]["types"])
        assert any("hegemony" in t.lower() or "guild" in t.lower()
                   for t in LOCATION_POOLS["scum"]["types"])


# ── Seed rollers ──────────────────────────────────────────────────────────────

class TestLocationSeedRollers:
    @pytest.mark.parametrize("game", GAMES)
    def test_returns_valid_json(self, game):
        result = ROLLERS[game]()
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("game", GAMES)
    def test_has_required_keys(self, game):
        data = json.loads(ROLLERS[game]())
        assert "type" in data
        assert "condition" in data
        assert "complication" in data
        assert "hook" in data

    @pytest.mark.parametrize("game", GAMES)
    def test_values_come_from_pool(self, game):
        for _ in range(10):
            data = json.loads(ROLLERS[game]())
            pool = LOCATION_POOLS[game]
            assert data["type"]        in pool["types"]
            assert data["condition"]   in pool["conditions"]
            assert data["complication"] in pool["complications"]
            assert data["hook"]        in pool["hooks"]

    @pytest.mark.parametrize("game", GAMES)
    def test_returns_variety(self, game):
        results = {json.loads(ROLLERS[game]())["type"] for _ in range(30)}
        assert len(results) >= 3, f"{game} seed roller shows no variety"


# ── Tool schemas ──────────────────────────────────────────────────────────────

class TestLocationToolSchemas:
    def test_dnd_schema_has_correct_name(self):
        assert DND_LOCATION_SEED_SCHEMA["name"] == "roll_dnd_location_seed"

    def test_traveller_schema_has_correct_name(self):
        assert TRAVELLER_LOCATION_SEED_SCHEMA["name"] == "roll_traveller_location_seed"

    def test_firefly_schema_has_correct_name(self):
        assert FIREFLY_LOCATION_SEED_SCHEMA["name"] == "roll_firefly_location_seed"

    def test_scum_schema_has_correct_name(self):
        assert SCUM_LOCATION_SEED_SCHEMA["name"] == "roll_scum_location_seed"

    def test_all_schemas_have_required_top_level_keys(self):
        schemas = [
            DND_LOCATION_SEED_SCHEMA,
            TRAVELLER_LOCATION_SEED_SCHEMA,
            FIREFLY_LOCATION_SEED_SCHEMA,
            SCUM_LOCATION_SEED_SCHEMA,
        ]
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema


# ── GAME_TOOLS ────────────────────────────────────────────────────────────────

class TestGameTools:
    def test_all_games_have_tools(self):
        assert set(GAME_TOOLS.keys()) == {"dnd", "traveller", "firefly", "scum"}

    def test_dnd_has_seed_and_name_but_no_ship(self):
        names = {t["name"] for t in GAME_TOOLS["dnd"]}
        assert "roll_dnd_location_seed" in names
        assert "roll_name_suggestion" in names
        assert "roll_ship_name" not in names

    def test_traveller_has_ship_tool(self):
        names = {t["name"] for t in GAME_TOOLS["traveller"]}
        assert "roll_ship_name" in names

    def test_firefly_has_ship_tool(self):
        names = {t["name"] for t in GAME_TOOLS["firefly"]}
        assert "roll_ship_name" in names

    def test_scum_has_ship_tool(self):
        names = {t["name"] for t in GAME_TOOLS["scum"]}
        assert "roll_ship_name" in names


# ── GAME_SYSTEM_PROMPTS ───────────────────────────────────────────────────────

class TestGameSystemPrompts:
    def test_all_games_have_system_prompt(self):
        assert set(GAME_SYSTEM_PROMPTS.keys()) == {"dnd", "traveller", "firefly", "scum"}

    def test_each_prompt_is_non_empty_string(self):
        for game, prompt in GAME_SYSTEM_PROMPTS.items():
            assert isinstance(prompt, str) and len(prompt) > 100, \
                f"{game} system prompt is too short"

    def test_prompts_mention_correct_seed_tool(self):
        assert "roll_dnd_location_seed" in GAME_SYSTEM_PROMPTS["dnd"]
        assert "roll_traveller_location_seed" in GAME_SYSTEM_PROMPTS["traveller"]
        assert "roll_firefly_location_seed" in GAME_SYSTEM_PROMPTS["firefly"]
        assert "roll_scum_location_seed" in GAME_SYSTEM_PROMPTS["scum"]


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_location_seed_tool_returns_seed(self):
        assert detect_phase("roll_dnd_location_seed", set()) == "seed"
        assert detect_phase("roll_traveller_location_seed", set()) == "seed"
        assert detect_phase("roll_firefly_location_seed", set()) == "seed"
        assert detect_phase("roll_scum_location_seed", set()) == "seed"

    def test_name_suggestion_returns_name(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_ship_name_returns_ship(self):
        assert detect_phase("roll_ship_name", set()) == "ship"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None
        assert detect_phase("roll_dice", set()) is None


# ── save_location ─────────────────────────────────────────────────────────────

class TestSaveLocation:
    def test_saves_to_correct_directory(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **The Crossroads Inn**\n*A roadside waystation at the edge of the known*"
        path = save_location(content, "dnd")
        assert "locations" in str(path)
        assert "dnd" in str(path)

    def test_filename_uses_slug(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **The Crossroads Inn**\n*detail*"
        path = save_location(content, "dnd")
        assert "the-crossroads-inn" in path.name

    def test_filename_ends_with_location_md(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **Test Place**\n*detail*"
        path = save_location(content, "dnd")
        assert path.name.endswith("-location.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **Orion Station**\n*A starport that lost its Class A rating*"
        path = save_location(content, "traveller")
        assert path.read_text() == content

    def test_scum_uses_scum_villainy_subdir(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **The Fringe Station**\n*detail*"
        path = save_location(content, "scum")
        assert "scum_villainy" in str(path)

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **Crossroads Inn**\n*detail*"
        path1 = save_location(content, "dnd")
        path2 = save_location(content, "dnd")
        assert path1 != path2
        assert path1.exists() and path2.exists()
        assert path2.name == "crossroads-inn-location-2.md"

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        import location_agent
        monkeypatch.setattr(location_agent, "_OUTPUT", tmp_path)
        content = "## **Bold Place**\n*detail*"
        path = save_location(content, "firefly")
        assert "**" not in path.name
        assert "#" not in path.name


# ── GAME_SUBDIRS ──────────────────────────────────────────────────────────────

class TestGameSubdirs:
    def test_all_four_games_present(self):
        assert set(GAME_SUBDIRS.keys()) == {"dnd", "traveller", "firefly", "scum"}

    def test_scum_maps_to_scum_villainy(self):
        assert GAME_SUBDIRS["scum"] == "scum_villainy"

    def test_others_map_to_themselves(self):
        assert GAME_SUBDIRS["dnd"] == "dnd"
        assert GAME_SUBDIRS["traveller"] == "traveller"
        assert GAME_SUBDIRS["firefly"] == "firefly"
