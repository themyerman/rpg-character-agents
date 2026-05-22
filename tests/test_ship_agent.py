"""
Tests for ship_agent.py — seed tables, stat generators, schemas, helpers.
No API calls: pure Python only.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.ship_agent import (
    SHIP_SEED_POOLS,
    GAME_SUBDIRS,
    GAME_TOOLS,
    DND_SHIP_SEED_SCHEMA,
    TRAVELLER_SHIP_SEED_SCHEMA,
    FIREFLY_SHIP_SEED_SCHEMA,
    SCUM_SHIP_SEED_SCHEMA,
    DND_SHIP_STATS_SCHEMA,
    TRAVELLER_SHIP_STATS_SCHEMA,
    FIREFLY_SHIP_STATS_SCHEMA,
    SCUM_SHIP_STATS_SCHEMA,
    DND_SHIP_TOOLS,
    TRAVELLER_SHIP_TOOLS,
    FIREFLY_SHIP_TOOLS,
    SCUM_SHIP_TOOLS,
    roll_dnd_ship_seed,
    roll_traveller_ship_seed,
    roll_firefly_ship_seed,
    roll_scum_ship_seed,
    roll_dnd_ship_stats,
    roll_traveller_ship_stats,
    roll_firefly_ship_stats,
    roll_scum_ship_stats,
    SEED_ROLLERS,
    STAT_ROLLERS,
    detect_phase,
    make_run_tool,
    save_ship,
)

ALL_GAMES = ["dnd", "traveller", "firefly", "scum"]

ALL_SEED_SCHEMAS = [
    DND_SHIP_SEED_SCHEMA,
    TRAVELLER_SHIP_SEED_SCHEMA,
    FIREFLY_SHIP_SEED_SCHEMA,
    SCUM_SHIP_SEED_SCHEMA,
]

ALL_STATS_SCHEMAS = [
    DND_SHIP_STATS_SCHEMA,
    TRAVELLER_SHIP_STATS_SCHEMA,
    FIREFLY_SHIP_STATS_SCHEMA,
    SCUM_SHIP_STATS_SCHEMA,
]


# ── SHIP_SEED_POOLS structure ─────────────────────────────────────────────────

class TestShipSeedPools:
    REQUIRED_KEYS = {"histories", "quirks", "situations"}

    def test_all_games_present(self):
        for game in ALL_GAMES:
            assert game in SHIP_SEED_POOLS

    def test_each_pool_has_required_keys(self):
        for game, pool in SHIP_SEED_POOLS.items():
            for key in self.REQUIRED_KEYS:
                assert key in pool, f"'{game}' missing '{key}'"

    def test_histories_adequate_count(self):
        for game, pool in SHIP_SEED_POOLS.items():
            assert len(pool["histories"]) >= 12, \
                f"'{game}' has only {len(pool['histories'])} histories"

    def test_quirks_adequate_count(self):
        for game, pool in SHIP_SEED_POOLS.items():
            assert len(pool["quirks"]) >= 12, \
                f"'{game}' has only {len(pool['quirks'])} quirks"

    def test_situations_adequate_count(self):
        for game, pool in SHIP_SEED_POOLS.items():
            assert len(pool["situations"]) >= 12, \
                f"'{game}' has only {len(pool['situations'])} situations"

    def test_all_entries_are_non_empty_strings(self):
        for game, pool in SHIP_SEED_POOLS.items():
            for key in self.REQUIRED_KEYS:
                for entry in pool[key]:
                    assert isinstance(entry, str) and len(entry) > 15, \
                        f"Short/invalid entry in '{game}' {key}: {entry!r}"

    def test_no_duplicate_entries_per_key(self):
        for game, pool in SHIP_SEED_POOLS.items():
            for key in self.REQUIRED_KEYS:
                entries = pool[key]
                assert len(entries) == len(set(entries)), \
                    f"Duplicate entries in '{game}' {key}"

    # ── Spot-checks ───────────────────────────────────────────────────────────

    def test_traveller_histories_mention_imperium_flavour(self):
        histories = SHIP_SEED_POOLS["traveller"]["histories"]
        imperium_words = {"Imperial", "subsidised", "scout", "decommission",
                          "registry", "Navy", "corsair", "drive"}
        assert any(any(w in h for w in imperium_words) for h in histories)

    def test_firefly_histories_reference_war(self):
        histories = SHIP_SEED_POOLS["firefly"]["histories"]
        war_words = {"Alliance", "Unification War", "Independents",
                     "Browncoat", "war", "rim"}
        assert any(any(w in h for w in war_words) for h in histories)

    def test_scum_histories_reference_factions(self):
        histories = SHIP_SEED_POOLS["scum"]["histories"]
        faction_words = {"Hegemony", "Guild", "Ur", "Forgotten", "cult",
                         "faction", "noble"}
        assert any(any(w in h for w in faction_words) for h in histories)

    def test_dnd_quirks_are_evocative(self):
        quirks = SHIP_SEED_POOLS["dnd"]["quirks"]
        assert all(len(q) > 20 for q in quirks)

    def test_scum_special_systems_referenced_in_quirks(self):
        quirks = SHIP_SEED_POOLS["scum"]["quirks"]
        technical = {"drive", "sensor", "cargo", "reactor", "signal",
                     "transponder", "heat", "hull"}
        assert any(any(w in q.lower() for w in technical) for q in quirks)


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
            data = json.loads(SEED_ROLLERS[game]())
            assert isinstance(data, dict)

    def test_has_required_keys(self):
        for game in ALL_GAMES:
            data = json.loads(SEED_ROLLERS[game]())
            for key in ("history", "quirk", "situation"):
                assert key in data, f"'{game}' seed missing '{key}'"

    def test_values_come_from_pool(self):
        for game in ALL_GAMES:
            for _ in range(10):
                data = json.loads(SEED_ROLLERS[game]())
                pool = SHIP_SEED_POOLS[game]
                assert data["history"]   in pool["histories"]
                assert data["quirk"]     in pool["quirks"]
                assert data["situation"] in pool["situations"]

    def test_returns_variety(self):
        for game in ALL_GAMES:
            quirks = {json.loads(SEED_ROLLERS[game]())["quirk"] for _ in range(40)}
            assert len(quirks) >= 3, f"'{game}' seed not producing varied quirks"

    def test_individual_functions_match_rollers(self):
        fn_map = {
            "dnd":       roll_dnd_ship_seed,
            "traveller": roll_traveller_ship_seed,
            "firefly":   roll_firefly_ship_seed,
            "scum":      roll_scum_ship_seed,
        }
        for game, fn in fn_map.items():
            data = json.loads(fn())
            pool = SHIP_SEED_POOLS[game]
            assert data["history"] in pool["histories"]


# ── Stat roller functions ─────────────────────────────────────────────────────

class TestTravellerShipStats:
    def _roll(self):
        return json.loads(roll_traveller_ship_stats())

    def test_returns_valid_json(self):
        assert isinstance(self._roll(), dict)

    def test_has_required_keys(self):
        data = self._roll()
        for key in ("displacement", "jump_rating", "maneuver_rating",
                    "power_plant", "fuel_capacity", "cargo_capacity",
                    "staterooms", "hardpoints", "age", "condition"):
            assert key in data, f"Traveller stats missing '{key}'"

    def test_displacement_is_tonner(self):
        valid = {"100t", "200t", "400t", "800t", "1000t"}
        for _ in range(20):
            assert self._roll()["displacement"] in valid

    def test_jump_rating_is_reasonable(self):
        for _ in range(20):
            j = self._roll()["jump_rating"]
            assert j in {"J-1", "J-2", "J-3", "J-4"}

    def test_staterooms_are_positive(self):
        for _ in range(10):
            assert self._roll()["staterooms"] >= 2

    def test_hardpoints_at_least_one(self):
        for _ in range(10):
            assert self._roll()["hardpoints"] >= 1

    def test_condition_is_known_value(self):
        valid = {"Pristine", "Well-maintained", "Worn but reliable",
                 "Showing her age", "Barely spaceworthy"}
        for _ in range(20):
            assert self._roll()["condition"] in valid

    def test_cargo_is_non_negative(self):
        for _ in range(20):
            cargo_str = self._roll()["cargo_capacity"]
            # e.g. "47t" — extract integer
            cargo_val = int(cargo_str.replace("t", "").strip())
            assert cargo_val >= 0


class TestDndShipStats:
    def _roll(self):
        return json.loads(roll_dnd_ship_stats())

    def test_returns_valid_json(self):
        assert isinstance(self._roll(), dict)

    def test_has_required_keys(self):
        data = self._roll()
        for key in ("hull_points", "damage_threshold", "speed",
                    "crew_minimum", "crew_maximum", "cargo_capacity",
                    "weapon_mounts", "age", "condition"):
            assert key in data

    def test_hull_points_positive(self):
        for _ in range(20):
            assert self._roll()["hull_points"] > 0

    def test_damage_threshold_is_tenth_of_hull(self):
        for _ in range(20):
            data = self._roll()
            assert data["damage_threshold"] == data["hull_points"] // 10

    def test_crew_max_gte_min(self):
        for _ in range(20):
            data = self._roll()
            assert data["crew_maximum"] >= data["crew_minimum"]

    def test_weapon_mounts_positive(self):
        for _ in range(20):
            assert self._roll()["weapon_mounts"] > 0

    def test_condition_is_known_value(self):
        valid = {"Freshly fitted", "Sound", "Serviceable",
                 "Weathered", "Barely seaworthy"}
        for _ in range(20):
            assert self._roll()["condition"] in valid


class TestFireflyShipStats:
    _DICE = {"d4", "d6", "d8", "d10", "d12"}

    def _roll(self):
        return json.loads(roll_firefly_ship_stats())

    def test_returns_valid_json(self):
        assert isinstance(self._roll(), dict)

    def test_has_required_keys(self):
        data = self._roll()
        for key in ("engines", "agility", "strength", "toughness",
                    "crew_capacity", "cargo_capacity", "age", "condition"):
            assert key in data

    def test_dice_are_valid_cortex_dice(self):
        for _ in range(20):
            data = self._roll()
            assert data["engines"]  in self._dice
            assert data["agility"]  in self._dice
            assert data["strength"] in self._dice
            assert data["toughness"] in self._dice

    @property
    def _dice(self):
        return self._DICE

    def test_condition_is_known_value(self):
        valid = {"Practically new", "Good working order", "Well-worn",
                 "Beat up but flying", "One hard burn from dead"}
        for _ in range(20):
            assert self._roll()["condition"] in valid


class TestScumShipStats:
    def _roll(self):
        return json.loads(roll_scum_ship_stats())

    def test_returns_valid_json(self):
        assert isinstance(self._roll(), dict)

    def test_has_required_keys(self):
        data = self._roll()
        for key in ("speed", "hull", "crew_capacity", "cargo",
                    "special_systems", "age", "condition"):
            assert key in data

    def test_speed_is_valid_tier(self):
        valid = {"Slow (1)", "Average (2)", "Fast (3)", "Blazing (4)"}
        for _ in range(20):
            assert self._roll()["speed"] in valid

    def test_hull_is_valid_tier(self):
        valid = {"Light (4 hull)", "Medium (6 hull)", "Heavy (8 hull)"}
        for _ in range(20):
            assert self._roll()["hull"] in valid

    def test_special_systems_is_list(self):
        for _ in range(20):
            assert isinstance(self._roll()["special_systems"], list)

    def test_special_systems_non_empty(self):
        # Always has at least one entry (either a system or "None on record")
        for _ in range(20):
            assert len(self._roll()["special_systems"]) >= 1

    def test_condition_is_known_value(self):
        valid = {"Fresh off the line", "Maintained", "Working order",
                 "Rough", "Held together by spite"}
        for _ in range(20):
            assert self._roll()["condition"] in valid

    def test_stat_rollers_all_present(self):
        for game in ALL_GAMES:
            assert game in STAT_ROLLERS


# ── Tool schemas ──────────────────────────────────────────────────────────────

class TestSeedSchemas:
    def test_correct_names(self):
        expected = [
            (DND_SHIP_SEED_SCHEMA,       "roll_dnd_ship_seed"),
            (TRAVELLER_SHIP_SEED_SCHEMA, "roll_traveller_ship_seed"),
            (FIREFLY_SHIP_SEED_SCHEMA,   "roll_firefly_ship_seed"),
            (SCUM_SHIP_SEED_SCHEMA,      "roll_scum_ship_seed"),
        ]
        for schema, name in expected:
            assert schema["name"] == name

    def test_have_descriptions(self):
        for schema in ALL_SEED_SCHEMAS:
            assert len(schema["description"]) > 30

    def test_require_nothing(self):
        for schema in ALL_SEED_SCHEMAS:
            assert schema["input_schema"].get("required", []) == []

    def test_descriptions_are_distinct(self):
        descs = [s["description"] for s in ALL_SEED_SCHEMAS]
        assert len(descs) == len(set(descs))

    def test_descriptions_mention_prevent_or_first(self):
        for schema in ALL_SEED_SCHEMAS:
            desc = schema["description"].lower()
            assert "prevent" in desc or "before" in desc


class TestStatsSchemas:
    def test_correct_names(self):
        expected = [
            (DND_SHIP_STATS_SCHEMA,       "roll_dnd_ship_stats"),
            (TRAVELLER_SHIP_STATS_SCHEMA, "roll_traveller_ship_stats"),
            (FIREFLY_SHIP_STATS_SCHEMA,   "roll_firefly_ship_stats"),
            (SCUM_SHIP_STATS_SCHEMA,      "roll_scum_ship_stats"),
        ]
        for schema, name in expected:
            assert schema["name"] == name

    def test_have_descriptions(self):
        for schema in ALL_STATS_SCHEMAS:
            assert len(schema["description"]) > 20

    def test_require_nothing(self):
        for schema in ALL_STATS_SCHEMAS:
            assert schema["input_schema"].get("required", []) == []

    def test_traveller_description_mentions_jump(self):
        assert "jump" in TRAVELLER_SHIP_STATS_SCHEMA["description"].lower()

    def test_firefly_description_mentions_cortex(self):
        assert "Cortex" in FIREFLY_SHIP_STATS_SCHEMA["description"]

    def test_scum_description_mentions_fitd(self):
        assert "FitD" in SCUM_SHIP_STATS_SCHEMA["description"] or \
               "Forged" in SCUM_SHIP_STATS_SCHEMA["description"]


# ── GAME_TOOLS lists ──────────────────────────────────────────────────────────

class TestGameTools:
    EXPECTED_SEED_NAMES = {
        "dnd":       "roll_dnd_ship_seed",
        "traveller": "roll_traveller_ship_seed",
        "firefly":   "roll_firefly_ship_seed",
        "scum":      "roll_scum_ship_seed",
    }
    EXPECTED_STATS_NAMES = {
        "dnd":       "roll_dnd_ship_stats",
        "traveller": "roll_traveller_ship_stats",
        "firefly":   "roll_firefly_ship_stats",
        "scum":      "roll_scum_ship_stats",
    }

    def test_all_games_present(self):
        for game in ALL_GAMES:
            assert game in GAME_TOOLS

    def test_each_has_ship_name_tool(self):
        for game in ALL_GAMES:
            names = [t["name"] for t in GAME_TOOLS[game]]
            assert "roll_ship_name" in names

    def test_each_has_seed_tool(self):
        for game, expected in self.EXPECTED_SEED_NAMES.items():
            names = [t["name"] for t in GAME_TOOLS[game]]
            assert expected in names

    def test_each_has_stats_tool(self):
        for game, expected in self.EXPECTED_STATS_NAMES.items():
            names = [t["name"] for t in GAME_TOOLS[game]]
            assert expected in names

    def test_each_has_name_suggestion(self):
        for game in ALL_GAMES:
            names = [t["name"] for t in GAME_TOOLS[game]]
            assert "roll_name_suggestion" in names

    def test_no_duplicate_tool_names(self):
        for game in ALL_GAMES:
            names = [t["name"] for t in GAME_TOOLS[game]]
            assert len(names) == len(set(names))


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_roll_ship_name_is_name_phase(self):
        assert detect_phase("roll_ship_name", set()) == "name"

    def test_stats_tools_are_stats_phase(self):
        for name in ("roll_dnd_ship_stats", "roll_traveller_ship_stats",
                     "roll_firefly_ship_stats", "roll_scum_ship_stats"):
            assert detect_phase(name, set()) == "stats"

    def test_seed_tools_are_seed_phase(self):
        for name in ("roll_dnd_ship_seed", "roll_traveller_ship_seed",
                     "roll_firefly_ship_seed", "roll_scum_ship_seed"):
            assert detect_phase(name, set()) == "seed"

    def test_name_suggestion_is_crew_phase(self):
        assert detect_phase("roll_name_suggestion", set()) == "crew"

    def test_unknown_returns_none(self):
        assert detect_phase("some_other_tool", set()) is None


# ── make_run_tool ─────────────────────────────────────────────────────────────

class TestMakeRunTool:
    def test_ship_name_dispatches_with_correct_game(self):
        for game in ALL_GAMES:
            fn = make_run_tool(game)
            result = json.loads(fn("roll_ship_name", {}))
            assert "name" in result
            assert "ship_class" in result

    def test_seed_dispatches_correctly(self):
        seed_names = {
            "dnd":       "roll_dnd_ship_seed",
            "traveller": "roll_traveller_ship_seed",
            "firefly":   "roll_firefly_ship_seed",
            "scum":      "roll_scum_ship_seed",
        }
        for game, tool_name in seed_names.items():
            fn = make_run_tool(game)
            result = json.loads(fn(tool_name, {}))
            assert "history" in result

    def test_stats_dispatches_correctly(self):
        stats_names = {
            "dnd":       "roll_dnd_ship_stats",
            "traveller": "roll_traveller_ship_stats",
            "firefly":   "roll_firefly_ship_stats",
            "scum":      "roll_scum_ship_stats",
        }
        for game, tool_name in stats_names.items():
            fn = make_run_tool(game)
            result = json.loads(fn(tool_name, {}))
            assert "condition" in result

    def test_name_suggestion_dispatches(self):
        fn = make_run_tool("traveller")
        result = json.loads(fn("roll_name_suggestion", {}))
        assert "suggested_name" in result

    def test_unknown_returns_error_string(self):
        fn = make_run_tool("dnd")
        result = fn("nonexistent_tool", {})
        assert "Unknown" in result


# ── save_ship ─────────────────────────────────────────────────────────────────

class TestSaveShip:
    SAMPLE = "## The Iron Meridian\n*Type-A Free Trader — twenty years of honest work and one very dishonest year*\n\n### Registry\n..."

    def test_saves_to_correct_directory(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path = save_ship(self.SAMPLE, "traveller")
        assert path.parent == tmp_path / "traveller" / "ships"

    def test_scum_saves_to_scum_villainy(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path = save_ship(self.SAMPLE, "scum")
        assert "scum_villainy" in str(path)

    def test_filename_ends_with_ship(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path = save_ship(self.SAMPLE, "dnd")
        assert path.name.endswith("-ship.md")

    def test_filename_slugified_from_title(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path = save_ship(self.SAMPLE, "traveller")
        assert "the-iron-meridian" in path.name

    def test_file_content_preserved(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path = save_ship(self.SAMPLE, "firefly")
        assert path.read_text() == self.SAMPLE

    def test_collision_counter(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path1 = save_ship(self.SAMPLE, "dnd")
        path2 = save_ship(self.SAMPLE, "dnd")
        assert path1 != path2
        assert path1.exists() and path2.exists()

    def test_directory_created_if_missing(self, tmp_path, monkeypatch):
        import agents.ship_agent as sa
        monkeypatch.setattr(sa, "_OUTPUT", tmp_path)
        path = save_ship(self.SAMPLE, "firefly")
        assert path.parent.exists()
