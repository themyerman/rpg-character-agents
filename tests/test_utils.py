"""
Tests for utils.py — shared infrastructure used by all agents.
No API calls: exercises pure-Python helpers only.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lib.utils import strip_preamble, slug, save_character


# ── strip_preamble ────────────────────────────────────────────────────────────

class TestStripPreamble:
    def test_removes_text_before_first_heading(self):
        text = "Here is some preamble text.\n\n## **Character Name**\nContent"
        result = strip_preamble(text)
        assert result.startswith("## **Character Name**")

    def test_preserves_heading_and_body(self):
        text = "Intro\n## **Name**\nBody"
        result = strip_preamble(text)
        assert "## **Name**" in result
        assert "Body" in result

    def test_no_preamble_returns_text_unchanged(self):
        text = "## **Name**\nBody"
        result = strip_preamble(text)
        assert result.startswith("## **Name**")

    def test_multiline_preamble_removed(self):
        text = "Line one.\nLine two.\nLine three.\n## Heading\nContent"
        result = strip_preamble(text)
        assert result.startswith("## Heading")
        assert "Line one" not in result

    def test_strips_surrounding_whitespace(self):
        text = "   \n  ## **Name**\nBody\n  "
        result = strip_preamble(text)
        # Should not start with leading blank lines
        assert not result.startswith("\n")

    def test_empty_string_returns_empty(self):
        result = strip_preamble("")
        assert result == ""

    def test_no_heading_returns_full_text(self):
        text = "no heading here at all"
        result = strip_preamble(text)
        assert "no heading here at all" in result


# ── slug ──────────────────────────────────────────────────────────────────────

class TestSlug:
    def test_lowercases(self):
        assert slug("Hello World") == "hello-world"

    def test_replaces_spaces_with_dashes(self):
        assert slug("foo bar") == "foo-bar"

    def test_strips_leading_trailing_dashes(self):
        assert slug("  hello  ") == "hello"

    def test_collapses_multiple_separators(self):
        assert slug("foo  bar--baz") == "foo-bar-baz"

    def test_removes_special_chars(self):
        assert slug("Foo's & Bar!") == "foo-s-bar"

    def test_digits_preserved(self):
        assert slug("D&D 5e") == "d-d-5e"

    def test_already_slug_unchanged(self):
        assert slug("already-a-slug") == "already-a-slug"

    def test_all_special_chars(self):
        result = slug("!@#$%^")
        assert result == "" or not result.startswith("-")

    # ── Unicode / diacritic handling ──────────────────────────────────────────

    def test_accented_latin_chars_decompose(self):
        # é, à, ü etc. should map to their base letter
        assert slug("Élodie Renard") == "elodie-renard"

    def test_spanish_accents(self):
        assert slug("María José Vásquez") == "maria-jose-vasquez"

    def test_nordic_chars(self):
        assert slug("Björn Ångström") == "bjorn-angstrom"

    def test_caron_diacritics(self):
        # š → s, ȟ → h, č → c (common in Slavic and Lakȟóta romanization)
        assert slug("Tȟašína") == "thasina"

    def test_mixed_unicode_readable(self):
        # Full Lakȟóta name — ŋ doesn't decompose but result should be legible
        result = slug("Tȟašína Wakíŋyaŋ")
        assert result.startswith("thasina")
        assert "waki" in result
        assert result != "t-a-na-wak-ya-"   # the old broken output

    def test_pure_ascii_unchanged(self):
        assert slug("Selam Desta") == "selam-desta"
        assert slug("Dr. Kwabena Puma") == "dr-kwabena-puma"


# ── save_character ────────────────────────────────────────────────────────────

class TestSaveCharacter:
    CONTENT = "## **Kezia Oduya**\n*Scoundrel*\n\nSome backstory here."

    def test_file_created(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        path = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert path.exists()

    def test_file_in_characters_subdir(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        path = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert "output" in str(path)
        assert "characters" in str(path)
        assert "dnd" in str(path)

    def test_filename_contains_name_slug(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        path = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert "kezia-oduya" in path.name

    def test_filename_contains_mode(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        path = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert path.name.endswith("-npc.md")

    def test_file_content_matches_input(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        path = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert path.read_text() == self.CONTENT

    def test_collision_appends_counter(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        path1 = save_character(self.CONTENT, "npc", "dnd", agent_py)
        path2 = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

    def test_collision_counter_increments(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        p1 = save_character(self.CONTENT, "npc", "dnd", agent_py)
        p2 = save_character(self.CONTENT, "npc", "dnd", agent_py)
        p3 = save_character(self.CONTENT, "npc", "dnd", agent_py)
        assert p1.exists() and p2.exists() and p3.exists()
        assert len({p1, p2, p3}) == 3

    def test_different_modes_dont_collide(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        p_npc  = save_character(self.CONTENT, "npc",       "dnd", agent_py)
        p_char = save_character(self.CONTENT, "character", "dnd", agent_py)
        assert p_npc != p_char

    def test_fallback_when_no_heading(self, tmp_path):
        agent_py = str(tmp_path / "agent.py")
        content = "No heading here, just plain text."
        path = save_character(content, "npc", "dnd", agent_py)
        assert path.exists()

    def test_strips_markdown_from_name(self, tmp_path):
        agent_py = str(tmp_path / "dnd_agent.py")
        content = "## **Bold Name**\nContent"
        path = save_character(content, "npc", "dnd", agent_py)
        assert "**" not in path.name
        assert "#" not in path.name

    def test_subdir_respected(self, tmp_path):
        agent_py = str(tmp_path / "traveller_agent.py")
        path = save_character(self.CONTENT, "npc", "traveller", agent_py)
        assert "traveller" in str(path)


# ── save_character — output_type parameter ────────────────────────────────────

class TestSaveCharacterOutputType:
    CONTENT = "## **Test Entity**\nSome content here."

    def test_defaults_to_characters(self, tmp_path):
        path = save_character(self.CONTENT, "npc", "traveller", tmp_path)
        assert "characters" in str(path)

    def test_aliens_output_type_uses_aliens_dir(self, tmp_path):
        path = save_character(self.CONTENT, "alien", "traveller", tmp_path, output_type="aliens")
        assert "aliens" in str(path)
        assert "characters" not in str(path)

    def test_synthetics_output_type(self, tmp_path):
        path = save_character(self.CONTENT, "synthetic", "traveller", tmp_path, output_type="synthetics")
        assert "synthetics" in str(path)
        assert "characters" not in str(path)

    def test_first_contact_output_type(self, tmp_path):
        path = save_character(self.CONTENT, "first_contact", "traveller", tmp_path, output_type="first-contact")
        assert "first-contact" in str(path)

    def test_output_type_dir_created_automatically(self, tmp_path):
        path = save_character(self.CONTENT, "alien", "traveller", tmp_path, output_type="aliens")
        assert path.parent.exists()
        assert path.exists()

    def test_output_type_under_correct_subdir(self, tmp_path):
        path = save_character(self.CONTENT, "alien", "traveller", tmp_path, output_type="aliens")
        # path should be: <root>/output/traveller/aliens/<name>-alien.md
        parts = path.parts
        assert "traveller" in parts
        assert "aliens" in parts
        traveller_idx = list(parts).index("traveller")
        aliens_idx    = list(parts).index("aliens")
        assert aliens_idx == traveller_idx + 1

    def test_custom_output_type_creates_dir(self, tmp_path):
        path = save_character(self.CONTENT, "npc", "traveller", tmp_path, output_type="custom-type")
        assert "custom-type" in str(path)
        assert path.exists()
