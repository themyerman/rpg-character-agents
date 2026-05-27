"""
Tests for deadlands_agent.py and Deadlands gear in lib/gear.py.
Pure Python logic only — no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import deadlands_agent
from agents.deadlands_agent import (
    ARCHETYPES,
    HINDRANCES,
    WEIRD_WEST_HOOKS,
    get_archetype_info,
    roll_hindrance,
    roll_weird_west_hook,
    detect_phase,
)
from lib.gear import (
    _DEADLANDS_GEAR,
    _DEADLANDS_PERSONAL,
    roll_deadlands_gear,
    DEADLANDS_GEAR_TOOL_SCHEMA,
)


# ── ARCHETYPES data ───────────────────────────────────────────────────────────

EXPECTED_ARCHETYPES = [
    "Gunfighter", "Blessed", "Huckster", "Shaman", "Mad Scientist",
    "Harrowed", "Bounty Hunter", "Doc", "Drifter", "Cowboy", "Lawman",
]


class TestArchetypesData:
    def test_all_eleven_archetypes_present(self):
        assert set(ARCHETYPES.keys()) == set(EXPECTED_ARCHETYPES)

    def test_each_archetype_has_required_keys(self):
        required = {"description", "key_attributes", "key_skills", "typical_edges",
                    "typical_hindrances", "arcane_background", "flavor"}
        for name, arch in ARCHETYPES.items():
            missing = required - set(arch.keys())
            assert not missing, f"Archetype '{name}' missing: {missing}"

    def test_description_non_empty(self):
        for name, arch in ARCHETYPES.items():
            assert len(arch["description"]) > 20, f"'{name}' has thin description"

    def test_flavor_non_empty(self):
        for name, arch in ARCHETYPES.items():
            assert len(arch["flavor"]) > 10, f"'{name}' has thin flavor"

    def test_key_skills_non_empty(self):
        for name, arch in ARCHETYPES.items():
            assert len(arch["key_skills"]) >= 3, f"'{name}' has fewer than 3 key skills"

    def test_typical_edges_non_empty(self):
        for name, arch in ARCHETYPES.items():
            assert len(arch["typical_edges"]) >= 2, f"'{name}' has fewer than 2 edges"

    def test_typical_hindrances_non_empty(self):
        for name, arch in ARCHETYPES.items():
            assert len(arch["typical_hindrances"]) >= 2, f"'{name}' has fewer than 2 hindrances"

    def test_arcane_backgrounds_set_correctly(self):
        # Arcane archetypes have non-None arcane_background
        arcane = {"Blessed", "Huckster", "Shaman", "Mad Scientist", "Harrowed"}
        non_arcane = {"Gunfighter", "Bounty Hunter", "Doc", "Drifter", "Cowboy", "Lawman"}
        for name in arcane:
            assert ARCHETYPES[name]["arcane_background"] is not None, \
                f"'{name}' should have an arcane background"
        for name in non_arcane:
            assert ARCHETYPES[name]["arcane_background"] is None, \
                f"'{name}' should have arcane_background=None"

    def test_shaman_has_note_key(self):
        assert "note" in ARCHETYPES["Shaman"], "Shaman archetype missing 'note' key"

    def test_shaman_note_mentions_specific_nations(self):
        note = ARCHETYPES["Shaman"]["note"]
        assert "Sioux" in note or "Cheyenne" in note or "Apache" in note, \
            "Shaman note should reference specific Native nations"

    def test_shaman_note_warns_against_stereotypes(self):
        note = ARCHETYPES["Shaman"]["note"]
        assert len(note) > 100, "Shaman note is too thin"

    def test_gunfighter_is_agility_heavy(self):
        attrs = ARCHETYPES["Gunfighter"]["key_attributes"]
        assert any("Agility" in a for a in attrs)

    def test_blessed_is_spirit_heavy(self):
        attrs = ARCHETYPES["Blessed"]["key_attributes"]
        assert any("Spirit" in a for a in attrs)

    def test_huckster_is_smarts_heavy(self):
        attrs = ARCHETYPES["Huckster"]["key_attributes"]
        assert any("Smarts" in a for a in attrs)


# ── get_archetype_info ────────────────────────────────────────────────────────

class TestGetArchetypeInfo:
    def test_returns_json_string(self):
        result = get_archetype_info("Gunfighter")
        assert isinstance(result, str)
        json.loads(result)  # must not raise

    def test_known_archetype_has_skills(self):
        data = json.loads(get_archetype_info("Doc"))
        assert "key_skills" in data
        assert "typical_edges" in data

    def test_unknown_archetype_returns_error(self):
        data = json.loads(get_archetype_info("Witch"))
        assert "error" in data
        assert "available" in data

    def test_available_list_complete(self):
        data = json.loads(get_archetype_info("Nobody"))
        assert set(data["available"]) == set(EXPECTED_ARCHETYPES)

    def test_tool_in_tools_list(self):
        names = [t["name"] for t in deadlands_agent.TOOLS]
        assert "get_archetype_info" in names


# ── HINDRANCES data ───────────────────────────────────────────────────────────

class TestHindrancesData:
    def test_at_least_20_hindrances(self):
        assert len(HINDRANCES) >= 20

    def test_required_keys(self):
        required = {"name", "severity", "description"}
        for h in HINDRANCES:
            missing = required - set(h.keys())
            assert not missing, f"Hindrance '{h.get('name')}' missing: {missing}"

    def test_severity_values_valid(self):
        valid = {"Major", "Minor"}
        for h in HINDRANCES:
            assert h["severity"] in valid, \
                f"Hindrance '{h['name']}' has invalid severity '{h['severity']}'"

    def test_has_both_major_and_minor(self):
        severities = {h["severity"] for h in HINDRANCES}
        assert "Major" in severities
        assert "Minor" in severities

    def test_descriptions_non_empty(self):
        for h in HINDRANCES:
            assert isinstance(h["description"], str) and len(h["description"]) > 20, \
                f"Hindrance '{h['name']}' has thin description"

    def test_at_least_8_major_hindrances(self):
        majors = [h for h in HINDRANCES if h["severity"] == "Major"]
        assert len(majors) >= 8

    def test_at_least_8_minor_hindrances(self):
        minors = [h for h in HINDRANCES if h["severity"] == "Minor"]
        assert len(minors) >= 8

    def test_code_of_honor_present(self):
        names = {h["name"] for h in HINDRANCES}
        assert "Code of Honor" in names

    def test_wanted_present(self):
        names = {h["name"] for h in HINDRANCES}
        assert any("Wanted" in n for n in names)


# ── roll_hindrance ────────────────────────────────────────────────────────────

class TestRollHindrance:
    def test_returns_json_string(self):
        result = roll_hindrance()
        assert isinstance(result, str)
        json.loads(result)

    def test_has_required_keys(self):
        data = json.loads(roll_hindrance())
        assert "name" in data
        assert "severity" in data
        assert "description" in data

    def test_severity_is_valid(self):
        for _ in range(20):
            data = json.loads(roll_hindrance())
            assert data["severity"] in {"Major", "Minor"}

    def test_returns_variety(self):
        names = set()
        for _ in range(50):
            data = json.loads(roll_hindrance())
            names.add(data["name"])
        assert len(names) >= 5

    def test_tool_in_tools_list(self):
        names = [t["name"] for t in deadlands_agent.TOOLS]
        assert "roll_hindrance" in names


# ── WEIRD_WEST_HOOKS data ─────────────────────────────────────────────────────

class TestWeirdWestHooks:
    def test_at_least_6_hooks(self):
        assert len(WEIRD_WEST_HOOKS) >= 6

    def test_required_keys(self):
        required = {"type", "description", "complications"}
        for hook in WEIRD_WEST_HOOKS:
            missing = required - set(hook.keys())
            assert not missing, f"Hook '{hook.get('type')}' missing: {missing}"

    def test_each_hook_has_3_complications(self):
        for hook in WEIRD_WEST_HOOKS:
            assert len(hook["complications"]) >= 3, \
                f"Hook '{hook['type']}' has fewer than 3 complications"

    def test_bounty_contract_present(self):
        types = {h["type"] for h in WEIRD_WEST_HOOKS}
        assert "Bounty Contract" in types

    def test_haunted_territory_present(self):
        types = {h["type"] for h in WEIRD_WEST_HOOKS}
        assert "Haunted Territory" in types

    def test_ghost_rock_trouble_present(self):
        types = {h["type"] for h in WEIRD_WEST_HOOKS}
        assert "Ghost Rock Trouble" in types

    def test_descriptions_non_empty(self):
        for hook in WEIRD_WEST_HOOKS:
            assert len(hook["description"]) > 20, \
                f"Hook '{hook['type']}' has thin description"

    def test_complications_are_strings(self):
        for hook in WEIRD_WEST_HOOKS:
            for comp in hook["complications"]:
                assert isinstance(comp, str) and len(comp) > 20, \
                    f"Hook '{hook['type']}' has a thin complication"


# ── roll_weird_west_hook ──────────────────────────────────────────────────────

class TestRollWeirdWestHook:
    def test_returns_json_string(self):
        result = roll_weird_west_hook()
        assert isinstance(result, str)
        json.loads(result)

    def test_has_required_keys(self):
        data = json.loads(roll_weird_west_hook())
        assert "job_type" in data
        assert "description" in data
        assert "complication" in data

    def test_returns_variety(self):
        types = set()
        for _ in range(50):
            data = json.loads(roll_weird_west_hook())
            types.add(data["job_type"])
        assert len(types) >= 4

    def test_complication_is_non_empty(self):
        for _ in range(10):
            data = json.loads(roll_weird_west_hook())
            assert len(data["complication"]) > 20

    def test_tool_in_tools_list(self):
        names = [t["name"] for t in deadlands_agent.TOOLS]
        assert "roll_weird_west_hook" in names


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_name_tool(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_archetype_tool(self):
        assert detect_phase("get_archetype_info", set()) == "archetype"

    def test_hindrance_tool(self):
        assert detect_phase("roll_hindrance", set()) == "hindrance"

    def test_hook_tool(self):
        assert detect_phase("roll_weird_west_hook", set()) == "hook"

    def test_gear_tool(self):
        assert detect_phase("roll_deadlands_gear", set()) == "gear"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("roll_something_else", set()) is None


# ── System prompts ────────────────────────────────────────────────────────────

class TestSystemPrompts:
    def test_system_prompt_exists(self):
        assert hasattr(deadlands_agent, "SYSTEM_PROMPT")
        assert len(deadlands_agent.SYSTEM_PROMPT) > 500

    def test_npc_system_prompt_exists(self):
        assert hasattr(deadlands_agent, "NPC_SYSTEM_PROMPT")
        assert len(deadlands_agent.NPC_SYSTEM_PROMPT) > 200

    def test_contact_system_prompt_exists(self):
        assert hasattr(deadlands_agent, "CONTACT_SYSTEM_PROMPT")
        assert len(deadlands_agent.CONTACT_SYSTEM_PROMPT) > 200

    def test_system_prompt_mentions_savage_worlds(self):
        assert "Savage Worlds" in deadlands_agent.SYSTEM_PROMPT

    def test_system_prompt_mentions_hindrances(self):
        assert "Hindrances" in deadlands_agent.SYSTEM_PROMPT or \
               "Hindrance" in deadlands_agent.SYSTEM_PROMPT

    def test_system_prompt_mentions_edges(self):
        assert "Edges" in deadlands_agent.SYSTEM_PROMPT or \
               "Edge" in deadlands_agent.SYSTEM_PROMPT

    def test_contact_prompt_mentions_real_west(self):
        assert "Real West" in deadlands_agent.CONTACT_SYSTEM_PROMPT

    def test_contact_prompt_has_four_truths(self):
        src = deadlands_agent.CONTACT_SYSTEM_PROMPT
        assert "Straightforward" in src
        assert "One Layer Down" in src
        assert "The Real Story" in src
        assert "The Real West" in src

    def test_system_prompt_mentions_reckoning(self):
        assert "Reckoning" in deadlands_agent.SYSTEM_PROMPT or \
               "Reckoners" in deadlands_agent.SYSTEM_PROMPT

    def test_run_includes_all_modes(self):
        import inspect
        source = inspect.getsource(deadlands_agent.run)
        for mode in ("full", "npc", "contact"):
            assert mode in source, f"run() missing mode '{mode}'"


# ── Deadlands gear ────────────────────────────────────────────────────────────

class TestDeadlandsGearStructure:
    def test_all_archetypes_have_gear(self):
        for archetype in EXPECTED_ARCHETYPES:
            assert archetype in _DEADLANDS_GEAR, f"'{archetype}' missing from _DEADLANDS_GEAR"

    def test_each_archetype_has_weapons_and_kit(self):
        for archetype, gear in _DEADLANDS_GEAR.items():
            assert "weapons" in gear, f"'{archetype}' missing 'weapons'"
            assert "kit" in gear, f"'{archetype}' missing 'kit'"
            assert len(gear["weapons"]) >= 1, f"'{archetype}' has no weapons"
            assert len(gear["kit"]) >= 2, f"'{archetype}' has fewer than 2 kit items"

    def test_personal_list_non_empty(self):
        assert len(_DEADLANDS_PERSONAL) >= 8
        for item in _DEADLANDS_PERSONAL:
            assert isinstance(item, str) and item.strip()


class TestDeadlandsGearRoller:
    def _roll(self, archetype):
        return json.loads(roll_deadlands_gear(archetype))

    def test_returns_valid_json(self):
        json.loads(roll_deadlands_gear("Gunfighter"))

    def test_required_keys(self):
        data = self._roll("Doc")
        assert "gear" in data
        assert "note" in data

    def test_gear_has_four_items(self):
        for archetype in EXPECTED_ARCHETYPES:
            data = self._roll(archetype)
            assert len(data["gear"]) == 4, \
                f"'{archetype}': expected 4 items, got {len(data['gear'])}"

    def test_weapon_from_archetype_pool(self):
        for archetype in EXPECTED_ARCHETYPES:
            data = self._roll(archetype)
            weapon = data["gear"][0]
            assert weapon in _DEADLANDS_GEAR[archetype]["weapons"], \
                f"'{archetype}': weapon not in pool"

    def test_personal_item_is_last(self):
        for archetype in EXPECTED_ARCHETYPES:
            data = self._roll(archetype)
            assert data["gear"][-1] in _DEADLANDS_PERSONAL, \
                f"'{archetype}': last item not in personal pool"

    def test_unknown_archetype_fallback(self):
        data = self._roll("Preacher")
        assert len(data["gear"]) == 4

    def test_schema_name_matches(self):
        assert DEADLANDS_GEAR_TOOL_SCHEMA["name"] == "roll_deadlands_gear"

    def test_schema_enum_matches_data(self):
        enum = DEADLANDS_GEAR_TOOL_SCHEMA["input_schema"]["properties"]["archetype_name"]["enum"]
        assert set(enum) == set(_DEADLANDS_GEAR.keys())
