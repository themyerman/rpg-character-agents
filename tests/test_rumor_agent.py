"""
Tests for rumor_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.rumor_agent import (
    roll_dnd_rumor_seed,
    roll_traveller_rumor_seed,
    roll_firefly_rumor_seed,
    roll_scum_rumor_seed,
    roll_alien_rumor_seed,
    roll_deadlands_rumor_seed,
    save_rumor,
    detect_phase,
    RUMOR_SUBJECTS,
    TRUTH_ANGLES,
    TONES,
    GAME_SUBDIRS,
    GAME_TOOLS,
    GAME_SYSTEM_PROMPTS,
    DND_RUMOR_SEED_SCHEMA,
    TRAVELLER_RUMOR_SEED_SCHEMA,
    FIREFLY_RUMOR_SEED_SCHEMA,
    SCUM_RUMOR_SEED_SCHEMA,
    ALIEN_RUMOR_SEED_SCHEMA,
    DEADLANDS_RUMOR_SEED_SCHEMA,
)


GAMES = ["dnd", "traveller", "firefly", "scum", "alien", "deadlands"]
ROLLERS = {
    "dnd":       roll_dnd_rumor_seed,
    "traveller": roll_traveller_rumor_seed,
    "firefly":   roll_firefly_rumor_seed,
    "scum":      roll_scum_rumor_seed,
    "alien":     roll_alien_rumor_seed,
    "deadlands": roll_deadlands_rumor_seed,
}


# ── RUMOR_SUBJECTS structure ──────────────────────────────────────────────────

class TestRumorSubjects:
    def test_all_six_games_present(self):
        assert set(RUMOR_SUBJECTS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_each_game_has_at_least_fifteen_subjects(self):
        for game in GAMES:
            assert len(RUMOR_SUBJECTS[game]) >= 15, \
                f"{game} has only {len(RUMOR_SUBJECTS[game])} rumor subjects"

    def test_all_subjects_are_non_empty_strings(self):
        for game in GAMES:
            for subject in RUMOR_SUBJECTS[game]:
                assert isinstance(subject, str) and len(subject) > 10, \
                    f"{game} has an invalid subject: {subject!r}"

    def test_game_specific_subjects(self):
        # Subjects should reference game-appropriate concepts
        dnd_text = " ".join(RUMOR_SUBJECTS["dnd"]).lower()
        assert any(w in dnd_text for w in ["guild", "noble", "wizard", "temple", "heist", "cursed"])

        trav_text = " ".join(RUMOR_SUBJECTS["traveller"]).lower()
        assert any(w in trav_text for w in ["imperial", "megacorp", "scout", "jump", "ship", "starport"])

        ff_text = " ".join(RUMOR_SUBJECTS["firefly"]).lower()
        assert any(w in ff_text for w in ["alliance", "browncoat", "rim", "companion", "war"])

        scum_text = " ".join(RUMOR_SUBJECTS["scum"]).lower()
        assert any(w in scum_text for w in ["hegemony", "guild", "ur", "church", "faction"])


# ── TRUTH_ANGLES and TONES ────────────────────────────────────────────────────

class TestSharedPools:
    def test_truth_angles_has_at_least_five_entries(self):
        assert len(TRUTH_ANGLES) >= 5

    def test_tones_has_at_least_five_entries(self):
        assert len(TONES) >= 5

    def test_truth_angles_are_non_empty_strings(self):
        for angle in TRUTH_ANGLES:
            assert isinstance(angle, str) and len(angle) > 10

    def test_tones_are_non_empty_strings(self):
        for tone in TONES:
            assert isinstance(tone, str) and len(tone) > 10

    def test_truth_angles_are_distinct(self):
        assert len(TRUTH_ANGLES) == len(set(TRUTH_ANGLES))

    def test_tones_are_distinct(self):
        assert len(TONES) == len(set(TONES))


# ── Seed rollers ──────────────────────────────────────────────────────────────

class TestRumorSeedRollers:
    @pytest.mark.parametrize("game", GAMES)
    def test_returns_valid_json(self, game):
        result = ROLLERS[game]()
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("game", GAMES)
    def test_has_required_keys(self, game):
        data = json.loads(ROLLERS[game]())
        assert "subject" in data
        assert "truth_angle" in data
        assert "tone" in data

    @pytest.mark.parametrize("game", GAMES)
    def test_values_come_from_pools(self, game):
        for _ in range(10):
            data = json.loads(ROLLERS[game]())
            assert data["subject"]     in RUMOR_SUBJECTS[game]
            assert data["truth_angle"] in TRUTH_ANGLES
            assert data["tone"]        in TONES

    @pytest.mark.parametrize("game", GAMES)
    def test_returns_subject_variety(self, game):
        subjects = {json.loads(ROLLERS[game]())["subject"] for _ in range(30)}
        assert len(subjects) >= 3, f"{game} seed roller shows no subject variety"

    @pytest.mark.parametrize("game", GAMES)
    def test_returns_truth_angle_variety(self, game):
        angles = {json.loads(ROLLERS[game]())["truth_angle"] for _ in range(30)}
        assert len(angles) >= 2, f"{game} seed roller shows no truth_angle variety"


# ── Tool schemas ──────────────────────────────────────────────────────────────

class TestRumorToolSchemas:
    def test_dnd_schema_name(self):
        assert DND_RUMOR_SEED_SCHEMA["name"] == "roll_dnd_rumor_seed"

    def test_traveller_schema_name(self):
        assert TRAVELLER_RUMOR_SEED_SCHEMA["name"] == "roll_traveller_rumor_seed"

    def test_firefly_schema_name(self):
        assert FIREFLY_RUMOR_SEED_SCHEMA["name"] == "roll_firefly_rumor_seed"

    def test_scum_schema_name(self):
        assert SCUM_RUMOR_SEED_SCHEMA["name"] == "roll_scum_rumor_seed"

    def test_all_schemas_have_required_keys(self):
        schemas = [
            DND_RUMOR_SEED_SCHEMA,
            TRAVELLER_RUMOR_SEED_SCHEMA,
            FIREFLY_RUMOR_SEED_SCHEMA,
            SCUM_RUMOR_SEED_SCHEMA,
        ]
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema


# ── GAME_TOOLS ────────────────────────────────────────────────────────────────

class TestRumorGameTools:
    def test_all_games_have_tools(self):
        assert set(GAME_TOOLS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_each_game_has_seed_and_name_tool(self):
        for game in GAMES:
            names = {t["name"] for t in GAME_TOOLS[game]}
            assert f"roll_{game}_rumor_seed" in names
            assert "roll_name_suggestion" in names

    def test_no_ship_tool_in_any_game(self):
        # Rumor agent doesn't need ship names
        for game in GAMES:
            names = {t["name"] for t in GAME_TOOLS[game]}
            assert "roll_ship_name" not in names


# ── GAME_SYSTEM_PROMPTS ───────────────────────────────────────────────────────

class TestRumorSystemPrompts:
    def test_all_games_have_prompts(self):
        assert set(GAME_SYSTEM_PROMPTS.keys()) == {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

    def test_prompts_mention_correct_seed_tool(self):
        assert "roll_dnd_rumor_seed" in GAME_SYSTEM_PROMPTS["dnd"]
        assert "roll_traveller_rumor_seed" in GAME_SYSTEM_PROMPTS["traveller"]
        assert "roll_firefly_rumor_seed" in GAME_SYSTEM_PROMPTS["firefly"]
        assert "roll_scum_rumor_seed" in GAME_SYSTEM_PROMPTS["scum"]

    def test_prompts_are_non_empty(self):
        for game, prompt in GAME_SYSTEM_PROMPTS.items():
            assert isinstance(prompt, str) and len(prompt) > 100


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestRumorDetectPhase:
    def test_rumor_seed_tool_returns_seed(self):
        assert detect_phase("roll_dnd_rumor_seed", set()) == "seed"
        assert detect_phase("roll_traveller_rumor_seed", set()) == "seed"
        assert detect_phase("roll_firefly_rumor_seed", set()) == "seed"
        assert detect_phase("roll_scum_rumor_seed", set()) == "seed"

    def test_name_suggestion_returns_name(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None
        assert detect_phase("roll_ship_name", set()) is None

    def test_accepts_no_seen_arg(self):
        # detect_phase should accept no seen argument (default None)
        assert detect_phase("roll_dnd_rumor_seed") == "seed"


# ── save_rumor ────────────────────────────────────────────────────────────────

class TestSaveRumor:
    def test_saves_to_rumors_directory(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **The Missing Caravan**\n*What happened on the northern road*"
        path = save_rumor(content, "dnd")
        assert "rumors" in str(path)
        assert "dnd" in str(path)

    def test_filename_uses_slug(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **The Missing Caravan**\n*detail*"
        path = save_rumor(content, "dnd")
        assert "the-missing-caravan" in path.name

    def test_filename_ends_with_rumor_md(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **Test Rumor**\n*detail*"
        path = save_rumor(content, "dnd")
        assert path.name.endswith("-rumor.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **The Scout Who Didn't Report**\n*An IISS anomaly in the outer belt*"
        path = save_rumor(content, "traveller")
        assert path.read_text() == content

    def test_scum_uses_scum_villainy_subdir(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **The Faction's New Weapon**\n*detail*"
        path = save_rumor(content, "scum")
        assert "scum_villainy" in str(path)

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **The Guild War**\n*detail*"
        path1 = save_rumor(content, "dnd")
        path2 = save_rumor(content, "dnd")
        assert path1 != path2
        assert path1.exists() and path2.exists()
        assert path2.name == "the-guild-war-rumor-2.md"

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        import agents.rumor_agent as rumor_agent
        monkeypatch.setattr(rumor_agent, "_OUTPUT", tmp_path)
        content = "## **Bold Rumor**\n*detail*"
        path = save_rumor(content, "firefly")
        assert "**" not in path.name
        assert "#" not in path.name
