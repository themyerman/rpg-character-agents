"""
Tests for names.py — name pools and roll_name_suggestion().
No API calls: pure Python only.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.names import (
    roll_name_suggestion,
    roll_dnd_name_suggestion,
    NAME_TOOL_SCHEMA,
    DND_NAME_TOOL_SCHEMA,
    NAME_POOLS,
    DND_POOLS,
    _DND_RACES,
    _draw_last,
)


# ── NAME_POOLS structure ─────────────────────────────────────────────────────────

class TestNamePools:
    def test_at_least_fifteen_traditions(self):
        assert len(NAME_POOLS) >= 15

    def test_all_traditions_have_first_names(self):
        for tradition, pool in NAME_POOLS.items():
            assert "first" in pool, f"Tradition '{tradition}' missing first names"

    def test_standard_pools_have_last_names(self):
        # Icelandic uses patronymic_bases instead of a static last-name list.
        for tradition, pool in NAME_POOLS.items():
            if tradition == "Icelandic":
                continue
            assert "last" in pool, f"Tradition '{tradition}' missing last names"

    def test_all_traditions_have_min_twenty_first_names(self):
        for tradition, pool in NAME_POOLS.items():
            assert len(pool["first"]) >= 20, \
                f"Tradition '{tradition}' has only {len(pool['first'])} first names"

    def test_standard_pools_have_min_ten_last_names(self):
        for tradition, pool in NAME_POOLS.items():
            if tradition == "Icelandic":
                continue
            assert len(pool["last"]) >= 10, \
                f"Tradition '{tradition}' has only {len(pool['last'])} last names"

    def test_all_names_are_non_empty_strings(self):
        for tradition, pool in NAME_POOLS.items():
            name_lists = [pool["first"]]
            if "last" in pool:
                name_lists.append(pool["last"])
            if "patronymic_bases" in pool:
                name_lists.append(pool["patronymic_bases"])
            for lst in name_lists:
                for name in lst:
                    assert isinstance(name, str) and len(name) > 0, \
                        f"Empty/non-string name in tradition '{tradition}'"

    # ── Spot-checks for required traditions ────────────────────────────────────

    def test_west_african_present(self):
        assert "West African" in NAME_POOLS

    def test_east_asian_present(self):
        assert "East Asian" in NAME_POOLS

    def test_slavic_present(self):
        assert "Slavic" in NAME_POOLS

    def test_maori_present(self):
        assert "Māori" in NAME_POOLS

    def test_icelandic_present(self):
        assert "Icelandic" in NAME_POOLS

    def test_north_american_indigenous_present(self):
        assert "North American Indigenous" in NAME_POOLS

    def test_nahuatl_maya_present(self):
        assert "Nahuatl / Maya" in NAME_POOLS

    def test_andean_mapuche_present(self):
        assert "Andean / Mapuche" in NAME_POOLS


# ── Icelandic patronymics ────────────────────────────────────────────────────────

class TestIcelandicPatronymics:
    def test_icelandic_has_patronymic_bases(self):
        pool = NAME_POOLS["Icelandic"]
        assert "patronymic_bases" in pool
        assert len(pool["patronymic_bases"]) >= 10

    def test_draw_last_ends_in_son_or_dottir(self):
        pool = NAME_POOLS["Icelandic"]
        for _ in range(50):
            last = _draw_last(pool)
            assert last.endswith("son") or last.endswith("dóttir"), \
                f"Unexpected Icelandic last name: {last!r}"

    def test_draw_last_has_known_base(self):
        pool  = NAME_POOLS["Icelandic"]
        bases = pool["patronymic_bases"]
        for _ in range(50):
            last = _draw_last(pool)
            assert any(last.startswith(b) for b in bases), \
                f"Patronymic {last!r} doesn't match any declared base"

    def test_draw_last_standard_pool_returns_list_member(self):
        """_draw_last on a non-patronymic pool returns an item from its last list."""
        pool = NAME_POOLS["West African"]
        for _ in range(20):
            last = _draw_last(pool)
            assert last in pool["last"]


# ── roll_name_suggestion — single-tradition results ──────────────────────────────

class TestRollNameSuggestion:
    def _single(self):
        """Return a parsed result that is NOT a blend."""
        for _ in range(500):
            data = json.loads(roll_name_suggestion())
            if not data.get("is_blend", False):
                return data
        raise AssertionError("Could not produce a single-tradition result in 500 tries")

    def test_returns_valid_json(self):
        assert isinstance(json.loads(roll_name_suggestion()), dict)

    def test_has_required_keys(self):
        data = json.loads(roll_name_suggestion())
        for key in ("suggested_name", "first", "last", "tradition"):
            assert key in data, f"Missing key: {key}"

    def test_suggested_name_combines_first_and_last(self):
        for _ in range(10):
            data = json.loads(roll_name_suggestion())
            assert data["first"] in data["suggested_name"]
            assert data["last"]  in data["suggested_name"]

    def test_tradition_is_non_empty_string(self):
        data = json.loads(roll_name_suggestion())
        assert isinstance(data["tradition"], str) and len(data["tradition"]) > 0

    def test_single_tradition_is_not_blend(self):
        data = self._single()
        assert not data.get("is_blend", False)

    def test_single_tradition_is_known_pool(self):
        data = self._single()
        assert data["tradition"] in NAME_POOLS, \
            f"Unknown tradition: {data['tradition']}"

    def test_single_tradition_first_in_pool(self):
        data = self._single()
        assert data["first"] in NAME_POOLS[data["tradition"]]["first"]

    def test_single_tradition_last_in_pool_or_patronymic(self):
        data = self._single()
        pool = NAME_POOLS[data["tradition"]]
        if "patronymic_bases" in pool:
            # Icelandic: last ends in son/dóttir and starts with a known base
            assert data["last"].endswith("son") or data["last"].endswith("dóttir")
        else:
            assert data["last"] in pool["last"]

    def test_single_tradition_has_no_note(self):
        data = self._single()
        assert "note" not in data

    def test_returns_variety_across_traditions(self):
        traditions = {json.loads(roll_name_suggestion())["tradition"] for _ in range(60)}
        assert len(traditions) >= 5

    def test_non_empty_suggested_name(self):
        data = json.loads(roll_name_suggestion())
        assert len(data["suggested_name"]) > 2


# ── Cross-tradition blending ──────────────────────────────────────────────────────

class TestCrossBlend:
    def _blend(self):
        """Return a parsed result that IS a blend."""
        for _ in range(500):
            data = json.loads(roll_name_suggestion())
            if data.get("is_blend", False):
                return data
        raise AssertionError("No blended name produced in 500 rolls (expected ~25%)")

    def test_blend_occurs_within_200_rolls(self):
        found = any(
            json.loads(roll_name_suggestion()).get("is_blend", False)
            for _ in range(200)
        )
        assert found

    def test_blend_has_is_blend_true(self):
        data = self._blend()
        assert data["is_blend"] is True

    def test_blend_has_first_and_last_tradition_keys(self):
        data = self._blend()
        assert "first_tradition" in data
        assert "last_tradition"  in data

    def test_blend_tradition_pools_are_known(self):
        data = self._blend()
        assert data["first_tradition"] in NAME_POOLS
        assert data["last_tradition"]  in NAME_POOLS

    def test_blend_first_comes_from_first_tradition(self):
        data    = self._blend()
        t_first = data["first_tradition"]
        assert data["first"] in NAME_POOLS[t_first]["first"]

    def test_blend_last_comes_from_last_tradition(self):
        data   = self._blend()
        t_last = data["last_tradition"]
        pool   = NAME_POOLS[t_last]
        if "patronymic_bases" in pool:
            assert data["last"].endswith("son") or data["last"].endswith("dóttir")
        else:
            assert data["last"] in pool["last"]

    def test_blend_has_note_field(self):
        data = self._blend()
        assert "note" in data and len(data["note"]) > 20

    def test_blend_note_mentions_both_traditions(self):
        data = self._blend()
        assert data["first_tradition"] in data["note"]
        assert data["last_tradition"]  in data["note"]

    def test_blend_proportion_roughly_25_percent(self):
        """Blend rate should be ~25% — allow 10–40% for statistical noise."""
        n_blends = sum(
            1 for _ in range(300)
            if json.loads(roll_name_suggestion()).get("is_blend", False)
        )
        rate = n_blends / 300
        assert 0.10 <= rate <= 0.40, \
            f"Blend rate {rate:.1%} is outside expected 10–40% range"


# ── NAME_TOOL_SCHEMA ───────────────────────────────────────────────────────────────

class TestNameToolSchema:
    def test_has_name_key(self):
        assert NAME_TOOL_SCHEMA["name"] == "roll_name_suggestion"

    def test_has_description(self):
        assert "description" in NAME_TOOL_SCHEMA
        assert len(NAME_TOOL_SCHEMA["description"]) > 10

    def test_has_input_schema(self):
        assert "input_schema" in NAME_TOOL_SCHEMA

    def test_input_schema_requires_nothing(self):
        assert NAME_TOOL_SCHEMA["input_schema"].get("required", []) == []


# ── DND_POOLS structure ────────────────────────────────────────────────────────

class TestDndPools:
    EXPECTED_RACES = {"Dwarf", "Halfling", "Elf", "Tiefling",
                      "Dragonborn", "Gnome", "Half-Orc"}

    def test_expected_races_present(self):
        assert self.EXPECTED_RACES.issubset(set(DND_POOLS.keys()))

    def test_no_human_in_dnd_pools(self):
        # Human redirects to NAME_POOLS — it must NOT have its own DND_POOLS entry
        assert "Human" not in DND_POOLS

    def test_human_in_dnd_races_list(self):
        assert "Human" in _DND_RACES

    def test_each_race_has_first_and_last(self):
        for race, pool in DND_POOLS.items():
            assert "first" in pool, f"{race} missing 'first'"
            assert "last"  in pool, f"{race} missing 'last'"

    def test_each_race_has_adequate_first_names(self):
        for race, pool in DND_POOLS.items():
            assert len(pool["first"]) >= 20, f"{race} has <20 first names"

    def test_each_race_has_adequate_last_names(self):
        for race, pool in DND_POOLS.items():
            assert len(pool["last"]) >= 10, f"{race} has <10 last names"

    def test_all_dnd_names_non_empty_strings(self):
        for race, pool in DND_POOLS.items():
            for lst in (pool["first"], pool["last"]):
                for name in lst:
                    assert isinstance(name, str) and len(name) > 0, \
                        f"Empty/invalid name in {race}"

    # ── Spot-checks for invented surname conventions ───────────────────────

    def test_dwarf_has_compound_epithets(self):
        last_names = DND_POOLS["Dwarf"]["last"]
        # At least some should be multi-word compound style (no spaces, mixed case)
        compounds = [n for n in last_names if len(n) > 6 and n[0].isupper()]
        assert len(compounds) >= 5

    def test_halfling_has_compound_family_names(self):
        last_names = DND_POOLS["Halfling"]["last"]
        assert "Strongfeet" in last_names or "Warmhearth" in last_names

    def test_tiefling_has_virtue_names_in_first(self):
        first_names = DND_POOLS["Tiefling"]["first"]
        virtue_set  = {"Hope", "Torment", "Patience", "Sorrow", "Grace", "Mercy"}
        assert virtue_set & set(first_names), "No virtue names found in Tiefling firsts"

    def test_tiefling_has_infernal_surnames(self):
        last_names = DND_POOLS["Tiefling"]["last"]
        dark_words = {"Ash", "Ember", "Void", "Cinder", "Shadow", "Dark", "Night"}
        assert any(any(w in name for w in dark_words) for name in last_names)

    def test_dragonborn_clan_names_are_long(self):
        # Draconic clan names are characteristically long
        last_names = DND_POOLS["Dragonborn"]["last"]
        long_names = [n for n in last_names if len(n) > 8]
        assert len(long_names) >= 5

    def test_half_orc_has_orcish_surnames(self):
        last_names = DND_POOLS["Half-Orc"]["last"]
        orcish     = {"Gorehand", "Blacktusk", "Grimfang", "Boneshield", "Greystone"}
        assert orcish & set(last_names)


# ── roll_dnd_name_suggestion ───────────────────────────────────────────────────

class TestRollDndNameSuggestion:
    def test_returns_valid_json(self):
        assert isinstance(json.loads(roll_dnd_name_suggestion()), dict)

    def test_has_required_keys(self):
        data = json.loads(roll_dnd_name_suggestion())
        for key in ("suggested_name", "first", "last", "race"):
            assert key in data, f"Missing key: {key}"

    def test_race_is_known(self):
        for _ in range(30):
            data = json.loads(roll_dnd_name_suggestion())
            assert data["race"] in _DND_RACES, f"Unknown race: {data['race']}"

    def test_explicit_race_respected(self):
        for race in DND_POOLS:
            data = json.loads(roll_dnd_name_suggestion(race=race))
            assert data["race"] == race

    def test_explicit_race_first_in_pool(self):
        for race in DND_POOLS:
            data = json.loads(roll_dnd_name_suggestion(race=race))
            assert data["first"] in DND_POOLS[race]["first"]

    def test_explicit_race_last_in_pool(self):
        for race in DND_POOLS:
            data = json.loads(roll_dnd_name_suggestion(race=race))
            assert data["last"] in DND_POOLS[race]["last"]

    def test_human_redirects_to_cultural_pools(self):
        data = json.loads(roll_dnd_name_suggestion(race="Human"))
        assert data["race"] == "Human"
        # tradition should come from NAME_POOLS
        tradition = data.get("tradition", "")
        assert len(tradition) > 0

    def test_human_first_name_in_name_pools(self):
        for _ in range(20):
            data = json.loads(roll_dnd_name_suggestion(race="Human"))
            tradition = data.get("first_tradition") or data.get("tradition")
            if tradition in NAME_POOLS:
                assert data["first"] in NAME_POOLS[tradition]["first"]

    def test_invalid_race_returns_error(self):
        data = json.loads(roll_dnd_name_suggestion(race="Beholder"))
        assert "error" in data

    def test_suggested_name_combines_first_and_last(self):
        for _ in range(10):
            data = json.loads(roll_dnd_name_suggestion())
            assert data["first"] in data["suggested_name"]
            assert data["last"]  in data["suggested_name"]

    def test_returns_variety_across_races(self):
        races = {json.loads(roll_dnd_name_suggestion())["race"] for _ in range(60)}
        assert len(races) >= 4


# ── DND_NAME_TOOL_SCHEMA ───────────────────────────────────────────────────────

class TestDndNameToolSchema:
    def test_has_name_key(self):
        assert DND_NAME_TOOL_SCHEMA["name"] == "roll_dnd_name_suggestion"

    def test_has_description(self):
        assert len(DND_NAME_TOOL_SCHEMA["description"]) > 20

    def test_race_enum_contains_human(self):
        enum = DND_NAME_TOOL_SCHEMA["input_schema"]["properties"]["race"]["enum"]
        assert "Human" in enum

    def test_race_enum_contains_all_dnd_pools(self):
        enum = set(DND_NAME_TOOL_SCHEMA["input_schema"]["properties"]["race"]["enum"])
        assert set(DND_POOLS.keys()).issubset(enum)

    def test_race_is_not_required(self):
        assert DND_NAME_TOOL_SCHEMA["input_schema"].get("required", []) == []
