"""
Tests for traveller_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import traveller_agent
from traveller_agent import (
    characteristic_modifier,
    to_hex_char,
    roll_dice,
    roll_d66,
    roll_homeworld_uwp,
    get_career_info,
    get_characteristic_modifier,
    compute_upp,
    roll_patron_hook,
    detect_phase,
    save_result,
    VALID_DICE,
    MIN_ROLLS,
    MAX_ROLLS,
    CAREERS,
    PATRON_HOOKS,
)


# ── characteristic_modifier ─────────────────────────────────────────────────────

class TestCharacteristicModifier:
    def test_zero_is_minus_three(self):
        assert characteristic_modifier(0) == -3

    def test_two_is_minus_two(self):
        assert characteristic_modifier(2) == -2

    def test_five_is_minus_one(self):
        assert characteristic_modifier(5) == -1

    def test_six_is_zero(self):
        assert characteristic_modifier(6) == 0

    def test_eight_is_zero(self):
        assert characteristic_modifier(8) == 0

    def test_nine_is_plus_one(self):
        assert characteristic_modifier(9) == 1

    def test_eleven_is_plus_one(self):
        assert characteristic_modifier(11) == 1

    def test_twelve_is_plus_two(self):
        assert characteristic_modifier(12) == 2

    def test_fifteen_is_plus_three(self):
        assert characteristic_modifier(15) == 3

    def test_sixteen_is_plus_three(self):
        assert characteristic_modifier(16) == 3


# ── to_hex_char ─────────────────────────────────────────────────────────────────

class TestToHexChar:
    def test_single_digits_are_unchanged(self):
        for n in range(10):
            assert to_hex_char(n) == str(n)

    def test_ten_is_A(self):
        assert to_hex_char(10) == "A"

    def test_eleven_is_B(self):
        assert to_hex_char(11) == "B"

    def test_fifteen_is_F(self):
        assert to_hex_char(15) == "F"


# ── roll_dice ───────────────────────────────────────────────────────────────────

class TestRollDice:
    def test_valid_roll_returns_total(self):
        result = roll_dice(sides=6, count=2)
        assert "total:" in result

    def test_invalid_die_returns_error(self):
        result = roll_dice(sides=4)
        assert "Error" in result

    def test_count_too_high_returns_error(self):
        result = roll_dice(sides=6, count=MAX_ROLLS + 1)
        assert "Error" in result

    def test_count_zero_returns_error(self):
        result = roll_dice(sides=6, count=0)
        assert "Error" in result

    def test_total_in_range_2d6(self):
        for _ in range(50):
            result = roll_dice(sides=6, count=2)
            total = int(result.split("total:")[-1].strip())
            assert 2 <= total <= 12

    def test_total_in_range_1d6(self):
        for _ in range(30):
            result = roll_dice(sides=6, count=1)
            total = int(result.split("total:")[-1].strip())
            assert 1 <= total <= 6


# ── roll_d66 ────────────────────────────────────────────────────────────────────

class TestRollD66:
    def test_returns_string(self):
        assert isinstance(roll_d66(), str)

    def test_result_in_valid_range(self):
        # d66 valid results: 11-16, 21-26, 31-36, 41-46, 51-56, 61-66
        for _ in range(100):
            result = roll_d66()
            value = int(result.split(":")[1].strip().split()[0])
            tens  = value // 10
            units = value % 10
            assert 1 <= tens  <= 6, f"Tens digit out of range: {tens}"
            assert 1 <= units <= 6, f"Units digit out of range: {units}"


# ── roll_homeworld_uwp ──────────────────────────────────────────────────────────

class TestRollHomeworldUwp:
    def _get_uwp(self):
        return json.loads(roll_homeworld_uwp())

    def test_returns_valid_json(self):
        result = roll_homeworld_uwp()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = self._get_uwp()
        for key in ["uwp", "starport", "size", "atmosphere", "hydro",
                    "population", "government", "law_level", "tech_level",
                    "suggested_background_skills"]:
            assert key in data, f"Missing key: {key}"

    def test_uwp_string_format(self):
        for _ in range(20):
            data   = self._get_uwp()
            uwp    = data["uwp"]
            # Format: X######-# (9 chars with hyphen at position 7)
            assert len(uwp) == 9,            f"UWP wrong length: {uwp}"
            assert uwp[7]   == "-",          f"UWP missing hyphen: {uwp}"

    def test_background_skills_is_list(self):
        data = self._get_uwp()
        assert isinstance(data["suggested_background_skills"], list)

    def test_background_skills_not_empty(self):
        data = self._get_uwp()
        assert len(data["suggested_background_skills"]) > 0


# ── get_career_info ─────────────────────────────────────────────────────────────

class TestGetCareerInfo:
    def test_valid_career_returns_data(self):
        result = get_career_info("Navy")
        assert "Navy" in result or "description" in result

    def test_invalid_career_returns_error(self):
        result = get_career_info("Astronaut")
        assert "Unknown" in result

    def test_all_careers_return_data(self):
        for career in CAREERS:
            result = get_career_info(career)
            assert "Unknown" not in result, f"Career '{career}' returned unknown"


# ── get_characteristic_modifier ─────────────────────────────────────────────────

class TestGetCharacteristicModifier:
    def test_returns_string_with_dm(self):
        result = get_characteristic_modifier(8)
        assert "DM" in result

    def test_positive_modifier_has_plus(self):
        result = get_characteristic_modifier(12)
        assert "+" in result

    def test_zero_modifier_has_plus(self):
        result = get_characteristic_modifier(7)
        assert "+" in result or "DM 0" in result

    def test_negative_modifier_has_minus(self):
        result = get_characteristic_modifier(2)
        assert "-" in result


# ── compute_upp ─────────────────────────────────────────────────────────────────

class TestComputeUpp:
    def test_known_values(self):
        # 12 encodes as C in Traveller hex
        result = compute_upp([7, 9, 3, 8, 6, 12])
        assert result == "UPP: 79386C"

    def test_values_above_nine_use_hex(self):
        result = compute_upp([10, 11, 12, 13, 14, 15])
        assert result == "UPP: ABCDEF"

    def test_wrong_count_returns_error(self):
        result = compute_upp([7, 9, 3])
        assert "Error" in result

    def test_too_many_returns_error(self):
        result = compute_upp([1, 2, 3, 4, 5, 6, 7])
        assert "Error" in result

    def test_all_zeros(self):
        result = compute_upp([0, 0, 0, 0, 0, 0])
        assert result == "UPP: 000000"


# ── save_result ─────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Séverine Aldenberg-Vey**\nNavy, 4 terms"
        path = save_result(content, "full")
        assert "s-verine-aldenberg-vey" in path.name or "aldeenberg" in path.name or "aldenberg" in path.name

    def test_preamble_skipped_for_filename(self, tmp_path, monkeypatch):
        """Preamble before first ## heading must not end up in the filename."""
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "Now let me calculate the UPP.\n\nSTR 7, DEX 9...\n\n## **Korven Drask**\nDrifter, 6 terms"
        path = save_result(content, "full")
        assert "korven-drask" in path.name
        assert "now" not in path.name
        assert "calculate" not in path.name

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        """Second character with the same name gets -2 suffix, not a silent overwrite."""
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Nasrin al-Qadeer**\nScout, 2 terms"
        path1 = save_result(content, "full")
        path2 = save_result(content, "full")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()
        assert path2.name == "nasrin-al-qadeer-full-2.md"

    def test_collision_increments_beyond_two(self, tmp_path, monkeypatch):
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Nasrin al-Qadeer**\nScout"
        save_result(content, "full")
        save_result(content, "full")
        path3 = save_result(content, "full")
        assert path3.name == "nasrin-al-qadeer-full-3.md"

    def test_mode_used_as_suffix(self, tmp_path, monkeypatch):
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Halvar Czeszko**\nMerchant"
        assert save_result(content, "full").name.endswith("-full.md")
        content2 = "## **Vesper Lalique**\nDrifter"
        assert save_result(content2, "npc").name.endswith("-npc.md")
        content3 = "## **Halvar Czeszko III**\nPatron"
        assert save_result(content3, "patron").name.endswith("-patron.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Test Character**\nNavy, 3 terms"
        path = save_result(content, "full")
        assert path.read_text() == content

    def test_saves_to_correct_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Test**\nScout"
        path = save_result(content, "full")
        assert "characters" in str(path)
        assert "traveller" in str(path)

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(traveller_agent, "__file__", str(tmp_path / "traveller_agent.py"))
        content = "## **Korven Drask**\nDrifter"
        path = save_result(content, "full")
        assert "**" not in path.name
        assert "#" not in path.name


# ── roll_patron_hook ────────────────────────────────────────────────────────────

class TestRollPatronHook:
    def test_returns_valid_json(self):
        result = roll_patron_hook()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(roll_patron_hook())
        assert "job_type"     in data
        assert "description"  in data
        assert "complication" in data

    def test_job_type_is_known(self):
        known_types = {h["type"] for h in PATRON_HOOKS}
        for _ in range(20):
            data = json.loads(roll_patron_hook())
            assert data["job_type"] in known_types

    def test_returns_variety(self):
        # 30 rolls should yield at least 4 distinct job types
        types = {json.loads(roll_patron_hook())["job_type"] for _ in range(30)}
        assert len(types) >= 4

    def test_complication_is_non_empty_string(self):
        data = json.loads(roll_patron_hook())
        assert isinstance(data["complication"], str)
        assert len(data["complication"]) > 0

    def test_complication_belongs_to_job_type(self):
        for _ in range(20):
            data = json.loads(roll_patron_hook())
            hook = next(h for h in PATRON_HOOKS if h["type"] == data["job_type"])
            assert data["complication"] in hook["complications"]

    def test_at_least_ten_job_types(self):
        assert len(PATRON_HOOKS) >= 10

    def test_courier_and_extraction_present(self):
        known_types = {h["type"] for h in PATRON_HOOKS}
        assert "Courier Run"  in known_types
        assert "Extraction"   in known_types


# ── detect_phase ─────────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_roll_homeworld_uwp_returns_homeworld(self):
        assert detect_phase("roll_homeworld_uwp", set()) == "homeworld"

    def test_get_career_info_returns_career(self):
        assert detect_phase("get_career_info", set()) == "career"

    def test_roll_d66_returns_terms(self):
        assert detect_phase("roll_d66", set()) == "terms"

    def test_roll_dice_before_homeworld_returns_stats(self):
        # seen does not contain roll_homeworld_uwp → stats phase
        assert detect_phase("roll_dice", set()) == "stats"

    def test_roll_dice_after_homeworld_returns_career(self):
        seen = {"roll_homeworld_uwp"}
        assert detect_phase("roll_dice", seen) == "career"

    def test_roll_dice_after_d66_returns_muster(self):
        seen = {"roll_homeworld_uwp", "roll_d66"}
        assert detect_phase("roll_dice", seen) == "muster"

    def test_roll_name_suggestion_returns_name(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_roll_patron_hook_returns_patron(self):
        assert detect_phase("roll_patron_hook", set()) == "patron"

    def test_roll_ship_name_returns_ship(self):
        assert detect_phase("roll_ship_name", set()) == "ship"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None

    def test_compute_upp_returns_none(self):
        # suppressed — should not trigger a phase message
        assert detect_phase("compute_upp", set()) is None


# ── Constants sanity checks ─────────────────────────────────────────────────────

class TestConstants:
    def test_only_d6_is_valid(self):
        assert VALID_DICE == {6}

    def test_min_rolls_is_one(self):
        assert MIN_ROLLS == 1

    def test_max_rolls_is_reasonable(self):
        assert 1 < MAX_ROLLS <= 100

    def test_twelve_careers_defined(self):
        assert len(CAREERS) == 12
