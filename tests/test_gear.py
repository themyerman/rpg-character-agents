"""
Tests for gear.py — starting equipment for all four games.
"""

import json
import pytest
from lib.gear import (
    _DND_GEAR,
    _DND_PERSONAL,
    _WEAPON_DAMAGE,
    _match_weapon_damage,
    roll_dnd_gear,
    DND_GEAR_TOOL_SCHEMA,
    _TRAVELLER_GEAR,
    _TRAVELLER_PERSONAL,
    roll_traveller_gear,
    TRAVELLER_GEAR_TOOL_SCHEMA,
    _FIREFLY_GEAR,
    _FIREFLY_PERSONAL,
    roll_firefly_gear,
    FIREFLY_GEAR_TOOL_SCHEMA,
    _SCUM_GEAR,
    _SCUM_PERSONAL,
    roll_scum_gear,
    SCUM_GEAR_TOOL_SCHEMA,
)


# ── D&D gear ──────────────────────────────────────────────────────────────────

DND_CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
    "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard",
]


class TestDndGearStructure:
    def test_all_classes_present(self):
        assert set(_DND_GEAR.keys()) == set(DND_CLASSES)

    def test_each_class_has_weapons(self):
        for cls, gear in _DND_GEAR.items():
            assert "weapons" in gear, f"{cls} missing 'weapons'"
            assert len(gear["weapons"]) >= 1, f"{cls} weapons list is empty"

    def test_each_class_has_kit(self):
        for cls, gear in _DND_GEAR.items():
            assert "kit" in gear, f"{cls} missing 'kit'"
            assert len(gear["kit"]) >= 2, f"{cls} kit has fewer than 2 items"

    def test_all_weapon_strings_non_empty(self):
        for cls, gear in _DND_GEAR.items():
            for item in gear["weapons"]:
                assert isinstance(item, str) and item.strip(), \
                    f"{cls} has an empty/non-string weapon"

    def test_all_kit_strings_non_empty(self):
        for cls, gear in _DND_GEAR.items():
            for item in gear["kit"]:
                assert isinstance(item, str) and item.strip(), \
                    f"{cls} has an empty/non-string kit item"

    def test_personal_list_non_empty(self):
        assert len(_DND_PERSONAL) >= 10
        for item in _DND_PERSONAL:
            assert isinstance(item, str) and item.strip()


class TestDndGearRoller:
    def _roll(self, cls):
        raw = roll_dnd_gear(cls)
        return json.loads(raw)

    def test_returns_valid_json(self):
        result = roll_dnd_gear("Fighter")
        json.loads(result)  # must not raise

    def test_required_keys(self):
        data = self._roll("Wizard")
        assert "gear" in data
        assert "note" in data

    def test_gear_is_list_of_four_items(self):
        for cls in DND_CLASSES:
            data = self._roll(cls)
            assert len(data["gear"]) == 4, \
                f"{cls}: expected 4 items, got {len(data['gear'])}"

    def test_all_gear_items_are_strings(self):
        for cls in DND_CLASSES:
            data = self._roll(cls)
            for item in data["gear"]:
                assert isinstance(item, str) and item.strip(), \
                    f"{cls} returned an empty/non-string gear item"

    def test_weapon_comes_from_class_pool(self):
        """First item must be one of the class's weapon options."""
        for cls in DND_CLASSES:
            data = self._roll(cls)
            weapon = data["gear"][0]
            assert weapon in _DND_GEAR[cls]["weapons"], \
                f"{cls}: first item '{weapon}' not in weapons pool"

    def test_personal_item_is_last(self):
        """Last item must come from the shared personal list."""
        for cls in DND_CLASSES:
            data = self._roll(cls)
            personal = data["gear"][-1]
            assert personal in _DND_PERSONAL, \
                f"{cls}: last item '{personal}' not in personal pool"

    def test_middle_items_come_from_kit(self):
        """Middle items (index 1 and 2) must come from the class kit pool."""
        for cls in DND_CLASSES:
            data = self._roll(cls)
            kit_items = data["gear"][1:-1]
            for item in kit_items:
                assert item in _DND_GEAR[cls]["kit"], \
                    f"{cls}: kit item '{item}' not found in kit pool"

    def test_unknown_class_returns_fallback(self):
        data = self._roll("Alchemist")
        assert len(data["gear"]) == 4

    def test_note_is_non_empty_string(self):
        data = self._roll("Rogue")
        assert isinstance(data["note"], str) and data["note"].strip()

    def test_weapon_damage_key_present(self):
        """roll_dnd_gear must include weapon_damage in the returned JSON."""
        for cls in DND_CLASSES:
            data = self._roll(cls)
            assert "weapon_damage" in data, f"{cls}: 'weapon_damage' key missing"

    def test_weapon_damage_has_damage_field(self):
        """weapon_damage must always have a 'damage' sub-key."""
        for cls in DND_CLASSES:
            data = self._roll(cls)
            dmg = data["weapon_damage"]
            assert "damage" in dmg, f"{cls}: weapon_damage missing 'damage'"

    def test_weapon_damage_is_non_empty_string(self):
        for cls in DND_CLASSES:
            data = self._roll(cls)
            assert isinstance(data["weapon_damage"]["damage"], str)
            assert data["weapon_damage"]["damage"].strip()

    def test_note_mentions_damage_and_italics(self):
        """The updated note should tell Claude to append damage in italics."""
        data = self._roll("Fighter")
        note = data["note"]
        assert "damage" in note.lower()
        assert "italic" in note.lower()


# ── _match_weapon_damage ─────────────────────────────────────────────────────

class TestMatchWeaponDamage:
    def test_weapon_damage_list_has_entries(self):
        assert len(_WEAPON_DAMAGE) >= 20

    def test_each_entry_is_three_element_tuple(self):
        for entry in _WEAPON_DAMAGE:
            assert len(entry) == 3, f"Entry {entry!r} is not a 3-tuple"

    def test_all_damage_strings_contain_die(self):
        """Every damage string should look like NdN or NdN+N."""
        for keyword, damage, _ in _WEAPON_DAMAGE:
            assert "d" in damage, f"'{keyword}' damage '{damage}' has no die notation"

    def test_longsword_returns_1d8_slashing(self):
        result = _match_weapon_damage("a longsword with a notch in the blade")
        assert result["damage"] == "1d8 slashing"
        assert "Versatile" in result.get("properties", "")

    def test_greataxe_returns_1d12_slashing(self):
        result = _match_weapon_damage("a greataxe with a repaired haft")
        assert result["damage"] == "1d12 slashing"

    def test_rapier_returns_1d8_piercing_finesse(self):
        result = _match_weapon_damage("a rapier in a cracked leather scabbard, still perfectly balanced")
        assert result["damage"] == "1d8 piercing"
        assert "Finesse" in result.get("properties", "")

    def test_dagger_returns_1d4_piercing(self):
        result = _match_weapon_damage("three daggers in various states of concealment")
        assert result["damage"] == "1d4 piercing"

    def test_hand_crossbow_not_matched_as_crossbow(self):
        """'hand crossbow' must hit the hand crossbow entry, not a generic crossbow."""
        result = _match_weapon_damage("a hand crossbow worn under the coat with twelve bolts")
        assert result["damage"] == "1d6 piercing"          # hand crossbow
        assert "light" in result.get("properties", "").lower()

    def test_shortbow_not_confused_with_longbow(self):
        result = _match_weapon_damage("a shortbow and a quiver of twenty arrows")
        assert result["damage"] == "1d6 piercing"

    def test_longbow_returns_1d8_piercing(self):
        result = _match_weapon_damage("a longbow of yew, strung only when needed")
        assert result["damage"] == "1d8 piercing"

    def test_quarterstaff_returns_1d6_bludgeoning(self):
        result = _match_weapon_damage("a quarterstaff with grips worn smooth")
        assert result["damage"] == "1d6 bludgeoning"

    def test_warhammer_returns_1d8_bludgeoning(self):
        result = _match_weapon_damage("a warhammer with the deity's symbol stamped into the head")
        assert result["damage"] == "1d8 bludgeoning"

    def test_unknown_weapon_returns_varies(self):
        result = _match_weapon_damage("a halberd of great antiquity")
        assert result["damage"] == "varies"

    def test_empty_string_returns_varies(self):
        result = _match_weapon_damage("")
        assert result["damage"] == "varies"

    def test_all_dnd_weapon_strings_get_a_match(self):
        """Every weapon string in _DND_GEAR should resolve to a known damage die."""
        no_match = []
        for cls, gear in _DND_GEAR.items():
            for weapon in gear["weapons"]:
                result = _match_weapon_damage(weapon)
                if result["damage"] == "varies":
                    no_match.append((cls, weapon))
        # Allow up to 2 misses (some weapon strings are intentionally vague)
        assert len(no_match) <= 2, \
            f"Too many unmatched weapons ({len(no_match)}): {no_match}"


# ── Traveller gear ────────────────────────────────────────────────────────────

TRAVELLER_CAREERS = [
    "Navy", "Army", "Marines", "Scout", "Merchant",
    "Drifter", "Noble", "Agent", "Scholar", "Entertainer", "Rogue", "Citizen",
]


class TestTravellerGearStructure:
    def test_all_careers_present(self):
        assert set(_TRAVELLER_GEAR.keys()) == set(TRAVELLER_CAREERS)

    def test_each_career_has_weapons_and_kit(self):
        for career, gear in _TRAVELLER_GEAR.items():
            assert "weapons" in gear, f"{career} missing 'weapons'"
            assert "kit" in gear, f"{career} missing 'kit'"
            assert len(gear["weapons"]) >= 1, f"{career} weapons list is empty"
            assert len(gear["kit"]) >= 2, f"{career} kit has fewer than 2 items"

    def test_personal_list_non_empty(self):
        assert len(_TRAVELLER_PERSONAL) >= 8
        for item in _TRAVELLER_PERSONAL:
            assert isinstance(item, str) and item.strip()


class TestTravellerGearRoller:
    def _roll(self, career):
        return json.loads(roll_traveller_gear(career))

    def test_returns_valid_json(self):
        json.loads(roll_traveller_gear("Scout"))

    def test_gear_list_has_four_items(self):
        for career in TRAVELLER_CAREERS:
            data = self._roll(career)
            assert len(data["gear"]) == 4, \
                f"{career}: expected 4 items, got {len(data['gear'])}"

    def test_weapon_from_career_pool(self):
        for career in TRAVELLER_CAREERS:
            data = self._roll(career)
            weapon = data["gear"][0]
            assert weapon in _TRAVELLER_GEAR[career]["weapons"], \
                f"{career}: weapon '{weapon}' not in pool"

    def test_personal_item_is_last(self):
        for career in TRAVELLER_CAREERS:
            data = self._roll(career)
            assert data["gear"][-1] in _TRAVELLER_PERSONAL, \
                f"{career}: last item not in personal pool"

    def test_case_insensitive_exact_match(self):
        data = self._roll("navy")
        assert data["gear"][0] in _TRAVELLER_GEAR["Navy"]["weapons"]

    def test_case_insensitive_mixed_case(self):
        data = self._roll("SCOUT")
        assert data["gear"][0] in _TRAVELLER_GEAR["Scout"]["weapons"]

    def test_substring_fallback(self):
        """'Navy (3rd Officer, 4 terms)' should resolve to Navy via substring."""
        data = self._roll("Navy (3rd Officer, 4 terms)")
        assert data["gear"][0] in _TRAVELLER_GEAR["Navy"]["weapons"]

    def test_unknown_career_fallback(self):
        data = self._roll("Psion")
        assert len(data["gear"]) == 4


# ── Firefly gear ──────────────────────────────────────────────────────────────

FIREFLY_ROLES = [
    "Captain", "Pilot", "First Mate", "Mechanic", "Doctor",
    "Shepherd", "Muscle", "Grifter", "Thief",
]


class TestFireflyGearStructure:
    def test_all_roles_present(self):
        assert set(_FIREFLY_GEAR.keys()) == set(FIREFLY_ROLES)

    def test_each_role_has_weapons_and_kit(self):
        for role, gear in _FIREFLY_GEAR.items():
            assert "weapons" in gear, f"{role} missing 'weapons'"
            assert "kit" in gear, f"{role} missing 'kit'"
            assert len(gear["weapons"]) >= 1, f"{role} weapons list is empty"
            assert len(gear["kit"]) >= 2, f"{role} kit has fewer than 2 items"

    def test_personal_list_non_empty(self):
        assert len(_FIREFLY_PERSONAL) >= 8
        for item in _FIREFLY_PERSONAL:
            assert isinstance(item, str) and item.strip()


class TestFireflyGearRoller:
    def _roll(self, role):
        return json.loads(roll_firefly_gear(role))

    def test_returns_valid_json(self):
        json.loads(roll_firefly_gear("Captain"))

    def test_gear_list_has_four_items(self):
        for role in FIREFLY_ROLES:
            data = self._roll(role)
            assert len(data["gear"]) == 4, \
                f"{role}: expected 4 items, got {len(data['gear'])}"

    def test_weapon_from_role_pool(self):
        for role in FIREFLY_ROLES:
            data = self._roll(role)
            weapon = data["gear"][0]
            assert weapon in _FIREFLY_GEAR[role]["weapons"], \
                f"{role}: weapon '{weapon}' not in pool"

    def test_personal_item_is_last(self):
        for role in FIREFLY_ROLES:
            data = self._roll(role)
            assert data["gear"][-1] in _FIREFLY_PERSONAL, \
                f"{role}: last item not in personal pool"

    def test_case_insensitive_lookup(self):
        data = self._roll("mechanic")
        assert data["gear"][0] in _FIREFLY_GEAR["Mechanic"]["weapons"]

    def test_unknown_role_fallback(self):
        data = self._roll("Bounty Hunter")
        assert len(data["gear"]) == 4


# ── Scum and Villainy gear ────────────────────────────────────────────────────

SCUM_PLAYBOOKS = ["Muscle", "Pilot", "Scoundrel", "Mystic", "Speaker", "Stitch"]


class TestScumGearStructure:
    def test_all_playbooks_present(self):
        assert set(_SCUM_GEAR.keys()) == set(SCUM_PLAYBOOKS)

    def test_each_playbook_has_weapons_and_kit(self):
        for pb, gear in _SCUM_GEAR.items():
            assert "weapons" in gear, f"{pb} missing 'weapons'"
            assert "kit" in gear, f"{pb} missing 'kit'"
            assert len(gear["weapons"]) >= 1, f"{pb} weapons list is empty"
            assert len(gear["kit"]) >= 2, f"{pb} kit has fewer than 2 items"

    def test_personal_list_non_empty(self):
        assert len(_SCUM_PERSONAL) >= 8
        for item in _SCUM_PERSONAL:
            assert isinstance(item, str) and item.strip()


class TestScumGearRoller:
    def _roll(self, playbook):
        return json.loads(roll_scum_gear(playbook))

    def test_returns_valid_json(self):
        json.loads(roll_scum_gear("Muscle"))

    def test_gear_list_has_four_items(self):
        for pb in SCUM_PLAYBOOKS:
            data = self._roll(pb)
            assert len(data["gear"]) == 4, \
                f"{pb}: expected 4 items, got {len(data['gear'])}"

    def test_weapon_from_playbook_pool(self):
        for pb in SCUM_PLAYBOOKS:
            data = self._roll(pb)
            weapon = data["gear"][0]
            assert weapon in _SCUM_GEAR[pb]["weapons"], \
                f"{pb}: weapon '{weapon}' not in pool"

    def test_personal_item_is_last(self):
        for pb in SCUM_PLAYBOOKS:
            data = self._roll(pb)
            assert data["gear"][-1] in _SCUM_PERSONAL, \
                f"{pb}: last item not in personal pool"

    def test_case_insensitive_lookup(self):
        data = self._roll("stitch")
        assert data["gear"][0] in _SCUM_GEAR["Stitch"]["weapons"]

    def test_unknown_playbook_fallback(self):
        data = self._roll("Ghost")
        assert len(data["gear"]) == 4


# ── Tool schemas ──────────────────────────────────────────────────────────────

class TestGearToolSchemas:
    SCHEMAS = [
        ("DND_GEAR_TOOL_SCHEMA",       DND_GEAR_TOOL_SCHEMA,       "roll_dnd_gear"),
        ("TRAVELLER_GEAR_TOOL_SCHEMA", TRAVELLER_GEAR_TOOL_SCHEMA, "roll_traveller_gear"),
        ("FIREFLY_GEAR_TOOL_SCHEMA",   FIREFLY_GEAR_TOOL_SCHEMA,   "roll_firefly_gear"),
        ("SCUM_GEAR_TOOL_SCHEMA",      SCUM_GEAR_TOOL_SCHEMA,      "roll_scum_gear"),
    ]

    def test_schemas_have_required_keys(self):
        for label, schema, _ in self.SCHEMAS:
            assert "name" in schema,         f"{label}: missing 'name'"
            assert "description" in schema,  f"{label}: missing 'description'"
            assert "input_schema" in schema, f"{label}: missing 'input_schema'"

    def test_schema_names_match_functions(self):
        for label, schema, expected_name in self.SCHEMAS:
            assert schema["name"] == expected_name, \
                f"{label}: schema name '{schema['name']}' != '{expected_name}'"

    def test_descriptions_non_empty(self):
        for label, schema, _ in self.SCHEMAS:
            assert isinstance(schema["description"], str) and schema["description"].strip(), \
                f"{label}: description is empty"

    def test_input_schemas_are_objects(self):
        for label, schema, _ in self.SCHEMAS:
            assert schema["input_schema"]["type"] == "object", \
                f"{label}: input_schema type is not 'object'"

    def test_dnd_gear_schema_enum_matches_data(self):
        enum = DND_GEAR_TOOL_SCHEMA["input_schema"]["properties"]["class_name"]["enum"]
        assert set(enum) == set(_DND_GEAR.keys())

    def test_firefly_gear_schema_enum_matches_data(self):
        enum = FIREFLY_GEAR_TOOL_SCHEMA["input_schema"]["properties"]["role"]["enum"]
        assert set(enum) == set(_FIREFLY_GEAR.keys())

    def test_scum_gear_schema_enum_matches_data(self):
        enum = SCUM_GEAR_TOOL_SCHEMA["input_schema"]["properties"]["playbook"]["enum"]
        assert set(enum) == set(_SCUM_GEAR.keys())

    def test_traveller_schema_has_no_enum(self):
        """Traveller career is a free string (substring matching), not an enum."""
        props = TRAVELLER_GEAR_TOOL_SCHEMA["input_schema"]["properties"]
        assert "enum" not in props["career"], \
            "Traveller schema should not have an enum — careers can have varied forms"

    def test_all_schemas_require_their_parameter(self):
        required_map = {
            "roll_dnd_gear":       "class_name",
            "roll_traveller_gear": "career",
            "roll_firefly_gear":   "role",
            "roll_scum_gear":      "playbook",
        }
        for label, schema, expected_name in self.SCHEMAS:
            required = schema["input_schema"].get("required", [])
            expected_param = required_map[expected_name]
            assert expected_param in required, \
                f"{label}: '{expected_param}' not in required list"
