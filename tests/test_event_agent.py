"""
Tests for event_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.event_agent import (
    roll_dnd_event_seed,
    roll_traveller_event_seed,
    roll_firefly_event_seed,
    roll_scum_event_seed,
    roll_alien_event_seed,
    roll_deadlands_event_seed,
    save_event,
    detect_phase,
    EVENT_POOLS,
    GAME_SUBDIRS,
    GAME_TOOLS,
    GAME_SYSTEM_PROMPTS,
    DND_EVENT_SEED_SCHEMA,
    TRAVELLER_EVENT_SEED_SCHEMA,
    FIREFLY_EVENT_SEED_SCHEMA,
    SCUM_EVENT_SEED_SCHEMA,
    ALIEN_EVENT_SEED_SCHEMA,
    DEADLANDS_EVENT_SEED_SCHEMA,
)


GAMES = ["dnd", "traveller", "firefly", "scum", "alien", "deadlands"]
ROLLERS = {
    "dnd":       roll_dnd_event_seed,
    "traveller": roll_traveller_event_seed,
    "firefly":   roll_firefly_event_seed,
    "scum":      roll_scum_event_seed,
    "alien":     roll_alien_event_seed,
    "deadlands": roll_deadlands_event_seed,
}


# ── EVENT_POOLS structure ─────────────────────────────────────────────────────

class TestEventPools:
    def test_all_six_games_present(self):
        assert set(EVENT_POOLS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_each_game_has_contexts_and_events(self):
        for game in GAMES:
            assert "contexts" in EVENT_POOLS[game], f"{game} missing 'contexts'"
            assert "events" in EVENT_POOLS[game], f"{game} missing 'events'"

    def test_contexts_has_at_least_twelve_entries(self):
        for game in GAMES:
            entries = EVENT_POOLS[game]["contexts"]
            assert len(entries) >= 12, f"{game}/contexts has only {len(entries)} entries"

    def test_events_has_at_least_twelve_entries(self):
        for game in GAMES:
            entries = EVENT_POOLS[game]["events"]
            assert len(entries) >= 12, f"{game}/events has only {len(entries)} entries"

    def test_all_entries_are_non_empty_strings(self):
        for game in GAMES:
            for category in ("contexts", "events"):
                for entry in EVENT_POOLS[game][category]:
                    assert isinstance(entry, str) and len(entry) > 10, \
                        f"{game}/{category} has invalid entry: {entry!r}"

    def test_game_specific_contexts(self):
        # Each game's contexts should reflect its setting
        dnd_contexts = " ".join(EVENT_POOLS["dnd"]["contexts"]).lower()
        assert any(w in dnd_contexts for w in ["rest", "road", "market", "ceremony", "funeral"])

        trav_contexts = " ".join(EVENT_POOLS["traveller"]["contexts"]).lower()
        assert any(w in trav_contexts for w in ["jump", "starport", "cargo", "ship", "patron"])

        ff_contexts = " ".join(EVENT_POOLS["firefly"]["contexts"]).lower()
        assert any(w in ff_contexts for w in ["job", "alliance", "ship", "landing", "bar"])

        scum_contexts = " ".join(EVENT_POOLS["scum"]["contexts"]).lower()
        assert any(w in scum_contexts for w in ["score", "faction", "hegemony", "heat", "mystic"])

    def test_game_specific_events(self):
        dnd_events = " ".join(EVENT_POOLS["dnd"]["events"]).lower()
        assert any(w in dnd_events for w in ["backstory", "body", "spell", "faction"])

        trav_events = " ".join(EVENT_POOLS["traveller"]["events"]).lower()
        assert any(w in trav_events for w in ["ship", "cargo", "imperial", "scout", "patron"])

        ff_events = " ".join(EVENT_POOLS["firefly"]["events"]).lower()
        assert any(w in ff_events for w in ["war", "alliance", "browncoat", "cargo", "job"])

        scum_events = " ".join(EVENT_POOLS["scum"]["events"]).lower()
        assert any(w in scum_events for w in ["faction", "ur", "hegemony", "mystic", "score"])


# ── Seed rollers ──────────────────────────────────────────────────────────────

class TestEventSeedRollers:
    @pytest.mark.parametrize("game", GAMES)
    def test_returns_valid_json(self, game):
        result = ROLLERS[game]()
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("game", GAMES)
    def test_has_required_keys(self, game):
        data = json.loads(ROLLERS[game]())
        assert "context" in data
        assert "event" in data

    @pytest.mark.parametrize("game", GAMES)
    def test_values_come_from_pools(self, game):
        for _ in range(10):
            data = json.loads(ROLLERS[game]())
            pool = EVENT_POOLS[game]
            assert data["context"] in pool["contexts"], \
                f"{game}: context not in pool"
            assert data["event"] in pool["events"], \
                f"{game}: event not in pool"

    @pytest.mark.parametrize("game", GAMES)
    def test_context_variety(self, game):
        contexts = {json.loads(ROLLERS[game]())["context"] for _ in range(30)}
        assert len(contexts) >= 3, f"{game} context roller shows no variety"

    @pytest.mark.parametrize("game", GAMES)
    def test_event_variety(self, game):
        events = {json.loads(ROLLERS[game]())["event"] for _ in range(30)}
        assert len(events) >= 3, f"{game} event roller shows no variety"

    @pytest.mark.parametrize("game", GAMES)
    def test_context_and_event_are_independent(self, game):
        # A diversity of context+event pairs shows they're drawn independently
        pairs = {
            (json.loads(ROLLERS[game]())["context"], json.loads(ROLLERS[game]())["event"])
            for _ in range(20)
        }
        assert len(pairs) >= 5, f"{game} context/event appear correlated"


# ── Tool schemas ──────────────────────────────────────────────────────────────

class TestEventToolSchemas:
    def test_dnd_schema_name(self):
        assert DND_EVENT_SEED_SCHEMA["name"] == "roll_dnd_event_seed"

    def test_traveller_schema_name(self):
        assert TRAVELLER_EVENT_SEED_SCHEMA["name"] == "roll_traveller_event_seed"

    def test_firefly_schema_name(self):
        assert FIREFLY_EVENT_SEED_SCHEMA["name"] == "roll_firefly_event_seed"

    def test_scum_schema_name(self):
        assert SCUM_EVENT_SEED_SCHEMA["name"] == "roll_scum_event_seed"

    def test_all_schemas_have_required_keys(self):
        schemas = [
            DND_EVENT_SEED_SCHEMA,
            TRAVELLER_EVENT_SEED_SCHEMA,
            FIREFLY_EVENT_SEED_SCHEMA,
            SCUM_EVENT_SEED_SCHEMA,
        ]
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema


# ── GAME_TOOLS ────────────────────────────────────────────────────────────────

class TestEventGameTools:
    def test_all_games_have_tools(self):
        assert set(GAME_TOOLS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_each_game_has_seed_and_name_tool(self):
        for game in GAMES:
            names = {t["name"] for t in GAME_TOOLS[game]}
            assert f"roll_{game}_event_seed" in names
            assert "roll_name_suggestion" in names

    def test_no_ship_tool_in_any_game(self):
        for game in GAMES:
            names = {t["name"] for t in GAME_TOOLS[game]}
            assert "roll_ship_name" not in names


# ── GAME_SYSTEM_PROMPTS ───────────────────────────────────────────────────────

class TestEventSystemPrompts:
    def test_all_games_have_prompts(self):
        assert set(GAME_SYSTEM_PROMPTS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_prompts_mention_correct_seed_tool(self):
        assert "roll_dnd_event_seed" in GAME_SYSTEM_PROMPTS["dnd"]
        assert "roll_traveller_event_seed" in GAME_SYSTEM_PROMPTS["traveller"]
        assert "roll_firefly_event_seed" in GAME_SYSTEM_PROMPTS["firefly"]
        assert "roll_scum_event_seed" in GAME_SYSTEM_PROMPTS["scum"]
        assert "roll_alien_event_seed" in GAME_SYSTEM_PROMPTS["alien"]
        assert "roll_deadlands_event_seed" in GAME_SYSTEM_PROMPTS["deadlands"]

    def test_prompts_are_non_empty(self):
        for game, prompt in GAME_SYSTEM_PROMPTS.items():
            assert isinstance(prompt, str) and len(prompt) > 100


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestEventDetectPhase:
    def test_event_seed_tool_returns_seed(self):
        assert detect_phase("roll_dnd_event_seed", set()) == "seed"
        assert detect_phase("roll_traveller_event_seed", set()) == "seed"
        assert detect_phase("roll_firefly_event_seed", set()) == "seed"
        assert detect_phase("roll_scum_event_seed", set()) == "seed"

    def test_name_suggestion_returns_name(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None
        assert detect_phase("roll_ship_name", set()) is None

    def test_accepts_no_seen_arg(self):
        assert detect_phase("roll_dnd_event_seed") == "seed"
        assert detect_phase("roll_name_suggestion") == "name"
        assert detect_phase("flip_coin") is None


# ── save_event ────────────────────────────────────────────────────────────────

class TestSaveEvent:
    def test_saves_to_events_directory(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **The Factor Appears**\n*A familiar face at the wrong moment*"
        path = save_event(content, "dnd")
        assert "events" in str(path)
        assert "dnd" in str(path)

    def test_filename_uses_slug(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **The Factor Appears**\n*detail*"
        path = save_event(content, "dnd")
        assert "the-factor-appears" in path.name

    def test_filename_ends_with_event_md(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **Test Event**\n*detail*"
        path = save_event(content, "dnd")
        assert path.name.endswith("-event.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **Jump Anomaly**\n*Something on the sensors that isn't on any chart*"
        path = save_event(content, "traveller")
        assert path.read_text() == content

    def test_scum_uses_scum_villainy_subdir(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **The Faction Moves**\n*detail*"
        path = save_event(content, "scum")
        assert "scum_villainy" in str(path)

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **The Ambush**\n*detail*"
        path1 = save_event(content, "firefly")
        path2 = save_event(content, "firefly")
        assert path1 != path2
        assert path1.exists() and path2.exists()
        assert path2.name == "the-ambush-event-2.md"

    def test_collision_increments_beyond_two(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **The Ambush**\n*detail*"
        save_event(content, "firefly")
        save_event(content, "firefly")
        path3 = save_event(content, "firefly")
        assert path3.name == "the-ambush-event-3.md"

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        import agents.event_agent as event_agent
        monkeypatch.setattr(event_agent, "_OUTPUT", tmp_path)
        content = "## **Bold Event**\n*detail*"
        path = save_event(content, "scum")
        assert "**" not in path.name
        assert "#" not in path.name


# ── GAME_SUBDIRS ──────────────────────────────────────────────────────────────

class TestEventGameSubdirs:
    def test_all_six_games_present(self):
        assert set(GAME_SUBDIRS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_scum_maps_to_scum_villainy(self):
        assert GAME_SUBDIRS["scum"] == "scum_villainy"
