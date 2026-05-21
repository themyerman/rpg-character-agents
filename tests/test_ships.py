"""
Tests for ships.py — ship name pools and roll_ship_name().
No API calls: pure Python only.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from ships import (
    SHIP_POOLS,
    roll_ship_name,
    TRAVELLER_SHIP_TOOL_SCHEMA,
    FIREFLY_SHIP_TOOL_SCHEMA,
    SCUM_SHIP_TOOL_SCHEMA,
    DND_SHIP_TOOL_SCHEMA,
)

ALL_GAMES    = ["traveller", "firefly", "scum", "dnd"]
ALL_SCHEMAS  = [
    TRAVELLER_SHIP_TOOL_SCHEMA,
    FIREFLY_SHIP_TOOL_SCHEMA,
    SCUM_SHIP_TOOL_SCHEMA,
    DND_SHIP_TOOL_SCHEMA,
]


# ── SHIP_POOLS structure ───────────────────────────────────────────────────────

class TestShipPools:
    def test_all_games_present(self):
        for game in ALL_GAMES:
            assert game in SHIP_POOLS, f"'{game}' missing from SHIP_POOLS"

    def test_each_pool_has_required_keys(self):
        for game, pool in SHIP_POOLS.items():
            assert "names"    in pool, f"'{game}' missing 'names'"
            assert "classes"  in pool, f"'{game}' missing 'classes'"
            assert "register" in pool, f"'{game}' missing 'register'"

    def test_each_pool_has_adequate_names(self):
        for game, pool in SHIP_POOLS.items():
            assert len(pool["names"]) >= 20, \
                f"'{game}' has only {len(pool['names'])} ship names"

    def test_each_pool_has_adequate_classes(self):
        for game, pool in SHIP_POOLS.items():
            assert len(pool["classes"]) >= 5, \
                f"'{game}' has only {len(pool['classes'])} ship classes"

    def test_all_names_are_non_empty_strings(self):
        for game, pool in SHIP_POOLS.items():
            for name in pool["names"]:
                assert isinstance(name, str) and len(name) > 0, \
                    f"Invalid name in '{game}': {name!r}"

    def test_all_classes_are_non_empty_strings(self):
        for game, pool in SHIP_POOLS.items():
            for cls in pool["classes"]:
                assert isinstance(cls, str) and len(cls) > 0, \
                    f"Invalid class in '{game}': {cls!r}"

    def test_register_is_non_empty_string(self):
        for game, pool in SHIP_POOLS.items():
            assert isinstance(pool["register"], str) and len(pool["register"]) > 20, \
                f"'{game}' register too short"

    # ── Per-universe spot-checks ───────────────────────────────────────────────

    def test_traveller_has_imperial_names(self):
        names = SHIP_POOLS["traveller"]["names"]
        # Should have something evocative of the Third Imperium
        imperium = {"Empress Marava", "March Harrier", "Annic Nova", "Far Horizon"}
        assert imperium & set(names), "Missing key Traveller canon names"

    def test_traveller_has_typed_classes(self):
        classes = SHIP_POOLS["traveller"]["classes"]
        assert any("Type-" in c for c in classes), \
            "Traveller classes should include Type-* designations"

    def test_firefly_has_serenity(self):
        # Serenity is the canonical Firefly ship — it should be in the pool
        assert "Serenity" in SHIP_POOLS["firefly"]["names"]

    def test_firefly_has_firefly_class(self):
        assert any("Firefly" in c for c in SHIP_POOLS["firefly"]["classes"])

    def test_scum_names_feel_ominous_or_sardonic(self):
        names = SHIP_POOLS["scum"]["names"]
        # A selection of the specifically criminal-poetic names should be present
        expected = {"Pale Dreamer", "Nothing Personal", "Iron Hand", "Quiet Ruin"}
        assert expected & set(names)

    def test_dnd_has_nautical_names(self):
        names = SHIP_POOLS["dnd"]["names"]
        # Should have ocean / sea imagery
        sea_words = {"Storm", "Sea", "Tide", "Wave", "Kraken", "Leviathan"}
        assert any(any(w in n for w in sea_words) for n in names)

    def test_dnd_has_classic_ship_types(self):
        classes = SHIP_POOLS["dnd"]["classes"]
        classic = {"Sloop", "Brigantine", "Galleon", "Longship"}
        assert classic & set(classes)


# ── roll_ship_name ─────────────────────────────────────────────────────────────

class TestRollShipName:
    def test_returns_valid_json_for_all_games(self):
        for game in ALL_GAMES:
            result = json.loads(roll_ship_name(game))
            assert isinstance(result, dict), f"'{game}' did not return a dict"

    def test_has_required_keys(self):
        for game in ALL_GAMES:
            data = json.loads(roll_ship_name(game))
            for key in ("name", "ship_class", "register"):
                assert key in data, f"'{game}' result missing key: {key}"

    def test_name_comes_from_pool(self):
        for game in ALL_GAMES:
            for _ in range(10):
                data = json.loads(roll_ship_name(game))
                assert data["name"] in SHIP_POOLS[game]["names"], \
                    f"'{game}' name {data['name']!r} not in pool"

    def test_class_comes_from_pool(self):
        for game in ALL_GAMES:
            for _ in range(10):
                data = json.loads(roll_ship_name(game))
                assert data["ship_class"] in SHIP_POOLS[game]["classes"], \
                    f"'{game}' class {data['ship_class']!r} not in pool"

    def test_register_matches_game(self):
        for game in ALL_GAMES:
            data = json.loads(roll_ship_name(game))
            assert data["register"] == SHIP_POOLS[game]["register"]

    def test_returns_variety_of_names(self):
        for game in ALL_GAMES:
            names = {json.loads(roll_ship_name(game))["name"] for _ in range(30)}
            assert len(names) >= 3, f"'{game}' not producing varied names"

    def test_invalid_game_returns_error(self):
        data = json.loads(roll_ship_name("pathfinder"))
        assert "error" in data

    def test_error_lists_valid_games(self):
        data = json.loads(roll_ship_name("pathfinder"))
        for game in ALL_GAMES:
            assert game in data["error"]


# ── Tool schemas ───────────────────────────────────────────────────────────────

class TestShipToolSchemas:
    def test_all_schemas_have_roll_ship_name(self):
        for schema in ALL_SCHEMAS:
            assert schema["name"] == "roll_ship_name"

    def test_all_schemas_have_description(self):
        for schema in ALL_SCHEMAS:
            assert "description" in schema
            assert len(schema["description"]) > 20

    def test_all_schemas_have_input_schema(self):
        for schema in ALL_SCHEMAS:
            assert "input_schema" in schema

    def test_all_schemas_require_nothing(self):
        for schema in ALL_SCHEMAS:
            assert schema["input_schema"].get("required", []) == []

    def test_schemas_have_distinct_descriptions(self):
        descriptions = [s["description"] for s in ALL_SCHEMAS]
        assert len(descriptions) == len(set(descriptions)), \
            "Two schemas share an identical description"

    def test_traveller_schema_mentions_imperial(self):
        assert "Imperial" in TRAVELLER_SHIP_TOOL_SCHEMA["description"] or \
               "Traveller" in TRAVELLER_SHIP_TOOL_SCHEMA["description"]

    def test_firefly_schema_mentions_verse(self):
        desc = FIREFLY_SHIP_TOOL_SCHEMA["description"]
        assert "'Verse" in desc or "Firefly" in desc

    def test_scum_schema_mentions_menace(self):
        desc = SCUM_SHIP_TOOL_SCHEMA["description"]
        assert "menace" in desc or "Villainy" in desc or "criminal" in desc.lower()
