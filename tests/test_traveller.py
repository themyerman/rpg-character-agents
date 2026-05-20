"""
Tests for traveller_agent.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from traveller_agent import (
    characteristic_modifier,
    to_hex_char,
    roll_dice,
    roll_d66,
    roll_homeworld_uwp,
    get_career_info,
    get_characteristic_modifier,
    compute_upp,
    VALID_DICE,
    MIN_ROLLS,
    MAX_ROLLS,
    CAREERS,
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
