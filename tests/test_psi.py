"""
Tests for lib/psi.py — pure Python logic only, no API calls.

Covers all three games:
  - Traveller: talent pools, get_traveller_psi_profile, rarity roll
  - Scum & Villainy: Ur-web/artifact pools, get_mystic_profile, rarity roll
  - Firefly: Reader distinction/complication/asset pools, get_reader_profile, rarity roll
  - Shared: dispatcher, all six tool schemas
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from lib.psi import (
    # Traveller data
    TRAVELLER_TALENTS,
    TRAVELLER_DISCOVERY_HOOKS,
    TRAVELLER_STIGMA_HOOKS,
    TRAVELLER_PSI_THRESHOLDS,
    # Traveller functions
    get_traveller_psi_profile,
    roll_traveller_psi_chance,
    # Scum data
    SCUM_UR_WEB_CONNECTIONS,
    SCUM_UR_ARTIFACTS,
    SCUM_MYSTIC_ABILITY_HOOKS,
    SCUM_PSI_THRESHOLDS,
    # Scum functions
    get_mystic_profile,
    roll_scum_psi_chance,
    # Firefly data
    FIREFLY_READER_DISTINCTIONS,
    FIREFLY_READER_COMPLICATIONS,
    FIREFLY_ALLIANCE_THREAT_LEVELS,
    FIREFLY_READER_ASSETS,
    FIREFLY_PSI_THRESHOLDS,
    # Firefly functions
    get_reader_profile,
    roll_firefly_psi_chance,
    # Shared
    get_psi_profile,
    # Schemas
    TRAVELLER_PSI_TOOL_SCHEMA,
    TRAVELLER_PSI_CHANCE_TOOL_SCHEMA,
    SCUM_MYSTIC_TOOL_SCHEMA,
    SCUM_PSI_CHANCE_TOOL_SCHEMA,
    FIREFLY_READER_TOOL_SCHEMA,
    FIREFLY_PSI_CHANCE_TOOL_SCHEMA,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — talent pool structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestTravellerTalents:
    def test_six_talents_exist(self):
        expected = {"Telepathy", "Clairvoyance", "Telekinesis", "Teleportation", "Awareness", "Special"}
        assert set(TRAVELLER_TALENTS.keys()) == expected

    def test_each_talent_has_description(self):
        for name, talent in TRAVELLER_TALENTS.items():
            assert "description" in talent, f"{name} missing description"
            assert len(talent["description"]) > 20, f"{name} description too short"

    def test_each_talent_has_powers(self):
        for name, talent in TRAVELLER_TALENTS.items():
            assert "powers" in talent, f"{name} missing powers"
            assert len(talent["powers"]) >= 2, f"{name} has fewer than 2 powers"

    def test_each_power_has_required_keys(self):
        required = {"name", "psi_cost", "hook"}
        for talent_name, talent in TRAVELLER_TALENTS.items():
            for power in talent["powers"]:
                missing = required - power.keys()
                assert not missing, f"{talent_name}/{power.get('name')} missing keys: {missing}"

    def test_psi_costs_are_non_negative_integers(self):
        for talent_name, talent in TRAVELLER_TALENTS.items():
            for power in talent["powers"]:
                assert isinstance(power["psi_cost"], int), \
                    f"{talent_name}/{power['name']} psi_cost is not int"
                assert power["psi_cost"] >= 0, \
                    f"{talent_name}/{power['name']} psi_cost is negative"

    def test_hooks_are_substantial_strings(self):
        for talent_name, talent in TRAVELLER_TALENTS.items():
            for power in talent["powers"]:
                assert isinstance(power["hook"], str), \
                    f"{talent_name}/{power['name']} hook is not str"
                assert len(power["hook"]) > 20, \
                    f"{talent_name}/{power['name']} hook is too short"

    def test_teleportation_is_most_expensive(self):
        # Teleportation powers should all cost more than basic talents
        tp_costs = [p["psi_cost"] for p in TRAVELLER_TALENTS["Teleportation"]["powers"]]
        assert min(tp_costs) >= 3

    def test_awareness_has_zero_cost_power(self):
        # Suspended Animation costs 0 PSI
        awareness_costs = [p["psi_cost"] for p in TRAVELLER_TALENTS["Awareness"]["powers"]]
        assert 0 in awareness_costs


class TestTravellerDiscoveryAndStigma:
    def test_discovery_hooks_non_empty(self):
        assert len(TRAVELLER_DISCOVERY_HOOKS) >= 4

    def test_each_discovery_has_required_keys(self):
        required = {"method", "description", "hook"}
        for d in TRAVELLER_DISCOVERY_HOOKS:
            missing = required - d.keys()
            assert not missing, f"Discovery {d.get('method')} missing keys: {missing}"

    def test_discovery_methods_are_unique(self):
        methods = [d["method"] for d in TRAVELLER_DISCOVERY_HOOKS]
        assert len(methods) == len(set(methods)), "Duplicate discovery methods"

    def test_stigma_hooks_non_empty(self):
        assert len(TRAVELLER_STIGMA_HOOKS) >= 4

    def test_stigma_hooks_are_strings(self):
        for s in TRAVELLER_STIGMA_HOOKS:
            assert isinstance(s, str) and len(s) > 20


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — get_traveller_psi_profile
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetTravellerPsiProfile:
    def test_returns_valid_json(self):
        result = get_traveller_psi_profile()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(get_traveller_psi_profile())
        for key in ("talent", "talent_description", "powers", "discovery", "social_situation", "note"):
            assert key in data, f"Missing key: {key}"

    def test_talent_is_valid(self):
        for _ in range(20):
            data = json.loads(get_traveller_psi_profile())
            assert data["talent"] in TRAVELLER_TALENTS

    def test_powers_count_is_two_or_three(self):
        for _ in range(20):
            data = json.loads(get_traveller_psi_profile())
            assert 2 <= len(data["powers"]) <= 3, \
                f"Expected 2-3 powers, got {len(data['powers'])}"

    def test_each_power_has_required_keys(self):
        data = json.loads(get_traveller_psi_profile())
        for power in data["powers"]:
            assert "name" in power
            assert "psi_cost" in power
            assert "hook" in power

    def test_discovery_has_required_keys(self):
        data = json.loads(get_traveller_psi_profile())
        for key in ("method", "description", "hook"):
            assert key in data["discovery"], f"Discovery missing key: {key}"

    def test_social_situation_is_non_empty_string(self):
        data = json.loads(get_traveller_psi_profile())
        assert isinstance(data["social_situation"], str)
        assert len(data["social_situation"]) > 20

    def test_returns_variety_across_calls(self):
        seen = set()
        for _ in range(30):
            data = json.loads(get_traveller_psi_profile())
            seen.add(data["talent"])
        assert len(seen) >= 3, "Talent selection shows no variety"

    def test_cheapest_power_always_included(self):
        # The function always includes the lowest-cost power from the talent
        for _ in range(20):
            data = json.loads(get_traveller_psi_profile())
            talent = TRAVELLER_TALENTS[data["talent"]]
            min_cost = min(p["psi_cost"] for p in talent["powers"])
            returned_costs = [p["psi_cost"] for p in data["powers"]]
            assert min_cost in returned_costs, \
                f"Cheapest power (cost {min_cost}) not in returned powers"


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — rarity roll
# ═══════════════════════════════════════════════════════════════════════════════

class TestTravellerPsiChance:
    def test_all_contexts_defined(self):
        expected = {"imperial", "frontier", "zhodani_prole", "zhodani_noble", "droyne"}
        assert set(TRAVELLER_PSI_THRESHOLDS.keys()) == expected

    def test_thresholds_are_positive_integers(self):
        for ctx, val in TRAVELLER_PSI_THRESHOLDS.items():
            assert isinstance(val, int) and val > 0, f"{ctx} threshold invalid"

    def test_droyne_is_100(self):
        assert TRAVELLER_PSI_THRESHOLDS["droyne"] == 100

    def test_zhodani_noble_above_90(self):
        assert TRAVELLER_PSI_THRESHOLDS["zhodani_noble"] >= 90

    def test_imperial_below_frontier(self):
        assert TRAVELLER_PSI_THRESHOLDS["imperial"] < TRAVELLER_PSI_THRESHOLDS["frontier"]

    def test_returns_valid_json(self):
        result = roll_traveller_psi_chance("imperial")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_ability_is_bool(self):
        data = json.loads(roll_traveller_psi_chance("frontier"))
        assert isinstance(data["has_ability"], bool)

    def test_rolled_is_in_range(self):
        for _ in range(50):
            data = json.loads(roll_traveller_psi_chance("imperial"))
            assert 1 <= data["rolled"] <= 100

    def test_threshold_string_format(self):
        data = json.loads(roll_traveller_psi_chance("frontier"))
        assert data["threshold"].endswith("%")

    def test_next_step_present_when_has_ability(self):
        # Run until we get a hit (droyne is always true)
        data = json.loads(roll_traveller_psi_chance("droyne"))
        assert data["has_ability"] is True
        assert "next_step" in data
        assert "get_traveller_psi_profile" in data["next_step"]

    def test_next_step_absent_when_no_ability(self):
        # Run until we get a miss — use imperial (97% miss rate)
        for _ in range(200):
            data = json.loads(roll_traveller_psi_chance("imperial"))
            if not data["has_ability"]:
                assert "next_step" not in data
                return
        pytest.skip("Could not get a miss in 200 rolls — statistically unlikely")

    def test_invalid_context_returns_error(self):
        data = json.loads(roll_traveller_psi_chance("martian"))
        assert "error" in data
        assert "valid_contexts" in data

    def test_droyne_always_has_ability(self):
        for _ in range(20):
            data = json.loads(roll_traveller_psi_chance("droyne"))
            assert data["has_ability"] is True

    def test_probability_roughly_correct_imperial(self):
        hits = sum(json.loads(roll_traveller_psi_chance("imperial"))["has_ability"] for _ in range(1000))
        assert 0 <= hits <= 40, f"Imperial: expected ~3%, got {hits/10:.1f}%"

    def test_probability_roughly_correct_zhodani_noble(self):
        hits = sum(json.loads(roll_traveller_psi_chance("zhodani_noble"))["has_ability"] for _ in range(500))
        assert hits >= 400, f"Zhodani noble: expected ~95%, got {hits/5:.1f}%"


# ═══════════════════════════════════════════════════════════════════════════════
# SCUM & VILLAINY — data pool structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestScumDataPools:
    def test_ur_web_connections_non_empty(self):
        assert len(SCUM_UR_WEB_CONNECTIONS) >= 4

    def test_each_connection_has_required_keys(self):
        required = {"flavor", "description", "hook"}
        for c in SCUM_UR_WEB_CONNECTIONS:
            missing = required - c.keys()
            assert not missing, f"Connection {c.get('flavor')} missing keys: {missing}"

    def test_ur_artifacts_non_empty(self):
        assert len(SCUM_UR_ARTIFACTS) >= 4

    def test_each_artifact_has_required_keys(self):
        required = {"name", "property", "complication"}
        for a in SCUM_UR_ARTIFACTS:
            missing = required - a.keys()
            assert not missing, f"Artifact {a.get('name')} missing keys: {missing}"

    def test_mystic_ability_hooks_has_eight(self):
        # One per Mystic special ability
        assert len(SCUM_MYSTIC_ABILITY_HOOKS) == 8

    def test_each_ability_hook_has_required_keys(self):
        for entry in SCUM_MYSTIC_ABILITY_HOOKS:
            assert "ability" in entry
            assert "hook" in entry
            assert len(entry["hook"]) > 20

    def test_ability_names_are_unique(self):
        names = [e["ability"] for e in SCUM_MYSTIC_ABILITY_HOOKS]
        assert len(names) == len(set(names))


# ═══════════════════════════════════════════════════════════════════════════════
# SCUM & VILLAINY — get_mystic_profile
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetMysticProfile:
    def test_returns_valid_json(self):
        data = json.loads(get_mystic_profile())
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(get_mystic_profile())
        for key in ("playbook", "ur_web_connection", "suggested_abilities", "artifact", "note"):
            assert key in data, f"Missing key: {key}"

    def test_playbook_is_mystic(self):
        data = json.loads(get_mystic_profile())
        assert data["playbook"] == "Mystic"

    def test_ur_web_connection_has_required_keys(self):
        data = json.loads(get_mystic_profile())
        for key in ("flavor", "description", "hook"):
            assert key in data["ur_web_connection"]

    def test_suggested_abilities_count_is_three(self):
        for _ in range(10):
            data = json.loads(get_mystic_profile())
            assert len(data["suggested_abilities"]) == 3

    def test_each_ability_has_required_keys(self):
        data = json.loads(get_mystic_profile())
        for ability in data["suggested_abilities"]:
            assert "ability" in ability
            assert "hook" in ability

    def test_artifact_has_required_keys(self):
        data = json.loads(get_mystic_profile())
        for key in ("name", "property", "complication"):
            assert key in data["artifact"]

    def test_returns_variety_across_calls(self):
        seen_connections = set()
        seen_artifacts = set()
        for _ in range(20):
            data = json.loads(get_mystic_profile())
            seen_connections.add(data["ur_web_connection"]["flavor"])
            seen_artifacts.add(data["artifact"]["name"])
        assert len(seen_connections) >= 2, "Ur-web connections show no variety"
        assert len(seen_artifacts) >= 2, "Artifacts show no variety"

    def test_abilities_are_no_duplicates_within_result(self):
        for _ in range(20):
            data = json.loads(get_mystic_profile())
            names = [a["ability"] for a in data["suggested_abilities"]]
            assert len(names) == len(set(names)), "Duplicate abilities in single result"


# ═══════════════════════════════════════════════════════════════════════════════
# SCUM & VILLAINY — rarity roll
# ═══════════════════════════════════════════════════════════════════════════════

class TestScumPsiChance:
    def test_contexts_defined(self):
        assert "npc" in SCUM_PSI_THRESHOLDS
        assert "notable_npc" in SCUM_PSI_THRESHOLDS

    def test_notable_npc_higher_than_npc(self):
        assert SCUM_PSI_THRESHOLDS["notable_npc"] > SCUM_PSI_THRESHOLDS["npc"]

    def test_returns_valid_json(self):
        data = json.loads(roll_scum_psi_chance("npc"))
        assert isinstance(data, dict)

    def test_has_ability_is_bool(self):
        data = json.loads(roll_scum_psi_chance("npc"))
        assert isinstance(data["has_ability"], bool)

    def test_rolled_in_range(self):
        for _ in range(30):
            data = json.loads(roll_scum_psi_chance("npc"))
            assert 1 <= data["rolled"] <= 100

    def test_next_step_mentions_get_mystic_profile(self):
        # Force a hit by running enough times or using monkeypatch
        # Notable NPC is 10% — run 200 times to almost certainly get one
        for _ in range(200):
            data = json.loads(roll_scum_psi_chance("notable_npc"))
            if data["has_ability"]:
                assert "get_mystic_profile" in data["next_step"]
                return
        pytest.skip("No hit in 200 rolls — statistically unlikely at 10%")

    def test_invalid_context_returns_error(self):
        data = json.loads(roll_scum_psi_chance("player_character"))
        assert "error" in data

    def test_probability_roughly_correct_npc(self):
        hits = sum(json.loads(roll_scum_psi_chance("npc"))["has_ability"] for _ in range(1000))
        assert 0 <= hits <= 80, f"NPC: expected ~5%, got {hits/10:.1f}%"

    def test_probability_roughly_correct_notable_npc(self):
        hits = sum(json.loads(roll_scum_psi_chance("notable_npc"))["has_ability"] for _ in range(1000))
        assert 50 <= hits <= 160, f"Notable NPC: expected ~10%, got {hits/10:.1f}%"


# ═══════════════════════════════════════════════════════════════════════════════
# FIREFLY — data pool structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestFireflyDataPools:
    def test_distinctions_count(self):
        assert len(FIREFLY_READER_DISTINCTIONS) >= 4

    def test_each_distinction_has_required_keys(self):
        required = {"name", "description", "hinder_hook"}
        for d in FIREFLY_READER_DISTINCTIONS:
            missing = required - d.keys()
            assert not missing, f"Distinction {d.get('name')} missing keys: {missing}"

    def test_complications_count(self):
        assert len(FIREFLY_READER_COMPLICATIONS) >= 4

    def test_each_complication_has_required_keys(self):
        required = {"name", "description", "trigger", "expression"}
        for c in FIREFLY_READER_COMPLICATIONS:
            missing = required - c.keys()
            assert not missing, f"Complication {c.get('name')} missing keys: {missing}"

    def test_threat_levels_count(self):
        assert len(FIREFLY_ALLIANCE_THREAT_LEVELS) >= 3

    def test_each_threat_has_required_keys(self):
        required = {"level", "description", "risk"}
        for t in FIREFLY_ALLIANCE_THREAT_LEVELS:
            missing = required - t.keys()
            assert not missing, f"Threat {t.get('level')} missing keys: {missing}"

    def test_assets_count(self):
        assert len(FIREFLY_READER_ASSETS) >= 4

    def test_each_asset_has_required_keys(self):
        required = {"name", "description", "hook"}
        for a in FIREFLY_READER_ASSETS:
            missing = required - a.keys()
            assert not missing, f"Asset {a.get('name')} missing keys: {missing}"

    def test_threat_levels_are_escalating_in_name(self):
        # The four levels should be meaningfully distinct — not all the same
        level_names = [t["level"] for t in FIREFLY_ALLIANCE_THREAT_LEVELS]
        assert len(set(level_names)) == len(level_names), "Duplicate threat level names"


# ═══════════════════════════════════════════════════════════════════════════════
# FIREFLY — get_reader_profile
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetReaderProfile:
    def test_returns_valid_json(self):
        data = json.loads(get_reader_profile())
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(get_reader_profile())
        for key in ("reader_distinction", "complications", "alliance_threat", "signature_assets", "note"):
            assert key in data, f"Missing key: {key}"

    def test_distinction_has_required_keys(self):
        data = json.loads(get_reader_profile())
        for key in ("name", "description", "hinder_hook"):
            assert key in data["reader_distinction"]

    def test_complications_count_is_two(self):
        for _ in range(10):
            data = json.loads(get_reader_profile())
            assert len(data["complications"]) == 2

    def test_each_complication_has_required_keys(self):
        data = json.loads(get_reader_profile())
        for comp in data["complications"]:
            for key in ("name", "description", "trigger", "expression"):
                assert key in comp

    def test_complications_are_distinct(self):
        for _ in range(10):
            data = json.loads(get_reader_profile())
            names = [c["name"] for c in data["complications"]]
            assert len(names) == len(set(names)), "Duplicate complications in single result"

    def test_alliance_threat_has_required_keys(self):
        data = json.loads(get_reader_profile())
        for key in ("level", "description", "risk"):
            assert key in data["alliance_threat"]

    def test_signature_assets_count_is_two(self):
        for _ in range(10):
            data = json.loads(get_reader_profile())
            assert len(data["signature_assets"]) == 2

    def test_signature_assets_are_distinct(self):
        for _ in range(10):
            data = json.loads(get_reader_profile())
            names = [a["name"] for a in data["signature_assets"]]
            assert len(names) == len(set(names)), "Duplicate assets in single result"

    def test_returns_variety_across_calls(self):
        seen_distinctions = set()
        seen_threats = set()
        for _ in range(20):
            data = json.loads(get_reader_profile())
            seen_distinctions.add(data["reader_distinction"]["name"])
            seen_threats.add(data["alliance_threat"]["level"])
        assert len(seen_distinctions) >= 2, "Distinctions show no variety"
        assert len(seen_threats) >= 2, "Threat levels show no variety"


# ═══════════════════════════════════════════════════════════════════════════════
# FIREFLY — rarity roll
# ═══════════════════════════════════════════════════════════════════════════════

class TestFireflyPsiChance:
    def test_contexts_defined(self):
        assert "character" in FIREFLY_PSI_THRESHOLDS
        assert "academy_connection" in FIREFLY_PSI_THRESHOLDS

    def test_academy_connection_higher_than_character(self):
        assert FIREFLY_PSI_THRESHOLDS["academy_connection"] > FIREFLY_PSI_THRESHOLDS["character"]

    def test_character_threshold_is_very_low(self):
        # Readers are very rare — threshold should be <= 5%
        assert FIREFLY_PSI_THRESHOLDS["character"] <= 5

    def test_returns_valid_json(self):
        data = json.loads(roll_firefly_psi_chance("character"))
        assert isinstance(data, dict)

    def test_has_ability_is_bool(self):
        data = json.loads(roll_firefly_psi_chance("character"))
        assert isinstance(data["has_ability"], bool)

    def test_rolled_in_range(self):
        for _ in range(30):
            data = json.loads(roll_firefly_psi_chance("character"))
            assert 1 <= data["rolled"] <= 100

    def test_next_step_mentions_get_reader_profile(self):
        # academy_connection is 20% — run enough times to hit
        for _ in range(200):
            data = json.loads(roll_firefly_psi_chance("academy_connection"))
            if data["has_ability"]:
                assert "get_reader_profile" in data["next_step"]
                return
        pytest.skip("No hit in 200 rolls at 20% — statistically very unlikely")

    def test_invalid_context_returns_error(self):
        data = json.loads(roll_firefly_psi_chance("alliance_soldier"))
        assert "error" in data

    def test_probability_roughly_correct_character(self):
        hits = sum(json.loads(roll_firefly_psi_chance("character"))["has_ability"] for _ in range(1000))
        assert 0 <= hits <= 40, f"Character: expected ~2%, got {hits/10:.1f}%"

    def test_probability_roughly_correct_academy(self):
        hits = sum(json.loads(roll_firefly_psi_chance("academy_connection"))["has_ability"] for _ in range(1000))
        assert 100 <= hits <= 310, f"Academy connection: expected ~20%, got {hits/10:.1f}%"


# ═══════════════════════════════════════════════════════════════════════════════
# Shared dispatcher
# ═══════════════════════════════════════════════════════════════════════════════

class TestDispatcher:
    def test_traveller_returns_talent(self):
        data = json.loads(get_psi_profile("traveller"))
        assert "talent" in data

    def test_scum_returns_playbook(self):
        data = json.loads(get_psi_profile("scum"))
        assert data.get("playbook") == "Mystic"

    def test_firefly_returns_distinction(self):
        data = json.loads(get_psi_profile("firefly"))
        assert "reader_distinction" in data

    def test_unknown_game_returns_error(self):
        data = json.loads(get_psi_profile("dnd"))
        assert "error" in data

    def test_unknown_game_error_lists_valid_games(self):
        data = json.loads(get_psi_profile("blades"))
        assert "traveller" in data["error"] or "traveller" in str(data)


# ═══════════════════════════════════════════════════════════════════════════════
# Tool schemas
# ═══════════════════════════════════════════════════════════════════════════════

class TestToolSchemas:
    ALL_SCHEMAS = [
        TRAVELLER_PSI_TOOL_SCHEMA,
        TRAVELLER_PSI_CHANCE_TOOL_SCHEMA,
        SCUM_MYSTIC_TOOL_SCHEMA,
        SCUM_PSI_CHANCE_TOOL_SCHEMA,
        FIREFLY_READER_TOOL_SCHEMA,
        FIREFLY_PSI_CHANCE_TOOL_SCHEMA,
    ]

    def test_all_schemas_have_required_top_level_keys(self):
        for schema in self.ALL_SCHEMAS:
            assert "name" in schema, f"{schema} missing 'name'"
            assert "description" in schema, f"{schema} missing 'description'"
            assert "input_schema" in schema, f"{schema} missing 'input_schema'"

    def test_schema_names_are_unique(self):
        names = [s["name"] for s in self.ALL_SCHEMAS]
        assert len(names) == len(set(names)), "Duplicate schema names"

    def test_profile_schemas_have_empty_required(self):
        profile_schemas = [
            TRAVELLER_PSI_TOOL_SCHEMA,
            SCUM_MYSTIC_TOOL_SCHEMA,
            FIREFLY_READER_TOOL_SCHEMA,
        ]
        for schema in profile_schemas:
            required = schema["input_schema"].get("required", [])
            assert required == [], f"{schema['name']} profile schema should have no required params"

    def test_chance_schemas_require_context(self):
        chance_schemas = [
            TRAVELLER_PSI_CHANCE_TOOL_SCHEMA,
            SCUM_PSI_CHANCE_TOOL_SCHEMA,
            FIREFLY_PSI_CHANCE_TOOL_SCHEMA,
        ]
        for schema in chance_schemas:
            assert "context" in schema["input_schema"]["required"], \
                f"{schema['name']} should require 'context'"

    def test_traveller_chance_enum_matches_thresholds(self):
        enum = TRAVELLER_PSI_CHANCE_TOOL_SCHEMA["input_schema"]["properties"]["context"]["enum"]
        assert set(enum) == set(TRAVELLER_PSI_THRESHOLDS.keys())

    def test_scum_chance_enum_matches_thresholds(self):
        enum = SCUM_PSI_CHANCE_TOOL_SCHEMA["input_schema"]["properties"]["context"]["enum"]
        assert set(enum) == set(SCUM_PSI_THRESHOLDS.keys())

    def test_firefly_chance_enum_matches_thresholds(self):
        enum = FIREFLY_PSI_CHANCE_TOOL_SCHEMA["input_schema"]["properties"]["context"]["enum"]
        assert set(enum) == set(FIREFLY_PSI_THRESHOLDS.keys())

    def test_descriptions_are_substantial(self):
        for schema in self.ALL_SCHEMAS:
            assert len(schema["description"]) > 40, \
                f"{schema['name']} description too short"
