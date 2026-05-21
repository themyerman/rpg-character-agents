"""
Tests for names.py — pure Python logic, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from names import roll_name_suggestion, NAME_TOOL_SCHEMA, NAME_POOLS


# ── NAME_POOLS ───────────────────────────────────────────────────────────────────

class TestNamePools:
    def test_at_least_ten_traditions(self):
        assert len(NAME_POOLS) >= 10

    def test_each_tradition_has_first_and_last(self):
        for tradition, pool in NAME_POOLS.items():
            assert "first" in pool, f"Tradition '{tradition}' missing first names"
            assert "last"  in pool, f"Tradition '{tradition}' missing last names"

    def test_each_tradition_has_min_twenty_first_names(self):
        for tradition, pool in NAME_POOLS.items():
            assert len(pool["first"]) >= 20, f"Tradition '{tradition}' has <20 first names"

    def test_each_tradition_has_min_ten_last_names(self):
        for tradition, pool in NAME_POOLS.items():
            assert len(pool["last"]) >= 10, f"Tradition '{tradition}' has <10 last names"

    def test_all_names_are_non_empty_strings(self):
        for tradition, pool in NAME_POOLS.items():
            for name in pool["first"] + pool["last"]:
                assert isinstance(name, str) and len(name) > 0, \
                    f"Empty/non-string name in tradition '{tradition}'"

    def test_west_african_present(self):
        assert "West African" in NAME_POOLS

    def test_east_asian_present(self):
        assert "East Asian" in NAME_POOLS

    def test_slavic_present(self):
        assert "Slavic" in NAME_POOLS


# ── roll_name_suggestion ─────────────────────────────────────────────────────────

class TestRollNameSuggestion:
    def test_returns_valid_json(self):
        result = roll_name_suggestion()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(roll_name_suggestion())
        assert "suggested_name" in data
        assert "first" in data
        assert "last" in data
        assert "tradition" in data

    def test_tradition_is_known(self):
        for _ in range(20):
            data = json.loads(roll_name_suggestion())
            assert data["tradition"] in NAME_POOLS, f"Unknown tradition: {data['tradition']}"

    def test_first_name_is_in_tradition_pool(self):
        for _ in range(20):
            data = json.loads(roll_name_suggestion())
            pool = NAME_POOLS[data["tradition"]]
            assert data["first"] in pool["first"], \
                f"First name '{data['first']}' not in pool for '{data['tradition']}'"

    def test_last_name_is_in_tradition_pool(self):
        for _ in range(20):
            data = json.loads(roll_name_suggestion())
            pool = NAME_POOLS[data["tradition"]]
            assert data["last"] in pool["last"], \
                f"Last name '{data['last']}' not in pool for '{data['tradition']}'"

    def test_suggested_name_is_first_space_last(self):
        for _ in range(10):
            data = json.loads(roll_name_suggestion())
            assert data["suggested_name"] == f"{data['first']} {data['last']}"

    def test_returns_variety_across_traditions(self):
        # 30 rolls across 10+ traditions should yield at least 4 distinct ones
        traditions = {json.loads(roll_name_suggestion())["tradition"] for _ in range(30)}
        assert len(traditions) >= 4

    def test_non_empty_suggested_name(self):
        data = json.loads(roll_name_suggestion())
        assert len(data["suggested_name"]) > 2


# ── NAME_TOOL_SCHEMA ──────────────────────────────────────────────────────────────

class TestNameToolSchema:
    def test_has_name_key(self):
        assert NAME_TOOL_SCHEMA["name"] == "roll_name_suggestion"

    def test_has_description(self):
        assert "description" in NAME_TOOL_SCHEMA
        assert len(NAME_TOOL_SCHEMA["description"]) > 10

    def test_has_input_schema(self):
        assert "input_schema" in NAME_TOOL_SCHEMA

    def test_input_schema_requires_nothing(self):
        schema = NAME_TOOL_SCHEMA["input_schema"]
        assert schema.get("required", []) == []
