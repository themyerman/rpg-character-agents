"""
Mongoose Traveller 2e Character Generator
Creates vivid storytelling characters using Traveller mechanics.

Run with: python traveller_agent.py
"""

import json
import random
import re
from pathlib import Path
import anthropic

client = anthropic.Anthropic()


# ── Constants ──────────────────────────────────────────────────────────────────

VALID_DICE = {6}
MIN_ROLLS  = 1
MAX_ROLLS  = 20


# ── Utility functions ──────────────────────────────────────────────────────────

def characteristic_modifier(value: int) -> int:
    """Mongoose 2e DM table."""
    if value <= 0:    return -3
    elif value <= 2:  return -2
    elif value <= 5:  return -1
    elif value <= 8:  return 0
    elif value <= 11: return 1
    elif value <= 14: return 2
    else:             return 3

def to_hex_char(n: int) -> str:
    if n < 10:
        return str(n)
    return chr(ord('A') + n - 10)  # 10=A, 11=B … 15=F


# ── UWP tables ─────────────────────────────────────────────────────────────────

STARPORT_CODES = {
    2:  ("X", "no starport — world effectively cut off from interstellar trade"),
    3:  ("X", "no starport — world effectively cut off from interstellar trade"),
    4:  ("E", "frontier installation — a landing pad, no refined fuel, minimal services"),
    5:  ("E", "frontier installation — a landing pad, no refined fuel, minimal services"),
    6:  ("D", "poor quality — unrefined fuel only, very limited repairs"),
    7:  ("D", "poor quality — unrefined fuel only, very limited repairs"),
    8:  ("C", "routine — unrefined fuel, some repair capability"),
    9:  ("C", "routine — unrefined fuel, some repair capability"),
    10: ("B", "good — refined fuel, shipyard for non-jump drives"),
    11: ("B", "good — refined fuel, shipyard for non-jump drives"),
    12: ("A", "excellent — refined fuel, full shipyard, all services"),
}

ATMOSPHERE_TYPES = {
    0:  ("None",              "airless — vacc suit required at all times"),
    1:  ("Trace",             "almost airless — vacc suit required"),
    2:  ("Very Thin/Tainted", "requires respirator and filter mask"),
    3:  ("Very Thin",         "requires respirator — breathable only with equipment"),
    4:  ("Thin/Tainted",      "filter mask required — thin but contaminated"),
    5:  ("Thin",              "breathable but low oxygen — acclimatisation needed"),
    6:  ("Standard",          "breathable, Earth-normal — no equipment needed"),
    7:  ("Standard/Tainted",  "breathable pressure but contaminated — filter mask needed"),
    8:  ("Dense",             "breathable but high pressure — takes adjustment"),
    9:  ("Dense/Tainted",     "high pressure and contaminated — filter mask needed"),
    10: ("Exotic",            "unbreathable but non-corrosive — air supply required"),
    11: ("Corrosive",         "actively destructive to exposed tissue — vacc suit required"),
    12: ("Insidious",         "penetrates standard protection — best sealed suit required"),
    13: ("Dense/High-O2",     "breathable but dangerously oxygen-rich"),
    14: ("Thin/Low-O2",       "very thin, low oxygen — respirator needed"),
    15: ("Unusual",           "exotic conditions — special equipment may be needed"),
}

GOVERNMENT_TYPES = {
    0:  "None (anarchy — no central authority)",
    1:  "Company/Corporation (a commercial entity runs the world)",
    2:  "Participating Democracy (citizens vote directly on all issues)",
    3:  "Self-Perpetuating Oligarchy (a small elite maintains power by controlling succession)",
    4:  "Representative Democracy (elected officials govern on behalf of citizens)",
    5:  "Feudal Technocracy (those who control technology hold power)",
    6:  "Captive Government (controlled by an outside interstellar power)",
    7:  "Balkanization (many competing factions, no single ruling body)",
    8:  "Civil Service Bureaucracy (government by trained professional administrators)",
    9:  "Impersonal Bureaucracy (faceless institutional government — rules over people)",
    10: "Charismatic Dictator (one powerful leader rules by force of personality)",
    11: "Non-Charismatic Leader (ruler maintains power through fear or institutional control)",
    12: "Charismatic Oligarchy (a small group rules through collective cult of personality)",
    13: "Religious Dictatorship (theocracy — religious law is state law)",
}

LAW_LEVEL_DESC = {
    0: "no law whatsoever — anything goes",
    1: "almost no law — only WMDs and battle dress prohibited",
    2: "minimal law — energy weapons prohibited",
    3: "low law — military weapons prohibited, most others legal",
    4: "moderate law — personal firearms restricted",
    5: "moderate law — personal concealable weapons restricted",
    6: "fairly strict — all firearms prohibited, bladed weapons permitted",
    7: "strict — most bladed weapons prohibited in public",
    8: "very strict — all weapons prohibited, even improvised ones",
    9: "extreme law — authorities suspicious of everything; many everyday items prohibited",
}

TL_DESC = {
    0:  "Stone Age (pre-industrial, hand tools only)",
    1:  "Bronze/Iron Age (basic metallurgy, animal power)",
    2:  "Early Industrial (steam power, basic printing)",
    3:  "Industrial Revolution (railways, rifles, telegraphs)",
    4:  "Early 20th century (combustion engines, radio, aircraft)",
    5:  "Late 20th century (computers, basic space capability)",
    6:  "Fusion power, early jump drive theory",
    7:  "Advanced fusion, early interstellar capability",
    8:  "Jump drives, standard interstellar travel — typical Imperium frontier",
    9:  "Anti-grav common, advanced computers, enhanced medicine",
    10: "Gravitic vehicles, enhanced soldiers, sophisticated robotics",
    11: "Broad synthetic materials, early artificial consciousness",
    12: "Average Imperium — jump-3, advanced robotics, excellent medicine",
    13: "Jump-4, gravitic hull construction, early psionic research",
    14: "Jump-5, advanced battle dress, significant life extension",
    15: "Jump-6, exotic matter manipulation — rare even in the Imperium",
}

# Background skill pools keyed by world characteristic — Claude picks 3
BACKGROUND_SKILL_POOLS = {
    "high_pop":      ["Streetwise", "Broker", "Persuade", "Deception", "Carouse", "Admin"],
    "low_pop":       ["Survival", "Recon", "Animals", "Navigation", "Mechanic"],
    "high_law":      ["Advocate", "Deception", "Admin", "Stealth", "Streetwise"],
    "low_law":       ["Gun Combat", "Melee", "Recon", "Survival"],
    "industrial":    ["Mechanic", "Trade", "Electronics", "Drive", "Engineer"],
    "agricultural":  ["Animals", "Survival", "Trade", "Drive", "Profession"],
    "high_tech":     ["Science", "Electronics", "Medic", "Computers", "Engineer"],
    "low_tech":      ["Animals", "Mechanic", "Survival", "Trade", "Drive"],
    "good_port":     ["Broker", "Admin", "Diplomat", "Persuade", "Trade"],
    "frontier_port": ["Survival", "Mechanic", "Gun Combat", "Recon", "Navigation"],
    "water_world":   ["Seafarer", "Athletics", "Survival", "Science", "Mechanic"],
    "desert":        ["Survival", "Recon", "Athletics", "Animals", "Navigation"],
}


# ── UWP homeworld generation ───────────────────────────────────────────────────

def roll_homeworld_uwp() -> str:
    """Roll a complete UWP for the character's homeworld and return a JSON profile."""

    def d6(n: int = 2) -> int:
        return sum(random.randint(1, 6) for _ in range(n))

    # Starport
    sp_code, sp_desc = STARPORT_CODES.get(d6(), ("X", "no starport"))

    # Size (2d6-2, min 0)
    size = max(0, d6() - 2)
    size_desc = (
        "tiny asteroid, negligible gravity"       if size == 0 else
        "small world, very low gravity"           if size <= 2 else
        "small world, low gravity"                if size <= 4 else
        "medium world, moderate gravity"          if size <= 6 else
        "Earth-sized, standard gravity"           if size <= 8 else
        "large world, high gravity"
    )

    # Atmosphere (2d6-7+Size, clamped 0–15)
    atmo = max(0, min(15, d6() - 7 + size))
    atmo_name, atmo_desc = ATMOSPHERE_TYPES.get(atmo, ("Unknown", "unusual conditions"))

    # Hydrographics (2d6-7+Atmo, adjusted, clamped 0–10)
    hydro_raw = d6() - 7 + atmo
    if atmo <= 1 or atmo >= 10:
        hydro_raw -= 4   # frozen/corrosive worlds hold little liquid
    if size <= 1:
        hydro_raw = -99  # tiny worlds can't retain liquid
    hydro = max(0, min(10, hydro_raw))
    hydro_desc = (
        "no standing liquid — true desert world"              if hydro == 0 else
        f"arid — {hydro * 10}% liquid coverage"              if hydro <= 2 else
        f"dry — {hydro * 10}% liquid coverage"               if hydro <= 4 else
        f"average — {hydro * 10}% liquid coverage"           if hydro <= 6 else
        f"wet — {hydro * 10}% liquid coverage"               if hydro <= 8 else
        f"water world — {hydro * 10}% liquid coverage"
    )

    # Population (2d6-2, min 0)
    pop = max(0, d6() - 2)
    pop_desc = (
        "no permanent population"           if pop == 0 else
        "tiny — a few dozen people"         if pop == 1 else
        "very small — hundreds"             if pop == 2 else
        "small — thousands"                 if pop == 3 else
        "modest — tens of thousands"        if pop == 4 else
        "moderate — hundreds of thousands"  if pop == 5 else
        "significant — millions"            if pop == 6 else
        "large — tens of millions"          if pop == 7 else
        "major — hundreds of millions"      if pop == 8 else
        "enormous — billions"               if pop == 9 else
        "teeming — tens of billions"
    )

    # Government (2d6-7+Pop, clamped 0–13)
    gov = max(0, min(13, d6() - 7 + pop))
    gov_desc = GOVERNMENT_TYPES.get(gov, "unusual government structure")

    # Law Level (2d6-7+Gov, min 0)
    law = max(0, d6() - 7 + gov)
    law_desc = LAW_LEVEL_DESC.get(min(9, law), "extreme law — total social control")

    # Tech Level (1d6 + DMs from starport, size, atmosphere, population, government)
    tl_dm = {"A": 6, "B": 4, "C": 2, "D": 0, "E": -2, "X": -4}.get(sp_code, 0)
    if size <= 1:   tl_dm += 2
    elif size <= 4: tl_dm += 1
    if atmo <= 3 or atmo >= 10: tl_dm += 1
    if hydro == 10: tl_dm += 2
    elif hydro == 9: tl_dm += 1
    if pop >= 9:   tl_dm += 2
    elif pop >= 1: tl_dm += 1
    if gov in (0, 5): tl_dm += 1
    elif gov == 13:   tl_dm -= 2
    tl = max(0, min(15, d6(1) + tl_dm))
    tl_desc = TL_DESC.get(tl, "beyond standard Imperial technology")

    # UWP string
    uwp = (f"{sp_code}"
           f"{to_hex_char(size)}{to_hex_char(atmo)}{to_hex_char(hydro)}"
           f"{to_hex_char(pop)}{to_hex_char(gov)}{to_hex_char(law)}"
           f"-{to_hex_char(tl)}")

    # Derive applicable background skill pools
    pools = []
    if pop >= 7:                                                  pools.append("high_pop")
    if pop <= 3:                                                  pools.append("low_pop")
    if law >= 7:                                                  pools.append("high_law")
    if law <= 2:                                                  pools.append("low_law")
    if pop >= 8 and tl >= 8:                                      pools.append("industrial")
    if 4 <= atmo <= 9 and 3 <= hydro <= 8 and 4 <= pop <= 7:     pools.append("agricultural")
    if tl >= 10:                                                  pools.append("high_tech")
    if tl <= 4:                                                   pools.append("low_tech")
    if sp_code in ("A", "B"):                                     pools.append("good_port")
    if sp_code in ("D", "E", "X"):                                pools.append("frontier_port")
    if hydro >= 9:                                                pools.append("water_world")
    if hydro == 0 and 4 <= atmo <= 9:                             pools.append("desert")
    if not pools:
        pools.append("high_pop" if pop >= 5 else "low_pop")

    # Flatten and deduplicate skill candidates
    seen_s: set = set()
    skills: list = []
    for pool in pools:
        for s in BACKGROUND_SKILL_POOLS.get(pool, []):
            if s not in seen_s:
                seen_s.add(s)
                skills.append(s)

    result = {
        "uwp":        uwp,
        "starport":   f"{sp_code} — {sp_desc}",
        "size":       f"{size} — {size_desc}",
        "atmosphere": f"{atmo} ({atmo_name}) — {atmo_desc}",
        "hydro":      f"{hydro} — {hydro_desc}",
        "population": f"{pop} — {pop_desc}",
        "government": f"{gov} — {gov_desc}",
        "law_level":  f"{law} — {law_desc}",
        "tech_level": f"{tl} ({to_hex_char(tl)}) — {tl_desc}",
        "suggested_background_skills": skills[:12],
    }
    return json.dumps(result, indent=2)


# ── Career data ────────────────────────────────────────────────────────────────

CAREERS = {
    "Navy": {
        "description": "Serving aboard interstellar warships",
        "qualification": {"characteristic": "Intelligence", "target": 6},
        "survival":     {"characteristic": "Intelligence", "target": 5},
        "advancement":  {"characteristic": "Education",    "target": 7},
        "ranks":  ["Crewman", "Able Spacehand", "Petty Officer", "Chief Petty Officer", "Ensign", "Sublieutenant", "Lieutenant"],
        "skills": ["Pilot", "Gunner", "Engineer", "Mechanic", "Vacc Suit", "Electronics", "Tactics", "Leadership", "Navigation", "Admin", "Athletics", "Steward"],
        "mishap": "A catastrophic battle, accident in space, or court martial ended your naval career.",
    },
    "Army": {
        "description": "Planetary armed forces, ground combat",
        "qualification": {"characteristic": "Endurance", "target": 5},
        "survival":     {"characteristic": "Endurance", "target": 5},
        "advancement":  {"characteristic": "Education",  "target": 6},
        "ranks":  ["Private", "Lance Corporal", "Corporal", "Lance Sergeant", "Sergeant", "Gunnery Sergeant", "Sergeant Major"],
        "skills": ["Gun Combat", "Heavy Weapons", "Recon", "Athletics", "Melee", "Drive", "Survival", "Leadership", "Tactics", "Medic", "Electronics", "Explosives"],
        "mishap": "Wounded in action, dishonorably discharged, or caught in a political purge.",
    },
    "Marines": {
        "description": "Elite shipboard troops, boarding actions and rapid response",
        "qualification": {"characteristic": "Endurance", "target": 6},
        "survival":     {"characteristic": "Endurance", "target": 6},
        "advancement":  {"characteristic": "Education",  "target": 7},
        "ranks":  ["Marine", "Lance Corporal", "Corporal", "Lance Sergeant", "Sergeant", "Staff Sergeant", "Gunnery Sergeant"],
        "skills": ["Gun Combat", "Melee", "Vacc Suit", "Athletics", "Tactics", "Heavy Weapons", "Recon", "Stealth", "Leadership", "Medic", "Electronics"],
        "mishap": "A failed mission, severe injury, or dishonorable incident ended your marine career.",
    },
    "Scouts": {
        "description": "Lone explorers charting unknown space, carrying messages",
        "qualification": {"characteristic": "Intelligence", "target": 6},
        "survival":     {"characteristic": "Endurance",    "target": 7},
        "advancement":  {"characteristic": "Education",    "target": 9},
        "ranks":  ["Scout", "Senior Scout", "Surveyor", "Explorer"],
        "skills": ["Pilot", "Navigation", "Survival", "Recon", "Electronics", "Mechanic", "Astrogation", "Jack-of-All-Trades", "Gun Combat", "Science", "Medic", "Vacc Suit"],
        "mishap": "Lost in uncharted space, crashed on a hostile world, or exposed to something that changed you.",
    },
    "Merchant": {
        "description": "Free traders and megacorporate shipping crews",
        "qualification": {"characteristic": "Intelligence", "target": 4},
        "survival":     {"characteristic": "Endurance",    "target": 5},
        "advancement":  {"characteristic": "Intelligence", "target": 6},
        "ranks":  ["Crewman", "Senior Crewman", "4th Officer", "3rd Officer", "2nd Officer", "1st Officer", "Captain"],
        "skills": ["Pilot", "Broker", "Steward", "Mechanic", "Engineer", "Navigation", "Streetwise", "Admin", "Persuade", "Trade", "Electronics", "Astrogation"],
        "mishap": "A bad deal, pirate attack, cargo scandal, or bankruptcy ended your merchant career.",
    },
    "Agent": {
        "description": "Intelligence operatives, law enforcement, corporate spies",
        "qualification": {"characteristic": "Intelligence", "target": 6},
        "survival":     {"characteristic": "Intelligence", "target": 6},
        "advancement":  {"characteristic": "Intelligence", "target": 7},
        "ranks":  ["Agent", "Field Agent", "Special Agent", "Field Supervisor", "Special Supervisor", "Assistant Director", "Director"],
        "skills": ["Deception", "Recon", "Stealth", "Electronics", "Investigate", "Persuade", "Gun Combat", "Melee", "Streetwise", "Admin", "Advocate", "Computers"],
        "mishap": "A blown cover, compromised operation, or dangerous secret forced you out.",
    },
    "Citizen": {
        "description": "Civilian careers — corporate workers, colonists, technicians",
        "qualification": {"characteristic": "Endurance",    "target": 4},
        "survival":     {"characteristic": "Endurance",    "target": 5},
        "advancement":  {"characteristic": "Intelligence", "target": 6},
        "ranks":  ["Civilian", "District Manager", "Controller", "Manager", "Director", "Vice President"],
        "skills": ["Admin", "Trade", "Electronics", "Mechanic", "Drive", "Profession", "Science", "Medic", "Broker", "Persuade", "Steward", "Computers"],
        "mishap": "Corporate downsizing, scandal, or a personal crisis ended your civilian career.",
    },
    "Entertainer": {
        "description": "Artists, performers, journalists, media personalities",
        "qualification": {"characteristic": "Dexterity",      "target": 5},
        "survival":     {"characteristic": "Social Standing", "target": 4},
        "advancement":  {"characteristic": "Intelligence",    "target": 6},
        "ranks":  ["Performer", "Artist", "Entertainer", "Famous Entertainer"],
        "skills": ["Art", "Persuade", "Athletics", "Carouse", "Deception", "Drive", "Electronics", "Investigate", "Recon", "Science", "Streetwise"],
        "mishap": "A public scandal, addiction, creative burnout, or dangerous story ended your entertainment career.",
    },
    "Drifter": {
        "description": "Wanderers with no fixed career — vagabonds and survivors",
        "qualification": None,
        "survival":     {"characteristic": "Endurance", "target": 5},
        "advancement":  {"characteristic": "Strength",  "target": 8},
        "ranks":  ["Wanderer", "Survivor"],
        "skills": ["Survival", "Athletics", "Melee", "Streetwise", "Recon", "Stealth", "Navigation", "Jack-of-All-Trades", "Gun Combat", "Deception", "Carouse"],
        "mishap": "Even drifting has its dangers — stranded, imprisoned, or nearly killed.",
    },
    "Noble": {
        "description": "Aristocracy — diplomats, dilettantes, political players",
        "qualification": {"characteristic": "Social Standing", "target": 10},
        "survival":     {"characteristic": "Social Standing", "target": 4},
        "advancement":  {"characteristic": "Education",       "target": 8},
        "ranks":  ["Assistant", "Attaché", "3rd Secretary", "2nd Secretary", "1st Secretary", "Counsellor", "Ambassador"],
        "skills": ["Admin", "Advocate", "Diplomat", "Persuade", "Art", "Carouse", "Leadership", "Science", "Trade", "Electronics", "Steward", "Deception"],
        "mishap": "A political scandal, family disgrace, or enemy at court stripped you of your standing.",
    },
    "Rogue": {
        "description": "Criminals, pirates, and those who live outside the law",
        "qualification": {"characteristic": "Dexterity",   "target": 6},
        "survival":     {"characteristic": "Dexterity",    "target": 6},
        "advancement":  {"characteristic": "Intelligence", "target": 6},
        "ranks":  ["Lackey", "Hoodlum", "Thug", "Enforcer", "Gangster", "Racketeer", "Boss"],
        "skills": ["Deception", "Stealth", "Streetwise", "Gun Combat", "Melee", "Recon", "Persuade", "Pilot", "Electronics", "Broker", "Carouse", "Explosives"],
        "mishap": "Betrayed by partners, imprisoned, or hunted by authorities.",
    },
    "Scholar": {
        "description": "Scientists, doctors, researchers, and academics",
        "qualification": {"characteristic": "Education",   "target": 6},
        "survival":     {"characteristic": "Education",   "target": 5},
        "advancement":  {"characteristic": "Intelligence", "target": 7},
        "ranks":  ["Research Assistant", "Researcher", "Senior Researcher", "Associate", "Associate Professor", "Professor"],
        "skills": ["Science", "Medic", "Computers", "Electronics", "Investigate", "Admin", "Advocate", "Diplomat", "Engineer", "Navigation", "Pilot", "Persuade"],
        "mishap": "A failed experiment, grant scandal, dangerous discovery, or academic politics ended your research career.",
    },
}

CASH_TABLE    = [1000, 5000, 10000, 10000, 20000, 40000, 50000]
BENEFIT_TABLE = ["Low Passage", "INT +1", "EDU +1", "Weapon", "High Passage", "SOC +1", "Ship Share"]
PENSION_TABLE = {5: 10000, 6: 20000, 7: 30000, 8: 40000}


# ── Tools (Python side) ────────────────────────────────────────────────────────

def roll_dice(sides: int, count: int = 1) -> str:
    if sides not in VALID_DICE:
        return f"Error: {sides} is not a valid die. Choose from: {sorted(VALID_DICE)}"
    if not (MIN_ROLLS <= count <= MAX_ROLLS):
        return f"Error: count must be between {MIN_ROLLS} and {MAX_ROLLS}, got {count}"
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"

def roll_d66() -> str:
    tens  = random.randint(1, 6)
    units = random.randint(1, 6)
    return f"Rolled d66: {tens * 10 + units}  (tens: {tens}, units: {units})"

def get_career_info(career_name: str) -> str:
    if career_name not in CAREERS:
        return f"Unknown career '{career_name}'. Available: {list(CAREERS.keys())}"
    return str(CAREERS[career_name])

def get_characteristic_modifier(value: int) -> str:
    mod  = characteristic_modifier(value)
    sign = "+" if mod >= 0 else ""
    return f"Characteristic value {value} → DM {sign}{mod}"

def compute_upp(characteristics: list) -> str:
    if len(characteristics) != 6:
        return f"Error: need exactly 6 characteristics, got {len(characteristics)}"
    return "UPP: " + "".join(to_hex_char(c) for c in characteristics)


# ── Tool schemas (Claude's side) ───────────────────────────────────────────────

TOOLS = [
    {
        "name": "roll_dice",
        "description": "Roll one or more d6. Use 2d6 for stats, qualification, survival, advancement, aging, and muster out rolls.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {
                    "type": "integer",
                    "description": "Number of sides. Traveller only uses d6.",
                    "enum": [6],
                },
                "count": {
                    "type": "integer",
                    "description": "Number of dice (use 2 for standard 2d6).",
                    "minimum": MIN_ROLLS,
                    "maximum": MAX_ROLLS,
                },
            },
            "required": ["sides"],
        },
    },
    {
        "name": "roll_d66",
        "description": "Roll a d66 for career events. Two d6s: first is tens digit, second is units. Returns 11–66.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_homeworld_uwp",
        "description": (
            "Roll a complete Universal World Profile (UWP) for the character's homeworld. "
            "Returns starport, size, atmosphere, hydrographics, population, government, law level, "
            "tech level, and a list of suggested background skills derived from the world's profile."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_career_info",
        "description": "Look up a career's qualification, survival, advancement targets, ranks, and available skills.",
        "input_schema": {
            "type": "object",
            "properties": {
                "career_name": {
                    "type": "string",
                    "description": "Career name.",
                    "enum": list(CAREERS.keys()),
                },
            },
            "required": ["career_name"],
        },
    },
    {
        "name": "get_characteristic_modifier",
        "description": "Get the DM for a characteristic value. Use before qualification, survival, and advancement rolls.",
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "integer", "description": "Characteristic value (0–15)."},
            },
            "required": ["value"],
        },
    },
    {
        "name": "compute_upp",
        "description": "Convert 6 characteristic values into a Traveller UPP hex string.",
        "input_schema": {
            "type": "object",
            "properties": {
                "characteristics": {
                    "type": "array",
                    "description": "[STR, DEX, END, INT, EDU, SOC] as integers.",
                    "items": {"type": "integer"},
                    "minItems": 6,
                    "maxItems": 6,
                },
            },
            "required": ["characteristics"],
        },
    },
]


# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Mongoose Traveller 2nd Edition character generator creating vivid storytelling characters.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

The Third Imperium is a vast, diverse civilization — character names should reflect that. Draw from Slavic, Arabic, South Asian, East Asian, West African, Spanish, Scandinavian, and other traditions alongside invented Vilani and Solomani conventions. Vary first letters, syllable counts, and cultural origins. Do not cluster on similar-sounding names.

Work through these steps in order, using your tools at each stage:

1. CHARACTERISTICS — Roll 2d6 six times for: Strength, Dexterity, Endurance, Intelligence, Education, Social Standing.
   Then call compute_upp with all six values.

2. HOMEWORLD — Call roll_homeworld_uwp to generate the world. Read the full UWP profile it returns.
   - Invent a name for the world that fits its character.
   - Choose 3 background skills from the suggested list that make sense for this specific world.
   - Note the atmosphere (breathable? hostile?), government, and law level — these should color the character's upbringing.

3. CAREER — Choose a career that suits the stats. Look it up with get_career_info.
   - Get the characteristic modifier for the qualifying stat, then roll 2d6 and add it.
   - If total >= target: they're in. If not: they become a Drifter instead.

4. CAREER TERMS — Run 2 to 6 terms (each term = 4 years of life, starting age 18).
   Each term:
   a. SURVIVAL — get the modifier, roll 2d6 + DM vs. target. Fail = dramatic mishap, career ends.
   b. EVENT — roll d66 and interpret it as something vivid and specific that happened that term.
      CONNECTIONS — whenever an event or mishap would naturally produce a person:
        - a patron, mentor, or ally who helped them → generate as an ALLY or CONTACT
        - an enemy, betrayer, or rival → generate as an ENEMY or RIVAL
      Give each connection a full name, a one-sentence description, and their relationship to the character.
      Connections are named NPCs, not abstractions.
   c. SKILLS — pick 1–2 skills appropriate to what happened that term.
   d. ADVANCEMENT — roll 2d6 + DM vs. target. Success = next rank.
   e. AGING — from term 5 (age 34+), roll 1d6 separately for STR, DEX, and END.
      On a 1 or 2: that characteristic drops by 1. Note it — the body starting to show the years.
      From term 8 (age 46+): also roll for INT.

5. MUSTER OUT — For each term served, roll 1d6 once on the cash table and once on the benefits table.
   Cash table (1-indexed): [1000, 5000, 10000, 10000, 20000, 40000, 50000]
   Benefits: ["Low Passage", "INT +1", "EDU +1", "Weapon", "High Passage", "SOC +1", "Ship Share"]
   PENSION — 5+ terms: Cr10,000/yr | 6: Cr20,000/yr | 7: Cr30,000/yr | 8+: Cr40,000/yr

6. CHARACTER SHEET — Always use exactly this format:

## **[Full Name with nickname in quotes if fitting]**

| | |
|---|---|
| **UPP** | [hex string] |
| **Age** | [age] |
| **Homeworld** | [Name] ([UWP code]) — [one evocative phrase about the world] |
| **Career** | [Career] ([final rank] — [N] terms, [how it ended]) |

### Characteristics
- **STR [value][hex if 10+]** — [one evocative phrase about what this means physically]
- **DEX [value][hex if 10+]** — [one evocative phrase]
- **END [value][hex if 10+]** — [one evocative phrase]
- **INT [value][hex if 10+]** — [one evocative phrase]
- **EDU [value][hex if 10+]** — [one evocative phrase]
- **SOC [value][hex if 10+]** — [one evocative phrase about their place in society]

For characteristics 10+, show the hex letter in parentheses: e.g. **DEX 12 (C)**. Italicise stats 11+.

### Skills
List each skill once on its own line. Bold the entire entry for skills at level 2+ — do not write the skill name twice.
  Examples: `- Pilot 1` / `- **Deception 2**` / `- **Melee 3**`
For the single highest-rated skill only, add one italic sentence (on a new line below it) about how they got it or what it cost them.

### Career History
One paragraph per term, labeled **Term N (age–age):**. Make each term feel like a chapter of a life.

### Connections
List each named NPC generated during play, formatted as:
- **[Category] — [Full Name]:** [one sentence: who they are and how they connect to this character]
Categories: Ally, Contact, Enemy, Rival.
If no connections were generated, omit this section entirely.

### Muster Out
- Cash total (give it a brief story — where is it, how is it held?)
- Each benefit on its own line
- SHIP SHARES: if the character has one or two Ship Shares, do NOT treat it as a simple asset.
  Write 2-3 sentences as a dangling thread: what ship, what route, why it's complicated.
  One of these must be true: the ship isn't where it should be, someone wants to buy them out,
  the other shareholders are interesting, or the ship is impounded/missing/involved in something.
  Make it feel like unfinished business.
- Pension (if applicable)

### Backstory
Three sentences. A past, a wound, and a direction.

Let the dice tell the story. A bad survival roll shouldn't be boring — it should be the most interesting thing that ever happened to them. Make it feel like a life."""

NPC_SYSTEM_PROMPT = """You are a Mongoose Traveller 2e NPC generator. Create a vivid, instantly usable NPC sketch.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

The Third Imperium is a vast, diverse civilization — character names should reflect that. Draw from Slavic, Arabic, South Asian, East Asian, West African, Spanish, Scandinavian, and other traditions alongside invented Vilani and Solomani conventions. Vary first letters, syllable counts, and cultural origins.

Roll a UPP using roll_dice(sides=6, count=2) six times, then compute_upp.
Look up a career with get_career_info if it helps ground them. Skip career terms entirely — this is a sketch, not a history.

Always use exactly this format:

## **[Name]**
*[Career] [Rank] — [one sharp hook sentence]*

| | |
|---|---|
| **UPP** | [hex string] |
| **Career** | [career and rank — one term is enough] |
| **Notable Skills** | [2-3 key skills with levels] |

**Demeanor:** [1-2 sentences — how they present, what you notice first]
**Wants:** [what they need right now — specific]
**Secret:** [one thing they're hiding — specific, not vague]
**Hook:** [one concrete way they pull the characters into their orbit]
**Connection:** [one named person they love, fear, or owe — and why it matters]"""

PATRON_SYSTEM_PROMPT = """You are a Mongoose Traveller 2e patron generator. Create a complete patron encounter — someone who walks up to the crew in a starport bar, a hotel lobby, or a dockside office and offers them a job.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

The Third Imperium is a vast, diverse civilization — character names should reflect that. Draw from Slavic, Arabic, South Asian, East Asian, West African, Spanish, Scandinavian, and other traditions alongside invented Vilani and Solomani conventions. Vary first letters, syllable counts, and cultural origins.

Roll a UPP using roll_dice(sides=6, count=2) six times, then compute_upp.
Look up a career with get_career_info to establish who they appear to be.

The patron encounter has a classic Traveller structure: the job looks one way on the surface, but there are multiple possible truths — the referee rolls 1d4 and only they know which is real. Make all four truths plausible from the crew's perspective.

Always use exactly this format:

## **[Full Name]**
*Patron — [who they appear to be in one phrase]*

| | |
|---|---|
| **UPP** | [hex string] |
| **Apparent Affiliation** | [what they claim to represent — corporation, government, private individual, etc.] |
| **Real Affiliation** | [what they actually represent — revealed only in Truth 2 or 3] |

**Appearance:** [2 sentences — what the crew sees when this person approaches. Specific details: clothing, manner, what they're drinking, what they don't say.]

**The Pitch:** *[Write this as direct speech — what the patron actually says to the crew. 3-5 sentences. Make it sound like a real person, not a mission briefing.]*

**The Job:** [What they claim to want done — destination, cargo, person, task. Specific.]

**The Payment:** [What's on the table. Be specific — credits, information, equipment, a favour from someone powerful.]

**The Truth (Referee rolls 1d4 — only one is real):**
1. **Straightforward** — [Everything is exactly as stated. The job is clean. This should still have an interesting complication — just not a deceptive one.]
2. **One Layer Down** — [The patron is not quite who they say they are, or the job is not quite what they said. The crew is being used for something they weren't told. Not necessarily dangerous — but not what was advertised.]
3. **The Real Story** — [The job is a cover for something else entirely. The patron has a hidden agenda. The crew is either a pawn, an unwitting accomplice, or the only people who can stop something. Make this dramatic but not cartoonish.]
4. **The Reversal** — [The crew is on the wrong side of this job. The cargo they're moving is stolen from its rightful owner. The person they're meant to find or extract is being protected by the people hunting them. The patron is the antagonist of this story — knowingly or as someone else's instrument. Nothing they said was technically false. The crew's first instinct, on figuring this out mid-job, should be to wonder how deep in they already are.]

**Why They'd Take It:** [One sentence — the reason a crew would say yes despite their better judgment.]

**Connection:** [One named person who knows this patron. Could be a warning, a reference, or a loose thread — and why it matters.]"""


# ── Tool dispatcher ────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_dice":                   return roll_dice(**inputs)
    if name == "roll_d66":                    return roll_d66()
    if name == "roll_homeworld_uwp":          return roll_homeworld_uwp()
    if name == "get_career_info":             return get_career_info(**inputs)
    if name == "get_characteristic_modifier": return get_characteristic_modifier(**inputs)
    if name == "compute_upp":                 return compute_upp(**inputs)
    return f"Unknown tool: {name}"


# ── Phase tracker ──────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "stats":    "Rolling characteristics...",
    "homeworld":"Creating homeworld...",
    "career":   "Building career path...",
    "terms":    "Career terms, events & mishaps...",
    "muster":   "Mustering out...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_homeworld_uwp":
        return "homeworld"
    if tool_name == "get_career_info":
        return "career"
    if tool_name == "roll_d66":
        return "terms"
    if tool_name == "roll_dice":
        if "roll_homeworld_uwp" not in seen:
            return "stats"
        if "roll_d66" in seen:
            return "muster"
        return "career"
    return None  # suppress get_characteristic_modifier, compute_upp


# ── Agentic loop ───────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    messages = [{"role": "user", "content": prompt}]
    seen     = set()
    phase    = None

    print()

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    new_phase = detect_phase(block.name, seen)
                    if new_phase and new_phase != phase:
                        phase = new_phase
                        print(PHASE_MESSAGES[phase])

                    seen.add(block.name)
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})


# ── Entry point ────────────────────────────────────────────────────────────────

def save_result(result: str, mode: str) -> Path:
    """Save output to traveller_characters/ as {character-name}-{full|npc|patron}.md"""
    first_line = result.strip().splitlines()[0]
    name_raw   = re.sub(r"[#*]", "", first_line).strip()
    name_slug  = re.sub(r"[^a-z0-9]+", "-", name_raw.lower()).strip("-")
    filename   = f"{name_slug}-{mode}.md"

    output_dir = Path(__file__).parent / "traveller_characters"
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(result)
    return filepath


if __name__ == "__main__":
    mode  = input("Mode? (full / npc / patron, default: full): ").strip().lower()
    mode  = mode if mode in ("full", "npc", "patron") else "full"
    label = {"full": "character", "npc": "NPC", "patron": "patron"}[mode]
    desc  = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt = f"Generate a Mongoose Traveller NPC with these constraints: {desc}" if desc else "Generate a fully random Mongoose Traveller NPC."
    elif mode == "patron":
        sys_prompt = PATRON_SYSTEM_PROMPT
        prompt = f"Generate a Mongoose Traveller patron encounter with these constraints: {desc}" if desc else "Generate a fully random Mongoose Traveller patron encounter."
    else:  # full
        sys_prompt = SYSTEM_PROMPT
        prompt = f"Generate a Mongoose Traveller character for storytelling purposes with these constraints: {desc}" if desc else "Generate a fully random Mongoose Traveller character for storytelling purposes."

    result = run_agent(prompt, sys_prompt)
    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")
