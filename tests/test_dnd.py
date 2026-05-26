"""
Tests for dnd_agent.py — pure Python logic only, no API calls.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from agents import dnd_agent
from agents.dnd_agent import (
    ability_modifier,
    modifier_str,
    roll_stat,
    roll_dice,
    get_race_info,
    get_class_info,
    get_background_info,
    get_subclass_info,
    roll_alignment,
    roll_quest_hook,
    roll_villain_profile,
    calculate_ac,
    calculate_combat_stats,
    pick_skills,
    roll_deity,
    detect_phase,
    save_result,
    VALID_DICE,
    MIN_ROLLS,
    MAX_ROLLS,
    RACES,
    CLASSES,
    BACKGROUNDS,
    ALIGNMENTS,
    QUEST_HOOKS,
    ARMOR_TABLE,
    SKILL_POOLS,
    DEITIES,
    ALL_SKILLS,
    PROFICIENCY_BONUS,
    SPELLCASTING_STAT,
    SUBCLASSES,
    VILLAIN_SCHEMES,
    VILLAIN_WOUNDS,
)


# ── ability_modifier ────────────────────────────────────────────────────────────

class TestAbilityModifier:
    def test_score_10_is_zero(self):
        assert ability_modifier(10) == 0

    def test_score_11_is_zero(self):
        assert ability_modifier(11) == 0

    def test_score_8_is_minus_one(self):
        assert ability_modifier(8) == -1

    def test_score_9_is_minus_one(self):
        assert ability_modifier(9) == -1

    def test_score_12_is_plus_one(self):
        assert ability_modifier(12) == 1

    def test_score_20_is_plus_five(self):
        assert ability_modifier(20) == 5

    def test_score_1_is_minus_five(self):
        assert ability_modifier(1) == -5

    def test_score_18_is_plus_four(self):
        assert ability_modifier(18) == 4


# ── modifier_str ────────────────────────────────────────────────────────────────

class TestModifierStr:
    def test_positive_has_plus_sign(self):
        assert modifier_str(14) == "+2"

    def test_zero_has_plus_sign(self):
        assert modifier_str(10) == "+0"

    def test_negative_has_minus_sign(self):
        assert modifier_str(8) == "-1"


# ── roll_stat ───────────────────────────────────────────────────────────────────

class TestRollStat:
    def test_returns_string(self):
        result = roll_stat()
        assert isinstance(result, str)

    def test_contains_score_label(self):
        assert "score:" in roll_stat()

    def test_score_in_valid_range(self):
        # 4d6 drop lowest: min possible is 3 (1+1+1), max is 18 (6+6+6)
        for _ in range(50):
            result = roll_stat()
            score = int(result.split("score:")[-1].strip())
            assert 3 <= score <= 18


# ── roll_dice ───────────────────────────────────────────────────────────────────

class TestRollDice:
    def test_valid_die_returns_result(self):
        result = roll_dice(sides=6, count=1)
        assert "total:" in result

    def test_invalid_die_returns_error(self):
        result = roll_dice(sides=7)
        assert "Error" in result

    def test_invalid_die_57_returns_error(self):
        result = roll_dice(sides=57)
        assert "Error" in result

    def test_count_too_high_returns_error(self):
        result = roll_dice(sides=6, count=MAX_ROLLS + 1)
        assert "Error" in result

    def test_count_zero_returns_error(self):
        result = roll_dice(sides=6, count=0)
        assert "Error" in result

    def test_all_valid_dice_work(self):
        for sides in VALID_DICE:
            result = roll_dice(sides=sides, count=2)
            assert "total:" in result, f"d{sides} failed"

    def test_total_in_range(self):
        for _ in range(20):
            result = roll_dice(sides=6, count=2)
            total = int(result.split("total:")[-1].strip())
            assert 2 <= total <= 12


# ── get_race_info ───────────────────────────────────────────────────────────────

class TestGetRaceInfo:
    def test_valid_race_returns_data(self):
        result = get_race_info("Human")
        assert "Human" in result or "ability_bonuses" in result

    def test_invalid_race_returns_error(self):
        result = get_race_info("Klingon")
        assert "Unknown" in result or "not found" in result.lower() or "available" in result.lower()

    def test_all_races_return_data(self):
        for race in RACES:
            result = get_race_info(race)
            assert "Error" not in result, f"Race '{race}' returned an error"


# ── get_class_info ──────────────────────────────────────────────────────────────

class TestGetClassInfo:
    def test_valid_class_returns_data(self):
        result = get_class_info("Rogue")
        assert "Rogue" in result or "hit_die" in result

    def test_invalid_class_returns_error(self):
        result = get_class_info("Jedi")
        assert "Unknown" in result or "not found" in result.lower() or "available" in result.lower()

    def test_all_classes_return_data(self):
        for cls in CLASSES:
            result = get_class_info(cls)
            assert "Error" not in result, f"Class '{cls}' returned an error"


# ── get_background_info ─────────────────────────────────────────────────────────

class TestGetBackgroundInfo:
    def test_valid_background_returns_data(self):
        result = get_background_info("Urchin")
        assert "Urchin" in result or "skills" in result

    def test_invalid_background_returns_error(self):
        result = get_background_info("Astronaut")
        assert "Unknown" in result or "not found" in result.lower() or "available" in result.lower()

    def test_all_backgrounds_return_data(self):
        for bg in BACKGROUNDS:
            result = get_background_info(bg)
            assert "Error" not in result, f"Background '{bg}' returned an error"


# ── save_result ─────────────────────────────────────────────────────────────────

class TestSaveResult:
    def test_finds_heading_for_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Pip Underbough**\n*Rogue — light fingers, heavy conscience*"
        path = save_result(content, "full")
        assert "pip-underbough" in path.name

    def test_preamble_skipped_for_filename(self, tmp_path, monkeypatch):
        """Preamble before first ## heading must not end up in the filename."""
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "Now I have everything. Let me build her.\n\nHP = 8\n\n## **Iyari Sael**\n*Druid*"
        path = save_result(content, "full")
        assert "iyari-sael" in path.name
        assert "now" not in path.name
        assert "everything" not in path.name

    def test_collision_appends_counter(self, tmp_path, monkeypatch):
        """Second character with the same name gets -2 suffix, not a silent overwrite."""
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Aldric Vehr**\n*Fighter — wall of a man*"
        path1 = save_result(content, "full")
        path2 = save_result(content, "full")
        assert path1 != path2
        assert path1.exists()
        assert path2.exists()
        assert path2.name == "aldric-vehr-full-2.md"

    def test_collision_increments_beyond_two(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Aldric Vehr**\n*Fighter*"
        save_result(content, "full")
        save_result(content, "full")
        path3 = save_result(content, "full")
        assert path3.name == "aldric-vehr-full-3.md"

    def test_mode_used_as_suffix(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Rook Delmar**\n*Paladin*"
        assert save_result(content, "full").name.endswith("-full.md")
        content2 = "## **Siena Mott**\n*Warlock*"
        assert save_result(content2, "npc").name.endswith("-npc.md")
        content3 = "## **Halben Orriss**\n*Quest giver*"
        assert save_result(content3, "questgiver").name.endswith("-questgiver.md")

    def test_file_content_written(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Test Character**\n*Cleric — keeps everyone alive, barely*"
        path = save_result(content, "full")
        assert path.read_text() == content

    def test_saves_to_correct_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Test**\n*Fighter*"
        path = save_result(content, "full")
        assert "characters" in str(path)
        assert "dnd" in str(path)

    def test_strips_markdown_from_filename(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dnd_agent, "__file__", str(tmp_path / "agents" / "dnd_agent.py"))
        content = "## **Rook Delmar**\n*Fighter*"
        path = save_result(content, "full")
        assert "**" not in path.name
        assert "#" not in path.name


# ── roll_quest_hook ──────────────────────────────────────────────────────────────

class TestRollQuestHook:
    def test_returns_valid_json(self):
        result = roll_quest_hook()
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(roll_quest_hook())
        assert "quest_type"   in data
        assert "description"  in data
        assert "complication" in data

    def test_quest_type_is_known(self):
        known_types = {h["type"] for h in QUEST_HOOKS}
        for _ in range(20):
            data = json.loads(roll_quest_hook())
            assert data["quest_type"] in known_types

    def test_returns_variety(self):
        # 30 rolls should yield at least 4 distinct quest types
        types = {json.loads(roll_quest_hook())["quest_type"] for _ in range(30)}
        assert len(types) >= 4

    def test_complication_is_non_empty_string(self):
        data = json.loads(roll_quest_hook())
        assert isinstance(data["complication"], str)
        assert len(data["complication"]) > 0

    def test_complication_belongs_to_quest_type(self):
        for _ in range(20):
            data = json.loads(roll_quest_hook())
            hook = next(h for h in QUEST_HOOKS if h["type"] == data["quest_type"])
            assert data["complication"] in hook["complications"]

    def test_at_least_twelve_quest_types(self):
        assert len(QUEST_HOOKS) >= 12

    def test_monster_hunt_and_heist_present(self):
        known_types = {h["type"] for h in QUEST_HOOKS}
        assert "Monster Hunt" in known_types
        assert "Heist"        in known_types


# ── detect_phase ─────────────────────────────────────────────────────────────────

class TestDetectPhase:
    def test_roll_stat_returns_stats(self):
        assert detect_phase("roll_stat", set()) == "stats"

    def test_get_race_info_returns_race(self):
        assert detect_phase("get_race_info", set()) == "race"

    def test_get_class_info_returns_class(self):
        assert detect_phase("get_class_info", set()) == "class"

    def test_get_background_info_returns_background(self):
        assert detect_phase("get_background_info", set()) == "background"

    def test_roll_dnd_name_suggestion_returns_name(self):
        assert detect_phase("roll_dnd_name_suggestion", set()) == "name"

    def test_roll_quest_hook_returns_quest(self):
        assert detect_phase("roll_quest_hook", set()) == "quest"

    def test_unknown_tool_returns_none(self):
        assert detect_phase("flip_coin", set()) is None

    def test_roll_dice_returns_none(self):
        assert detect_phase("roll_dice", set()) is None

    def test_roll_dnd_gear_returns_gear(self):
        assert detect_phase("roll_dnd_gear", set()) == "gear"

    def test_roll_alignment_returns_alignment(self):
        assert detect_phase("roll_alignment", set()) == "alignment"


# ── Alignment data pool ───────────────────────────────────────────────────────────

class TestAlignmentPool:
    def test_nine_alignments(self):
        assert len(ALIGNMENTS) == 9

    def test_all_nine_names_present(self):
        names = {a["name"] for a in ALIGNMENTS}
        expected = {
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil",
        }
        assert names == expected

    def test_each_alignment_has_required_keys(self):
        for a in ALIGNMENTS:
            assert "name"        in a, f"{a.get('name', '?')} missing 'name'"
            assert "expressions" in a, f"{a.get('name', '?')} missing 'expressions'"
            assert "tension"     in a, f"{a.get('name', '?')} missing 'tension'"
            assert "shadow"      in a, f"{a.get('name', '?')} missing 'shadow'"

    def test_each_alignment_has_at_least_two_expressions(self):
        for a in ALIGNMENTS:
            assert len(a["expressions"]) >= 2, \
                f"{a['name']} has fewer than 2 expressions"

    def test_all_expressions_non_empty(self):
        for a in ALIGNMENTS:
            for expr in a["expressions"]:
                assert isinstance(expr, str) and expr.strip(), \
                    f"{a['name']} has empty expression"

    def test_tension_and_shadow_are_non_empty_strings(self):
        for a in ALIGNMENTS:
            assert isinstance(a["tension"], str) and a["tension"].strip()
            assert isinstance(a["shadow"],  str) and a["shadow"].strip()


# ── roll_alignment ────────────────────────────────────────────────────────────────

class TestRollAlignment:
    def test_returns_valid_json(self):
        data = json.loads(roll_alignment())
        assert isinstance(data, dict)

    def test_has_required_keys(self):
        data = json.loads(roll_alignment())
        assert "alignment"  in data
        assert "expression" in data
        assert "tension"    in data
        assert "shadow"     in data

    def test_alignment_is_one_of_nine(self):
        valid = {a["name"] for a in ALIGNMENTS}
        for _ in range(20):
            data = json.loads(roll_alignment())
            assert data["alignment"] in valid

    def test_expression_comes_from_pool(self):
        for _ in range(20):
            data   = json.loads(roll_alignment())
            entry  = next(a for a in ALIGNMENTS if a["name"] == data["alignment"])
            assert data["expression"] in entry["expressions"]

    def test_returns_variety_across_rolls(self):
        results = {json.loads(roll_alignment())["alignment"] for _ in range(50)}
        assert len(results) >= 4, "Should hit at least 4 distinct alignments in 50 rolls"

    def test_all_fields_are_non_empty_strings(self):
        data = json.loads(roll_alignment())
        for key in ("alignment", "expression", "tension", "shadow"):
            assert isinstance(data[key], str) and data[key].strip(), \
                f"Field '{key}' is empty or not a string"


# ── Alignment wiring ──────────────────────────────────────────────────────────────

class TestAlignmentWiring:
    def test_alignment_phase_message_present(self):
        assert "alignment" in dnd_agent.PHASE_MESSAGES

    def test_alignment_phase_message_is_string(self):
        assert isinstance(dnd_agent.PHASE_MESSAGES["alignment"], str)
        assert len(dnd_agent.PHASE_MESSAGES["alignment"]) > 0

    def test_roll_alignment_schema_in_tools(self):
        tool_names = [t["name"] for t in dnd_agent.TOOLS]
        assert "roll_alignment" in tool_names

    def test_run_tool_dispatches_roll_alignment(self):
        result = dnd_agent.run_tool("roll_alignment", {})
        data   = json.loads(result)
        assert "alignment" in data
        assert "expression" in data

    def test_system_prompt_mentions_roll_alignment(self):
        assert "roll_alignment" in dnd_agent.SYSTEM_PROMPT

    def test_npc_prompt_mentions_roll_alignment(self):
        assert "roll_alignment" in dnd_agent.NPC_SYSTEM_PROMPT

    def test_quest_giver_prompt_mentions_roll_alignment(self):
        assert "roll_alignment" in dnd_agent.QUEST_GIVER_SYSTEM_PROMPT


# ── Gear wiring ──────────────────────────────────────────────────────────────────

class TestGearWiring:
    def test_gear_phase_message_present(self):
        assert "gear" in dnd_agent.PHASE_MESSAGES

    def test_gear_phase_message_is_string(self):
        assert isinstance(dnd_agent.PHASE_MESSAGES["gear"], str)
        assert len(dnd_agent.PHASE_MESSAGES["gear"]) > 0

    def test_dnd_gear_schema_in_tools(self):
        tool_names = [t["name"] for t in dnd_agent.TOOLS]
        assert "roll_dnd_gear" in tool_names

    def test_run_tool_returns_gear_json(self):
        result = dnd_agent.run_tool("roll_dnd_gear", {"class_name": "Fighter"})
        data = json.loads(result)
        assert "gear" in data
        assert "note" in data
        assert len(data["gear"]) == 4

    def test_run_tool_gear_works_for_wizard(self):
        result = dnd_agent.run_tool("roll_dnd_gear", {"class_name": "Wizard"})
        data = json.loads(result)
        assert "gear" in data

    def test_system_prompt_mentions_roll_dnd_gear(self):
        assert "roll_dnd_gear" in dnd_agent.SYSTEM_PROMPT


# ── Constants sanity checks ─────────────────────────────────────────────────────

class TestConstants:
    def test_valid_dice_contains_standard_set(self):
        assert {4, 6, 8, 10, 12, 20}.issubset(VALID_DICE)

    def test_min_rolls_is_positive(self):
        assert MIN_ROLLS >= 1

    def test_max_rolls_is_reasonable(self):
        assert MAX_ROLLS <= 100


# ── New races — speed and languages ─────────────────────────────────────────────

class TestNewRaces:
    NEW_RACES = [
        "Drow", "Stout Halfling", "Rock Gnome", "Aasimar", "Tabaxi",
        "Fire Genasi", "Water Genasi", "Earth Genasi", "Air Genasi",
        "Goliath", "Firbolg", "Kenku", "Lizardfolk",
    ]

    def test_all_new_races_present(self):
        for race in self.NEW_RACES:
            assert race in RACES, f"Missing race: {race}"

    def test_all_races_have_speed(self):
        for name, data in RACES.items():
            assert "speed" in data, f"{name} missing 'speed'"
            assert isinstance(data["speed"], str) and data["speed"], f"{name} has empty speed"

    def test_all_races_have_languages(self):
        for name, data in RACES.items():
            assert "languages" in data, f"{name} missing 'languages'"
            assert isinstance(data["languages"], list) and len(data["languages"]) >= 1, \
                f"{name} has bad languages"

    def test_elemental_genasi_present(self):
        for genasi in ("Fire Genasi", "Water Genasi", "Earth Genasi", "Air Genasi"):
            assert genasi in RACES

    def test_genasi_speak_primordial(self):
        for genasi in ("Fire Genasi", "Water Genasi", "Earth Genasi", "Air Genasi"):
            assert "Primordial" in RACES[genasi]["languages"]

    def test_drow_has_sunlight_sensitivity(self):
        traits = " ".join(RACES["Drow"]["traits"])
        assert "Sunlight Sensitivity" in traits

    def test_drow_speaks_undercommon(self):
        assert "Undercommon" in RACES["Drow"]["languages"]

    def test_lizardfolk_has_natural_armor(self):
        traits = " ".join(RACES["Lizardfolk"]["traits"])
        assert "Natural Armor" in traits

    def test_lizardfolk_has_swim_speed(self):
        assert "swim" in RACES["Lizardfolk"]["speed"]

    def test_air_genasi_is_faster(self):
        assert "35" in RACES["Air Genasi"]["speed"]

    def test_wood_elf_is_35ft(self):
        assert "35" in RACES["Wood Elf"]["speed"]

    def test_get_race_info_returns_speed_and_languages(self):
        result = json.loads(get_race_info("Firbolg"))
        assert "speed" in result
        assert "languages" in result
        assert "Giant" in result["languages"]

    def test_all_races_in_get_race_info_enum(self):
        import agents.dnd_agent as m
        schema_races = None
        for tool in m.TOOLS:
            if tool["name"] == "get_race_info":
                schema_races = tool["input_schema"]["properties"]["race_name"]["enum"]
        assert schema_races is not None
        for race in self.NEW_RACES:
            assert race in schema_races, f"{race} missing from get_race_info enum"


# ── calculate_ac ─────────────────────────────────────────────────────────────────

class TestCalculateAc:
    def test_unarmored_base_10_plus_dex(self):
        result = json.loads(calculate_ac("Unarmored", dex_modifier=2))
        assert result["ac"] == 12

    def test_leather_11_plus_dex(self):
        result = json.loads(calculate_ac("Leather", dex_modifier=3))
        assert result["ac"] == 14

    def test_chain_mail_ignores_dex(self):
        result = json.loads(calculate_ac("Chain Mail", dex_modifier=5))
        assert result["ac"] == 16

    def test_scale_mail_caps_dex_at_2(self):
        result = json.loads(calculate_ac("Scale Mail", dex_modifier=5))
        assert result["ac"] == 16   # 14 + 2 (capped)

    def test_scale_mail_uses_dex_when_low(self):
        result = json.loads(calculate_ac("Scale Mail", dex_modifier=1))
        assert result["ac"] == 15   # 14 + 1

    def test_shield_adds_2(self):
        result = json.loads(calculate_ac("Leather", dex_modifier=2, has_shield=True))
        assert result["ac"] == 15   # 11 + 2 + 2

    def test_barbarian_unarmored_adds_con(self):
        result = json.loads(calculate_ac("Barbarian Unarmored", dex_modifier=2, con_modifier=3))
        assert result["ac"] == 15   # 10 + 2 + 3

    def test_monk_unarmored_adds_wis(self):
        result = json.loads(calculate_ac("Monk Unarmored", dex_modifier=3, wis_modifier=2))
        assert result["ac"] == 15   # 10 + 3 + 2

    def test_natural_armor_13_plus_dex(self):
        result = json.loads(calculate_ac("Natural Armor", dex_modifier=1))
        assert result["ac"] == 14   # 13 + 1

    def test_plate_is_18(self):
        result = json.loads(calculate_ac("Plate", dex_modifier=5))
        assert result["ac"] == 18   # heavy armor, DEX ignored

    def test_unknown_armor_returns_error(self):
        result = json.loads(calculate_ac("Mithral Bikini", dex_modifier=2))
        assert "error" in result

    def test_result_has_formula(self):
        result = json.loads(calculate_ac("Leather", dex_modifier=2))
        assert "formula" in result
        assert result["formula"]

    def test_negative_dex_reduces_ac(self):
        result = json.loads(calculate_ac("Leather", dex_modifier=-1))
        assert result["ac"] == 10   # 11 + (-1)

    def test_all_armor_types_produce_valid_ac(self):
        for armor_type in ARMOR_TABLE:
            result = json.loads(calculate_ac(armor_type, dex_modifier=2,
                                             con_modifier=2, wis_modifier=2))
            assert "ac" in result, f"{armor_type} did not return ac"
            assert isinstance(result["ac"], int)
            assert 8 <= result["ac"] <= 24, f"{armor_type} returned suspicious AC {result['ac']}"


# ── pick_skills ─────────────────────────────────────────────────────────────────

class TestPickSkills:
    def test_returns_valid_json(self):
        result = json.loads(pick_skills("Fighter"))
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = json.loads(pick_skills("Fighter"))
        assert "choose" in result
        assert "available" in result
        assert "already_have" in result

    def test_fighter_chooses_2(self):
        result = json.loads(pick_skills("Fighter"))
        assert result["choose"] == 2

    def test_rogue_chooses_4(self):
        result = json.loads(pick_skills("Rogue"))
        assert result["choose"] == 4

    def test_ranger_chooses_3(self):
        result = json.loads(pick_skills("Ranger"))
        assert result["choose"] == 3

    def test_bard_any_skill_available(self):
        result = json.loads(pick_skills("Bard"))
        # Bard can pick any skill — available list should be long
        assert len(result["available"]) >= 15

    def test_background_skills_excluded(self):
        result = json.loads(pick_skills("Cleric", background_skills=["Insight", "Religion"]))
        assert "Insight" not in result["available"]
        assert "Religion" not in result["available"]

    def test_background_skills_in_already_have(self):
        result = json.loads(pick_skills("Cleric", background_skills=["Insight"]))
        assert "Insight" in result["already_have"]

    def test_fighter_only_gets_valid_class_skills(self):
        fighter_skills = set(SKILL_POOLS["Fighter"]["options"])
        result = json.loads(pick_skills("Fighter"))
        for skill in result["available"]:
            assert skill in fighter_skills, f"{skill} not in Fighter skill list"

    def test_unknown_class_returns_error(self):
        result = json.loads(pick_skills("Jedi"))
        assert "error" in result

    def test_all_classes_return_valid_result(self):
        for cls in SKILL_POOLS:
            result = json.loads(pick_skills(cls))
            assert "choose" in result
            assert result["choose"] >= 1

    def test_empty_background_skills_is_safe(self):
        result = json.loads(pick_skills("Wizard", background_skills=[]))
        assert "available" in result

    def test_all_skills_constant_is_complete(self):
        assert len(ALL_SKILLS) == 18
        assert "Perception" in ALL_SKILLS
        assert "Sleight of Hand" in ALL_SKILLS


# ── roll_deity ───────────────────────────────────────────────────────────────────

class TestRollDeity:
    def test_returns_valid_json(self):
        result = json.loads(roll_deity())
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = json.loads(roll_deity())
        for key in ("name", "domain", "alignment", "portfolio", "symbol", "flavor"):
            assert key in result, f"Missing key: {key}"

    def test_domain_hint_filters_results(self):
        # Run 20 times — all should be War domain
        for _ in range(20):
            result = json.loads(roll_deity(domain_hint="War"))
            assert "War" in result["domain"], f"Got non-War deity: {result['name']}"

    def test_alignment_hint_filters_results(self):
        for _ in range(20):
            result = json.loads(roll_deity(alignment_hint="Good"))
            assert "Good" in result["alignment"], f"Got non-Good deity: {result['name']}"

    def test_unknown_hint_falls_back_to_any(self):
        # If hint matches nothing, should still return a deity
        result = json.loads(roll_deity(domain_hint="Cheese"))
        assert "name" in result

    def test_returns_variety_without_hints(self):
        names = {json.loads(roll_deity())["name"] for _ in range(50)}
        assert len(names) >= 5, "Should see at least 5 different deities in 50 rolls"

    def test_at_least_twenty_deities(self):
        assert len(DEITIES) >= 20

    def test_all_deities_have_non_empty_flavor(self):
        for d in DEITIES:
            assert d.get("flavor"), f"{d.get('name', '?')} has empty flavor"

    def test_tyr_is_in_pool(self):
        names = {d["name"] for d in DEITIES}
        assert "Tyr" in names

    def test_deity_wiring_in_tools(self):
        import agents.dnd_agent as m
        tool_names = [t["name"] for t in m.TOOLS]
        assert "roll_deity" in tool_names

    def test_detect_phase_deity(self):
        assert detect_phase("roll_deity", set()) == "deity"

    def test_phase_message_deity(self):
        import agents.dnd_agent as m
        assert "deity" in m.PHASE_MESSAGES

    def test_run_tool_dispatches_roll_deity(self):
        import agents.dnd_agent as m
        result = json.loads(m.run_tool("roll_deity", {}))
        assert "name" in result

    def test_system_prompt_mentions_roll_deity(self):
        import agents.dnd_agent as m
        assert "roll_deity" in m.SYSTEM_PROMPT

    def test_system_prompt_mentions_pick_skills(self):
        import agents.dnd_agent as m
        assert "pick_skills" in m.SYSTEM_PROMPT

    def test_system_prompt_mentions_calculate_ac(self):
        import agents.dnd_agent as m
        assert "calculate_ac" in m.SYSTEM_PROMPT


# ── classes have typical_armor ────────────────────────────────────────────────────

class TestClassTypicalArmor:
    def test_all_classes_have_typical_armor(self):
        for name, data in CLASSES.items():
            assert "typical_armor" in data, f"{name} missing 'typical_armor'"

    def test_typical_armor_values_are_in_armor_table(self):
        for name, data in CLASSES.items():
            armor = data["typical_armor"]
            assert armor in ARMOR_TABLE, \
                f"{name} typical_armor '{armor}' not in ARMOR_TABLE"

    def test_barbarian_uses_barbarian_unarmored(self):
        assert CLASSES["Barbarian"]["typical_armor"] == "Barbarian Unarmored"

    def test_monk_uses_monk_unarmored(self):
        assert CLASSES["Monk"]["typical_armor"] == "Monk Unarmored"

    def test_fighter_uses_chain_mail(self):
        assert CLASSES["Fighter"]["typical_armor"] == "Chain Mail"


# ── detect_phase new tools ────────────────────────────────────────────────────────

class TestDetectPhaseNewTools:
    def test_calculate_ac_returns_ac(self):
        assert detect_phase("calculate_ac", set()) == "ac"

    def test_pick_skills_returns_skills(self):
        assert detect_phase("pick_skills", set()) == "skills"

    def test_roll_deity_returns_deity(self):
        assert detect_phase("roll_deity", set()) == "deity"

    def test_calculate_combat_stats_returns_combat(self):
        assert detect_phase("calculate_combat_stats", set()) == "combat"


# ── calculate_combat_stats ─────────────────────────────────────────────────────

class TestCalculateCombatStats:
    # ── return structure ────────────────────────────────────────────────────────

    def test_returns_json_string(self):
        result = calculate_combat_stats("Fighter", str_modifier=3, dex_modifier=1)
        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_proficiency_bonus_is_2(self):
        data = json.loads(calculate_combat_stats("Fighter", str_modifier=2, dex_modifier=1))
        assert data["proficiency_bonus"] == 2

    def test_proficiency_bonus_constant_matches(self):
        assert PROFICIENCY_BONUS == 2

    def test_has_initiative(self):
        data = json.loads(calculate_combat_stats("Rogue", str_modifier=0, dex_modifier=3))
        assert "initiative" in data

    def test_has_str_attack_bonus(self):
        data = json.loads(calculate_combat_stats("Fighter", str_modifier=3, dex_modifier=1))
        assert "str_attack_bonus" in data

    def test_has_dex_attack_bonus(self):
        data = json.loads(calculate_combat_stats("Rogue", str_modifier=0, dex_modifier=3))
        assert "dex_attack_bonus" in data

    # ── initiative math ────────────────────────────────────────────────────────

    def test_initiative_equals_dex_modifier(self):
        data = json.loads(calculate_combat_stats("Ranger", str_modifier=1, dex_modifier=3))
        assert data["initiative"] == "+3"

    def test_initiative_negative_dex(self):
        data = json.loads(calculate_combat_stats("Barbarian", str_modifier=4, dex_modifier=-1))
        assert data["initiative"] == "-1"

    def test_initiative_zero_dex(self):
        data = json.loads(calculate_combat_stats("Fighter", str_modifier=3, dex_modifier=0))
        assert data["initiative"] == "+0"

    # ── attack bonus math ──────────────────────────────────────────────────────

    def test_str_attack_is_str_mod_plus_proficiency(self):
        data = json.loads(calculate_combat_stats("Fighter", str_modifier=3, dex_modifier=1))
        # STR mod 3 + proficiency 2 = +5
        assert data["str_attack_bonus"] == "+5"

    def test_dex_attack_is_dex_mod_plus_proficiency(self):
        data = json.loads(calculate_combat_stats("Rogue", str_modifier=0, dex_modifier=4))
        # DEX mod 4 + proficiency 2 = +6
        assert data["dex_attack_bonus"] == "+6"

    def test_attack_bonus_with_negative_str(self):
        data = json.loads(calculate_combat_stats("Wizard", str_modifier=-1, dex_modifier=2))
        assert data["str_attack_bonus"] == "+1"   # -1 + 2

    # ── non-caster has no spell stats ─────────────────────────────────────────

    def test_barbarian_has_no_spell_save_dc(self):
        data = json.loads(calculate_combat_stats("Barbarian", str_modifier=4, dex_modifier=1))
        assert "spell_save_dc" not in data

    def test_fighter_has_no_spellcasting_ability(self):
        data = json.loads(calculate_combat_stats("Fighter", str_modifier=3, dex_modifier=2))
        assert "spellcasting_ability" not in data

    def test_rogue_has_no_spell_attack_bonus(self):
        data = json.loads(calculate_combat_stats("Rogue", str_modifier=0, dex_modifier=3))
        assert "spell_attack_bonus" not in data

    # ── caster spell stats ─────────────────────────────────────────────────────

    def test_wizard_spellcasting_ability_is_int(self):
        data = json.loads(calculate_combat_stats("Wizard", str_modifier=0, dex_modifier=1, int_modifier=3))
        assert data["spellcasting_ability"] == "INT"

    def test_wizard_spell_save_dc(self):
        # 8 + proficiency (2) + INT mod (3) = 13
        data = json.loads(calculate_combat_stats("Wizard", str_modifier=0, dex_modifier=1, int_modifier=3))
        assert data["spell_save_dc"] == 13

    def test_wizard_spell_attack_bonus(self):
        # proficiency (2) + INT mod (3) = +5
        data = json.loads(calculate_combat_stats("Wizard", str_modifier=0, dex_modifier=1, int_modifier=3))
        assert data["spell_attack_bonus"] == "+5"

    def test_cleric_spellcasting_ability_is_wis(self):
        data = json.loads(calculate_combat_stats("Cleric", str_modifier=1, dex_modifier=0, wis_modifier=3))
        assert data["spellcasting_ability"] == "WIS"

    def test_cleric_spell_save_dc(self):
        # 8 + 2 + 3 = 13
        data = json.loads(calculate_combat_stats("Cleric", str_modifier=1, dex_modifier=0, wis_modifier=3))
        assert data["spell_save_dc"] == 13

    def test_warlock_spellcasting_ability_is_cha(self):
        data = json.loads(calculate_combat_stats("Warlock", str_modifier=0, dex_modifier=1, cha_modifier=4))
        assert data["spellcasting_ability"] == "CHA"

    def test_warlock_spell_save_dc(self):
        # 8 + 2 + 4 = 14
        data = json.loads(calculate_combat_stats("Warlock", str_modifier=0, dex_modifier=1, cha_modifier=4))
        assert data["spell_save_dc"] == 14

    def test_bard_spellcasting_ability_is_cha(self):
        data = json.loads(calculate_combat_stats("Bard", str_modifier=0, dex_modifier=2, cha_modifier=3))
        assert data["spellcasting_ability"] == "CHA"

    def test_druid_spellcasting_ability_is_wis(self):
        data = json.loads(calculate_combat_stats("Druid", str_modifier=0, dex_modifier=1, wis_modifier=4))
        assert data["spellcasting_ability"] == "WIS"

    def test_ranger_spellcasting_ability_is_wis(self):
        data = json.loads(calculate_combat_stats("Ranger", str_modifier=1, dex_modifier=3, wis_modifier=2))
        assert data["spellcasting_ability"] == "WIS"

    def test_paladin_spellcasting_ability_is_cha(self):
        data = json.loads(calculate_combat_stats("Paladin", str_modifier=3, dex_modifier=1, cha_modifier=2))
        assert data["spellcasting_ability"] == "CHA"

    def test_sorcerer_spellcasting_ability_is_cha(self):
        data = json.loads(calculate_combat_stats("Sorcerer", str_modifier=0, dex_modifier=1, cha_modifier=4))
        assert data["spellcasting_ability"] == "CHA"

    # ── spellcasting stat coverage ─────────────────────────────────────────────

    def test_spellcasting_stat_has_8_classes(self):
        assert len(SPELLCASTING_STAT) == 8

    def test_spellcasting_stat_covers_all_caster_classes(self):
        expected = {"Bard", "Cleric", "Druid", "Paladin", "Ranger", "Sorcerer", "Warlock", "Wizard"}
        assert set(SPELLCASTING_STAT.keys()) == expected

    # ── unknown class error ────────────────────────────────────────────────────

    def test_unknown_class_returns_error(self):
        data = json.loads(calculate_combat_stats("Gunslinger", str_modifier=2, dex_modifier=3))
        assert "error" in data

    # ── tool wiring ────────────────────────────────────────────────────────────

    def test_tool_in_tools_list(self):
        import agents.dnd_agent as m
        names = [t["name"] for t in m.TOOLS]
        assert "calculate_combat_stats" in names

    def test_system_prompt_mentions_calculate_combat_stats(self):
        import agents.dnd_agent as m
        assert "calculate_combat_stats" in m.SYSTEM_PROMPT

    def test_system_prompt_mentions_initiative(self):
        import agents.dnd_agent as m
        assert "Initiative" in m.SYSTEM_PROMPT

    def test_system_prompt_mentions_spell_save_dc(self):
        import agents.dnd_agent as m
        assert "Spell Save DC" in m.SYSTEM_PROMPT


# ── SCAG backgrounds ───────────────────────────────────────────────────────────

class TestScagBackgrounds:
    SCAG = ["Haunted One", "Far Traveler", "City Watch", "Clan Crafter",
            "Faction Agent", "Urban Bounty Hunter", "Mercenary Veteran"]

    def test_all_scag_backgrounds_present(self):
        for bg in self.SCAG:
            assert bg in BACKGROUNDS, f"'{bg}' missing from BACKGROUNDS"

    def test_haunted_one_has_arcana(self):
        assert "Arcana" in BACKGROUNDS["Haunted One"]["skills"]

    def test_far_traveler_has_perception(self):
        assert "Perception" in BACKGROUNDS["Far Traveler"]["skills"]

    def test_city_watch_has_athletics_and_insight(self):
        bg = BACKGROUNDS["City Watch"]
        assert "Athletics" in bg["skills"]
        assert "Insight" in bg["skills"]

    def test_clan_crafter_has_history_and_insight(self):
        bg = BACKGROUNDS["Clan Crafter"]
        assert "History" in bg["skills"]
        assert "Insight" in bg["skills"]

    def test_mercenary_veteran_has_athletics_and_persuasion(self):
        bg = BACKGROUNDS["Mercenary Veteran"]
        assert "Athletics" in bg["skills"]
        assert "Persuasion" in bg["skills"]

    def test_urban_bounty_hunter_has_deception(self):
        assert "Deception" in BACKGROUNDS["Urban Bounty Hunter"]["skills"]

    def test_all_backgrounds_have_required_keys(self):
        required = {"description", "skills", "feature", "personality_seeds", "story_hooks"}
        for name, data in BACKGROUNDS.items():
            missing = required - set(data.keys())
            assert not missing, f"'{name}' missing keys: {missing}"

    def test_total_backgrounds_at_least_20(self):
        assert len(BACKGROUNDS) >= 20


# ── SUBCLASSES structure ───────────────────────────────────────────────────────

class TestSubclassesStructure:
    REQUIRED_KEYS = {"description", "level_gained", "key_feature_name", "key_feature", "flavor"}

    def test_subclasses_covers_all_12_classes(self):
        for class_name in CLASSES:
            assert class_name in SUBCLASSES, f"{class_name} missing from SUBCLASSES"

    def test_every_subclass_has_required_keys(self):
        for class_name, subs in SUBCLASSES.items():
            for sub_name, data in subs.items():
                missing = self.REQUIRED_KEYS - set(data.keys())
                assert not missing, f"{class_name}/{sub_name} missing: {missing}"

    def test_level_gained_values_are_valid(self):
        valid = {1, 2, 3}
        for class_name, subs in SUBCLASSES.items():
            for sub_name, data in subs.items():
                assert data["level_gained"] in valid, \
                    f"{class_name}/{sub_name} has invalid level_gained={data['level_gained']}"

    def test_cleric_subclasses_gain_at_level_1(self):
        for sub_name, data in SUBCLASSES["Cleric"].items():
            assert data["level_gained"] == 1, f"Cleric/{sub_name} should unlock at level 1"

    def test_warlock_subclasses_gain_at_level_1(self):
        for sub_name, data in SUBCLASSES["Warlock"].items():
            assert data["level_gained"] == 1, f"Warlock/{sub_name} should unlock at level 1"

    def test_sorcerer_subclasses_gain_at_level_1(self):
        for sub_name, data in SUBCLASSES["Sorcerer"].items():
            assert data["level_gained"] == 1, f"Sorcerer/{sub_name} should unlock at level 1"

    def test_wizard_subclasses_gain_at_level_2(self):
        for sub_name, data in SUBCLASSES["Wizard"].items():
            assert data["level_gained"] == 2, f"Wizard/{sub_name} should unlock at level 2"

    def test_druid_subclasses_gain_at_level_2(self):
        for sub_name, data in SUBCLASSES["Druid"].items():
            assert data["level_gained"] == 2, f"Druid/{sub_name} should unlock at level 2"

    def test_fighter_subclasses_gain_at_level_3(self):
        for sub_name, data in SUBCLASSES["Fighter"].items():
            assert data["level_gained"] == 3, f"Fighter/{sub_name} should unlock at level 3"

    def test_barbarian_has_berserker(self):
        assert "Path of the Berserker" in SUBCLASSES["Barbarian"]

    def test_bard_has_three_subclasses(self):
        assert len(SUBCLASSES["Bard"]) >= 3

    def test_rogue_has_assassin(self):
        assert "Assassin" in SUBCLASSES["Rogue"]

    def test_paladin_has_oathbreaker(self):
        assert "Oathbreaker" in SUBCLASSES["Paladin"]

    def test_wizard_has_eight_schools(self):
        assert len(SUBCLASSES["Wizard"]) == 8

    def test_total_subclasses_at_least_40(self):
        total = sum(len(v) for v in SUBCLASSES.values())
        assert total >= 40


# ── get_subclass_info ──────────────────────────────────────────────────────────

class TestGetSubclassInfo:
    def test_returns_json_string(self):
        result = get_subclass_info("Wizard", "School of Evocation")
        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_returns_all_required_keys(self):
        data = json.loads(get_subclass_info("Fighter", "Champion"))
        for key in ("description", "level_gained", "key_feature_name", "key_feature", "flavor"):
            assert key in data

    def test_champion_level_gained_is_3(self):
        data = json.loads(get_subclass_info("Fighter", "Champion"))
        assert data["level_gained"] == 3

    def test_life_domain_level_gained_is_1(self):
        data = json.loads(get_subclass_info("Cleric", "Life Domain"))
        assert data["level_gained"] == 1

    def test_circle_of_moon_level_gained_is_2(self):
        data = json.loads(get_subclass_info("Druid", "Circle of the Moon"))
        assert data["level_gained"] == 2

    def test_fiend_warlock_has_dark_ones_blessing(self):
        data = json.loads(get_subclass_info("Warlock", "The Fiend"))
        assert "Blessing" in data["key_feature_name"]

    def test_unknown_class_returns_error(self):
        data = json.loads(get_subclass_info("Gunslinger", "Dead Eye"))
        assert "error" in data

    def test_unknown_subclass_returns_error(self):
        data = json.loads(get_subclass_info("Wizard", "School of Pyromancy"))
        assert "error" in data

    def test_tool_in_tools_list(self):
        import agents.dnd_agent as m
        names = [t["name"] for t in m.TOOLS]
        assert "get_subclass_info" in names

    def test_system_prompt_mentions_get_subclass_info(self):
        import agents.dnd_agent as m
        assert "get_subclass_info" in m.SYSTEM_PROMPT

    def test_system_prompt_mentions_subclass_row(self):
        import agents.dnd_agent as m
        assert "Subclass" in m.SYSTEM_PROMPT

    def test_detect_phase_subclass(self):
        assert detect_phase("get_subclass_info", set()) == "subclass"

    def test_phase_message_subclass(self):
        import agents.dnd_agent as m
        assert "subclass" in m.PHASE_MESSAGES


# ── Villain mode ───────────────────────────────────────────────────────────────

class TestVillainData:
    def test_villain_schemes_at_least_8(self):
        assert len(VILLAIN_SCHEMES) >= 8

    def test_villain_wounds_at_least_8(self):
        assert len(VILLAIN_WOUNDS) >= 8

    def test_scheme_has_required_keys(self):
        required = {"scheme", "goal", "method", "signature"}
        for s in VILLAIN_SCHEMES:
            missing = required - set(s.keys())
            assert not missing, f"Scheme '{s.get('scheme')}' missing: {missing}"

    def test_wound_has_required_keys(self):
        required = {"wound", "origin", "what_it_did", "what_remains"}
        for w in VILLAIN_WOUNDS:
            missing = required - set(w.keys())
            assert not missing, f"Wound '{w.get('wound')}' missing: {missing}"

    def test_revenge_scheme_present(self):
        names = {s["scheme"] for s in VILLAIN_SCHEMES}
        assert "Revenge" in names

    def test_betrayal_wound_present(self):
        names = {w["wound"] for w in VILLAIN_WOUNDS}
        assert "Betrayal" in names

    def test_all_scheme_goals_non_empty(self):
        for s in VILLAIN_SCHEMES:
            assert len(s["goal"]) > 10, f"Scheme '{s['scheme']}' has thin goal"

    def test_all_wound_origins_non_empty(self):
        for w in VILLAIN_WOUNDS:
            assert len(w["origin"]) > 10, f"Wound '{w['wound']}' has thin origin"


class TestRollVillainProfile:
    def test_returns_json_string(self):
        result = roll_villain_profile()
        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_scheme_and_wound_keys(self):
        data = json.loads(roll_villain_profile())
        assert "scheme" in data
        assert "wound" in data

    def test_scheme_is_dict(self):
        data = json.loads(roll_villain_profile())
        assert isinstance(data["scheme"], dict)

    def test_wound_is_dict(self):
        data = json.loads(roll_villain_profile())
        assert isinstance(data["wound"], dict)

    def test_returns_variety_across_rolls(self):
        schemes = set()
        for _ in range(30):
            data = json.loads(roll_villain_profile())
            schemes.add(data["scheme"]["scheme"])
        assert len(schemes) >= 3, "Expected variety in villain schemes over 30 rolls"

    def test_tool_in_tools_list(self):
        import agents.dnd_agent as m
        names = [t["name"] for t in m.TOOLS]
        assert "roll_villain_profile" in names

    def test_villain_system_prompt_exists(self):
        import agents.dnd_agent as m
        assert hasattr(m, "VILLAIN_SYSTEM_PROMPT")
        assert len(m.VILLAIN_SYSTEM_PROMPT) > 200

    def test_villain_system_prompt_mentions_scheme(self):
        import agents.dnd_agent as m
        assert "Scheme" in m.VILLAIN_SYSTEM_PROMPT

    def test_villain_system_prompt_mentions_wound(self):
        import agents.dnd_agent as m
        assert "Wound" in m.VILLAIN_SYSTEM_PROMPT

    def test_villain_system_prompt_mentions_defeat_condition(self):
        import agents.dnd_agent as m
        assert "Defeat Condition" in m.VILLAIN_SYSTEM_PROMPT

    def test_villain_system_prompt_mentions_minions(self):
        import agents.dnd_agent as m
        assert "Minions" in m.VILLAIN_SYSTEM_PROMPT

    def test_detect_phase_villain(self):
        assert detect_phase("roll_villain_profile", set()) == "villain"

    def test_run_includes_villain_mode(self):
        import inspect, agents.dnd_agent as m
        source = inspect.getsource(m.run)
        assert "villain" in source
