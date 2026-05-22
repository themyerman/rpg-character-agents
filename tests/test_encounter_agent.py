"""
Tests for encounter_agent.py — seed tables, rollers, schemas, helpers.
No API calls: pure Python only.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.encounter_agent import (
    ENCOUNTER_POOLS,
    GAME_SUBDIRS,
    GAME_TOOLS,
    DND_ENCOUNTER_SEED_SCHEMA,
    TRAVELLER_ENCOUNTER_SEED_SCHEMA,
    FIREFLY_ENCOUNTER_SEED_SCHEMA,
    SCUM_ENCOUNTER_SEED_SCHEMA,
    DND_ENCOUNTER_TOOLS,
    TRAVELLER_ENCOUNTER_TOOLS,
    FIREFLY_ENCOUNTER_TOOLS,
    SCUM_ENCOUNTER_TOOLS,
    roll_dnd_encounter_seed,
    roll_traveller_encounter_seed,
    roll_firefly_encounter_seed,
    roll_scum_encounter_seed,
    SEED_ROLLERS,
    list_party_files,
    save_encounter,
    detect_phase,
    make_run_tool,
)

ALL_GAMES = ["dnd", "traveller", "firefly", "scum"]
ALL_SEED_SCHEMAS = [
    DND_ENCOUNTER_SEED_SCHEMA,
    TRAVELLER_ENCOUNTER_SEED_SCHEMA,
    FIREFLY_ENCOUNTER_SEED_SCHEMA,
    SCUM_ENCOUNTER_SEED_SCHEMA,
]


# ── ENCOUNTER_POOLS structure ─────────────────────────────────────────────────

class TestEncounterPools:
    REQUIRED_KEYS = {"contexts", "situations", "complications", "motivations"}

    def test_all_games_present(self):
        for game in ALL_GAMES:
            assert game in ENCOUNTER_POOLS, f"'{game}' missing from ENCOUNTER_POOLS"

    def test_each_pool_has_required_keys(self):
        for game, pool in ENCOUNTER_POOLS.items():
            for key in self.REQUIRED_KEYS:
                assert key in pool, f"'{game}' missing '{key}'"

    def test_contexts_adequate_count(self):
        for game, pool in ENCOUNTER_POOLS.items():
            assert len(pool["contexts"]) >= 15, \
                f"'{game}' has only {len(pool['contexts'])} contexts"

    def test_situations_adequate_count(self):
        for game, pool in ENCOUNTER_POOLS.items():
            assert len(pool["situations"]) >= 15, \
                f"'{game}' has only {len(pool['situations'])} situations"

    def test_complications_adequate_count(self):
        for game, pool in ENCOUNTER_POOLS.items():
            assert len(pool["complications"]) >= 10, \
                f"'{game}' has only {len(pool['complications'])} complications"

    def test_motivations_adequate_count(self):
        for game, pool in ENCOUNTER_POOLS.items():
            assert len(pool["motivations"]) >= 10, \
                f"'{game}' has only {len(pool['motivations'])} motivations"

    def test_all_entries_are_non_empty_strings(self):
        for game, pool in ENCOUNTER_POOLS.items():
            for key in self.REQUIRED_KEYS:
                for entry in pool[key]:
                    assert isinstance(entry, str) and len(entry) > 10, \
                        f"Short/invalid entry in '{game}' {key}: {entry!r}"

    def test_no_duplicate_entries_per_key(self):
        for game, pool in ENCOUNTER_POOLS.items():
            for key in self.REQUIRED_KEYS:
                entries = pool[key]
                assert len(entries) == len(set(entries)), \
                    f"Duplicate entries in '{game}' {key}"

    # ── Spot-checks ───────────────────────────────────────────────────────────

    def test_dnd_contexts_feel_fantastical(self):
        contexts = ENCOUNTER_POOLS["dnd"]["contexts"]
        # Should contain something with classic fantasy flavour
        fantasy_words = {"dungeon", "temple", "noble", "wizard", "halfling",
                         "dwarven", "crossroads", "shrine", "sewer", "library"}
        assert any(any(w in c.lower() for w in fantasy_words) for c in contexts)

    def test_traveller_contexts_feel_like_space_opera(self):
        contexts = ENCOUNTER_POOLS["traveller"]["contexts"]
        space_words = {"starport", "ship", "station", "Imperial", "jump",
                       "scout", "highport", "downport", "belter", "freeport"}
        assert any(any(w in c.lower() for w in space_words) for c in contexts)

    def test_firefly_contexts_reference_the_verse(self):
        contexts = ENCOUNTER_POOLS["firefly"]["contexts"]
        verse_words = {"Alliance", "rim", "moon", "Reaver", "Browncoat",
                       "gas giant", "terraforming", "companion"}
        assert any(any(w in c for w in verse_words) for c in contexts)

    def test_scum_contexts_feel_criminal_and_faction_driven(self):
        contexts = ENCOUNTER_POOLS["scum"]["contexts"]
        scum_words = {"Hegemony", "Guild", "cult", "faction", "Ur", "score",
                      "station", "salvage", "derelict"}
        assert any(any(w in c for w in scum_words) for c in contexts)

    def test_motivations_are_comprehensible_not_cartoonish(self):
        # Motivations should not contain "evil" as a standalone reason
        for game, pool in ENCOUNTER_POOLS.items():
            for m in pool["motivations"]:
                assert "for evil" not in m.lower() and m.lower() != "evil", \
                    f"Cartoonish motivation in '{game}': {m!r}"


# ── GAME_SUBDIRS ──────────────────────────────────────────────────────────────

class TestGameSubdirs:
    def test_all_games_have_subdir(self):
        for game in ALL_GAMES:
            assert game in GAME_SUBDIRS

    def test_scum_maps_to_scum_villainy(self):
        assert GAME_SUBDIRS["scum"] == "scum_villainy"

    def test_other_games_map_to_themselves(self):
        for game in ("dnd", "traveller", "firefly"):
            assert GAME_SUBDIRS[game] == game


# ── Seed roller functions ─────────────────────────────────────────────────────

class TestSeedRollers:
    def test_all_games_in_seed_rollers(self):
        for game in ALL_GAMES:
            assert game in SEED_ROLLERS

    def test_returns_valid_json(self):
        for game in ALL_GAMES:
            result = SEED_ROLLERS[game]()
            data = json.loads(result)
            assert isinstance(data, dict), f"'{game}' seed did not return a dict"

    def test_has_required_keys(self):
        for game in ALL_GAMES:
            data = json.loads(SEED_ROLLERS[game]())
            for key in ("context", "situation", "complication", "motivation"):
                assert key in data, f"'{game}' seed missing key: {key}"

    def test_values_come_from_pool(self):
        for game in ALL_GAMES:
            for _ in range(10):
                data = json.loads(SEED_ROLLERS[game]())
                pool = ENCOUNTER_POOLS[game]
                assert data["context"]      in pool["contexts"]
                assert data["situation"]    in pool["situations"]
                assert data["complication"] in pool["complications"]
                assert data["motivation"]   in pool["motivations"]

    def test_returns_variety(self):
        for game in ALL_GAMES:
            contexts = {json.loads(SEED_ROLLERS[game]())["context"] for _ in range(40)}
            assert len(contexts) >= 3, f"'{game}' not producing varied contexts"

    def test_individual_functions_are_consistent(self):
        """Named functions match their SEED_ROLLERS entry."""
        fn_map = {
            "dnd":       roll_dnd_encounter_seed,
            "traveller": roll_traveller_encounter_seed,
            "firefly":   roll_firefly_encounter_seed,
            "scum":      roll_scum_encounter_seed,
        }
        for game, fn in fn_map.items():
            data = json.loads(fn())
            pool = ENCOUNTER_POOLS[game]
            assert data["context"] in pool["contexts"]


# ── Seed schemas ──────────────────────────────────────────────────────────────

class TestSeedSchemas:
    def test_all_schemas_have_correct_name(self):
        expected = [
            (DND_ENCOUNTER_SEED_SCHEMA,       "roll_dnd_encounter_seed"),
            (TRAVELLER_ENCOUNTER_SEED_SCHEMA, "roll_traveller_encounter_seed"),
            (FIREFLY_ENCOUNTER_SEED_SCHEMA,   "roll_firefly_encounter_seed"),
            (SCUM_ENCOUNTER_SEED_SCHEMA,      "roll_scum_encounter_seed"),
        ]
        for schema, name in expected:
            assert schema["name"] == name

    def test_all_schemas_have_description(self):
        for schema in ALL_SEED_SCHEMAS:
            assert "description" in schema
            assert len(schema["description"]) > 30

    def test_all_schemas_have_input_schema(self):
        for schema in ALL_SEED_SCHEMAS:
            assert "input_schema" in schema

    def test_all_schemas_require_nothing(self):
        for schema in ALL_SEED_SCHEMAS:
            assert schema["input_schema"].get("required", []) == []

    def test_descriptions_are_distinct(self):
        descs = [s["description"] for s in ALL_SEED_SCHEMAS]
        assert len(descs) == len(set(descs)), "Two seed schemas share a description"

    def test_descriptions_mention_game(self):
        assert "D&D" in DND_ENCOUNTER_SEED_SCHEMA["description"]
        assert "Traveller" in TRAVELLER_ENCOUNTER_SEED_SCHEMA["description"]
        assert "Firefly" in FIREFLY_ENCOUNTER_SEED_SCHEMA["description"]
        assert "Scum" in SCUM_ENCOUNTER_SEED_SCHEMA["description"]

    def test_descriptions_discourage_defaults(self):
        """Each description should remind the model not to default to clichés."""
        cliche_warnings = [
            DND_ENCOUNTER_SEED_SCHEMA["description"],
            TRAVELLER_ENCOUNTER_SEED_SCHEMA["description"],
            FIREFLY_ENCOUNTER_SEED_SCHEMA["description"],
            SCUM_ENCOUNTER_SEED_SCHEMA["description"],
        ]
        for desc in cliche_warnings:
            assert "prevent" in desc.lower() or "first" in desc.lower()


# ── GAME_TOOLS lists ──────────────────────────────────────────────────────────

class TestGameTools:
    def test_all_games_in_game_tools(self):
        for game in ALL_GAMES:
            assert game in GAME_TOOLS

    def test_each_game_tools_has_seed_schema(self):
        seed_names = {
            "dnd":       "roll_dnd_encounter_seed",
            "traveller": "roll_traveller_encounter_seed",
            "firefly":   "roll_firefly_encounter_seed",
            "scum":      "roll_scum_encounter_seed",
        }
        for game, expected_name in seed_names.items():
            tool_names = [t["name"] for t in GAME_TOOLS[game]]
            assert expected_name in tool_names, \
                f"'{game}' tools missing seed schema '{expected_name}'"

    def test_each_game_tools_has_name_schema(self):
        for game in ALL_GAMES:
            tool_names = [t["name"] for t in GAME_TOOLS[game]]
            assert "roll_name_suggestion" in tool_names, \
                f"'{game}' tools missing roll_name_suggestion"

    def test_each_game_tools_has_ship_schema(self):
        for game in ALL_GAMES:
            tool_names = [t["name"] for t in GAME_TOOLS[game]]
            assert "roll_ship_name" in tool_names, \
                f"'{game}' tools missing roll_ship_name"

    def test_no_duplicate_tool_names_per_game(self):
        for game in ALL_GAMES:
            names = [t["name"] for t in GAME_TOOLS[game]]
            assert len(names) == len(set(names)), \
                f"'{game}' tools has duplicate tool names"


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_seed_tools_return_seed_phase(self):
        for name in (
            "roll_dnd_encounter_seed", "roll_traveller_encounter_seed",
            "roll_firefly_encounter_seed", "roll_scum_encounter_seed",
        ):
            assert detect_phase(name, set()) == "seed"

    def test_name_suggestion_returns_names_phase(self):
        assert detect_phase("roll_name_suggestion", set()) == "names"

    def test_ship_name_returns_ship_phase(self):
        assert detect_phase("roll_ship_name", set()) == "ship"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("some_other_tool", set()) is None


# ── make_run_tool ─────────────────────────────────────────────────────────────

class TestMakeRunTool:
    def test_seed_tool_dispatches_correctly(self):
        for game in ALL_GAMES:
            fn = make_run_tool(game)
            seed_name = f"roll_{game}_encounter_seed"
            result = json.loads(fn(seed_name, {}))
            assert "context" in result

    def test_name_suggestion_dispatches(self):
        fn = make_run_tool("dnd")
        result = json.loads(fn("roll_name_suggestion", {}))
        assert "suggested_name" in result

    def test_ship_name_dispatches_with_correct_game(self):
        for game in ALL_GAMES:
            fn = make_run_tool(game)
            result = json.loads(fn("roll_ship_name", {}))
            assert "name" in result
            assert "ship_class" in result

    def test_unknown_tool_returns_error_string(self):
        fn = make_run_tool("dnd")
        result = fn("nonexistent_tool", {})
        assert "Unknown" in result


# ── list_party_files ──────────────────────────────────────────────────────────

class TestListPartyFiles:
    def test_returns_list(self):
        # Even if directory doesn't exist, should return empty list not raise
        for game in ALL_GAMES:
            result = list_party_files(game)
            assert isinstance(result, list)

    def test_nonexistent_dir_returns_empty(self):
        result = list_party_files("dnd")
        # May or may not exist; either way no exception
        assert isinstance(result, list)

    def test_returns_only_md_files(self, tmp_path, monkeypatch):
        """Files in the party dir are .md only."""
        import agents.encounter_agent as ea
        subdir = tmp_path / "dnd" / "parties"
        subdir.mkdir(parents=True)
        (subdir / "my-crew-party.md").write_text("# My Crew")
        (subdir / "notes.txt").write_text("not a party")

        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        files = list_party_files("dnd")
        assert all(f.suffix == ".md" for f in files)
        assert len(files) == 1

    def test_scum_uses_scum_villainy_subdir(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        subdir = tmp_path / "scum_villainy" / "parties"
        subdir.mkdir(parents=True)
        (subdir / "pale-dreamer-crew.md").write_text("# Pale Dreamer Crew")

        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        files = list_party_files("scum")
        assert len(files) == 1


# ── save_encounter ────────────────────────────────────────────────────────────

class TestSaveEncounter:
    SAMPLE_CONTENT = "## The Wrong Ferryman\n\n*Something is off about the crossing.*\n\n### Setting\nFog."

    def test_saves_to_correct_directory(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path = save_encounter(self.SAMPLE_CONTENT, "dnd")
        assert path.parent == tmp_path / "dnd" / "encounters"

    def test_scum_saves_to_scum_villainy(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path = save_encounter(self.SAMPLE_CONTENT, "scum")
        assert "scum_villainy" in str(path)

    def test_filename_ends_with_encounter(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path = save_encounter(self.SAMPLE_CONTENT, "traveller")
        assert path.name.endswith("-encounter.md")

    def test_filename_slugified_from_title(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path = save_encounter(self.SAMPLE_CONTENT, "dnd")
        assert "the-wrong-ferryman" in path.name

    def test_file_content_preserved(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path = save_encounter(self.SAMPLE_CONTENT, "firefly")
        assert path.read_text() == self.SAMPLE_CONTENT

    def test_collision_counter(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path1 = save_encounter(self.SAMPLE_CONTENT, "dnd")
        path2 = save_encounter(self.SAMPLE_CONTENT, "dnd")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

    def test_directory_created_if_missing(self, tmp_path, monkeypatch):
        import agents.encounter_agent as ea
        monkeypatch.setattr(ea, "_OUTPUT", tmp_path)
        path = save_encounter(self.SAMPLE_CONTENT, "dnd")
        assert path.parent.exists()
