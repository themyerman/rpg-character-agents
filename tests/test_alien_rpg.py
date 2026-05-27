"""
Tests for alien_agent.py and Alien RPG gear in lib/gear.py.
Pure Python logic only — no API calls.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import alien_agent
from agents.alien_agent import (
    ROLES,
    PERSONAL_AGENDAS,
    SCENARIO_HOOKS,
    get_role_info,
    roll_personal_agenda,
    roll_scenario_hook,
    detect_phase,
)
from lib.gear import (
    _ALIEN_GEAR,
    _ALIEN_PERSONAL,
    roll_alien_gear,
    ALIEN_GEAR_TOOL_SCHEMA,
)


# ── ROLES data ────────────────────────────────────────────────────────────────

EXPECTED_ROLES = [
    "Colonial Marine", "Company Agent", "Colonial Marshal",
    "Roughneck", "Scientist", "Pilot", "Medic",
]


class TestRolesData:
    def test_all_seven_roles_present(self):
        assert set(ROLES.keys()) == set(EXPECTED_ROLES)

    def test_each_role_has_required_keys(self):
        required = {"description", "attributes", "key_skills", "career_talents", "flavor"}
        for name, role in ROLES.items():
            missing = required - set(role.keys())
            assert not missing, f"Role '{name}' missing: {missing}"

    def test_attributes_sum_to_12(self):
        for name, role in ROLES.items():
            total = sum(role["attributes"].values())
            assert total == 12, f"Role '{name}' attributes sum to {total}, expected 12"

    def test_attributes_have_four_stats(self):
        expected_stats = {"Strength", "Agility", "Wits", "Empathy"}
        for name, role in ROLES.items():
            assert set(role["attributes"].keys()) == expected_stats, \
                f"Role '{name}' has unexpected attribute names"

    def test_all_attributes_in_range_2_to_5(self):
        for name, role in ROLES.items():
            for stat, val in role["attributes"].items():
                assert 2 <= val <= 5, \
                    f"Role '{name}' {stat}={val} out of range 2–5"

    def test_career_talents_are_tuples(self):
        for name, role in ROLES.items():
            for talent in role["career_talents"]:
                assert len(talent) == 2, \
                    f"Role '{name}' talent {talent!r} is not a 2-tuple"

    def test_flavor_strings_non_empty(self):
        for name, role in ROLES.items():
            assert len(role["flavor"]) > 10, f"Role '{name}' has thin flavor"

    def test_marine_is_strength_and_agility_heavy(self):
        attrs = ROLES["Colonial Marine"]["attributes"]
        assert attrs["Strength"] >= 4
        assert attrs["Agility"] >= 4

    def test_scientist_is_wits_heavy(self):
        attrs = ROLES["Scientist"]["attributes"]
        assert attrs["Wits"] >= 5

    def test_pilot_is_agility_heavy(self):
        attrs = ROLES["Pilot"]["attributes"]
        assert attrs["Agility"] >= 5

    def test_medic_is_empathy_heavy(self):
        attrs = ROLES["Medic"]["attributes"]
        assert attrs["Empathy"] >= 4


# ── get_role_info ─────────────────────────────────────────────────────────────

class TestGetRoleInfo:
    def test_returns_json_string(self):
        result = get_role_info("Colonial Marine")
        assert isinstance(result, str)
        json.loads(result)  # must not raise

    def test_known_role_has_attributes(self):
        data = json.loads(get_role_info("Pilot"))
        assert "attributes" in data
        assert "key_skills" in data

    def test_unknown_role_returns_error(self):
        data = json.loads(get_role_info("Xenomorph"))
        assert "error" in data
        assert "available" in data

    def test_tool_in_tools_list(self):
        names = [t["name"] for t in alien_agent.TOOLS]
        assert "get_role_info" in names


# ── PERSONAL_AGENDAS data ─────────────────────────────────────────────────────

class TestPersonalAgendas:
    def test_all_roles_have_agendas(self):
        for role in EXPECTED_ROLES:
            assert role in PERSONAL_AGENDAS, f"'{role}' missing from PERSONAL_AGENDAS"

    def test_each_role_has_at_least_4_agendas(self):
        for role, agendas in PERSONAL_AGENDAS.items():
            assert len(agendas) >= 4, f"'{role}' has only {len(agendas)} agendas"

    def test_all_agendas_are_non_empty_strings(self):
        for role, agendas in PERSONAL_AGENDAS.items():
            for agenda in agendas:
                assert isinstance(agenda, str) and len(agenda) > 20, \
                    f"'{role}' has a thin/empty agenda"


# ── roll_personal_agenda ──────────────────────────────────────────────────────

class TestRollPersonalAgenda:
    def test_returns_json_string(self):
        result = roll_personal_agenda("Colonial Marine")
        assert isinstance(result, str)
        json.loads(result)

    def test_has_role_and_agenda_keys(self):
        data = json.loads(roll_personal_agenda("Company Agent"))
        assert "role" in data
        assert "personal_agenda" in data

    def test_agenda_is_non_empty_string(self):
        data = json.loads(roll_personal_agenda("Medic"))
        assert isinstance(data["personal_agenda"], str)
        assert len(data["personal_agenda"]) > 20

    def test_unknown_role_returns_error(self):
        data = json.loads(roll_personal_agenda("Navigator"))
        assert "error" in data

    def test_returns_variety_across_rolls(self):
        agendas = set()
        for _ in range(30):
            data = json.loads(roll_personal_agenda("Roughneck"))
            agendas.add(data["personal_agenda"])
        assert len(agendas) >= 2

    def test_tool_in_tools_list(self):
        names = [t["name"] for t in alien_agent.TOOLS]
        assert "roll_personal_agenda" in names


# ── SCENARIO_HOOKS data ───────────────────────────────────────────────────────

class TestScenarioHooks:
    def test_at_least_6_hooks(self):
        assert len(SCENARIO_HOOKS) >= 6

    def test_required_keys(self):
        required = {"type", "description", "location_type", "complications"}
        for hook in SCENARIO_HOOKS:
            missing = required - set(hook.keys())
            assert not missing, f"Hook '{hook.get('type')}' missing: {missing}"

    def test_each_hook_has_3_complications(self):
        for hook in SCENARIO_HOOKS:
            assert len(hook["complications"]) >= 3, \
                f"Hook '{hook['type']}' has fewer than 3 complications"

    def test_derelict_investigation_present(self):
        types = {h["type"] for h in SCENARIO_HOOKS}
        assert "Derelict Investigation" in types

    def test_outbreak_response_present(self):
        types = {h["type"] for h in SCENARIO_HOOKS}
        assert "Outbreak Response" in types


# ── roll_scenario_hook ────────────────────────────────────────────────────────

class TestRollScenarioHook:
    def test_returns_json_string(self):
        result = roll_scenario_hook()
        assert isinstance(result, str)
        json.loads(result)

    def test_has_required_keys(self):
        data = json.loads(roll_scenario_hook())
        assert "scenario_type" in data
        assert "description" in data
        assert "complication" in data

    def test_returns_variety(self):
        types = set()
        for _ in range(30):
            data = json.loads(roll_scenario_hook())
            types.add(data["scenario_type"])
        assert len(types) >= 3

    def test_tool_in_tools_list(self):
        names = [t["name"] for t in alien_agent.TOOLS]
        assert "roll_scenario_hook" in names


# ── detect_phase ──────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_name_tool(self):
        assert detect_phase("roll_name_suggestion", set()) == "name"

    def test_role_tool(self):
        assert detect_phase("get_role_info", set()) == "role"

    def test_agenda_tool(self):
        assert detect_phase("roll_personal_agenda", set()) == "agenda"

    def test_gear_tool(self):
        assert detect_phase("roll_alien_gear", set()) == "gear"

    def test_scenario_tool(self):
        assert detect_phase("roll_scenario_hook", set()) == "scenario"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("roll_something_else", set()) is None


# ── System prompts ────────────────────────────────────────────────────────────

class TestSystemPrompts:
    def test_system_prompt_exists(self):
        assert hasattr(alien_agent, "SYSTEM_PROMPT")
        assert len(alien_agent.SYSTEM_PROMPT) > 500

    def test_npc_system_prompt_exists(self):
        assert hasattr(alien_agent, "NPC_SYSTEM_PROMPT")
        assert len(alien_agent.NPC_SYSTEM_PROMPT) > 200

    def test_contact_system_prompt_exists(self):
        assert hasattr(alien_agent, "CONTACT_SYSTEM_PROMPT")
        assert len(alien_agent.CONTACT_SYSTEM_PROMPT) > 200

    def test_scenario_system_prompt_exists(self):
        assert hasattr(alien_agent, "SCENARIO_SYSTEM_PROMPT")
        assert len(alien_agent.SCENARIO_SYSTEM_PROMPT) > 200

    def test_system_prompt_mentions_personal_agenda(self):
        assert "Personal Agenda" in alien_agent.SYSTEM_PROMPT

    def test_system_prompt_mentions_stress(self):
        assert "Stress" in alien_agent.SYSTEM_PROMPT

    def test_contact_prompt_mentions_company_knew(self):
        assert "Company Knew" in alien_agent.CONTACT_SYSTEM_PROMPT

    def test_run_includes_all_modes(self):
        import inspect
        source = inspect.getsource(alien_agent.run)
        for mode in ("cinematic", "npc", "contact", "scenario"):
            assert mode in source, f"run() missing mode '{mode}'"


# ── Alien gear ────────────────────────────────────────────────────────────────

class TestAlienGearStructure:
    def test_all_roles_have_gear(self):
        for role in EXPECTED_ROLES:
            assert role in _ALIEN_GEAR, f"'{role}' missing from _ALIEN_GEAR"

    def test_each_role_has_weapons_and_kit(self):
        for role, gear in _ALIEN_GEAR.items():
            assert "weapons" in gear, f"'{role}' missing 'weapons'"
            assert "kit" in gear, f"'{role}' missing 'kit'"
            assert len(gear["weapons"]) >= 1
            assert len(gear["kit"]) >= 2

    def test_personal_list_non_empty(self):
        assert len(_ALIEN_PERSONAL) >= 8
        for item in _ALIEN_PERSONAL:
            assert isinstance(item, str) and item.strip()


class TestAlienGearRoller:
    def _roll(self, role):
        return json.loads(roll_alien_gear(role))

    def test_returns_valid_json(self):
        json.loads(roll_alien_gear("Colonial Marine"))

    def test_required_keys(self):
        data = self._roll("Scientist")
        assert "gear" in data
        assert "note" in data

    def test_gear_has_four_items(self):
        for role in EXPECTED_ROLES:
            data = self._roll(role)
            assert len(data["gear"]) == 4, \
                f"'{role}': expected 4 items, got {len(data['gear'])}"

    def test_weapon_from_role_pool(self):
        for role in EXPECTED_ROLES:
            data = self._roll(role)
            weapon = data["gear"][0]
            assert weapon in _ALIEN_GEAR[role]["weapons"], \
                f"'{role}': weapon not in pool"

    def test_personal_item_is_last(self):
        for role in EXPECTED_ROLES:
            data = self._roll(role)
            assert data["gear"][-1] in _ALIEN_PERSONAL, \
                f"'{role}': last item not in personal pool"

    def test_unknown_role_fallback(self):
        data = self._roll("Navigator")
        assert len(data["gear"]) == 4

    def test_schema_name_matches(self):
        assert ALIEN_GEAR_TOOL_SCHEMA["name"] == "roll_alien_gear"

    def test_schema_enum_matches_data(self):
        enum = ALIEN_GEAR_TOOL_SCHEMA["input_schema"]["properties"]["role_name"]["enum"]
        assert set(enum) == set(_ALIEN_GEAR.keys())
