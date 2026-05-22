"""
Tests for spells.py — pure Python logic only, no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lib.spells import (
    get_spell_suggestions,
    SPELL_POOLS,
    SPELLCASTING_CLASSES,
    _NON_CASTERS,
    DND_SPELL_TOOL_SCHEMA,
)


# ── SPELL_POOLS structure ─────────────────────────────────────────────────────

class TestSpellPools:
    def test_eight_casting_classes(self):
        expected = {"Wizard", "Cleric", "Druid", "Bard", "Sorcerer", "Warlock", "Paladin", "Ranger"}
        assert set(SPELL_POOLS.keys()) == expected

    def test_each_class_has_spells(self):
        for cls, spells in SPELL_POOLS.items():
            assert len(spells) >= 10, f"{cls} has fewer than 10 spells"

    def test_each_spell_has_required_keys(self):
        required = {"name", "level", "school", "hook"}
        for cls, spells in SPELL_POOLS.items():
            for spell in spells:
                missing = required - spell.keys()
                assert not missing, f"{cls}/{spell.get('name')} missing keys: {missing}"

    def test_spell_levels_are_non_negative_integers(self):
        for cls, spells in SPELL_POOLS.items():
            for spell in spells:
                assert isinstance(spell["level"], int), f"{cls}/{spell['name']} level is not int"
                assert spell["level"] >= 0, f"{cls}/{spell['name']} has negative level"

    def test_each_class_has_at_least_one_cantrip(self):
        # Paladin and Ranger don't get cantrips in 5e — exclude them
        no_cantrip_classes = {"Paladin", "Ranger"}
        for cls, spells in SPELL_POOLS.items():
            if cls in no_cantrip_classes:
                continue
            cantrips = [s for s in spells if s["level"] == 0]
            assert cantrips, f"{cls} has no cantrips"

    def test_each_class_has_at_least_one_low_level_spell(self):
        for cls, spells in SPELL_POOLS.items():
            low = [s for s in spells if 1 <= s["level"] <= 2]
            assert low, f"{cls} has no low-level spells (1-2)"

    def test_each_class_has_at_least_one_high_level_spell(self):
        for cls, spells in SPELL_POOLS.items():
            high = [s for s in spells if s["level"] >= 3]
            assert high, f"{cls} has no higher-level spells (3+)"

    def test_each_class_has_level_5_plus_coverage(self):
        # All classes now extend to at least level 5
        for cls, spells in SPELL_POOLS.items():
            high = [s for s in spells if s["level"] >= 5]
            assert high, f"{cls} has no spells at level 5+"

    def test_full_casters_reach_level_9(self):
        full_casters = {"Wizard", "Cleric", "Druid", "Bard", "Sorcerer", "Warlock"}
        for cls in full_casters:
            spells = SPELL_POOLS[cls]
            level9 = [s for s in spells if s["level"] == 9]
            assert level9, f"{cls} has no level 9 spells"

    def test_paladin_reaches_level_5(self):
        spells = SPELL_POOLS["Paladin"]
        assert any(s["level"] == 5 for s in spells), "Paladin has no level 5 spells"

    def test_ranger_reaches_level_5(self):
        spells = SPELL_POOLS["Ranger"]
        assert any(s["level"] == 5 for s in spells), "Ranger has no level 5 spells"

    def test_hooks_are_non_empty_strings(self):
        for cls, spells in SPELL_POOLS.items():
            for spell in spells:
                assert isinstance(spell["hook"], str), f"{cls}/{spell['name']} hook is not str"
                assert len(spell["hook"]) > 10, f"{cls}/{spell['name']} hook is too short"

    def test_spell_names_are_non_empty_strings(self):
        for cls, spells in SPELL_POOLS.items():
            for spell in spells:
                assert isinstance(spell["name"], str)
                assert len(spell["name"]) > 0


# ── SPELLCASTING_CLASSES ──────────────────────────────────────────────────────

class TestSpellcastingClasses:
    def test_is_sorted(self):
        assert SPELLCASTING_CLASSES == sorted(SPELLCASTING_CLASSES)

    def test_matches_spell_pool_keys(self):
        assert set(SPELLCASTING_CLASSES) == set(SPELL_POOLS.keys())

    def test_length(self):
        assert len(SPELLCASTING_CLASSES) == 8


# ── _NON_CASTERS ──────────────────────────────────────────────────────────────

class TestNonCasters:
    def test_non_casters_not_in_spell_pools(self):
        for cls in _NON_CASTERS:
            # Eldritch Knight / Arcane Trickster are aliases to Wizard — handled by alias logic
            if cls not in {"Eldritch Knight", "Arcane Trickster"}:
                assert cls not in SPELL_POOLS, f"{cls} should not be in SPELL_POOLS"

    def test_basic_martials_present(self):
        assert "Barbarian" in _NON_CASTERS
        assert "Fighter" in _NON_CASTERS
        assert "Monk" in _NON_CASTERS
        assert "Rogue" in _NON_CASTERS


# ── get_spell_suggestions ─────────────────────────────────────────────────────

class TestGetSpellSuggestions:
    def test_returns_valid_json_for_all_classes(self):
        for cls in SPELLCASTING_CLASSES:
            result = get_spell_suggestions(cls)
            data = json.loads(result)
            assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(get_spell_suggestions("Wizard"))
        assert "class" in data
        assert "spells" in data
        assert "note" in data

    def test_class_key_matches_input(self):
        for cls in SPELLCASTING_CLASSES:
            data = json.loads(get_spell_suggestions(cls))
            assert data["class"] == cls

    def test_returns_five_or_six_spells(self):
        # Paladin and Ranger have no cantrips, so they return 4 spells (3 low + 1 high)
        no_cantrip_classes = {"Paladin", "Ranger"}
        for cls in SPELLCASTING_CLASSES:
            data = json.loads(get_spell_suggestions(cls))
            if cls in no_cantrip_classes:
                assert 4 <= len(data["spells"]) <= 5, \
                    f"{cls} returned {len(data['spells'])} spells, expected 4-5"
            else:
                assert 5 <= len(data["spells"]) <= 6, \
                    f"{cls} returned {len(data['spells'])} spells, expected 5-6"

    def test_each_spell_has_required_keys(self):
        data = json.loads(get_spell_suggestions("Cleric"))
        for spell in data["spells"]:
            assert "name" in spell
            assert "level" in spell
            assert "school" in spell
            assert "hook" in spell

    def test_level_is_cantrip_or_level_n(self):
        data = json.loads(get_spell_suggestions("Druid"))
        for spell in data["spells"]:
            lvl = spell["level"]
            assert lvl == "Cantrip" or lvl.startswith("Level "), \
                f"Unexpected level format: {lvl!r}"

    def test_selection_includes_cantrip(self):
        # Run 20 times to account for randomness
        for _ in range(20):
            data = json.loads(get_spell_suggestions("Wizard"))
            cantrips = [s for s in data["spells"] if s["level"] == "Cantrip"]
            assert len(cantrips) >= 1, "Expected at least 1 cantrip"

    def test_selection_includes_higher_level_spell(self):
        for _ in range(20):
            data = json.loads(get_spell_suggestions("Bard"))
            high = [s for s in data["spells"] if s["level"].startswith("Level") and int(s["level"].split()[-1]) >= 3]
            assert len(high) >= 1, "Expected at least 1 higher-level spell"

    def test_subclass_included_in_result(self):
        data = json.loads(get_spell_suggestions("Wizard", subclass="School of Divination"))
        assert data.get("subclass") == "School of Divination"

    def test_no_subclass_key_when_omitted(self):
        data = json.loads(get_spell_suggestions("Cleric"))
        assert "subclass" not in data

    def test_non_caster_returns_note(self):
        data = json.loads(get_spell_suggestions("Barbarian"))
        assert "note" in data
        assert "not a spellcasting class" in data["note"]

    def test_non_caster_fighter_returns_note(self):
        data = json.loads(get_spell_suggestions("Fighter"))
        assert "note" in data

    def test_unknown_class_returns_error(self):
        data = json.loads(get_spell_suggestions("Necromancer"))
        assert "error" in data

    def test_returns_variety_across_calls(self):
        # 10 calls should produce at least 3 different spell sets
        seen = set()
        for _ in range(10):
            data = json.loads(get_spell_suggestions("Wizard"))
            names = tuple(sorted(s["name"] for s in data["spells"]))
            seen.add(names)
        assert len(seen) >= 3, "Spell selection shows no variety across calls"

    def test_paladin_has_no_cantrips(self):
        # Paladin has no cantrips in the pool — check graceful handling
        paladin_pool = SPELL_POOLS["Paladin"]
        cantrips = [s for s in paladin_pool if s["level"] == 0]
        assert len(cantrips) == 0, "Paladin pool should have no cantrips"
        # get_spell_suggestions should still work
        data = json.loads(get_spell_suggestions("Paladin"))
        assert "spells" in data

    def test_ranger_has_no_cantrips(self):
        ranger_pool = SPELL_POOLS["Ranger"]
        cantrips = [s for s in ranger_pool if s["level"] == 0]
        assert len(cantrips) == 0, "Ranger pool should have no cantrips"
        data = json.loads(get_spell_suggestions("Ranger"))
        assert "spells" in data

    def test_high_level_selection_can_return_level_5_plus(self):
        # Run many times — the high tier is level 3+, so level 5+ should appear
        seen_high = set()
        for _ in range(50):
            data = json.loads(get_spell_suggestions("Wizard"))
            for s in data["spells"]:
                if s["level"].startswith("Level"):
                    lvl = int(s["level"].split()[-1])
                    if lvl >= 5:
                        seen_high.add(s["name"])
        assert seen_high, "No level 5+ spells ever appeared in 50 Wizard selections"


# ── DND_SPELL_TOOL_SCHEMA ─────────────────────────────────────────────────────

class TestDndSpellToolSchema:
    def test_has_required_top_level_keys(self):
        assert "name" in DND_SPELL_TOOL_SCHEMA
        assert "description" in DND_SPELL_TOOL_SCHEMA
        assert "input_schema" in DND_SPELL_TOOL_SCHEMA

    def test_name_is_get_spell_suggestions(self):
        assert DND_SPELL_TOOL_SCHEMA["name"] == "get_spell_suggestions"

    def test_class_name_is_required(self):
        schema = DND_SPELL_TOOL_SCHEMA["input_schema"]
        assert "class_name" in schema["required"]

    def test_class_name_enum_matches_spellcasting_classes(self):
        schema = DND_SPELL_TOOL_SCHEMA["input_schema"]
        enum = schema["properties"]["class_name"]["enum"]
        assert set(enum) == set(SPELLCASTING_CLASSES)

    def test_subclass_is_optional(self):
        schema = DND_SPELL_TOOL_SCHEMA["input_schema"]
        assert "subclass" in schema["properties"]
        assert "subclass" not in schema.get("required", [])
