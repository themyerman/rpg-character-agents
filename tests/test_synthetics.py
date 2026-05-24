"""
Tests for lib/synthetics.py

Covers: Stardancer profile, S&V synthetic chance, Traveller droid profiles
and chance rolls, AI system profiles (with capability weighting and autonomous
flag logic), auxiliary AI profiles, alias normalisation, and all tool schemas.
"""

import json
import sys
from pathlib import Path
import collections

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.synthetics import (
    get_stardancer_profile,
    roll_scum_synthetic_chance,
    get_traveller_droid_profile,
    roll_traveller_droid_chance,
    get_traveller_ai_profile,
    get_traveller_auxiliary_profile,
    SCUM_SYNTHETIC_THRESHOLDS,
    TRAVELLER_DROID_THRESHOLDS,
    STARDANCER_TOOL_SCHEMA,
    SCUM_SYNTHETIC_CHANCE_TOOL_SCHEMA,
    TRAVELLER_DROID_TOOL_SCHEMA,
    TRAVELLER_DROID_CHANCE_TOOL_SCHEMA,
    TRAVELLER_AI_TOOL_SCHEMA,
    TRAVELLER_AUXILIARY_TOOL_SCHEMA,
    STARDANCER_BODY_TYPES,
    STARDANCER_CONSCIOUSNESS_ORIGINS,
    STARDANCER_MEMORY_HOOKS,
    STARDANCER_HEGEMONY_STATUSES,
    STARDANCER_NEEDS,
    STARDANCER_COMPLICATION_HOOKS,
    TRAVELLER_DROID_PURPOSE,
    TRAVELLER_DROID_LEGAL,
    TRAVELLER_DROID_PERSONALITY,
    TRAVELLER_DROID_CONDITION,
    TRAVELLER_DROID_RESTRICTION,
    TRAVELLER_DROID_HOOKS,
    TRAVELLER_AI_INSTALLATION_TYPES,
    _AI_CAPABILITY_LEVELS,
    _AI_CAPABILITY_WEIGHTS,
    TRAVELLER_AI_PERSONALITY_LEVELS,
    TRAVELLER_AI_OPERATIONAL_AGE,
    TRAVELLER_AI_HOOKS,
    TRAVELLER_AUXILIARY_PURPOSE,
    TRAVELLER_AUXILIARY_PERSONALITY,
    TRAVELLER_AUXILIARY_HOOKS,
)


# ─── S&V Stardancer profile ───────────────────────────────────────────────────

class TestStardancerProfile:

    def test_playbook_label(self):
        r = json.loads(get_stardancer_profile())
        assert r["playbook"] == "Stardancer"

    def test_required_fields_present(self):
        required = [
            "playbook", "body_type", "consciousness_origin",
            "memory_approach", "hegemony_status", "primary_need",
            "complication_hook", "mechanic_note",
        ]
        for _ in range(10):
            r = json.loads(get_stardancer_profile())
            for field in required:
                assert field in r, f"Missing field: {field}"

    def test_body_type_has_type_and_note(self):
        for _ in range(20):
            r = json.loads(get_stardancer_profile())
            bt = r["body_type"]
            assert "type" in bt
            assert "note" in bt
            assert len(bt["note"]) > 20

    def test_consciousness_origin_has_origin_and_hook(self):
        for _ in range(20):
            r = json.loads(get_stardancer_profile())
            co = r["consciousness_origin"]
            assert "origin" in co
            assert "hook" in co
            assert len(co["hook"]) > 20

    def test_hegemony_status_has_status_and_implication(self):
        for _ in range(20):
            r = json.loads(get_stardancer_profile())
            hs = r["hegemony_status"]
            assert "status" in hs
            assert "implication" in hs

    def test_primary_need_has_need_and_note(self):
        for _ in range(20):
            r = json.loads(get_stardancer_profile())
            pn = r["primary_need"]
            assert "need" in pn
            assert "note" in pn

    def test_complication_hook_is_string(self):
        for _ in range(20):
            r = json.loads(get_stardancer_profile())
            assert isinstance(r["complication_hook"], str)
            assert len(r["complication_hook"]) > 15

    def test_mechanic_note_mentions_stardancer(self):
        r = json.loads(get_stardancer_profile())
        assert "Stardancer" in r["mechanic_note"]

    def test_body_type_values_from_pool(self):
        pool_types = {b["type"] for b in STARDANCER_BODY_TYPES}
        for _ in range(50):
            r = json.loads(get_stardancer_profile())
            assert r["body_type"]["type"] in pool_types

    def test_consciousness_values_from_pool(self):
        pool_origins = {c["origin"] for c in STARDANCER_CONSCIOUSNESS_ORIGINS}
        for _ in range(50):
            r = json.loads(get_stardancer_profile())
            assert r["consciousness_origin"]["origin"] in pool_origins

    def test_memory_approach_from_pool(self):
        for _ in range(50):
            r = json.loads(get_stardancer_profile())
            assert r["memory_approach"] in STARDANCER_MEMORY_HOOKS

    def test_complication_from_pool(self):
        for _ in range(50):
            r = json.loads(get_stardancer_profile())
            assert r["complication_hook"] in STARDANCER_COMPLICATION_HOOKS

    def test_results_vary(self):
        origins = {
            json.loads(get_stardancer_profile())["consciousness_origin"]["origin"]
            for _ in range(20)
        }
        assert len(origins) > 3, "Consciousness origins not varying"


# ─── S&V synthetic chance roll ────────────────────────────────────────────────

class TestScumSyntheticChance:

    def test_npc_threshold(self):
        r = json.loads(roll_scum_synthetic_chance("npc"))
        assert r["threshold"] == SCUM_SYNTHETIC_THRESHOLDS["npc"]

    def test_playbook_random_threshold(self):
        r = json.loads(roll_scum_synthetic_chance("playbook_random"))
        assert r["threshold"] == SCUM_SYNTHETIC_THRESHOLDS["playbook_random"]

    def test_playbook_random_higher_than_npc(self):
        assert SCUM_SYNTHETIC_THRESHOLDS["playbook_random"] > SCUM_SYNTHETIC_THRESHOLDS["npc"]

    def test_has_ability_field_present(self):
        for _ in range(20):
            r = json.loads(roll_scum_synthetic_chance("npc"))
            assert "has_ability" in r

    def test_next_step_present_when_synthetic(self):
        # Force a synthetic result by mocking — instead test over many rolls
        for _ in range(500):
            r = json.loads(roll_scum_synthetic_chance("playbook_random"))
            if r["has_ability"]:
                assert "next_step" in r
                assert "get_stardancer_profile" in r["next_step"]
                break

    def test_note_always_present(self):
        for _ in range(20):
            r = json.loads(roll_scum_synthetic_chance("npc"))
            assert "note" in r

    def test_roll_within_range(self):
        for _ in range(100):
            r = json.loads(roll_scum_synthetic_chance("npc"))
            assert 1 <= r["roll"] <= 100

    def test_probability_roughly_correct_npc(self):
        hits = sum(
            1 for _ in range(2000)
            if json.loads(roll_scum_synthetic_chance("npc"))["has_ability"]
        )
        rate = hits / 2000
        assert 0.01 <= rate <= 0.10, f"NPC synthetic rate {rate:.1%} outside expected 1–10%"

    def test_probability_roughly_correct_playbook(self):
        hits = sum(
            1 for _ in range(2000)
            if json.loads(roll_scum_synthetic_chance("playbook_random"))["has_ability"]
        )
        rate = hits / 2000
        assert 0.07 <= rate <= 0.22, f"Playbook synthetic rate {rate:.1%} outside expected 7–22%"


# ─── Traveller droid NPC profiles ────────────────────────────────────────────

class TestTravellerDroidProfile:

    def test_required_fields_present(self):
        required = [
            "type", "purpose", "legal_status", "personality_emergence",
            "physical_condition", "behavioral_restriction", "hook", "mechanic_note",
        ]
        for _ in range(10):
            d = json.loads(get_traveller_droid_profile())
            for field in required:
                assert field in d, f"Missing field: {field}"

    def test_type_label(self):
        d = json.loads(get_traveller_droid_profile())
        assert d["type"] == "Traveller Droid NPC"

    def test_purpose_has_class_and_description(self):
        for _ in range(20):
            d = json.loads(get_traveller_droid_profile())
            p = d["purpose"]
            assert "class" in p
            assert "description" in p

    def test_legal_status_has_status_and_note(self):
        for _ in range(20):
            d = json.loads(get_traveller_droid_profile())
            ls = d["legal_status"]
            assert "status" in ls
            assert "note" in ls

    def test_personality_has_emergence_and_note(self):
        for _ in range(20):
            d = json.loads(get_traveller_droid_profile())
            pe = d["personality_emergence"]
            assert "emergence" in pe
            assert "note" in pe

    def test_behavioral_restriction_has_level_and_note(self):
        for _ in range(20):
            d = json.loads(get_traveller_droid_profile())
            br = d["behavioral_restriction"]
            assert "level" in br
            assert "note" in br

    def test_hook_from_pool(self):
        for _ in range(50):
            d = json.loads(get_traveller_droid_profile())
            assert d["hook"] in TRAVELLER_DROID_HOOKS

    def test_mechanic_note_mentions_psi(self):
        d = json.loads(get_traveller_droid_profile())
        assert "PSI" in d["mechanic_note"]

    def test_purpose_filter_medical(self):
        for _ in range(10):
            d = json.loads(get_traveller_droid_profile(purpose="medical"))
            assert "medical" in d["purpose"]["class"]

    def test_purpose_filter_security(self):
        for _ in range(10):
            d = json.loads(get_traveller_droid_profile(purpose="security"))
            assert "security" in d["purpose"]["class"]

    def test_purpose_filter_labor(self):
        d = json.loads(get_traveller_droid_profile(purpose="labor"))
        assert "labor" in d["purpose"]["class"]

    def test_purpose_filter_cargo_alias(self):
        d = json.loads(get_traveller_droid_profile(purpose="cargo"))
        assert "labor" in d["purpose"]["class"]

    def test_purpose_filter_companion(self):
        d = json.loads(get_traveller_droid_profile(purpose="companion"))
        assert "companion" in d["purpose"]["class"]

    def test_unknown_purpose_falls_back_to_random(self):
        d = json.loads(get_traveller_droid_profile(purpose="jedi_knight"))
        assert "purpose" in d  # falls back gracefully

    def test_results_vary_without_purpose(self):
        purposes = {
            json.loads(get_traveller_droid_profile())["purpose"]["class"]
            for _ in range(30)
        }
        assert len(purposes) > 3, "Purpose not varying across 30 rolls"


# ─── Traveller droid chance roll ─────────────────────────────────────────────

class TestTravellerDroidChance:

    def test_all_contexts_work(self):
        for ctx in ["tl_low", "tl_medium", "tl_high", "tl_very_high"]:
            r = json.loads(roll_traveller_droid_chance(ctx))
            assert "is_droid" in r
            assert r["threshold"] == TRAVELLER_DROID_THRESHOLDS[ctx]

    def test_threshold_ordering(self):
        t = TRAVELLER_DROID_THRESHOLDS
        assert t["tl_low"] < t["tl_medium"] < t["tl_high"] < t["tl_very_high"]

    def test_next_step_when_droid(self):
        for _ in range(500):
            r = json.loads(roll_traveller_droid_chance("tl_very_high"))
            if r["is_droid"]:
                assert "next_step" in r
                assert "get_traveller_droid_profile" in r["next_step"]
                break

    def test_note_always_present(self):
        for _ in range(20):
            r = json.loads(roll_traveller_droid_chance("tl_medium"))
            assert "note" in r

    def test_probability_tl_low_rare(self):
        hits = sum(
            1 for _ in range(1000)
            if json.loads(roll_traveller_droid_chance("tl_low"))["is_droid"]
        )
        rate = hits / 1000
        assert rate <= 0.07, f"TL-low droid rate {rate:.1%} too high"

    def test_probability_tl_very_high_common(self):
        hits = sum(
            1 for _ in range(1000)
            if json.loads(roll_traveller_droid_chance("tl_very_high"))["is_droid"]
        )
        rate = hits / 1000
        assert rate >= 0.50, f"TL-very-high droid rate {rate:.1%} too low"


# ─── Traveller AI system profiles ────────────────────────────────────────────

class TestTravellerAiProfile:

    def test_required_fields_present(self):
        required = [
            "type", "installation_type", "capability_tier", "personality_level",
            "operational_age", "hook", "autonomous_flag", "legal_note",
        ]
        for _ in range(10):
            ai = json.loads(get_traveller_ai_profile())
            for field in required:
                assert field in ai, f"Missing field: {field}"

    def test_type_label(self):
        ai = json.loads(get_traveller_ai_profile())
        assert ai["type"] == "Traveller AI System"

    def test_autonomous_flag_matches_capability(self):
        for _ in range(200):
            ai = json.loads(get_traveller_ai_profile())
            if "autonomous" in ai["capability_tier"]:
                assert ai["autonomous_flag"] is True
            else:
                assert ai["autonomous_flag"] is False

    def test_capability_always_valid(self):
        for _ in range(100):
            ai = json.loads(get_traveller_ai_profile())
            assert ai["capability_tier"] in _AI_CAPABILITY_LEVELS

    def test_personality_always_valid(self):
        for _ in range(100):
            ai = json.loads(get_traveller_ai_profile())
            assert ai["personality_level"] in TRAVELLER_AI_PERSONALITY_LEVELS

    def test_hook_from_pool(self):
        for _ in range(50):
            ai = json.loads(get_traveller_ai_profile())
            assert ai["hook"] in TRAVELLER_AI_HOOKS

    def test_operational_age_has_age_and_drift(self):
        for _ in range(20):
            ai = json.loads(get_traveller_ai_profile())
            age = ai["operational_age"]
            assert "age" in age
            assert "drift" in age

    def test_installation_alias_ship(self):
        for _ in range(5):
            ai = json.loads(get_traveller_ai_profile(installation_type="ship"))
            assert "ship" in ai["installation_type"].lower() or "liner" in ai["installation_type"].lower()

    def test_installation_alias_home(self):
        ai = json.loads(get_traveller_ai_profile(installation_type="home"))
        assert "residence" in ai["installation_type"].lower() or "habitat" in ai["installation_type"].lower()

    def test_installation_alias_starport(self):
        ai = json.loads(get_traveller_ai_profile(installation_type="starport"))
        assert "starport" in ai["installation_type"].lower()

    def test_installation_alias_smart_home(self):
        ai = json.loads(get_traveller_ai_profile(installation_type="smart home"))
        assert "residence" in ai["installation_type"].lower() or "habitat" in ai["installation_type"].lower()

    def test_residence_skews_toward_basic(self):
        """Private residences should rarely have autonomous AI."""
        autonomous_count = 0
        for _ in range(200):
            ai = json.loads(get_traveller_ai_profile(installation_type="home"))
            if ai["autonomous_flag"]:
                autonomous_count += 1
        rate = autonomous_count / 200
        assert rate <= 0.05, f"Residence autonomous rate {rate:.1%} too high"

    def test_military_skews_toward_higher_capability(self):
        """Military installations should have higher average capability."""
        high_cap_count = 0
        for _ in range(200):
            ai = json.loads(get_traveller_ai_profile(installation_type="military"))
            if ai["capability_tier"] in [
                "genuine intelligence — opinions, preferences, something that functions like curiosity",
                "autonomous intelligence — open-ended reasoning; legally restricted by Imperial statute",
            ]:
                high_cap_count += 1
        rate = high_cap_count / 200
        assert rate >= 0.30, f"Military high-capability rate {rate:.1%} too low"

    def test_legal_note_present_and_non_empty(self):
        for _ in range(20):
            ai = json.loads(get_traveller_ai_profile())
            assert isinstance(ai["legal_note"], str)
            assert len(ai["legal_note"]) > 20

    def test_all_installation_types_have_weight_table(self):
        for install in TRAVELLER_AI_INSTALLATION_TYPES:
            assert install in _AI_CAPABILITY_WEIGHTS, f"Missing weight table for: {install}"

    def test_all_weight_tables_correct_length(self):
        for install, weights in _AI_CAPABILITY_WEIGHTS.items():
            assert len(weights) == len(_AI_CAPABILITY_LEVELS), (
                f"{install} has {len(weights)} weights, expected {len(_AI_CAPABILITY_LEVELS)}"
            )

    def test_installation_type_varies_randomly(self):
        installs = {
            json.loads(get_traveller_ai_profile())["installation_type"]
            for _ in range(30)
        }
        assert len(installs) > 4, "Installation type not varying"


# ─── Traveller auxiliary AI profiles ─────────────────────────────────────────

class TestTravellerAuxiliaryProfile:

    def test_required_fields_present(self):
        required = ["type", "purpose", "personality", "hook", "capability_ceiling"]
        for _ in range(10):
            aux = json.loads(get_traveller_auxiliary_profile())
            for field in required:
                assert field in aux, f"Missing field: {field}"

    def test_type_label(self):
        aux = json.loads(get_traveller_auxiliary_profile())
        assert aux["type"] == "Traveller Auxiliary AI"

    def test_purpose_has_purpose_and_capability_note(self):
        for _ in range(20):
            aux = json.loads(get_traveller_auxiliary_profile())
            p = aux["purpose"]
            assert "purpose" in p
            assert "capability_note" in p
            assert len(p["capability_note"]) > 20

    def test_personality_has_level_and_note(self):
        for _ in range(20):
            aux = json.loads(get_traveller_auxiliary_profile())
            pn = aux["personality"]
            assert "level" in pn
            assert "note" in pn

    def test_hook_from_pool(self):
        for _ in range(50):
            aux = json.loads(get_traveller_auxiliary_profile())
            assert aux["hook"] in TRAVELLER_AUXILIARY_HOOKS

    def test_capability_ceiling_is_string(self):
        aux = json.loads(get_traveller_auxiliary_profile())
        assert isinstance(aux["capability_ceiling"], str)
        assert len(aux["capability_ceiling"]) > 30

    def test_purpose_alias_shuttle(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="shuttle"))
        assert "shuttle" in aux["purpose"]["purpose"].lower()

    def test_purpose_alias_home(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="home"))
        assert "habitat" in aux["purpose"]["purpose"].lower() or "smart home" in aux["purpose"]["purpose"].lower()

    def test_purpose_alias_cargo(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="cargo"))
        assert "cargo" in aux["purpose"]["purpose"].lower()

    def test_purpose_alias_medical(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="medical"))
        assert "medical" in aux["purpose"]["purpose"].lower()

    def test_purpose_alias_comms(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="comms"))
        assert "communications" in aux["purpose"]["purpose"].lower()

    def test_purpose_alias_security(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="security"))
        assert "security" in aux["purpose"]["purpose"].lower()

    def test_unknown_purpose_falls_back_to_random(self):
        aux = json.loads(get_traveller_auxiliary_profile(purpose="warp_drive"))
        assert "purpose" in aux

    def test_purpose_varies_without_argument(self):
        purposes = {
            json.loads(get_traveller_auxiliary_profile())["purpose"]["purpose"]
            for _ in range(30)
        }
        assert len(purposes) > 3, "Auxiliary purpose not varying"


# ─── Tool schemas ─────────────────────────────────────────────────────────────

class TestToolSchemas:

    def _validate(self, schema, name):
        assert schema["name"] == name
        assert "description" in schema
        assert len(schema["description"]) > 20
        assert "input_schema" in schema
        assert schema["input_schema"]["type"] == "object"
        assert "required" in schema["input_schema"]

    def test_stardancer_schema(self):
        self._validate(STARDANCER_TOOL_SCHEMA, "get_stardancer_profile")

    def test_stardancer_schema_no_required_params(self):
        assert STARDANCER_TOOL_SCHEMA["input_schema"]["required"] == []

    def test_stardancer_schema_mentions_firefly(self):
        assert "Firefly" in STARDANCER_TOOL_SCHEMA["description"]

    def test_synthetic_chance_schema(self):
        self._validate(SCUM_SYNTHETIC_CHANCE_TOOL_SCHEMA, "roll_scum_synthetic_chance")

    def test_synthetic_chance_schema_requires_context(self):
        assert "context" in SCUM_SYNTHETIC_CHANCE_TOOL_SCHEMA["input_schema"]["required"]

    def test_synthetic_chance_schema_context_enum(self):
        enum = SCUM_SYNTHETIC_CHANCE_TOOL_SCHEMA["input_schema"]["properties"]["context"]["enum"]
        assert set(enum) == set(SCUM_SYNTHETIC_THRESHOLDS.keys())

    def test_droid_schema(self):
        self._validate(TRAVELLER_DROID_TOOL_SCHEMA, "get_traveller_droid_profile")

    def test_droid_schema_no_required_params(self):
        assert TRAVELLER_DROID_TOOL_SCHEMA["input_schema"]["required"] == []

    def test_droid_chance_schema(self):
        self._validate(TRAVELLER_DROID_CHANCE_TOOL_SCHEMA, "roll_traveller_droid_chance")

    def test_droid_chance_schema_requires_context(self):
        assert "context" in TRAVELLER_DROID_CHANCE_TOOL_SCHEMA["input_schema"]["required"]

    def test_droid_chance_schema_context_enum(self):
        enum = TRAVELLER_DROID_CHANCE_TOOL_SCHEMA["input_schema"]["properties"]["context"]["enum"]
        assert set(enum) == set(TRAVELLER_DROID_THRESHOLDS.keys())

    def test_ai_schema(self):
        self._validate(TRAVELLER_AI_TOOL_SCHEMA, "get_traveller_ai_profile")

    def test_ai_schema_no_required_params(self):
        assert TRAVELLER_AI_TOOL_SCHEMA["input_schema"]["required"] == []

    def test_ai_schema_mentions_smart_home(self):
        assert "smart home" in TRAVELLER_AI_TOOL_SCHEMA["description"].lower() or \
               "home" in TRAVELLER_AI_TOOL_SCHEMA["description"].lower()

    def test_auxiliary_schema(self):
        self._validate(TRAVELLER_AUXILIARY_TOOL_SCHEMA, "get_traveller_auxiliary_profile")

    def test_auxiliary_schema_no_required_params(self):
        assert TRAVELLER_AUXILIARY_TOOL_SCHEMA["input_schema"]["required"] == []

    def test_auxiliary_schema_mentions_shuttle(self):
        assert "shuttle" in TRAVELLER_AUXILIARY_TOOL_SCHEMA["description"].lower()
