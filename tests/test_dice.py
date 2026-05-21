"""
Tests for dice.py — all RPG dice-rolling utilities.
No API calls: pure Python only.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from dice import roll_stat_dnd, roll_dice_dnd, roll_dice_traveller


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
