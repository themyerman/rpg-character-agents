"""
Tests for party_agent.py — pure Python logic only, no API calls.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import pytest
from agents import party_agent
from agents.party_agent import (
    list_characters,
    build_prompt,
    save_result,
    FOLDERS,
)


# ── list_characters ─────────────────────────────────────────────────────────────

class TestListCharacters:
    def test_returns_list(self):
        result = list_characters("dnd")
        assert isinstance(result, list)

    def test_each_entry_is_three_tuple(self):
        for entry in list_characters("dnd"):
            assert len(entry) == 3

    def test_numbers_start_at_one(self):
        chars = list_characters("dnd")
        if chars:
            assert chars[0][0] == 1

    def test_numbers_are_sequential(self):
        chars = list_characters("traveller")
        for i, (num, _, _) in enumerate(chars):
            assert num == i + 1

    def test_excludes_patron_files(self):
        chars = list_characters("traveller")
        names = [name for _, name, _ in chars]
        assert not any("patron" in n for n in names)

    def test_excludes_questgiver_files(self):
        chars = list_characters("dnd")
        names = [name for _, name, _ in chars]
        assert not any("questgiver" in n for n in names)

    def test_includes_full_files(self):
        chars = list_characters("traveller")
        names = [name for _, name, _ in chars]
        assert any("full" in n for n in names)

    def test_includes_npc_files(self):
        chars = list_characters("traveller")
        names = [name for _, name, _ in chars]
        assert any("npc" in n for n in names)

    def test_unknown_game_returns_empty_or_handles_gracefully(self):
        # Unknown game folder won't exist — should return empty list
        result = list_characters("pathfinder")
        assert result == []


# ── build_prompt ────────────────────────────────────────────────────────────────

class TestBuildPrompt:
    def test_fresh_only_no_theme(self):
        result = build_prompt([], 4, 4, "party")
        assert "Generate 4 additional character sketch" in result
        assert "Theme" not in result

    def test_sheets_only_no_theme(self):
        result = build_prompt(["Sheet A", "Sheet B"], 0, 2, "crew")
        assert "CHARACTER 1" in result
        assert "CHARACTER 2" in result
        assert "Theme" not in result

    def test_theme_appended_when_provided(self):
        result = build_prompt([], 3, 3, "party", theme="gothic horror, vampire hunters")
        assert "gothic horror, vampire hunters" in result
        assert "Theme / constraints from the GM" in result

    def test_empty_theme_not_appended(self):
        result = build_prompt([], 3, 3, "party", theme="")
        assert "Theme" not in result

    def test_whitespace_theme_not_appended(self):
        # theme is .strip()ped before being passed in — empty string after strip
        result = build_prompt([], 3, 3, "party", theme="   ".strip())
        assert "Theme" not in result

    def test_mix_sheets_fresh_and_theme(self):
        result = build_prompt(["Sheet A"], 2, 3, "party", theme="all rogues, no paladins")
        assert "CHARACTER 1" in result
        assert "Generate 2 additional" in result
        assert "all rogues, no paladins" in result

    def test_single_sheet_uses_singular(self):
        result = build_prompt(["Sheet A"], 0, 1, "crew")
        assert "Here is 1 character sheet" in result

    def test_multiple_sheets_uses_plural(self):
        result = build_prompt(["Sheet A", "Sheet B"], 0, 2, "crew")
        assert "Here are 2 character sheet(s)" in result


# ── save_result ─────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(party_agent, "_OUTPUT", tmp_path)
        content = "Some preamble text\n\n## The Iron Crew — Crew Brief\n\n### Members\n..."
        path = save_result(content, "traveller")
        assert "the-iron-crew" in path.name
        assert "traveller" in str(path)
        assert "parties" in str(path)
        assert path.name.endswith("-party.md")

    def test_falls_back_to_first_line_if_no_heading(self, tmp_path, monkeypatch):
        monkeypatch.setattr(party_agent, "_OUTPUT", tmp_path)
        content = "No heading here\nJust some text"
        path = save_result(content, "dnd")
        assert path.exists()

    def test_file_is_written(self, tmp_path, monkeypatch):
        monkeypatch.setattr(party_agent, "_OUTPUT", tmp_path)
        content = "## The Last Ride\n\n### Members\n..."
        path = save_result(content, "dnd")
        assert path.read_text() == content

    def test_special_chars_stripped_from_slug(self, tmp_path, monkeypatch):
        monkeypatch.setattr(party_agent, "_OUTPUT", tmp_path)
        content = '## **"The Broken Stars"** — Crew Brief\n\nContent'
        path = save_result(content, "traveller")
        assert '"' not in path.name
        assert "**" not in path.name

    def test_creates_game_parties_dir_if_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(party_agent, "_OUTPUT", tmp_path)
        content = "## Test Party\n\nContent"
        path = save_result(content, "dnd")
        assert (tmp_path / "dnd" / "parties").exists()


