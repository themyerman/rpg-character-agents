"""
Tests for lib/aliens.py

Covers: major race profiles, minor race profiles, alias normalisation,
error handling, first contact generation, posture weighting, NIP threshold,
communication barrier lookup, and tool schema structure.
"""

import json
import sys
from pathlib import Path
import collections

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.aliens import (
    get_major_race_profile,
    get_minor_race_profile,
    generate_species_profile,
    generate_contact_situation,
    generate_first_contact,
    list_major_races,
    list_minor_races,
    MAJOR_RACES,
    MINOR_RACES,
    MAJOR_RACE_TOOL_SCHEMA,
    MINOR_RACE_TOOL_SCHEMA,
    FIRST_CONTACT_TOOL_SCHEMA,
    LIST_MAJOR_RACES_TOOL_SCHEMA,
    LIST_MINOR_RACES_TOOL_SCHEMA,
    _POSTURES,
    _DIET_POSTURE_WEIGHTS,
    _COMMUNICATION_BARRIER,
    _TL_POWER_DYNAMIC,
    _SOCIAL_NEGOTIATION,
    _FC_DIET,
    _FC_SOCIAL,
    _FC_COMMUNICATION,
)


# ─── Major race profiles ──────────────────────────────────────────────────────

class TestMajorRaceProfile:

    def test_all_six_major_races_exist(self):
        for race in ["aslan", "vargr", "droyne", "k_kree", "hivers", "zhodani"]:
            assert race in MAJOR_RACES, f"Missing major race: {race}"

    def test_aslan_characteristic_mods(self):
        r = json.loads(get_major_race_profile("aslan"))
        assert r["characteristic_mods"]["STR"] == 2
        assert r["characteristic_mods"]["DEX"] == -2

    def test_vargr_characteristic_mods(self):
        r = json.loads(get_major_race_profile("vargr"))
        assert r["characteristic_mods"]["STR"] == -1
        assert r["characteristic_mods"]["DEX"] == 1
        assert r["characteristic_mods"]["END"] == -1

    def test_vargr_soc_replacement(self):
        r = json.loads(get_major_race_profile("vargr"))
        assert "soc_replacement" in r
        assert "CHA" in r["soc_replacement"]

    def test_droyne_has_caste_mods(self):
        r = json.loads(get_major_race_profile("droyne"))
        assert "caste_mods" in r
        castes = ["Worker", "Warrior", "Drone", "Technician", "Sport", "Leader"]
        for caste in castes:
            assert caste in r["caste_mods"], f"Missing caste: {caste}"

    def test_droyne_warrior_caste_str_bonus(self):
        r = json.loads(get_major_race_profile("droyne"))
        assert r["caste_mods"]["Warrior"]["STR"] == 2

    def test_droyne_leader_caste_soc_bonus(self):
        r = json.loads(get_major_race_profile("droyne"))
        assert r["caste_mods"]["Leader"]["SOC"] == 4

    def test_kkree_str_bonus(self):
        r = json.loads(get_major_race_profile("k_kree"))
        assert r["characteristic_mods"]["STR"] == 4
        assert r["characteristic_mods"]["DEX"] == -4
        assert r["characteristic_mods"]["END"] == 2

    def test_hivers_dex_bonus(self):
        r = json.loads(get_major_race_profile("hivers"))
        assert r["characteristic_mods"]["DEX"] == 4
        assert r["characteristic_mods"]["STR"] == -4

    def test_zhodani_empty_char_mods(self):
        r = json.loads(get_major_race_profile("zhodani"))
        assert r["characteristic_mods"] == {}

    def test_each_major_race_has_required_fields(self):
        required = ["name", "homeworld", "social_structure", "key_drives",
                    "campaign_presence", "psi_note", "npc_hooks"]
        for race_key in MAJOR_RACES:
            r = json.loads(get_major_race_profile(race_key))
            for field in required:
                assert field in r, f"{race_key} missing field: {field}"

    def test_each_major_race_has_npc_hooks_list(self):
        for race_key in MAJOR_RACES:
            r = json.loads(get_major_race_profile(race_key))
            assert isinstance(r["npc_hooks"], list)
            assert len(r["npc_hooks"]) >= 2

    def test_each_major_race_has_usage_note(self):
        for race_key in MAJOR_RACES:
            r = json.loads(get_major_race_profile(race_key))
            assert "usage_note" in r

    def test_unknown_major_race_returns_error(self):
        r = json.loads(get_major_race_profile("human"))
        assert "error" in r
        assert "available" in r

    def test_unknown_major_race_lists_available(self):
        r = json.loads(get_major_race_profile("trekkies"))
        for race in MAJOR_RACES:
            assert race in r["available"]


class TestMajorRaceAliases:

    def test_kkree_apostrophe(self):
        r = json.loads(get_major_race_profile("k'kree"))
        assert r["name"] == "K'kree"

    def test_kkree_no_separator(self):
        r = json.loads(get_major_race_profile("kkree"))
        assert r["name"] == "K'kree"

    def test_kkree_underscore(self):
        r = json.loads(get_major_race_profile("k_kree"))
        assert r["name"] == "K'kree"

    def test_hiver_singular(self):
        r = json.loads(get_major_race_profile("hiver"))
        assert r["name"] == "Hivers"

    def test_case_insensitive(self):
        r = json.loads(get_major_race_profile("ASLAN"))
        assert r["name"] == "Aslan"

    def test_zhodani_case(self):
        r = json.loads(get_major_race_profile("Zhodani"))
        assert r["name"] == "Zhodani"


# ─── Minor race profiles ──────────────────────────────────────────────────────

class TestMinorRaceProfile:

    def test_all_seven_minor_races_exist(self):
        expected = ["bwaps", "darrians", "llellewyoly", "virushi",
                    "hhkar", "jonkeereen", "dolphins"]
        for race in expected:
            assert race in MINOR_RACES, f"Missing minor race: {race}"

    def test_each_minor_race_has_required_fields(self):
        required = ["name", "homeworld", "characteristic_mods",
                    "description", "behavioral_notes", "npc_hook"]
        for race_key in MINOR_RACES:
            r = json.loads(get_minor_race_profile(race_key))
            for field in required:
                assert field in r, f"{race_key} missing field: {field}"

    def test_bwaps_dex_bonus(self):
        r = json.loads(get_minor_race_profile("bwaps"))
        assert r["characteristic_mods"]["DEX"] == 2
        assert r["characteristic_mods"]["END"] == -2

    def test_darrians_int_bonus(self):
        r = json.loads(get_minor_race_profile("darrians"))
        assert r["characteristic_mods"]["INT"] == 2

    def test_llellewyoly_dex_bonus(self):
        r = json.loads(get_minor_race_profile("llellewyoly"))
        assert r["characteristic_mods"]["DEX"] == 4
        assert r["characteristic_mods"]["STR"] == -4

    def test_virushi_str_bonus(self):
        r = json.loads(get_minor_race_profile("virushi"))
        assert r["characteristic_mods"]["STR"] == 6
        assert r["characteristic_mods"]["END"] == 4

    def test_each_minor_race_has_usage_note(self):
        for race_key in MINOR_RACES:
            r = json.loads(get_minor_race_profile(race_key))
            assert "usage_note" in r

    def test_unknown_minor_race_returns_error(self):
        r = json.loads(get_minor_race_profile("klingon"))
        assert "error" in r

    def test_unknown_minor_race_lists_available(self):
        r = json.loads(get_minor_race_profile("jedi"))
        for race in MINOR_RACES:
            assert race in r["available"]


class TestMinorRaceAliases:

    def test_newts_alias(self):
        r = json.loads(get_minor_race_profile("newts"))
        assert "Bwaps" in r["name"]

    def test_dandelions_alias(self):
        r = json.loads(get_minor_race_profile("dandelions"))
        assert "Llellewyoly" in r["name"]

    def test_darrian_singular(self):
        r = json.loads(get_minor_race_profile("darrian"))
        assert "Darrians" in r["name"]

    def test_dolphin_singular(self):
        r = json.loads(get_minor_race_profile("dolphin"))
        assert "Dolphins" in r["name"]

    def test_case_insensitive(self):
        r = json.loads(get_minor_race_profile("BWAPS"))
        assert "Bwaps" in r["name"]


# ─── List functions ───────────────────────────────────────────────────────────

class TestListFunctions:

    def test_list_major_races_returns_all_six(self):
        r = json.loads(list_major_races())
        assert "major_races" in r
        for race in ["aslan", "vargr", "droyne", "k_kree", "hivers", "zhodani"]:
            assert race in r["major_races"]

    def test_list_major_races_summaries_are_strings(self):
        r = json.loads(list_major_races())
        for key, summary in r["major_races"].items():
            assert isinstance(summary, str) and len(summary) > 10

    def test_list_minor_races_returns_all_seven(self):
        r = json.loads(list_minor_races())
        assert "minor_races" in r
        for race in ["bwaps", "darrians", "llellewyoly", "virushi",
                     "hhkar", "jonkeereen", "dolphins"]:
            assert race in r["minor_races"]

    def test_list_minor_races_summaries_are_strings(self):
        r = json.loads(list_minor_races())
        for key, summary in r["minor_races"].items():
            assert isinstance(summary, str) and len(summary) > 10


# ─── Species profile generation ──────────────────────────────────────────────

class TestGenerateSpeciesProfile:

    def _generate_many(self, n=200):
        return [generate_species_profile() for _ in range(n)]

    def test_required_fields_present(self):
        sp = generate_species_profile()
        required = [
            "provisional_name", "designation_note", "body_symmetry",
            "locomotion", "primary_sense", "size", "diet",
            "social_structure", "communication", "cognitive_style",
            "lifespan", "tech_level", "tech_level_label",
        ]
        for field in required:
            assert field in sp, f"Missing field: {field}"

    def test_provisional_name_is_string(self):
        for sp in self._generate_many(50):
            assert isinstance(sp["provisional_name"], str)
            assert len(sp["provisional_name"]) >= 4

    def test_tech_level_range(self):
        for sp in self._generate_many(500):
            assert 0 <= sp["tech_level"] <= 10

    def test_diet_always_valid(self):
        for sp in self._generate_many(200):
            assert sp["diet"] in _FC_DIET

    def test_social_always_valid(self):
        for sp in self._generate_many(200):
            assert sp["social_structure"] in _FC_SOCIAL

    def test_communication_always_valid(self):
        for sp in self._generate_many(200):
            assert sp["communication"] in _FC_COMMUNICATION

    def test_tech_level_label_matches_value(self):
        for sp in self._generate_many(100):
            assert sp["tech_level_label"] == f"TL {sp['tech_level']}"

    def test_diet_distribution_covers_all_types(self):
        """All diet types should appear in 1000 rolls."""
        seen = set()
        for _ in range(1000):
            sp = generate_species_profile()
            seen.add(sp["diet"])
        assert seen == set(_FC_DIET), f"Missing diet types: {set(_FC_DIET) - seen}"


# ─── Contact situation generation ────────────────────────────────────────────

class TestGenerateContactSituation:

    def _situation(self, diet=None, social=None, comm=None, tl=None):
        sp = generate_species_profile()
        if diet:
            sp["diet"] = diet
        if social:
            sp["social_structure"] = social
        if comm:
            sp["communication"] = comm
        if tl is not None:
            sp["tech_level"] = tl
        return generate_contact_situation(sp), sp

    def test_required_fields_present(self):
        cs, _ = self._situation()
        required = [
            "discovery_vector", "initial_posture", "posture_note",
            "what_they_want", "communication_barrier", "negotiation_shape",
            "power_dynamic", "non_interference_protocol_applies", "nip_note",
            "size_note", "imperial_stake", "complications",
        ]
        for field in required:
            assert field in cs, f"Missing field: {field}"

    def test_posture_always_in_valid_set(self):
        for _ in range(200):
            cs, _ = self._situation()
            assert cs["initial_posture"] in _POSTURES

    def test_complications_is_list_of_at_least_one(self):
        for _ in range(100):
            cs, _ = self._situation()
            assert isinstance(cs["complications"], list)
            assert len(cs["complications"]) >= 1

    def test_complications_max_two(self):
        for _ in range(100):
            cs, _ = self._situation()
            assert len(cs["complications"]) <= 2

    def test_imperial_stake_has_required_fields(self):
        for _ in range(50):
            cs, _ = self._situation()
            stake = cs["imperial_stake"]
            assert "stake" in stake
            assert "value" in stake
            assert "complication" in stake

    def test_nip_applies_at_tl_5_and_below(self):
        for tl in range(6):
            for _ in range(20):
                cs, _ = self._situation(tl=tl)
                assert cs["non_interference_protocol_applies"] is True, \
                    f"NIP should apply at TL {tl}"

    def test_nip_does_not_apply_at_tl_6_and_above(self):
        for tl in range(6, 11):
            for _ in range(20):
                cs, _ = self._situation(tl=tl)
                assert cs["non_interference_protocol_applies"] is False, \
                    f"NIP should not apply at TL {tl}"

    def test_communication_barrier_has_required_fields(self):
        for _ in range(50):
            cs, _ = self._situation()
            cb = cs["communication_barrier"]
            assert "barrier" in cb
            assert "note" in cb

    def test_negotiation_shape_is_string(self):
        for _ in range(50):
            cs, _ = self._situation()
            assert isinstance(cs["negotiation_shape"], str)
            assert len(cs["negotiation_shape"]) > 10

    def test_power_dynamic_is_string(self):
        for _ in range(50):
            cs, _ = self._situation()
            assert isinstance(cs["power_dynamic"], str)


class TestPostureWeighting:
    """Verify that diet→posture weighting produces statistically expected skews."""

    def _posture_rates(self, diet, n=1000):
        counts = collections.Counter()
        for _ in range(n):
            sp = generate_species_profile()
            sp["diet"] = diet
            cs = generate_contact_situation(sp)
            counts[cs["initial_posture"]] += 1
        return {k: v / n for k, v in counts.items()}

    def test_carnivore_skews_hostile_or_territorial(self):
        rates = self._posture_rates("apex carnivore", n=1000)
        hostile_rate = rates.get("actively hostile", 0) + rates.get("territorial", 0)
        assert hostile_rate > 0.35, (
            f"Carnivore hostile+territorial rate {hostile_rate:.1%} below 35%"
        )

    def test_grazer_skews_fearful_or_watchful(self):
        rates = self._posture_rates("grazer", n=1000)
        retreat_rate = rates.get("fearful", 0) + rates.get("watchful", 0)
        assert retreat_rate > 0.45, (
            f"Grazer fearful+watchful rate {retreat_rate:.1%} below 45%"
        )

    def test_photosynthetic_skews_indifferent_or_curious(self):
        rates = self._posture_rates("photosynthetic", n=1000)
        passive_rate = (
            rates.get("indifferent", 0)
            + rates.get("openly curious", 0)
            + rates.get("cautiously curious", 0)
        )
        assert passive_rate > 0.50, (
            f"Photosynthetic passive rate {passive_rate:.1%} below 50%"
        )

    def test_carnivore_rarely_welcoming(self):
        rates = self._posture_rates("apex carnivore", n=1000)
        assert rates.get("welcoming", 0) == 0.0, "Apex carnivore should never be welcoming"

    def test_all_diet_types_have_weight_table(self):
        for diet in _FC_DIET:
            assert diet in _DIET_POSTURE_WEIGHTS, f"Missing weight table for: {diet}"

    def test_weight_tables_have_correct_length(self):
        for diet, weights in _DIET_POSTURE_WEIGHTS.items():
            assert len(weights) == len(_POSTURES), (
                f"{diet} has {len(weights)} weights, expected {len(_POSTURES)}"
            )


# ─── Full first contact pipeline ─────────────────────────────────────────────

class TestGenerateFirstContact:

    def test_returns_valid_json(self):
        result = generate_first_contact()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_top_level_structure(self):
        data = json.loads(generate_first_contact())
        assert "species_profile" in data
        assert "contact_situation" in data
        assert "gm_note" in data

    def test_situation_is_seeded_from_profile(self):
        """NIP in situation should match TL in profile — 200 runs."""
        for _ in range(200):
            data = json.loads(generate_first_contact())
            sp = data["species_profile"]
            cs = data["contact_situation"]
            if sp["tech_level"] <= 5:
                assert cs["non_interference_protocol_applies"] is True
            else:
                assert cs["non_interference_protocol_applies"] is False

    def test_gm_note_is_string(self):
        data = json.loads(generate_first_contact())
        assert isinstance(data["gm_note"], str)
        assert len(data["gm_note"]) > 20

    def test_provisional_name_varies(self):
        """Names should not all be the same across 20 runs."""
        names = {
            json.loads(generate_first_contact())["species_profile"]["provisional_name"]
            for _ in range(20)
        }
        assert len(names) > 5, f"Names not varying enough: {names}"


# ─── Reference table coverage ────────────────────────────────────────────────

class TestReferenceTableCoverage:

    def test_all_communication_types_have_barrier_entry(self):
        for comm in _FC_COMMUNICATION:
            assert comm in _COMMUNICATION_BARRIER, (
                f"No barrier entry for communication type: '{comm}'"
            )

    def test_all_barrier_entries_have_required_fields(self):
        for comm, data in _COMMUNICATION_BARRIER.items():
            assert "barrier" in data, f"Missing 'barrier' for: {comm}"
            assert "note" in data, f"Missing 'note' for: {comm}"

    def test_all_tl_levels_have_power_dynamic(self):
        for tl in range(11):
            assert tl in _TL_POWER_DYNAMIC, f"No power dynamic for TL {tl}"

    def test_all_social_structures_have_negotiation(self):
        for social in _FC_SOCIAL:
            assert social in _SOCIAL_NEGOTIATION, (
                f"No negotiation shape for social structure: '{social}'"
            )

    def test_power_dynamic_strings_non_empty(self):
        for tl, text in _TL_POWER_DYNAMIC.items():
            assert isinstance(text, str) and len(text) > 20, (
                f"TL {tl} power dynamic text too short"
            )


# ─── Tool schemas ─────────────────────────────────────────────────────────────

class TestToolSchemas:

    def _validate_schema(self, schema, name):
        assert schema["name"] == name, f"Schema name mismatch: {schema['name']} != {name}"
        assert "description" in schema
        assert len(schema["description"]) > 20
        assert "input_schema" in schema
        assert schema["input_schema"]["type"] == "object"
        assert "required" in schema["input_schema"]

    def test_major_race_schema_structure(self):
        self._validate_schema(MAJOR_RACE_TOOL_SCHEMA, "get_major_race_profile")

    def test_major_race_schema_has_race_enum(self):
        props = MAJOR_RACE_TOOL_SCHEMA["input_schema"]["properties"]
        assert "race" in props
        enum = props["race"]["enum"]
        assert len(enum) == 6
        assert "aslan" in enum

    def test_major_race_schema_requires_race(self):
        assert "race" in MAJOR_RACE_TOOL_SCHEMA["input_schema"]["required"]

    def test_minor_race_schema_structure(self):
        self._validate_schema(MINOR_RACE_TOOL_SCHEMA, "get_minor_race_profile")

    def test_minor_race_schema_has_race_enum(self):
        props = MINOR_RACE_TOOL_SCHEMA["input_schema"]["properties"]
        assert "race" in props
        enum = props["race"]["enum"]
        assert len(enum) == 7
        assert "bwaps" in enum

    def test_minor_race_schema_requires_race(self):
        assert "race" in MINOR_RACE_TOOL_SCHEMA["input_schema"]["required"]

    def test_first_contact_schema_structure(self):
        self._validate_schema(FIRST_CONTACT_TOOL_SCHEMA, "generate_first_contact")

    def test_first_contact_schema_no_required_params(self):
        assert FIRST_CONTACT_TOOL_SCHEMA["input_schema"]["required"] == []

    def test_list_schemas_no_required_params(self):
        assert LIST_MAJOR_RACES_TOOL_SCHEMA["input_schema"]["required"] == []
        assert LIST_MINOR_RACES_TOOL_SCHEMA["input_schema"]["required"] == []

    def test_all_schema_descriptions_mention_traveller(self):
        for schema in [
            MAJOR_RACE_TOOL_SCHEMA,
            MINOR_RACE_TOOL_SCHEMA,
            FIRST_CONTACT_TOOL_SCHEMA,
        ]:
            assert "Traveller" in schema["description"] or "traveller" in schema["description"].lower()

    def test_first_contact_schema_mentions_firefly_warning(self):
        assert "Firefly" in FIRST_CONTACT_TOOL_SCHEMA["description"]
