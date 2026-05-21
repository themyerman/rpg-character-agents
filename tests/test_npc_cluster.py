"""
Tests for npc_cluster_agent.py — pure Python logic, no API calls.
"""

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import npc_cluster_agent
from npc_cluster_agent import (
    GAME_AGENTS,
    RELATIONSHIP_TYPES,
    _slug,
    _extract_name,
    _strip_heading,
    _strip_preamble,
    save_cluster,
)


# ── GAME_AGENTS ───────────────────────────────────────────────────────────────────

class TestGameAgents:
    def test_four_games_registered(self):
        assert set(GAME_AGENTS.keys()) == {"dnd", "traveller", "firefly", "scum"}

    def test_each_game_has_required_keys(self):
        required = {"tools", "run_tool", "npc_prompt", "label", "save_subdir"}
        for game, config in GAME_AGENTS.items():
            missing = required - config.keys()
            assert not missing, f"Game '{game}' missing keys: {missing}"

    def test_tools_are_non_empty_lists(self):
        for game, config in GAME_AGENTS.items():
            assert isinstance(config["tools"], list)
            assert len(config["tools"]) >= 3, f"Game '{game}' has too few tools"

    def test_run_tool_is_callable(self):
        for game, config in GAME_AGENTS.items():
            assert callable(config["run_tool"]), f"Game '{game}' run_tool is not callable"

    def test_npc_prompt_is_non_empty_string(self):
        for game, config in GAME_AGENTS.items():
            assert isinstance(config["npc_prompt"], str)
            assert len(config["npc_prompt"]) > 50, f"Game '{game}' npc_prompt too short"

    def test_labels_are_unique(self):
        labels = [c["label"] for c in GAME_AGENTS.values()]
        assert len(labels) == len(set(labels))


# ── RELATIONSHIP_TYPES ────────────────────────────────────────────────────────────

class TestRelationshipTypes:
    def test_at_least_five_types(self):
        assert len(RELATIONSHIP_TYPES) >= 5

    def test_each_entry_is_two_tuple(self):
        for entry in RELATIONSHIP_TYPES:
            assert len(entry) == 2, f"Expected 2-tuple, got {entry}"

    def test_keys_are_strings(self):
        for key, label in RELATIONSHIP_TYPES:
            assert isinstance(key, str) and len(key) > 0
            assert isinstance(label, str) and len(label) > 0

    def test_team_and_rivals_present(self):
        keys = {k for k, _ in RELATIONSHIP_TYPES}
        assert "team"   in keys
        assert "rivals" in keys

    def test_keys_are_unique(self):
        keys = [k for k, _ in RELATIONSHIP_TYPES]
        assert len(keys) == len(set(keys))


# ── _slug ─────────────────────────────────────────────────────────────────────────

class TestSlug:
    def test_lowercases(self):
        assert _slug("Hello World") == "hello-world"

    def test_replaces_spaces_with_dashes(self):
        assert _slug("foo bar") == "foo-bar"

    def test_strips_leading_trailing_dashes(self):
        assert _slug("  hello  ") == "hello"

    def test_collapses_multiple_separators(self):
        assert _slug("foo  bar--baz") == "foo-bar-baz"

    def test_removes_special_chars(self):
        assert _slug("Foo's & Bar!") == "foo-s-bar"


# ── _extract_name ─────────────────────────────────────────────────────────────────

class TestExtractName:
    def test_extracts_from_double_hash(self):
        text = "## **Reva Marsh**\n*Scoundrel*"
        assert _extract_name(text) == "Reva Marsh"

    def test_strips_asterisks_and_hash(self):
        text = "## **Tess Varo**\nSomething"
        name = _extract_name(text)
        assert "**" not in name
        assert "#" not in name

    def test_returns_unknown_when_no_heading(self):
        assert _extract_name("no heading here") == "Unknown"

    def test_strips_whitespace(self):
        text = "##   Spaced Name   \nContent"
        name = _extract_name(text)
        assert name == name.strip()


# ── _strip_heading ────────────────────────────────────────────────────────────────

class TestStripHeading:
    def test_removes_first_heading_line(self):
        text = "## **Name**\nContent line\nMore content"
        result = _strip_heading(text)
        assert not result.startswith("##")

    def test_preserves_body_content(self):
        text = "## **Name**\nContent line\nMore content"
        result = _strip_heading(text)
        assert "Content line" in result
        assert "More content" in result


# ── _strip_preamble ───────────────────────────────────────────────────────────────

class TestStripPreamble:
    def test_removes_text_before_heading(self):
        text = "Here is some preamble text.\n\n## **Character Name**\nContent"
        result = _strip_preamble(text)
        assert result.startswith("## **Character Name**")

    def test_preserves_heading_and_body(self):
        text = "Intro\n## **Name**\nBody"
        result = _strip_preamble(text)
        assert "## **Name**" in result
        assert "Body" in result

    def test_no_preamble_unchanged(self):
        text = "## **Name**\nBody"
        result = _strip_preamble(text)
        assert result.startswith("## **Name**")


# ── save_cluster ──────────────────────────────────────────────────────────────────

class TestSaveCluster:
    def _make_synthesis(self, title="Iron Dogs: Firefly RPG — Rivals"):
        return (
            f"# {title}\n"
            "*Three ex-soldiers who can't stop following each other into trouble.*\n\n"
            "## Web of Connections\n"
            "- **Vance / Mira:** Former squadmates, one saved the other, neither has forgiven it.\n"
            "- **Mira / Dov:** They were on opposite sides at Hera; now they share a ship.\n"
            "- **Vance / Dov:** Vance thinks Dov knows where the money went. He's right.\n\n"
            "## GM Hooks\n"
            "1. Someone from the old unit turns up dead — and the circumstances look familiar.\n"
            "2. A job offer arrives that only works if all three of them cooperate.\n"
            "3. One of them has been lying about who sent the job. The others are about to find out.\n"
        )

    def _make_npc(self, name="Vance Rook"):
        return f"## **{name}**\n*Muscle — does the hitting professionally*\n\n**Demeanor:** Quiet."

    def test_saves_to_parties_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Vance Rook"), self._make_npc("Mira Soto")]
        path = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        assert "parties" in str(path)

    def test_filename_contains_game_and_relationship(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Vance Rook"), self._make_npc("Mira Soto")]
        path = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        assert "firefly" in path.name
        assert "rivals"  in path.name

    def test_filename_ends_with_party_md(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Vance Rook"), self._make_npc("Mira Soto")]
        path = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        assert path.name.endswith("-party.md")

    def test_file_content_includes_npc_names(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Vance Rook"), self._make_npc("Mira Soto")]
        path = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        content = path.read_text()
        assert "Vance Rook" in content
        assert "Mira Soto"  in content

    def test_file_content_includes_gm_hooks(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Vance Rook"), self._make_npc("Mira Soto")]
        path = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        content = path.read_text()
        assert "GM Hooks" in content

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Vance Rook"), self._make_npc("Mira Soto")]
        path1 = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        path2 = save_cluster(self._make_synthesis(), npcs, "firefly", "rivals")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

    def test_slug_extracted_from_title_before_colon(self, tmp_path, monkeypatch):
        monkeypatch.setattr(npc_cluster_agent, "__file__", str(tmp_path / "npc_cluster_agent.py"))
        npcs = [self._make_npc("Alpha"), self._make_npc("Beta")]
        # Title has a colon — slug should come from the part before it
        synthesis = self._make_synthesis("Iron Dogs: Firefly RPG — Rivals")
        path = save_cluster(synthesis, npcs, "firefly", "rivals")
        assert "iron-dogs" in path.name
        # The part after the colon should NOT appear in the slug portion before "-party.md"
        assert "firefly-rpg" not in path.name
