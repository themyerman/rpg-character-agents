"""
Tests for dice.py — all RPG dice-rolling utilities.
No API calls: pure Python only.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from dice import (
    roll_stat_dnd,
    roll_dice_dnd,
    roll_dice_traveller,
    get_traveller_title,
    run_tool_traveller,
)


# ── roll_stat_dnd ───────────────────────────────────────────────────────────────

class TestRollStatDnd:
    def test_returns_string(self):
        assert isinstance(roll_stat_dnd(), str)

    def test_score_in_valid_range(self):
        for _ in range(50):
            result = roll_stat_dnd()
            score = int(result.split("score:")[-1].strip())
            assert 3 <= score <= 18

    def test_contains_score_label(self):
        assert "score:" in roll_stat_dnd()


# ── roll_dice_dnd ───────────────────────────────────────────────────────────────

class TestRollDiceDnd:
    def test_valid_die_returns_result(self):
        result = roll_dice_dnd(sides=6, count=1)
        assert "total:" in result

    def test_invalid_die_returns_error(self):
        result = roll_dice_dnd(sides=7)
        assert "Error" in result

    def test_all_valid_dice(self):
        for sides in [4, 6, 8, 10, 12, 20]:
            result = roll_dice_dnd(sides=sides)
            assert "Error" not in result, f"d{sides} failed"


# ── roll_dice_traveller ─────────────────────────────────────────────────────────

class TestRollDiceTraveller:
    def test_d6_returns_result(self):
        result = roll_dice_traveller(sides=6, count=2)
        assert "total:" in result

    def test_non_d6_returns_error(self):
        result = roll_dice_traveller(sides=8)
        assert "Error" in result

    def test_total_in_range(self):
        for _ in range(30):
            result = roll_dice_traveller(sides=6, count=2)
            total = int(result.split("total:")[-1].strip())
            assert 2 <= total <= 12


# ── get_traveller_title ─────────────────────────────────────────────────────────

class TestGetTravellerTitle:
    def test_returns_json_string(self):
        result = get_traveller_title(11)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_below_noble_has_no_title(self):
        data = json.loads(get_traveller_title(10))
        assert data["title"] is None

    def test_soc_11_is_knight(self):
        data = json.loads(get_traveller_title(11))
        assert data["rank"] == "Knight"
        assert data["masculine"] == "Sir"
        assert data["feminine"] == "Dame"

    def test_soc_12_is_baron(self):
        data = json.loads(get_traveller_title(12))
        assert data["rank"] == "Baron"
        assert data["feminine"] == "Baroness"

    def test_soc_13_is_marquis(self):
        data = json.loads(get_traveller_title(13))
        assert data["rank"] == "Marquis"

    def test_soc_14_is_count(self):
        data = json.loads(get_traveller_title(14))
        assert data["rank"] == "Count"
        assert data["feminine"] == "Countess"

    def test_soc_15_is_duke(self):
        data = json.loads(get_traveller_title(15))
        assert data["rank"] == "Duke"
        assert data["feminine"] == "Duchess"

    def test_note_field_present_for_noble(self):
        data = json.loads(get_traveller_title(11))
        assert "note" in data and len(data["note"]) > 0

    def test_dispatcher_routes_get_noble_title(self):
        result = run_tool_traveller("get_noble_title", {"soc": 12})
        data = json.loads(result)
        assert data["rank"] == "Baron"

    def test_dispatcher_unknown_tool(self):
        result = run_tool_traveller("nonexistent", {})
        assert "Unknown" in result
