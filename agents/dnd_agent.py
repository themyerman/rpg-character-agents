"""
D&D 5e Character Generator
Creates vivid storytelling characters using D&D 5th Edition mechanics.

Run with: python dnd_dice_agent.py
"""

import json
import random
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.names import roll_dnd_name_suggestion, DND_NAME_TOOL_SCHEMA
from lib.spells import get_spell_suggestions, DND_SPELL_TOOL_SCHEMA
from lib.gear import roll_dnd_gear, DND_GEAR_TOOL_SCHEMA
from lib.utils import get_client, run_agent_loop, save_character, strip_preamble
from lib.safety import sanitize_desc, screen_desc, wrap_desc, screen_output


# ── Constants ──────────────────────────────────────────────────────────────────

VALID_DICE = {4, 6, 8, 10, 12, 20}   # full D&D dice set
MIN_ROLLS  = 1
MAX_ROLLS  = 20

ALL_SKILLS = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
    "History", "Insight", "Intimidation", "Investigation", "Medicine",
    "Nature", "Perception", "Performance", "Persuasion", "Religion",
    "Sleight of Hand", "Stealth", "Survival",
]

PROFICIENCY_BONUS = 2  # Level 1; all characters start here

# Which ability score drives spellcasting for each class (non-casters omitted)
SPELLCASTING_STAT: dict[str, str] = {
    "Bard":     "CHA",
    "Cleric":   "WIS",
    "Druid":    "WIS",
    "Paladin":  "CHA",
    "Ranger":   "WIS",
    "Sorcerer": "CHA",
    "Warlock":  "CHA",
    "Wizard":   "INT",
}


# ── Utility functions ──────────────────────────────────────────────────────────

def ability_modifier(score: int) -> int:
    return (score - 10) // 2

def modifier_str(score: int) -> str:
    mod = ability_modifier(score)
    return f"+{mod}" if mod >= 0 else str(mod)


# ── Race data ──────────────────────────────────────────────────────────────────

RACES = {
    "Human": {
        "description": "Versatile and ambitious, found everywhere, driven by a lifespan short enough to make every year count",
        "ability_bonuses": {"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1},
        "traits": ["Extra skill proficiency", "Extra language"],
        "flavor": "adaptable, relentlessly ambitious, underestimated by longer-lived races",
        "speed": "30 ft",
        "languages": ["Common", "one additional language of choice"],
    },
    "High Elf": {
        "description": "Ancient, graceful, and quietly condescending — keepers of arcane knowledge and deep memory",
        "ability_bonuses": {"DEX": 2, "INT": 1},
        "traits": ["Darkvision 60ft", "Keen Senses (Perception proficiency)", "Fey Ancestry (advantage vs charm, immune to magical sleep)", "Trance (meditate 4hrs instead of sleeping 8)", "One Wizard cantrip", "Extra language"],
        "flavor": "patient to a fault, beautiful in an unsettling way, remembers things that happened before your nation existed",
        "speed": "30 ft",
        "languages": ["Common", "Elvish", "one additional language of choice"],
    },
    "Wood Elf": {
        "description": "Reclusive guardians of ancient forests — swifter and more grounded than their high elf cousins",
        "ability_bonuses": {"DEX": 2, "WIS": 1},
        "traits": ["Darkvision 60ft", "Keen Senses", "Fey Ancestry", "Trance", "Fleet of Foot (35ft speed)", "Mask of the Wild (hide in natural terrain)"],
        "flavor": "quiet, observant, trusts a forest over a city any day",
        "speed": "35 ft",
        "languages": ["Common", "Elvish"],
    },
    "Drow": {
        "description": "Children of the Underdark — elegant, dangerous, and shaped by a society built entirely on betrayal",
        "ability_bonuses": {"DEX": 2, "CHA": 1},
        "traits": ["Superior Darkvision 120ft", "Keen Senses (Perception proficiency)", "Fey Ancestry", "Trance", "Sunlight Sensitivity (disadvantage on attacks and Perception in sunlight)", "Drow Magic (Dancing Lights cantrip; Faerie Fire 1/day at level 3; Darkness 1/day at level 5)", "Drow Weapon Training (rapiers, shortswords, hand crossbows)"],
        "flavor": "navigates every room like it might be a trap — because growing up, it usually was; warmth, when it comes, is hard-won and quietly fierce",
        "speed": "30 ft",
        "languages": ["Common", "Elvish", "Undercommon"],
    },
    "Hill Dwarf": {
        "description": "Stubborn, tough, and loyal — forged in stone and tradition, holds grudges across generations",
        "ability_bonuses": {"CON": 2, "WIS": 1},
        "traits": ["Darkvision 60ft", "Dwarven Resilience (advantage vs poison)", "Stonecunning", "Dwarven Toughness (+1 HP per level)", "Artisan's tool proficiency"],
        "flavor": "gruff, deeply honorable, has strong opinions about ale and stonework",
        "speed": "25 ft",
        "languages": ["Common", "Dwarvish"],
    },
    "Mountain Dwarf": {
        "description": "Warriors born underground — built like stone, equally immovable",
        "ability_bonuses": {"STR": 2, "CON": 2},
        "traits": ["Darkvision 60ft", "Dwarven Resilience", "Stonecunning", "Light and medium armor proficiency"],
        "flavor": "militaristic and direct, respects strength and craft in equal measure",
        "speed": "25 ft",
        "languages": ["Common", "Dwarvish"],
    },
    "Lightfoot Halfling": {
        "description": "Small, lucky, and surprisingly hard to notice — more resilient than they look",
        "ability_bonuses": {"DEX": 2, "CHA": 1},
        "traits": ["Lucky (reroll 1s on attack rolls, ability checks, saving throws)", "Brave (advantage vs frightened)", "Halfling Nimbleness (move through larger creatures' spaces)", "Naturally Stealthy (can hide behind larger creatures)"],
        "flavor": "cheerful, comfort-seeking, tends to survive situations that kill more imposing people",
        "speed": "25 ft",
        "languages": ["Common", "Halfling"],
    },
    "Stout Halfling": {
        "description": "Tougher than their cheerful demeanor suggests — weathered, resilient, and harder to poison than almost anything",
        "ability_bonuses": {"DEX": 2, "CON": 1},
        "traits": ["Lucky (reroll 1s)", "Brave (advantage vs frightened)", "Halfling Nimbleness", "Stout Resilience (advantage vs poison, resistance to poison damage)"],
        "flavor": "seen more than they let on, carries quiet toughness behind an easy smile, not the halfling that gets rescued",
        "speed": "25 ft",
        "languages": ["Common", "Halfling"],
    },
    "Forest Gnome": {
        "description": "Curious tinkerers and woodland tricksters with infectious enthusiasm and short attention spans",
        "ability_bonuses": {"INT": 2, "DEX": 1},
        "traits": ["Darkvision 60ft", "Gnome Cunning (advantage on INT/WIS/CHA saves vs magic)", "Minor Illusion cantrip", "Speak with Small Beasts"],
        "flavor": "enthusiastic, easily distracted, sees everything as a puzzle",
        "speed": "25 ft",
        "languages": ["Common", "Gnomish"],
    },
    "Rock Gnome": {
        "description": "Inventors and artificers who regard 'impossible' as a personal challenge rather than a limit",
        "ability_bonuses": {"INT": 2, "CON": 1},
        "traits": ["Darkvision 60ft", "Gnome Cunning (advantage on INT/WIS/CHA saves vs magic)", "Artificer's Lore (double proficiency bonus on History checks for magical/alchemical/technological items)", "Tinker (craft tiny clockwork devices during short rest)"],
        "flavor": "hands always busy, workshop always cluttered, has accidentally solved problems no one asked them to solve",
        "speed": "25 ft",
        "languages": ["Common", "Gnomish"],
    },
    "Half-Elf": {
        "description": "Caught between two worlds, belonging to neither — which makes them very good at reading rooms",
        "ability_bonuses": {"CHA": 2, "two others of choice": 1},
        "traits": ["Darkvision 60ft", "Fey Ancestry", "Skill Versatility (proficiency in any 2 skills)", "Extra language"],
        "flavor": "charming, subtly restless, used to performing for audiences that aren't quite sure what to make of them",
        "speed": "30 ft",
        "languages": ["Common", "Elvish", "one additional language of choice"],
    },
    "Half-Orc": {
        "description": "Marked by orcish blood — strength, ferocity, and a will to survive that borders on supernatural",
        "ability_bonuses": {"STR": 2, "CON": 1},
        "traits": ["Darkvision 60ft", "Intimidation proficiency", "Relentless Endurance (drop to 1 HP instead of 0, once per long rest)", "Savage Attacks (roll one extra weapon die on a melee critical hit)"],
        "flavor": "intense and practical, has learned to use the fear others project onto them as a tool",
        "speed": "30 ft",
        "languages": ["Common", "Orc"],
    },
    "Tiefling": {
        "description": "Infernal heritage written on their skin — horns, tail, unnerving eyes. Always the outsider.",
        "ability_bonuses": {"CHA": 2, "INT": 1},
        "traits": ["Darkvision 60ft", "Hellish Resistance (resistance to fire damage)", "Infernal Legacy (Thaumaturgy cantrip; Hellish Rebuke and Darkness as they level)"],
        "flavor": "often mistrusted from birth, learned self-reliance early, can be warm or cold depending entirely on how the world treated them",
        "speed": "30 ft",
        "languages": ["Common", "Infernal"],
    },
    "Dragonborn": {
        "description": "Dragon blood in human form — breath weapons, natural pride, and a culture built around glory",
        "ability_bonuses": {"STR": 2, "CHA": 1},
        "traits": ["Draconic Ancestry (choose dragon type — determines damage type)", "Breath Weapon (line or cone, scales with level)", "Damage Resistance (matching ancestry type)"],
        "flavor": "honor-driven, proud to the point of arrogance, spectacular and terrifying when they finally breathe",
        "speed": "30 ft",
        "languages": ["Common", "Draconic"],
    },
    "Aasimar": {
        "description": "Touched by celestial blood — luminous, calm, carrying a divine charge they may or may not have asked for",
        "ability_bonuses": {"CHA": 2, "WIS": 1},
        "traits": ["Darkvision 60ft", "Celestial Resistance (resistance to necrotic and radiant damage)", "Healing Hands (heal HP equal to level by touch, 1/long rest)", "Light Bearer (Light cantrip)"],
        "flavor": "unmistakably other — silver hair, luminous eyes, or an unsettling serenity; people expect things from them that they haven't agreed to be",
        "speed": "30 ft",
        "languages": ["Common", "Celestial"],
    },
    "Tabaxi": {
        "description": "Cat-folk driven by insatiable curiosity — the information is the treasure, always",
        "ability_bonuses": {"DEX": 2, "CHA": 1},
        "traits": ["Darkvision 60ft", "Feline Agility (double speed for a turn, then must move 0 ft to trigger again)", "Cat's Claws (climb speed 20ft; unarmed strike deals 1d4+STR slashing)", "Cat's Talent (proficiency in Perception and Stealth)"],
        "flavor": "follows a fascinating rumor the way others follow gold; the collection never stops growing, and they've learned the hard way that not all information is free",
        "speed": "30 ft",
        "languages": ["Common", "one additional language of choice"],
    },
    "Fire Genasi": {
        "description": "Born of flame and elemental fire — volatile, warm, and drawn to conflict the way fire draws oxygen",
        "ability_bonuses": {"CON": 2, "INT": 1},
        "traits": ["Darkvision 60ft", "Fire Resistance", "Reach to the Blaze (Produce Flame cantrip; Burning Hands 1/long rest at level 3)"],
        "flavor": "marks everything they touch with warmth or char; not destructive by nature but the world tends to get combustible around them",
        "speed": "30 ft",
        "languages": ["Common", "Primordial"],
    },
    "Water Genasi": {
        "description": "Born of tide and elemental water — patient, deep, and capable of reading a room the way still water reads light",
        "ability_bonuses": {"CON": 2, "WIS": 1},
        "traits": ["Acid Resistance", "Amphibious (breathe air and water)", "Swim speed 30ft", "Call to the Wave (Shape Water cantrip; Create or Destroy Water 1/long rest at level 3)"],
        "flavor": "takes the long view; processes information slowly and thoroughly; things surface eventually, and they know how to wait",
        "speed": "30 ft (swim 30 ft)",
        "languages": ["Common", "Primordial"],
    },
    "Earth Genasi": {
        "description": "Born of stone and elemental earth — immovable, permanent-feeling, deeply connected to what endures",
        "ability_bonuses": {"CON": 2, "STR": 1},
        "traits": ["Earth Walk (ignore difficult terrain from earth or stone)", "Merge with Stone (Earth Tremor cantrip; Pass Without Trace 1/long rest at level 3)"],
        "flavor": "processes things slowly and completely; the kind of person you'd trust to guard something for a century and find it exactly as you left it",
        "speed": "30 ft",
        "languages": ["Common", "Primordial"],
    },
    "Air Genasi": {
        "description": "Born of wind and elemental air — restless, impossible to pin down, always half-a-thought ahead",
        "ability_bonuses": {"CON": 2, "DEX": 1},
        "traits": ["Unending Breath (hold breath indefinitely)", "Mingle with the Wind (Levitate 1/short rest, concentration up to 1 minute)"],
        "flavor": "uncomfortable in enclosed spaces both physical and social; the horizon is always more interesting than here",
        "speed": "35 ft",
        "languages": ["Common", "Primordial"],
    },
    "Goliath": {
        "description": "Mountain-born giants among humanoids — they understand that the drop is always visible, and act accordingly",
        "ability_bonuses": {"STR": 2, "CON": 1},
        "traits": ["Natural Athlete (Athletics proficiency)", "Stone's Endurance (reaction: reduce damage by 1d12+CON mod, 1/short rest)", "Mountain Born (cold resistance; ignore difficult terrain from ice or snow)", "Powerful Build (count as Large for carrying capacity and pushing/dragging/lifting)"],
        "flavor": "judges exclusively by deeds and endurance; the concept of 'safe margin' never quite took hold; finds most other races alarmingly fragile",
        "speed": "30 ft",
        "languages": ["Common", "Giant"],
    },
    "Firbolg": {
        "description": "Enormous and self-effacing forest giants who have been hiding their nature for so long the performance has become comfortable",
        "ability_bonuses": {"WIS": 2, "STR": 1},
        "traits": ["Firbolg Magic (Detect Magic + Disguise Self each 1/short rest; appear as a Medium humanoid)", "Hidden Step (bonus action: turn invisible until start of next turn, 1/short rest)", "Powerful Build", "Speech of Beast and Leaf (communicate simple ideas with beasts and plants; advantage on Persuasion vs them)"],
        "flavor": "prefers the forest's company to almost anyone; carries the weight of something ancient and rarely explains it; the gentleness is real, and so is the strength behind it",
        "speed": "30 ft",
        "languages": ["Common", "Elvish", "Giant"],
    },
    "Kenku": {
        "description": "Flightless bird-folk bound by a curse that stripped them of their original voice — they speak entirely in borrowed sounds",
        "ability_bonuses": {"DEX": 2, "WIS": 1},
        "traits": ["Expert Forgery (advantage on checks to copy documents or objects)", "Mimicry (perfectly reproduce voices and sounds heard; Deception/Performance checks to pass as mimicked voice)", "Kenku Training (proficiency in 2 of: Acrobatics, Deception, Stealth, Sleight of Hand)"],
        "flavor": "communicates through a patchwork of borrowed voices, music, and environmental noise; the tragedy is the curse, and the adaptation is remarkable; what they'd say in their own voice remains unknown",
        "speed": "30 ft",
        "languages": ["Common", "Auran (understand but cannot produce original speech — communicate through mimicry only)"],
    },
    "Lizardfolk": {
        "description": "Cold-blooded pragmatists who process emotion as data — utterly alien in affect, utterly reliable once they've claimed you as tribe",
        "ability_bonuses": {"CON": 2, "WIS": 1},
        "traits": ["Bite (unarmed strike: 1d6+STR piercing)", "Cunning Artisan (craft weapons/shields from fallen creatures during short rest)", "Hold Breath (15 minutes)", "Hunter's Lore (2 skills from: Animal Handling, Nature, Perception, Stealth, Survival)", "Natural Armor (AC = 13 + DEX modifier when wearing no armor)", "Hungry Jaws (bonus action bite that grants THP equal to CON modifier, 1/short rest)"],
        "flavor": "loyalty to those who earn the designation 'tribe' runs absolute and permanent; complete indifference to everyone else; the empathy is a learned behavior, and they've put genuine effort into it",
        "speed": "30 ft (swim 30 ft)",
        "languages": ["Common", "Draconic"],
    },
}


# ── Class data ─────────────────────────────────────────────────────────────────

CLASSES = {
    "Barbarian": {
        "description": "Primal warriors who channel rage into devastating combat power",
        "hit_die": "d12",
        "hp_at_1": 12,
        "primary_stats": ["STR", "CON"],
        "saving_throws": ["STR", "CON"],
        "armor": ["Light armor", "Medium armor", "Shields"],
        "weapons": ["Simple weapons", "Martial weapons"],
        "skills": "Choose 2 from: Animal Handling, Athletics, Intimidation, Nature, Perception, Survival",
        "typical_armor": "Barbarian Unarmored",
        "flavor": "unstoppable in a straight fight, often uncomfortable in social situations, deeply connected to instinct over intellect",
        "subclass_hint": "Path of Berserker (more rage, more violence), Path of Totem Warrior (spiritual connection to an animal), Path of Storm Herald (elemental fury)",
    },
    "Bard": {
        "description": "Magical performers who weave music and magic — masters of knowing a little about everything",
        "hit_die": "d8",
        "hp_at_1": 8,
        "primary_stats": ["CHA", "DEX"],
        "saving_throws": ["DEX", "CHA"],
        "armor": ["Light armor"],
        "weapons": ["Simple weapons", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
        "skills": "Choose any 3 skills",
        "typical_armor": "Leather",
        "flavor": "charming, adaptable, has an opinion on everything and usually makes it sound authoritative",
        "subclass_hint": "College of Lore (master of secrets), College of Valor (warrior-poet), College of Glamour (fey-touched enchanter)",
    },
    "Cleric": {
        "description": "Divine agents — the deity and domain define everything about who they are",
        "hit_die": "d8",
        "hp_at_1": 8,
        "primary_stats": ["WIS", "CON"],
        "saving_throws": ["WIS", "CHA"],
        "armor": ["Light armor", "Medium armor", "Shields"],
        "weapons": ["Simple weapons"],
        "skills": "Choose 2 from: History, Insight, Medicine, Persuasion, Religion",
        "typical_armor": "Chain Mail",
        "flavor": "their god matters — a cleric of a war god is a completely different creature from a cleric of a trickster",
        "subclass_hint": "Life (healer), War (divine warrior), Trickery (spy of the gods), Knowledge (lore keeper), Light (radiant defender)",
    },
    "Druid": {
        "description": "Guardians of nature who wield primal magic and transform into beasts",
        "hit_die": "d8",
        "hp_at_1": 8,
        "primary_stats": ["WIS", "CON"],
        "saving_throws": ["INT", "WIS"],
        "armor": ["Light armor (non-metal)", "Medium armor (non-metal)", "Shields (non-metal)"],
        "weapons": ["Clubs", "Daggers", "Quarterstaffs", "Scimitars", "Sickles", "Slings", "Spears"],
        "skills": "Choose 2 from: Arcana, Animal Handling, Insight, Medicine, Nature, Perception, Religion, Survival",
        "typical_armor": "Hide",
        "flavor": "ancient, patient, sees civilization as a thin crust over wild earth",
        "subclass_hint": "Circle of the Land (natural scholar), Circle of the Moon (powerful shapeshifter), Circle of Spores (decay and rebirth)",
    },
    "Fighter": {
        "description": "Masters of martial combat — adaptive, disciplined, and devastating with any weapon",
        "hit_die": "d10",
        "hp_at_1": 10,
        "primary_stats": ["STR or DEX", "CON"],
        "saving_throws": ["STR", "CON"],
        "armor": ["All armor", "Shields"],
        "weapons": ["Simple weapons", "Martial weapons"],
        "skills": "Choose 2 from: Acrobatics, Animal Handling, Athletics, History, Insight, Intimidation, Perception, Survival",
        "typical_armor": "Chain Mail",
        "flavor": "consistently underestimated as 'just a fighter' — actually the most reliable thing in a desperate situation",
        "subclass_hint": "Champion (peak physical perfection), Battle Master (tactical genius), Eldritch Knight (steel meets sorcery)",
    },
    "Monk": {
        "description": "Disciplined warriors who harness ki energy to perform superhuman feats",
        "hit_die": "d8",
        "hp_at_1": 8,
        "primary_stats": ["DEX", "WIS"],
        "saving_throws": ["STR", "DEX"],
        "armor": ["None — unarmored defense uses DEX+WIS"],
        "weapons": ["Simple weapons", "Shortswords"],
        "skills": "Choose 2 from: Acrobatics, Athletics, History, Insight, Religion, Stealth",
        "typical_armor": "Monk Unarmored",
        "flavor": "intensely disciplined, sometimes detached — their body is their weapon and their monastery is their origin story",
        "subclass_hint": "Way of the Open Hand (perfect martial artist), Way of Shadow (ninja), Way of the Four Elements (elemental strikes)",
    },
    "Paladin": {
        "description": "Holy warriors bound by a sacred oath — their oath defines them as much as their sword arm",
        "hit_die": "d10",
        "hp_at_1": 10,
        "primary_stats": ["STR", "CHA"],
        "saving_throws": ["WIS", "CHA"],
        "armor": ["All armor", "Shields"],
        "weapons": ["Simple weapons", "Martial weapons"],
        "skills": "Choose 2 from: Athletics, Insight, Intimidation, Medicine, Persuasion, Religion",
        "typical_armor": "Chain Mail",
        "flavor": "the oath is everything — what they swore to, and whether they've kept it, is the core of who they are",
        "subclass_hint": "Oath of Devotion (classic holy knight), Oath of the Ancients (protector of life and light), Oath of Vengeance (relentless hunter of evil), Oathbreaker (dark and fallen)",
    },
    "Ranger": {
        "description": "Hunters and trackers who bridge wilderness and civilization",
        "hit_die": "d10",
        "hp_at_1": 10,
        "primary_stats": ["DEX", "WIS"],
        "saving_throws": ["STR", "DEX"],
        "armor": ["Light armor", "Medium armor", "Shields"],
        "weapons": ["Simple weapons", "Martial weapons"],
        "skills": "Choose 3 from: Animal Handling, Athletics, Insight, Investigation, Nature, Perception, Stealth, Survival",
        "typical_armor": "Scale Mail",
        "flavor": "defined by what they hunt and where they roam — favored enemy and terrain are their biography",
        "subclass_hint": "Hunter (tactical predator), Beast Master (bonded with an animal companion), Gloom Stalker (darkness and ambush)",
    },
    "Rogue": {
        "description": "Cunning opportunists who strike once and precisely, then disappear",
        "hit_die": "d8",
        "hp_at_1": 8,
        "primary_stats": ["DEX", "INT"],
        "saving_throws": ["DEX", "INT"],
        "armor": ["Light armor"],
        "weapons": ["Simple weapons", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
        "skills": "Choose 4 from: Acrobatics, Athletics, Deception, Insight, Intimidation, Investigation, Perception, Performance, Persuasion, Sleight of Hand, Stealth",
        "typical_armor": "Leather",
        "flavor": "every rogue has a code — even if they'd never admit it out loud",
        "subclass_hint": "Thief (classic dexterity and opportunism), Assassin (precision and disguise), Arcane Trickster (magic and misdirection)",
    },
    "Sorcerer": {
        "description": "Magic flows in their blood — raw power, not learned craft. The source matters.",
        "hit_die": "d6",
        "hp_at_1": 6,
        "primary_stats": ["CHA", "CON"],
        "saving_throws": ["CON", "CHA"],
        "armor": ["None"],
        "weapons": ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light crossbows"],
        "skills": "Choose 2 from: Arcana, Deception, Insight, Intimidation, Persuasion, Religion",
        "typical_armor": "Unarmored",
        "flavor": "their magical origin is their character — wild magic, draconic blood, divine soul, storm, or shadow",
        "subclass_hint": "Wild Magic (chaotic and unpredictable), Draconic Bloodline (power and scales), Divine Soul (celestial or fiendish lineage)",
    },
    "Warlock": {
        "description": "Spellcasters who made a deal — their patron's gifts come with strings they may not fully understand",
        "hit_die": "d8",
        "hp_at_1": 8,
        "primary_stats": ["CHA", "CON"],
        "saving_throws": ["WIS", "CHA"],
        "armor": ["Light armor"],
        "weapons": ["Simple weapons"],
        "skills": "Choose 2 from: Arcana, Deception, History, Intimidation, Investigation, Nature, Religion",
        "typical_armor": "Leather",
        "flavor": "the patron relationship is everything — who they made the deal with, why they did it, and what it actually cost them",
        "subclass_hint": "The Fiend (dark power and hellfire), The Great Old One (alien whispers and forbidden knowledge), The Archfey (glamour, fear, and fey bargains)",
    },
    "Wizard": {
        "description": "Scholars of the arcane who reshape reality through disciplined study",
        "hit_die": "d6",
        "hp_at_1": 6,
        "primary_stats": ["INT", "CON"],
        "saving_throws": ["INT", "WIS"],
        "armor": ["None"],
        "weapons": ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light crossbows"],
        "skills": "Choose 2 from: Arcana, History, Insight, Investigation, Medicine, Religion",
        "typical_armor": "Unarmored",
        "flavor": "their spellbook is their biography — the spells they chose reveal exactly what they value",
        "subclass_hint": "School of Evocation (raw destructive power), School of Divination (knowledge and prediction), School of Necromancy (life, death, and the space between), School of Illusion (deception and misdirection)",
    },
}


# ── Background data ────────────────────────────────────────────────────────────

BACKGROUNDS = {
    "Acolyte": {
        "description": "You have spent your life in service to a temple — devotion is your foundation",
        "skills": ["Insight", "Religion"],
        "tools": [],
        "languages": 2,
        "feature": "Shelter of the Faithful — temples of your faith will house, feed, and assist you and your companions",
        "personality_seeds": {
            "traits": ["I idolize a particular hero of my faith and constantly reference their example", "I find it hard to shake the habits of devotion even in hostile environments"],
            "ideals": ["Faith — my deity's will guides me even when I can't see the path", "Tradition — the old rituals exist for reasons that must be respected"],
            "bonds": ["I owe my life to the cleric who took me in after my family died", "I will do anything to protect the temple where I grew up"],
            "flaws": ["I judge others harshly and myself even more so", "I am rigid in my thinking and slow to accept new ideas"],
        },
        "story_hooks": "What faith do you serve? Why did you leave the temple? What does your deity ask of you that you find difficult?",
    },
    "Charlatan": {
        "description": "You have always had a talent for making people believe what you need them to believe",
        "skills": ["Deception", "Sleight of Hand"],
        "tools": ["Disguise kit", "Forgery kit"],
        "languages": 0,
        "feature": "False Identity — you maintain a second identity with complete documentation; you can forge official papers",
        "personality_seeds": {
            "traits": ["I have a scheme running at all times, just in case", "I'm a gifted mimic — I pick up accents and mannerisms quickly"],
            "ideals": ["Independence — no one tells me what to do", "Creativity — I never run the same con twice"],
            "bonds": ["I conned the wrong person once. I'm still paying for it.", "My mentor taught me everything I know and was a terrible person — I'm still sorting out how I feel about that"],
            "flaws": ["I can't resist an easy mark even when I know better", "I'm convinced no one could ever fool me the way I fool others"],
        },
        "story_hooks": "What's your signature con? Who did you ruin that you still think about? What line won't you cross — and why?",
    },
    "Criminal": {
        "description": "You have a history of breaking the law and learned things the law-abiding never do",
        "skills": ["Deception", "Stealth"],
        "tools": ["Gaming set", "Thieves' tools"],
        "languages": 0,
        "feature": "Criminal Contact — you have a reliable and discreet contact in the criminal underworld who can get things",
        "personality_seeds": {
            "traits": ["I always have a plan for when things go wrong", "I'm genuinely calm in dangerous situations — it's peace that makes me nervous"],
            "ideals": ["Freedom — chains are meant to be broken", "Honor — I don't steal from people who can't afford it"],
            "bonds": ["I'm trying to repay a debt I owe to someone who didn't have to help me but did", "Someone I cared about died because of something I did or didn't do"],
            "flaws": ["When I see something valuable, I start thinking about how to take it", "I'll run if things look truly bad — I'm not dying for a principle"],
        },
        "story_hooks": "What kind of criminal were you? Who do you still owe something to from that life? What would make you go back?",
    },
    "Entertainer": {
        "description": "You thrive before an audience — performance is your craft, your armor, and your addiction",
        "skills": ["Acrobatics", "Performance"],
        "tools": ["Disguise kit", "One musical instrument"],
        "languages": 0,
        "feature": "By Popular Demand — you can always find a place to perform; taverns, courts, and festivals welcome you",
        "personality_seeds": {
            "traits": ["I know something interesting about almost every place I've been — it's how I get work", "I'm a relentless romantic"],
            "ideals": ["Beauty — when I perform I make the world better than it was", "Honesty — art should comfort the disturbed and disturb the comfortable"],
            "bonds": ["The mentor who gave me my first real break — I'll pay that forward", "My greatest performance ruined something that mattered to me"],
            "flaws": ["I'll do almost anything for fame", "I cannot abide people who don't appreciate craft"],
        },
        "story_hooks": "What's your act? Who made you? What happened that forced you off the stage and into the world?",
    },
    "Folk Hero": {
        "description": "You come from humble roots, but something happened that set you apart from your neighbors",
        "skills": ["Animal Handling", "Survival"],
        "tools": ["Artisan's tools", "Vehicles (land)"],
        "languages": 0,
        "feature": "Rustic Hospitality — common people will shelter you, feed you, and keep your presence quiet",
        "personality_seeds": {
            "traits": ["I judge by actions, not words", "If someone needs help and I can give it, the question is already answered"],
            "ideals": ["Respect — people deserve dignity regardless of station", "Responsibility — I have this power; it came from somewhere; I owe something"],
            "bonds": ["There are people back home who are counting on me to fix something", "The land I grew up on was taken. I haven't forgotten."],
            "flaws": ["I have powerful enemies because I stood up to them once", "I'm too proud to ask for help and too stubborn to admit I need it"],
        },
        "story_hooks": "What was the moment that made people call you a hero? Did you think of yourself as one? What did it cost you?",
    },
    "Guild Artisan": {
        "description": "A skilled craftsperson with a network, a reputation, and a strong sense of professional pride",
        "skills": ["Insight", "Persuasion"],
        "tools": ["One artisan's tools"],
        "languages": 1,
        "feature": "Guild Membership — the guild provides lodging, legal support, and connections across trade cities",
        "personality_seeds": {
            "traits": ["If a thing is worth doing it's worth doing correctly", "I form opinions about craftsmanship immediately and hold them firmly"],
            "ideals": ["Community — the guild is a family; you protect it and it protects you", "Aspiration — my work will outlast me"],
            "bonds": ["The workshop where I learned my trade is sacred to me", "I owe a significant debt to a fellow guild member who covered for me"],
            "flaws": ["I'm a perfectionist and I make other people's lives difficult because of it", "I will not be satisfied with what I have — there's always better work to do"],
        },
        "story_hooks": "What do you make? Why did you leave the guild life? Was it your choice?",
    },
    "Hermit": {
        "description": "You lived in seclusion — monastery, cave, deep forest — and found something in the silence",
        "skills": ["Medicine", "Religion"],
        "tools": ["Herbalism kit"],
        "languages": 1,
        "feature": "Discovery — during your isolation you found or uncovered something significant that most people don't know",
        "personality_seeds": {
            "traits": ["I've been alone so long I forget that silence can unnerve people", "I am genuinely calm in crisis — I've had time to think about death"],
            "ideals": ["Greater Good — what I found is not mine to keep", "Self-Knowledge — understanding yourself is the only real project"],
            "bonds": ["My isolation revealed something that only I know how to stop", "I left behind someone when I withdrew. I still think about whether that was right."],
            "flaws": ["I am doctrinaire in my thinking — I found answers and I hold them tightly", "I have genuinely forgotten how to make small talk"],
        },
        "story_hooks": "Why did you withdraw from the world? What did you find there? What finally pulled you back?",
    },
    "Noble": {
        "description": "Born to rank, wealth, and expectation — you've never not been watched",
        "skills": ["History", "Persuasion"],
        "tools": ["Gaming set"],
        "languages": 1,
        "feature": "Position of Privilege — common people make way for you; nobles receive you as a peer; doors open",
        "personality_seeds": {
            "traits": ["I make people feel genuinely seen and valued — I learned this as a survival skill", "I know which fork to use at any table and I find this knowledge mostly useless"],
            "ideals": ["Responsibility — privilege is a contract, not a right", "Noble Obligation — I protect those who cannot protect themselves because I can"],
            "bonds": ["My family expects something specific from me and I haven't decided if I'll give it to them", "There is a secret that would destroy my family's name — I carry it alone"],
            "flaws": ["I have a deeply ingrained belief that I am simply better than most people — I fight this and sometimes lose", "My instinct is to solve every problem by spending money or leveraging status"],
        },
        "story_hooks": "What does your family want from you? What does your rank cost you? What made you leave?",
    },
    "Outlander": {
        "description": "You grew up in the wilds — hunter, wanderer, someone who understands that civilization is optional",
        "skills": ["Athletics", "Survival"],
        "tools": ["Musical instrument"],
        "languages": 1,
        "feature": "Wanderer — you have a perfect memory for terrain you've crossed and can always find food and water for a small group",
        "personality_seeds": {
            "traits": ["I'm driven by a wanderlust that has never once been satisfied", "My loyalty to the people I travel with runs deeper than most people's family bonds"],
            "ideals": ["Change — the world turns; adapt or fail", "The Land — it was here before us and will outlast us; that deserves respect"],
            "bonds": ["My people — clan, tribe, family — are the axis my world spins on", "I saw something done to a place I loved. I remember who did it."],
            "flaws": ["I am slow to trust people I can't read", "My first response to most problems is to ask whether violence would solve it"],
        },
        "story_hooks": "Where did you grow up? What drove you into the wider world? What do you miss about the wild?",
    },
    "Sage": {
        "description": "Years in academic pursuit — libraries, labs, long arguments over texts that most people have never heard of",
        "skills": ["Arcana", "History"],
        "tools": [],
        "languages": 2,
        "feature": "Researcher — if you don't know something, you know exactly who to ask or where to look",
        "personality_seeds": {
            "traits": ["I use precise language and get quietly frustrated when others don't", "I will help anyone who can't keep up — it has never once occurred to me not to"],
            "ideals": ["Knowledge — understanding is the highest good", "No Limits — the restriction of inquiry is the restriction of humanity"],
            "bonds": ["There is a question I have been trying to answer my entire life — I am closer now than I've ever been", "I have a text, or a formula, or a name, that must not fall into certain hands"],
            "flaws": ["I am easily pulled off task by interesting information", "I forget that most people find my area of expertise somewhere between confusing and terrifying"],
        },
        "story_hooks": "What are you researching? What sent you out of the library and into the world? What would it mean to finally answer your question?",
    },
    "Sailor": {
        "description": "You worked the water — ocean, river, stranger seas — and it left its mark permanently",
        "skills": ["Athletics", "Perception"],
        "tools": ["Navigator's tools", "Vehicles (water)"],
        "languages": 0,
        "feature": "Ship's Passage — you can secure free passage for yourself and companions on most ships, in exchange for work",
        "personality_seeds": {
            "traits": ["My word is my bond and I take that seriously", "I stretch the truth for a better story and see no ethical problem with this"],
            "ideals": ["Freedom — the sea is freedom; the horizon is always there", "Loyalty — a crew is a crew; you protect yours"],
            "bonds": ["My first ship and the crew on her — some of them are gone now", "I made a promise at sea that I haven't kept yet"],
            "flaws": ["I follow orders to a fault, even when I know they're wrong", "I drink more than I should and I know it"],
        },
        "story_hooks": "What ship, what waters, what happened out there? What brought you to dry land?",
    },
    "Soldier": {
        "description": "You fought in an organized force — regular army, mercenary company, guerrilla militia",
        "skills": ["Athletics", "Intimidation"],
        "tools": ["Gaming set", "Vehicles (land)"],
        "languages": 0,
        "feature": "Military Rank — soldiers and veterans recognize your rank and defer to it; you can requisition equipment in some situations",
        "personality_seeds": {
            "traits": ["I am courteous and direct — I don't have patience for social games", "I face problems head-on and I am suspicious of complex solutions"],
            "ideals": ["Greater Good — we lay down our lives for something larger than ourselves", "Competence — do the job right or don't take it on"],
            "bonds": ["The soldiers I served alongside are the people I trust most in the world", "Someone saved my life. I haven't repaid that yet."],
            "flaws": ["What I saw in battle visits me in quiet moments", "I have no respect for people who haven't proven themselves under pressure"],
        },
        "story_hooks": "What army, what war, what did you do that you can't shake? Why are you no longer a soldier?",
    },
    "Urchin": {
        "description": "You grew up on the streets — resourceful, street-smart, and invisible to people who mattered",
        "skills": ["Sleight of Hand", "Stealth"],
        "tools": ["Disguise kit", "Thieves' tools"],
        "languages": 0,
        "feature": "City Secrets — you know the hidden passages, back routes, and shortcuts of any city you spend time in",
        "personality_seeds": {
            "traits": ["I hide food and small objects out of habit — I notice myself doing it and I don't stop", "I ask too many questions; it kept me alive as a kid"],
            "ideals": ["Community — we look out for each other because no one else will", "Survival — whatever it takes"],
            "bonds": ["The city I grew up in is home, even if I've left it", "I still send money to the corner where I slept as a child — someone else is there now"],
            "flaws": ["If I'm losing a fight I will run — I have no shame about this", "I assume everyone is hiding something because I always am"],
        },
        "story_hooks": "What city? Who looked out for you when you were small? What finally forced you into a bigger world?",
    },
    "Haunted One": {
        "description": "You have been touched by something terrible — hunted, possessed, cursed, or witness to something no one should see. The experience left a mark.",
        "skills": ["Arcana", "Investigation"],
        "tools": [],
        "languages": 2,
        "feature": "Heart of Darkness — common folk, sensing something wrong, go out of their way to help you; they don't know why they're afraid of you, but they'd rather you not be in trouble",
        "personality_seeds": {
            "traits": ["I don't sleep well and I've stopped pretending otherwise", "I notice things others don't — exits, shadows, the way a room goes quiet"],
            "ideals": ["Understanding — if I can name what hunts me, I can face it", "Protection — I will not let what happened to me happen to anyone else"],
            "bonds": ["The thing that haunts me is connected to someone I love — I haven't decided what to do about that", "I made a promise to someone who didn't survive — I intend to keep it"],
            "flaws": ["I pull away from people I care about because caring about things makes you vulnerable", "I know things I can't un-know, and sometimes I tell people when I shouldn't"],
        },
        "story_hooks": "What happened to you? Did you seek it out or did it find you? What are you still carrying from it?",
    },
    "Far Traveler": {
        "description": "You come from somewhere distant and strange — a different continent, a forgotten culture, a community that doesn't put itself on maps. You are unmistakably other.",
        "skills": ["Insight", "Perception"],
        "tools": ["One musical instrument or gaming set from your homeland"],
        "languages": 1,
        "feature": "All Eyes on You — your exotic origin opens doors — nobles want to meet you, merchants want to trade with you, and common folk want to ask questions. This cuts both ways.",
        "personality_seeds": {
            "traits": ["I compare everything to how it's done at home, usually unfavorably", "I am genuinely curious about the customs of wherever I am — even when they're baffling"],
            "ideals": ["Open Mind — the world is larger than any one tradition", "Home — I carry my people with me everywhere; I represent something"],
            "bonds": ["I left home for a reason I don't discuss with strangers", "There is something or someone here that my people sent me to find"],
            "flaws": ["I have difficulty trusting systems I didn't grow up with — and I'm not always wrong about that", "My cultural assumptions make me seem arrogant even when I'm trying to be respectful"],
        },
        "story_hooks": "Where are you from and why does it matter? What brought you here specifically? What do you miss that doesn't exist where you've ended up?",
    },
    "City Watch": {
        "description": "You served as a guard, constable, or investigator — you know the official face of law and the uglier face behind it",
        "skills": ["Athletics", "Insight"],
        "tools": [],
        "languages": 2,
        "feature": "Watcher's Eye — you know where the local constabulary is, how to make contact, and how to navigate watch jurisdictions; criminals also recognize you as someone who knows their world",
        "personality_seeds": {
            "traits": ["I watch people automatically — who's carrying what, who's watching who, what doesn't fit", "I believe in the law even when I don't believe in the people running it"],
            "ideals": ["Order — without structure, the only law is who's strongest", "Justice — the law should protect the weak, not just the connected"],
            "bonds": ["My old partner is in trouble and I'm the only one who knows enough to help them", "I left the watch because of something I couldn't look away from"],
            "flaws": ["I have contempt for people who break laws they think don't apply to them", "I'm too willing to bend rules I've decided are wrong"],
        },
        "story_hooks": "What city? What did you investigate? What did you see that you couldn't report?",
    },
    "Clan Crafter": {
        "description": "You were trained by a dwarven craft guild — precision, tradition, and the deep satisfaction of a thing built to last",
        "skills": ["History", "Insight"],
        "tools": ["One artisan's tools"],
        "languages": 1,
        "feature": "Respect of the Stout Folk — dwarves and other crafting cultures extend professional courtesy; you can always find work, apprentices, and honest assessments of your work's quality",
        "personality_seeds": {
            "traits": ["I can tell you how something was made, often who made it, and whether it was done well", "I am methodical to a fault and get twitchy when things are rushed"],
            "ideals": ["Craft — the work itself is the argument; nothing needs to be said if it's built right", "Legacy — I make things that will outlast me and I find this comforting"],
            "bonds": ["My master taught me something I only recently understood — I need to tell them", "I was given a commission I haven't fulfilled yet. It matters."],
            "flaws": ["I am contemptuous of things made carelessly — and I show it", "I invest too much of my sense of self in the quality of what I make"],
        },
        "story_hooks": "What's your craft? Who trained you? What are you building toward — the object or the title?",
    },
    "Faction Agent": {
        "description": "You serve an organization — political, religious, arcane, or criminal — that operates across borders and keeps its own counsel",
        "skills": ["Insight", "one skill determined by faction"],
        "tools": [],
        "languages": 2,
        "feature": "Safe Haven — members of your faction will shelter, feed, and pass messages for you; you have access to the faction's network even in unfamiliar cities",
        "personality_seeds": {
            "traits": ["I always know which people in a room have power and who they owe it to", "I am loyal to my organization's ideals, and more flexible about its current leadership"],
            "ideals": ["The Cause — the faction's goal is worth the cost; I believe that", "Loyalty — the network survives because everyone holds up their part"],
            "bonds": ["My handler took a risk on me once that they shouldn't have — I haven't forgotten it", "The faction and I disagree about something significant. I'm still figuring out what to do about it."],
            "flaws": ["I think in terms of assets and operations even in situations that don't need it", "My loyalty to the faction has made me do things I'm not proud of"],
        },
        "story_hooks": "What faction? What do they actually want? What do you know that they'd rather you didn't?",
    },
    "Urban Bounty Hunter": {
        "description": "You hunt people for money — not in the wilderness, but in cities, among people who know how to hide in plain sight",
        "skills": ["Deception", "Insight", "Stealth", "Persuasion"],
        "tools": ["Thieves' tools or musical instrument or gaming set"],
        "languages": 0,
        "feature": "Ear to the Ground — you have contacts in the underworld who know where people are; you can get information about specific individuals in a city faster than most",
        "personality_seeds": {
            "traits": ["I read people quickly and rarely need to be told twice", "I'm patient in ways that other people find unnerving"],
            "ideals": ["The Contract — I took the job; the job gets done", "Fair Payment — I provide a service and I deserve to be compensated honestly for it"],
            "bonds": ["I once let someone go and I've thought about it every day since", "The person who set me up in this business has disappeared and I need to know why"],
            "flaws": ["I find it very difficult to care about people I'm not being paid to find", "I'm too willing to take work that has a bad smell if the money is right"],
        },
        "story_hooks": "Who was your most memorable mark? What's the line you won't cross? What work are you doing now — and why?",
    },
    "Mercenary Veteran": {
        "description": "You fought for money in organized military units — not a hero, a professional. There's a difference.",
        "skills": ["Athletics", "Persuasion"],
        "tools": ["Gaming set", "Vehicles (land)"],
        "languages": 0,
        "feature": "Mercenary Life — you know the mercenary world: the companies, the brokers, the markets. You can find work, check a company's reputation, and navigate contracts.",
        "personality_seeds": {
            "traits": ["I evaluate every situation for threats before I do anything else", "I don't volunteer information but I give straight answers when asked"],
            "ideals": ["Professionalism — the job is the job; do it right or don't take it", "Loyalty — to the people beside you, which is all that holds a unit together"],
            "bonds": ["My old company disbanded under bad circumstances — I carry the people who didn't make it out", "Someone from my old unit is in trouble and I'm the only one who can help them"],
            "flaws": ["I have difficulty with situations that don't have a clear objective", "I've learned to manage violence but I haven't learned to manage its absence"],
        },
        "story_hooks": "What company? What campaign? What finally made you stop taking contracts — or are you still taking them?",
    },
}


# ── Alignments ─────────────────────────────────────────────────────────────────

ALIGNMENTS: list[dict] = [
    {
        "name": "Lawful Good",
        "expressions": [
            "They keep promises they didn't have to make and decline rewards they didn't earn.",
            "They follow the chain of command even when they disagree — but they log the disagreement.",
            "They hold themselves to a higher standard than they hold others, and find it quietly exhausting.",
        ],
        "tension": "When the law is wrong, they have to choose between obedience and conscience — and they know it.",
        "shadow": "Rigidity. They can become the institution they once served, punishing deviation they have no authority over.",
    },
    {
        "name": "Neutral Good",
        "expressions": [
            "They help people. They don't need a system for it and they don't need credit.",
            "They'll work with whoever gets the job done — guild, outlaw, lord, peasant — and feel no particular loyalty to any of them.",
            "They have opinions about right and wrong that they'll act on, but they hold them loosely enough to update.",
        ],
        "tension": "They're everyone's ally and no one's member. That independence is a strength and a source of loneliness.",
        "shadow": "Diffusion. Without the spine of law or the edge of chaos, their goodness can become passive or opportunistically convenient.",
    },
    {
        "name": "Chaotic Good",
        "expressions": [
            "They break rules for people, not for themselves — there's a difference and they know exactly what it is.",
            "They trust their read on a situation over any authority's, and they're right often enough to keep doing it.",
            "They inspire people who've given up on institutions to try one more time.",
        ],
        "tension": "Their instinct to act — now, personally, without waiting for permission — sometimes costs allies they need.",
        "shadow": "Arrogance. The line between 'I know better' and 'I get to decide for everyone' is one they don't always see coming.",
    },
    {
        "name": "Lawful Neutral",
        "expressions": [
            "They do the job. Precisely. Without editorializing.",
            "They believe structure is what prevents chaos — and chaos, in their experience, is where people get hurt.",
            "They honor contracts, hierarchies, and traditions not because they think they're always right, but because consistency is.",
        ],
        "tension": "They sometimes work for the wrong side with perfect competence, because the contract was signed and the order came through proper channels.",
        "shadow": "Detachment. Their commitment to process over outcome means they can do real harm while technically following the rules.",
    },
    {
        "name": "True Neutral",
        "expressions": [
            "They take the long view — usually longer than anyone around them finds comfortable.",
            "They don't pick sides, but they watch carefully, and what they've observed has made them cautious about everyone.",
            "They help when it doesn't cost much and step back when it does, which people call pragmatism or cowardice depending on how it affects them.",
        ],
        "tension": "In a crisis, 'True Neutral' starts to feel like a reason not to act, and they know it.",
        "shadow": "Moral passivity. The world doesn't balance itself; someone has to push, and they usually watch that person do it alone.",
    },
    {
        "name": "Chaotic Neutral",
        "expressions": [
            "They do what the moment asks, and they're surprisingly good at reading what the moment asks.",
            "They're loyal to people, not causes — which makes them unpredictable to institutions and reliable to individuals.",
            "They've survived by staying light, and they've made a philosophy out of what started as necessity.",
        ],
        "tension": "Their freedom is real, but it keeps them from committing to things that would make them harder to replace.",
        "shadow": "Volatility. When things get bad enough, 'I follow my own code' and 'I do whatever I want' start to sound the same.",
    },
    {
        "name": "Lawful Evil",
        "expressions": [
            "They believe hierarchy exists so the strong can extract value from the weak without constant renegotiation.",
            "They keep their word — it's a competitive advantage, and it lets them sleep.",
            "They're polite, organized, and genuinely frightening, because their cruelty is deliberate and planned.",
        ],
        "tension": "They serve a system that may one day turn on them, and they know it — they're already planning for it.",
        "shadow": "They've mistaken order for virtue so many times they've forgotten there's a difference. Everything is a transaction, including mercy.",
    },
    {
        "name": "Neutral Evil",
        "expressions": [
            "They help themselves. If others benefit, fine. If not, also fine.",
            "They don't hate anyone — hate is expensive. They simply aren't accounting for you unless you're in their ledger.",
            "They'll work for anyone who pays well enough, and betray anyone who stops.",
        ],
        "tension": "No loyalty, no code, no ideology — which means no allies in a crisis, and they're often in crises.",
        "shadow": "Isolation. Their self-interest is so clean it eventually strips away everything that would make someone help them when it matters.",
    },
    {
        "name": "Chaotic Evil",
        "expressions": [
            "They want what they want and they take it, and they experience other people's distress as confirmation they were strong enough.",
            "They've decided the rules are a fiction the weak use to protect themselves from the strong — and they've made themselves strong.",
            "They move fast, burn bright, and leave things worse than they found them. This is not an accident.",
        ],
        "tension": "Their power requires constant violence or the threat of it, which is exhausting and increasingly unsustainable.",
        "shadow": "They're not free. They're as enslaved to their appetites as any Lawful character is to their codes — they've just convinced themselves the chain is a choice.",
    },
]


# ── Quest hooks ────────────────────────────────────────────────────────────────

QUEST_HOOKS: list[dict] = [
    {
        "type": "Monster Hunt",
        "description": "Something is killing people, livestock, or livelihoods, and the town can't handle it alone.",
        "complications": [
            "The monster turns out to be protecting something — or someone.",
            "Multiple factions want the creature taken alive for different reasons.",
            "The beast is the last of its kind; scholars will be furious if it dies.",
        ],
    },
    {
        "type": "Dungeon Delve",
        "description": "A ruin, tomb, or underground complex holds something the quest giver needs — or needs sealed.",
        "complications": [
            "Another party has already entered and stirred things up.",
            "The dungeon's original purpose is still operating — someone designed it that way.",
            "Something in there doesn't want to be found, and it's been waiting.",
        ],
    },
    {
        "type": "Escort",
        "description": "Get a person, group, or cargo safely from one place to another through dangerous territory.",
        "complications": [
            "The person being escorted is the reason they're in danger — they won't say why.",
            "The route the party planned is no longer safe; improvisation required.",
            "Someone hired to protect the same charge is working against the party.",
        ],
    },
    {
        "type": "Investigation",
        "description": "Find out what happened — a disappearance, a theft, a death that doesn't add up.",
        "complications": [
            "The most obvious suspect is innocent; the actual culprit is well-connected.",
            "Evidence keeps pointing somewhere the quest giver doesn't want looked at.",
            "The crime is still ongoing; the party is in danger of becoming victims.",
        ],
    },
    {
        "type": "Retrieval",
        "description": "Recover a specific object — stolen, lost, cursed, or locked behind people who'd rather keep it.",
        "complications": [
            "The object has changed hands more than once; its current holder has a claim.",
            "Retrieving it requires crossing a faction that will take this personally.",
            "What it actually does is not what the quest giver described.",
        ],
    },
    {
        "type": "Rescue",
        "description": "Someone is being held — captive, imprisoned, or trapped somewhere they cannot leave alone.",
        "complications": [
            "The person being rescued doesn't want to be rescued — at least not yet.",
            "Getting them out means leaving someone else behind.",
            "Their captors have leverage that outlasts any successful rescue.",
        ],
    },
    {
        "type": "Defense",
        "description": "Hold a location, person, or community against a coming threat — buy time, hold the line, survive.",
        "complications": [
            "The threat is larger than the briefing suggested, and the timeline is wrong.",
            "Someone inside the perimeter is giving information to the attackers.",
            "Holding the position requires making an enemy of a neutral party.",
        ],
    },
    {
        "type": "Political Mission",
        "description": "Navigate a negotiation, alliance, or power struggle where swords are the last resort — but never ruled out.",
        "complications": [
            "One of the parties is negotiating in bad faith; figuring out which one is the job.",
            "The party's presence changes the political calculus in ways no one predicted.",
            "Success requires delivering news that will personally devastate the quest giver.",
        ],
    },
    {
        "type": "Heist",
        "description": "Get in, get what's needed, get out — ideally without anyone knowing you were there.",
        "complications": [
            "The target is more heavily guarded than the intelligence suggested.",
            "Someone else is running the same heist on the same night.",
            "What they're stealing is booby-trapped by the person who hid it.",
        ],
    },
    {
        "type": "Wilderness Expedition",
        "description": "Travel into unmapped or dangerous territory — to find something, reach somewhere, or simply survive the journey.",
        "complications": [
            "The map the quest giver provided is wrong in at least one critical place.",
            "The destination has already been reached by someone whose goals conflict with theirs.",
            "The wilderness isn't uninhabited; the party is the intruder here.",
        ],
    },
    {
        "type": "Haunting / Curse",
        "description": "Something from the past has made the present uninhabitable — lift it, find its source, or end it.",
        "complications": [
            "The haunting is real but not malevolent; the curse was deserved.",
            "Ending it requires confronting someone still alive who doesn't want it ended.",
            "The source of the curse is connected to the quest giver's own family.",
        ],
    },
    {
        "type": "Ancient Mystery",
        "description": "Something old and strange has surfaced — an artifact, a prophecy, a ruin that wasn't supposed to exist.",
        "complications": [
            "Multiple factions already know about it and are racing to get there first.",
            "Understanding it requires a sacrifice — information, safety, or something else.",
            "It's connected to the party's own past in a way none of them expected.",
        ],
    },
    {
        "type": "Rebellion Support",
        "description": "A group is fighting an unjust power — they need supplies, information, a strike executed, or simply proof they're not alone.",
        "complications": [
            "The faction the party is helping has done something the party cannot condone.",
            "The power they're fighting against isn't entirely wrong about the situation.",
            "Supporting the rebellion makes the party wanted across a much wider area.",
        ],
    },
    {
        "type": "Creature Rescue",
        "description": "A rare, magical, or intelligent creature needs to be freed, relocated, or protected from those who'd exploit it.",
        "complications": [
            "The creature is dangerous — not as a villain, but because it's terrified.",
            "Its captors have legal possession; breaking it free is technically a crime.",
            "Relocating it will devastate an ecosystem or community that depends on it.",
        ],
    },
]


# ── Armor table ────────────────────────────────────────────────────────────────
# Each entry: base AC, whether DEX applies, max DEX bonus (None = unlimited),
# optional per-class stat additions.

ARMOR_TABLE: dict[str, dict] = {
    "Unarmored":           {"base": 10, "dex": True,  "dex_max": None},
    "Leather":             {"base": 11, "dex": True,  "dex_max": None},
    "Padded":              {"base": 11, "dex": True,  "dex_max": None},
    "Studded Leather":     {"base": 12, "dex": True,  "dex_max": None},
    "Hide":                {"base": 12, "dex": True,  "dex_max": 2},
    "Chain Shirt":         {"base": 13, "dex": True,  "dex_max": 2},
    "Scale Mail":          {"base": 14, "dex": True,  "dex_max": 2},
    "Breastplate":         {"base": 14, "dex": True,  "dex_max": 2},
    "Half Plate":          {"base": 15, "dex": True,  "dex_max": 2},
    "Ring Mail":           {"base": 14, "dex": False, "dex_max": 0},
    "Chain Mail":          {"base": 16, "dex": False, "dex_max": 0},
    "Splint":              {"base": 17, "dex": False, "dex_max": 0},
    "Plate":               {"base": 18, "dex": False, "dex_max": 0},
    # Special unarmored defenses
    "Barbarian Unarmored": {"base": 10, "dex": True, "dex_max": None, "add_con": True},
    "Monk Unarmored":      {"base": 10, "dex": True, "dex_max": None, "add_wis": True},
    # Natural armor (Lizardfolk, Draconic Sorcerer subclass)
    "Natural Armor":       {"base": 13, "dex": True, "dex_max": None},
}


# ── Skill pools by class ───────────────────────────────────────────────────────

SKILL_POOLS: dict[str, dict] = {
    "Barbarian": {"count": 2, "options": ["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"]},
    "Bard":      {"count": 3, "options": "any"},
    "Cleric":    {"count": 2, "options": ["History", "Insight", "Medicine", "Persuasion", "Religion"]},
    "Druid":     {"count": 2, "options": ["Arcana", "Animal Handling", "Insight", "Medicine", "Nature", "Perception", "Religion", "Survival"]},
    "Fighter":   {"count": 2, "options": ["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"]},
    "Monk":      {"count": 2, "options": ["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"]},
    "Paladin":   {"count": 2, "options": ["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"]},
    "Ranger":    {"count": 3, "options": ["Animal Handling", "Athletics", "Insight", "Investigation", "Nature", "Perception", "Stealth", "Survival"]},
    "Rogue":     {"count": 4, "options": ["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"]},
    "Sorcerer":  {"count": 2, "options": ["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"]},
    "Warlock":   {"count": 2, "options": ["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"]},
    "Wizard":    {"count": 2, "options": ["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"]},
}


# ── Deity pool ─────────────────────────────────────────────────────────────────

DEITIES: list[dict] = [
    {
        "name": "Tyr",
        "domain": "War / Justice",
        "alignment": "Lawful Good",
        "portfolio": "Justice, law, righteous combat",
        "symbol": "Balanced scales resting on a warhammer",
        "flavor": "The blind god of justice. His clerics are prosecutors of the divine — they believe the law exists to protect the weak, and they hold that belief even when the law fails to.",
    },
    {
        "name": "Lathander",
        "domain": "Life / Light",
        "alignment": "Neutral Good",
        "portfolio": "Dawn, renewal, vitality, creativity, youth",
        "symbol": "Road traveling into a sunrise",
        "flavor": "The Morninglord demands optimism as a discipline. His clerics greet each dawn as a second chance — and they mean it every single time, which is exhausting and genuine.",
    },
    {
        "name": "Selûne",
        "domain": "Life / Twilight",
        "alignment": "Chaotic Good",
        "portfolio": "The moon, stars, navigation, wanderers, lycanthropes",
        "symbol": "Pair of eyes surrounded by seven stars",
        "flavor": "Goddess of the moon and all who travel by night. Her clerics tend to be wanderers themselves — comfortable in the dark, useful to those who are lost.",
    },
    {
        "name": "Tempus",
        "domain": "War",
        "alignment": "Chaotic Neutral",
        "portfolio": "War, battle, warriors",
        "symbol": "Upright flaming sword",
        "flavor": "The Lord of Battles doesn't pick sides — he simply wants the fighting to be worthy. His clerics are soldiers who believe war is honest in a way peace never quite manages.",
    },
    {
        "name": "Silvanus",
        "domain": "Nature",
        "alignment": "True Neutral",
        "portfolio": "Wild nature, forests, druids",
        "symbol": "Oak leaf",
        "flavor": "The Oak Father cares about balance, not mercy. His clerics love the wild as it is, not as civilization wishes it were — ancient, indifferent, and absolutely necessary.",
    },
    {
        "name": "Kelemvor",
        "domain": "Death",
        "alignment": "Lawful Neutral",
        "portfolio": "The dead, passage of souls, judgment of the dead",
        "symbol": "Skeletal arm holding golden scales",
        "flavor": "The Judge of the Dead ensures every soul reaches its proper place. His clerics are pragmatists about mortality — they comfort the dying and destroy undead with equal calm.",
    },
    {
        "name": "Helm",
        "domain": "Life / Light",
        "alignment": "Lawful Neutral",
        "portfolio": "Guardians, protection, watchfulness, duty",
        "symbol": "Staring eye on an upright gauntlet",
        "flavor": "The Vigilant One demands that his clerics protect what they've been charged to protect — even when no one is watching, especially when no one is watching.",
    },
    {
        "name": "Ilmater",
        "domain": "Life",
        "alignment": "Lawful Good",
        "portfolio": "Endurance, suffering, martyrdom, perseverance, compassion",
        "symbol": "Pair of white hands bound at the wrist with a red cord",
        "flavor": "The Crying God asks his clerics to take on others' pain — literally and spiritually. They're the ones who go into burning buildings and come out carrying someone else.",
    },
    {
        "name": "Mystra",
        "domain": "Arcana / Knowledge",
        "alignment": "Neutral Good",
        "portfolio": "Magic, spells, the Weave",
        "symbol": "Circle of seven stars, or nine stars encircling a flowing red mist",
        "flavor": "The Lady of Mysteries is the magic itself, and her clerics are its stewards — obsessive about the integrity of the Weave, occasionally reckless about everything else.",
    },
    {
        "name": "Oghma",
        "domain": "Knowledge",
        "alignment": "True Neutral",
        "portfolio": "Knowledge, inspiration, invention, bards",
        "symbol": "Blank scroll",
        "flavor": "The Binder values knowledge for its own sake — not for what it does. His clerics collect truths the way others collect gold, and they're equally reluctant to share.",
    },
    {
        "name": "Tymora",
        "domain": "Trickery",
        "alignment": "Chaotic Good",
        "portfolio": "Good fortune, skill, victory, adventurers",
        "symbol": "Face-up coin",
        "flavor": "Lady Luck rewards the bold. Her clerics are gamblers who've decided that fortune favors those who act, and they've put their lives behind that theology.",
    },
    {
        "name": "Waukeen",
        "domain": "Knowledge / Trickery",
        "alignment": "True Neutral",
        "portfolio": "Trade, money, wealth, merchants",
        "symbol": "Upright coin with Waukeen's profile facing left",
        "flavor": "The Merchant's Friend values honest trade and fair dealing — not charity, but exchange. Her clerics are pragmatic, well-connected, and very good at math.",
    },
    {
        "name": "Gond",
        "domain": "Knowledge / Forge",
        "alignment": "True Neutral",
        "portfolio": "Craft, smithwork, engineering, invention",
        "symbol": "Toothed cog with four spokes",
        "flavor": "The Wonderbringer delights in the act of making. His clerics build things — always — and they believe any problem can be solved if the mechanism is correctly designed.",
    },
    {
        "name": "Mask",
        "domain": "Trickery",
        "alignment": "Chaotic Neutral",
        "portfolio": "Thieves, shadows, intrigue, liars",
        "symbol": "Black mask",
        "flavor": "The Lord of Shadows teaches that truth is a resource to be managed. His clerics are not liars — they're practitioners of selective disclosure.",
    },
    {
        "name": "Bane",
        "domain": "War",
        "alignment": "Lawful Evil",
        "portfolio": "Tyranny, hatred, fear",
        "symbol": "Upright black hand, thumb and fingers together",
        "flavor": "The Black Hand believes fear is the most efficient form of governance. His clerics don't disagree — they find mercy sentimental and mercy's consequences instructive.",
    },
    {
        "name": "Shar",
        "domain": "Death / Trickery",
        "alignment": "Neutral Evil",
        "portfolio": "Darkness, loss, forgotten things, secrets",
        "symbol": "Black disk encircled with a border",
        "flavor": "The Mistress of the Night offers the comfort of forgetting. Her clerics tend to carry something they'd rather not remember — and they've learned that the dark is kinder about it than the light.",
    },
    {
        "name": "Talos",
        "domain": "Tempest",
        "alignment": "Chaotic Evil",
        "portfolio": "Storms, destruction, rebellion, conflagration",
        "symbol": "Three lightning bolts radiating from a point",
        "flavor": "The Storm Lord is not subtle. His clerics believe that destruction clears the way for what comes next — and they're in a hurry to get there.",
    },
    {
        "name": "Umberlee",
        "domain": "Tempest",
        "alignment": "Chaotic Evil",
        "portfolio": "Oceans, currents, underwater perils, sea winds",
        "symbol": "Wave curling left and right",
        "flavor": "The Bitch Queen is propitiated more than worshipped — sailors pay her priests because the alternative is worse. Her clerics know this and find the honesty refreshing.",
    },
    {
        "name": "Lliira",
        "domain": "Life",
        "alignment": "Chaotic Good",
        "portfolio": "Joy, celebration, freedom, dance, festivals",
        "symbol": "Triangle of three six-pointed stars",
        "flavor": "Our Lady of Joy believes in pleasure as a practice of resistance. Her clerics are the ones who insist on celebrating even in the bad years — especially in the bad years.",
    },
    {
        "name": "Myrkul",
        "domain": "Death",
        "alignment": "Neutral Evil",
        "portfolio": "The dead, decay, old age, exhaustion",
        "symbol": "White human skull",
        "flavor": "The Lord of Bones believes everything dies and that pretending otherwise is the source of most human suffering. His clerics agree, which makes them unpopular at parties.",
    },
    {
        "name": "Cyric",
        "domain": "Trickery / War",
        "alignment": "Chaotic Evil",
        "portfolio": "Murder, lies, intrigue, illusion, deception",
        "symbol": "White jawless skull on black or purple sunburst",
        "flavor": "The Prince of Lies is the god of those who've decided reality is whatever they can make others believe. His clerics are the dangerous kind of delusional — fully committed.",
    },
]


# ── Subclass data ──────────────────────────────────────────────────────────────
# Keys: level_gained, key_feature_name, key_feature, flavor

SUBCLASSES: dict[str, dict] = {
    "Barbarian": {
        "Path of the Berserker": {
            "description": "Pure rage refined into unstoppable violence",
            "level_gained": 3,
            "key_feature_name": "Frenzy",
            "key_feature": "Make a bonus action melee attack on every turn of your rage — then suffer one level of exhaustion when it ends",
            "flavor": "the barbarian who has stopped fighting for a reason and fights now because it's the only thing left",
        },
        "Path of the Totem Warrior": {
            "description": "Spiritual warrior bonded to an animal spirit",
            "level_gained": 3,
            "key_feature_name": "Totem Spirit",
            "key_feature": "Bear: resistance to all damage while raging. Eagle: advantage on DEX checks, enemies have disadvantage on opportunity attacks. Wolf: allies have advantage on melee attacks against enemies near you.",
            "flavor": "the barbarian who sees their rage as sacred — an animal walks inside them, and the rage is when it comes out",
        },
        "Path of the Storm Herald": {
            "description": "Rage channeled through elemental fury",
            "level_gained": 3,
            "key_feature_name": "Storm Aura",
            "key_feature": "Emit an elemental aura while raging — tundra (THP for allies), sea (lightning vs nearby enemies), desert (fire damage in radius)",
            "flavor": "the barbarian who doesn't just feel the storm — they ARE the storm, and everything within ten feet knows it",
        },
    },
    "Bard": {
        "College of Lore": {
            "description": "Scholar-performer who collects secrets the way others collect gold",
            "level_gained": 3,
            "key_feature_name": "Cutting Words",
            "key_feature": "Use a Bardic Inspiration die to subtract from an enemy's attack roll, damage roll, or ability check as a reaction",
            "flavor": "the bard who's in every library they can find, every conspiracy they can pry open, always knowing one more thing than they should",
        },
        "College of Valor": {
            "description": "Warrior-poet who inspires through example as much as song",
            "level_gained": 3,
            "key_feature_name": "Combat Inspiration",
            "key_feature": "Inspired allies can add the Inspiration die to weapon damage rolls or to AC against one attack",
            "flavor": "the bard who walks into battle at the front, reciting poetry the whole way, and genuinely believes art and violence are the same impulse",
        },
        "College of Glamour": {
            "description": "Fey-touched enchanter whose beauty and manner are weapons",
            "level_gained": 3,
            "key_feature_name": "Mantle of Inspiration",
            "key_feature": "Spend Bardic Inspiration to give nearby creatures THP and let them immediately move without triggering opportunity attacks",
            "flavor": "the bard who walked out of a fey glade different than they went in, and has been charming things into submission ever since",
        },
    },
    "Cleric": {
        "Life Domain": {
            "description": "Champion of healing and vitality — the purest expression of divine compassion",
            "level_gained": 1,
            "key_feature_name": "Disciple of Life",
            "key_feature": "Your healing spells restore 2 + spell level additional HP per cast",
            "flavor": "the cleric who believes staying alive is itself a form of resistance, and heals with the quiet ferocity of someone who knows what death costs",
        },
        "Light Domain": {
            "description": "Radiant defender against darkness and corruption",
            "level_gained": 1,
            "key_feature_name": "Warding Flare",
            "key_feature": "When attacked, use a reaction to impose disadvantage on that attack roll (WIS modifier times per day)",
            "flavor": "the cleric who takes the command 'be a light in darkness' completely literally, and has the burn marks to prove it",
        },
        "Knowledge Domain": {
            "description": "Keeper of secrets and divine lore",
            "level_gained": 1,
            "key_feature_name": "Blessings of Knowledge",
            "key_feature": "Proficiency in two languages and double proficiency bonus in two skills from: Arcana, History, Nature, or Religion",
            "flavor": "the cleric who experiences their deity as a vast library that answers questions with more questions, and finds this deeply satisfying",
        },
        "Nature Domain": {
            "description": "Divine guardian of wild places and natural order",
            "level_gained": 1,
            "key_feature_name": "Acolyte of Nature",
            "key_feature": "Learn a Druid cantrip; gain proficiency in Animal Handling, Nature, or Survival",
            "flavor": "the cleric who found their god in a forest rather than a temple, and isn't entirely sure the temple crowd would approve",
        },
        "Trickery Domain": {
            "description": "Divine agent of misdirection — the spy of the gods",
            "level_gained": 1,
            "key_feature_name": "Blessing of the Trickster",
            "key_feature": "Grant one willing creature advantage on Stealth checks for one hour",
            "flavor": "the cleric whose deity uses them the way a general uses an operative: deniably and at arm's length",
        },
        "War Domain": {
            "description": "Divine warrior who is the answer to the prayer 'send someone to fight'",
            "level_gained": 1,
            "key_feature_name": "War Priest",
            "key_feature": "Make a bonus action weapon attack when you take the Attack action (WIS modifier times per day)",
            "flavor": "the cleric who draws a weapon first and prays second — or simultaneously, which takes practice",
        },
        "Tempest Domain": {
            "description": "Voice of the storm — wrath made divine",
            "level_gained": 1,
            "key_feature_name": "Wrath of the Storm",
            "key_feature": "When a creature hits you in melee, deal 2d8 lightning or thunder damage as a reaction (WIS modifier times per day)",
            "flavor": "the cleric who interprets 'divine wrath' as a literal meteorological phenomenon and has never once been wrong about it",
        },
    },
    "Druid": {
        "Circle of the Land": {
            "description": "Keeper of natural lore and arcane power drawn from specific terrain",
            "level_gained": 2,
            "key_feature_name": "Natural Recovery",
            "key_feature": "Recover expended spell slots totaling half your Druid level (rounded up) after a short rest, once per day",
            "flavor": "the druid who is more scholar than shapeshifter — the land they're bound to is their book, and they've memorized it",
        },
        "Circle of the Moon": {
            "description": "Wild shapeshifter who transforms into powerful beasts",
            "level_gained": 2,
            "key_feature_name": "Combat Wild Shape",
            "key_feature": "Wild Shape into beasts up to CR 1, use Wild Shape as a bonus action, and spend spell slots to heal while transformed",
            "flavor": "the druid who stops talking when there's a problem and starts becoming something with teeth",
        },
        "Circle of Spores": {
            "description": "Philosopher of decay and rebirth — life and death as one continuous cycle",
            "level_gained": 2,
            "key_feature_name": "Halo of Spores",
            "key_feature": "When a creature moves near you, deal 1d4 necrotic damage as a reaction; Symbiotic Entity doubles your Wild Shape HP and enhances unarmed strikes",
            "flavor": "the druid who finds mushrooms more interesting than flowers, and has some nuanced views on death that other druids find unsettling",
        },
    },
    "Fighter": {
        "Champion": {
            "description": "Physical perfection — simple, direct, devastatingly effective",
            "level_gained": 3,
            "key_feature_name": "Improved Critical",
            "key_feature": "Score critical hits on a roll of 19 or 20 instead of only on 20",
            "flavor": "the fighter who decided that being better at the thing fighters do was better than being clever about it — and has been right every time",
        },
        "Battle Master": {
            "description": "Tactical genius who turns combat into a chess game",
            "level_gained": 3,
            "key_feature_name": "Combat Superiority",
            "key_feature": "4 superiority dice (d8) and 3 maneuvers: Trip Attack, Precision Attack, Riposte, Commander's Strike, and more — each adding the die to specific effects",
            "flavor": "the fighter who has read every military manual ever written and treats each fight as an opportunity to apply chapter seven",
        },
        "Eldritch Knight": {
            "description": "Steel meets sorcery — the martial artist who learned the arcane",
            "level_gained": 3,
            "key_feature_name": "Spellcasting + Weapon Bond",
            "key_feature": "Access to Wizard spells (primarily abjuration and evocation); bond a weapon and summon it to your hand as a bonus action",
            "flavor": "the fighter who decided that swords were interesting but fire was more interesting, and found a way to have both",
        },
    },
    "Monk": {
        "Way of the Open Hand": {
            "description": "Perfection of the body — the purest expression of Monk combat",
            "level_gained": 3,
            "key_feature_name": "Open Hand Technique",
            "key_feature": "After landing a Flurry of Blows hit: knock the target prone, push them 15 feet, or prevent them from using reactions until their next turn",
            "flavor": "the monk who spent years learning to make their body a weapon and has arrived at something that doesn't look like anger anymore",
        },
        "Way of Shadow": {
            "description": "Darkness and silence as art forms — the ninja tradition",
            "level_gained": 3,
            "key_feature_name": "Shadow Arts",
            "key_feature": "Spend ki to cast Darkness, Darkvision, Pass Without Trace, or Silence",
            "flavor": "the monk whose monastery was a school for people who needed to disappear — and they graduated at the top",
        },
        "Way of the Four Elements": {
            "description": "Elemental bender who channels ki into elemental disciplines",
            "level_gained": 3,
            "key_feature_name": "Elemental Disciplines",
            "key_feature": "Spend ki to use elemental techniques: flame strikes, water whips, earth tremors, air blasts — choose disciplines as you level",
            "flavor": "the monk who found a tradition that combined fighting and philosophy with catastrophic weather, and found this appealing",
        },
    },
    "Paladin": {
        "Oath of Devotion": {
            "description": "The classic holy knight — virtue in arms, unwavering",
            "level_gained": 3,
            "key_feature_name": "Sacred Weapon",
            "key_feature": "Add CHA modifier to all attack rolls for one weapon for 1 minute; the weapon emits bright light in a 20-foot radius",
            "flavor": "the paladin who takes their oath literally, holds it completely, and is quietly terrifying to those who've broken things they swore to protect",
        },
        "Oath of the Ancients": {
            "description": "Protector of the light of life — older than any civilization",
            "level_gained": 3,
            "key_feature_name": "Nature's Wrath",
            "key_feature": "Ensnare enemies in spectral vines that restrain them (STR or DEX save), or turn fey and fiends with Turn the Faithless",
            "flavor": "the paladin whose faith is in things that were growing before the first city was built — less concerned with law, more concerned with whether the light survives",
        },
        "Oath of Vengeance": {
            "description": "Relentless hunter of the wicked — mercy is not in the oath",
            "level_gained": 3,
            "key_feature_name": "Abjure Enemy + Vow of Enmity",
            "key_feature": "Frighten a creature and halve its speed (WIS save), or gain advantage on all attacks against one target for one minute",
            "flavor": "the paladin who swore to find the thing that did something unforgivable — and found that keeping that oath has made them hard to distinguish from what they hunt",
        },
        "Oathbreaker": {
            "description": "A paladin who broke their sacred oath and now serves something darker",
            "level_gained": 3,
            "key_feature_name": "Dreadful Aspect",
            "key_feature": "Radiate terror in a 30-foot radius (WIS save), and channel divinity to control undead rather than destroying them",
            "flavor": "the paladin who did something their god couldn't forgive, or whose god could forgive it — and that fact broke them worse",
        },
    },
    "Ranger": {
        "Hunter": {
            "description": "Tactical predator who has learned every trick for killing the specific thing they hunt",
            "level_gained": 3,
            "key_feature_name": "Hunter's Prey",
            "key_feature": "Choose one: Colossus Slayer (extra 1d8 vs already-damaged target), Giant Killer (reaction attack vs Large+), or Horde Breaker (second attack vs adjacent enemy)",
            "flavor": "the ranger who studies the thing before they hunt it and has a preferred technique for every creature type",
        },
        "Beast Master": {
            "description": "Bonded with an animal companion — two hunters in one",
            "level_gained": 3,
            "key_feature_name": "Ranger's Companion",
            "key_feature": "Bond with a beast (CR ¼ or lower) that obeys commands, uses your proficiency bonus, and fights alongside you",
            "flavor": "the ranger whose relationship with their animal is the most honest connection in their life, and knows it",
        },
        "Gloom Stalker": {
            "description": "Darkness specialist — ambush predator who owns the first moment of combat",
            "level_gained": 3,
            "key_feature_name": "Dread Ambusher",
            "key_feature": "+10 ft speed on first turn, an extra attack on first turn, and impose -4 to all enemy initiative rolls",
            "flavor": "the ranger who spent enough time in the dark that the dark became comfortable, and now uses that against everything that hunts in it",
        },
    },
    "Rogue": {
        "Thief": {
            "description": "Dexterity and opportunism — the advantage that comes from never being where you're expected",
            "level_gained": 3,
            "key_feature_name": "Fast Hands + Second-Story Work",
            "key_feature": "Use Cunning Action to pick locks, use thieves' tools, or use an object as a bonus action; climb at full speed without penalty",
            "flavor": "the rogue who has elevated taking things that aren't theirs to something that requires genuine respect",
        },
        "Assassin": {
            "description": "Death as precision craft — the first strike is the only one that matters",
            "level_gained": 3,
            "key_feature_name": "Assassinate",
            "key_feature": "Advantage on all attack rolls against creatures that haven't taken a turn yet; automatic critical hit against surprised targets",
            "flavor": "the rogue for whom patience is the actual skill — anyone can strike, the art is making sure the target never sees it coming",
        },
        "Arcane Trickster": {
            "description": "Misdirection raised to a magical art form",
            "level_gained": 3,
            "key_feature_name": "Spellcasting + Mage Hand Legerdemain",
            "key_feature": "Access to Wizard spells (enchantment and illusion); Mage Hand can pick pockets, pick locks, and disarm traps remotely",
            "flavor": "the rogue who discovered that magic made their existing toolkit considerably harder to defend against, and had thoughts about this",
        },
    },
    "Sorcerer": {
        "Wild Magic": {
            "description": "Raw chaotic power without a proper container — and they've made their peace with it",
            "level_gained": 1,
            "key_feature_name": "Wild Magic Surge",
            "key_feature": "After casting a 1st-level+ spell, the DM may call for a d20 — on a 1, roll on the Wild Magic Surge table (fireball centered on you, turn invisible, sprout wings, etc.)",
            "flavor": "the sorcerer who cannot fully control their power and has decided the chaos is a feature rather than a flaw, even when it absolutely is not",
        },
        "Draconic Bloodline": {
            "description": "Dragon's blood made flesh — power, scales, and ancient pride",
            "level_gained": 1,
            "key_feature_name": "Draconic Resilience",
            "key_feature": "AC = 13 + DEX modifier when unarmored; gain HP equal to your Sorcerer level",
            "flavor": "the sorcerer who knows exactly where their power comes from and has complicated feelings about the ancestor who gave it to them",
        },
        "Divine Soul": {
            "description": "Magic flowing from a celestial or infernal source — the exception to a divine rule",
            "level_gained": 1,
            "key_feature_name": "Divine Magic",
            "key_feature": "Access to the full Cleric spell list in addition to Sorcerer spells; gain Cure Wounds (good) or Inflict Wounds (evil) for free",
            "flavor": "the sorcerer who is technically divine chosen and technically not a Cleric and finds the distinction important for reasons they can't always explain",
        },
    },
    "Warlock": {
        "The Fiend": {
            "description": "Power from a devil or demon — both parties knew what they were doing",
            "level_gained": 1,
            "key_feature_name": "Dark One's Blessing",
            "key_feature": "When you kill a creature, gain THP equal to CHA modifier + Warlock level",
            "flavor": "the warlock who made the deal with clear eyes — and has been paying the price and cashing the check in equal measure ever since",
        },
        "The Great Old One": {
            "description": "Power from something utterly alien — a mind that shouldn't be able to know you, knowing you",
            "level_gained": 1,
            "key_feature_name": "Awakened Mind",
            "key_feature": "Communicate telepathically with any creature you can see within 30 feet in any language",
            "flavor": "the warlock who made contact with something that was paying attention to this world long before they arrived, and the attention has not been comfortable",
        },
        "The Archfey": {
            "description": "Power from the fey courts — glamour, fear, and bargains that mean something else entirely",
            "level_gained": 1,
            "key_feature_name": "Fey Presence",
            "key_feature": "Charm or frighten all creatures in a 10-foot cube around you (WIS save) once per short rest",
            "flavor": "the warlock who made a deal in a forest that seemed reasonable at the time and has been discovering the fine print ever since",
        },
    },
    "Wizard": {
        "School of Evocation": {
            "description": "Raw magical force — the school of people who want fire to do exactly what fire does",
            "level_gained": 2,
            "key_feature_name": "Sculpt Spells",
            "key_feature": "When casting an evocation spell, choose up to (spell level + 1) creatures to automatically succeed their saves and take no damage",
            "flavor": "the wizard who studied evocation because they wanted results and wasn't willing to wait three rounds for conditions to be right",
        },
        "School of Divination": {
            "description": "Knowledge of what is, was, and will be",
            "level_gained": 2,
            "key_feature_name": "Portent",
            "key_feature": "Roll two d20s after a long rest; replace any attack roll, saving throw, or ability check with one of your portent rolls — for any creature",
            "flavor": "the wizard who found that knowing things in advance was more useful than most magic, and has been right about that twice a day ever since",
        },
        "School of Necromancy": {
            "description": "Life, death, and the space between — treated as natural phenomena rather than moral categories",
            "level_gained": 2,
            "key_feature_name": "Grim Harvest",
            "key_feature": "When you kill a creature with a spell, regain HP equal to twice the spell's level (or three times for necromancy spells)",
            "flavor": "the wizard for whom death is data, undead are tools, and the ethical arguments against this position are interesting but ultimately unpersuasive",
        },
        "School of Illusion": {
            "description": "Reality is a negotiation — and they're very good at negotiating",
            "level_gained": 2,
            "key_feature_name": "Improved Minor Illusion",
            "key_feature": "Cast Minor Illusion with both sound and image simultaneously (normally one or the other)",
            "flavor": "the wizard who understood very early that what people believe is more important than what's true, and has been working in that gap ever since",
        },
        "School of Abjuration": {
            "description": "The shield-bearers of the arcane — protection as a form of power",
            "level_gained": 2,
            "key_feature_name": "Arcane Ward",
            "key_feature": "Casting an abjuration spell of level 1+ creates a ward with HP = 2x Wizard level + INT modifier that absorbs damage before you do",
            "flavor": "the wizard who decided that staying alive was the prerequisite for everything else, and has been consistently right about this",
        },
        "School of Transmutation": {
            "description": "Reshaper of matter and form — what is can always become something else",
            "level_gained": 2,
            "key_feature_name": "Minor Alchemy",
            "key_feature": "Touch a non-magical object and temporarily transform it into another material (wood to stone, stone to metal, etc.)",
            "flavor": "the wizard with a practical, optimistic view of the world: if this isn't working, it can probably become something that does",
        },
        "School of Conjuration": {
            "description": "Summoner and teleporter — the school of bringing things from there to here",
            "level_gained": 2,
            "key_feature_name": "Minor Conjuration",
            "key_feature": "Conjure a small object you've seen before (max 3 lbs, 1 cubic foot) that lasts 1 hour",
            "flavor": "the wizard whose solution to most problems is to introduce something new into the situation, usually something with teeth",
        },
        "School of Enchantment": {
            "description": "Mind as the battlefield — make them want to cooperate",
            "level_gained": 2,
            "key_feature_name": "Hypnotic Gaze",
            "key_feature": "As an action, hold one creature within 5 feet charmed and incapacitated (WIS save each turn to break) — action reusable once it sticks",
            "flavor": "the wizard who noticed that changing people's minds was more efficient than overcoming their bodies, and has been right every time the alternative would have involved more explosions",
        },
    },
}


# ── Villain data ───────────────────────────────────────────────────────────────

VILLAIN_SCHEMES: list[dict] = [
    {
        "scheme": "Domination",
        "goal": "Control over a city, region, or institution — total and permanent",
        "method": "Fear, leverage, and strategic elimination of anyone capable of organizing resistance",
        "signature": "They have already won somewhere. The current target is just the next one.",
    },
    {
        "scheme": "Revenge",
        "goal": "Systematic destruction of those who wronged them — and everyone connected to them",
        "method": "Patience, preparation, and escalating attacks designed to make the target understand who is coming for them",
        "signature": "They started with someone specific and the list has been growing ever since.",
    },
    {
        "scheme": "Ascension",
        "goal": "Achieve godhood, lichdom, immortality, or transcendence — at any cost",
        "method": "Ritual sacrifice, forbidden research, deals with entities that require payment in suffering",
        "signature": "Everything they do is preparation. They are not in a hurry because they intend to have all the time in the world.",
    },
    {
        "scheme": "Purification",
        "goal": "Eliminate what they've decided is wrong with the world — starting locally, expanding outward",
        "method": "They have a list. They work the list. The definition of 'wrong' expands as the list shrinks.",
        "signature": "They believe they are doing good. This is what makes them dangerous.",
    },
    {
        "scheme": "Collection",
        "goal": "Amass a specific type of power, knowledge, or object regardless of cost",
        "method": "Acquisition by purchase, theft, coercion, or destruction of anyone who won't cooperate",
        "signature": "They have already collected more than anyone knows. The collection has become its own logic.",
    },
    {
        "scheme": "Protection",
        "goal": "Shield something or someone they love at the expense of everyone else",
        "method": "Preemptive strikes, elimination of threats, ruthless sacrifice of anything that isn't the protected thing",
        "signature": "Ask them why they do what they do and they will tell you without hesitation. They do not see this as a flaw.",
    },
    {
        "scheme": "Restoration",
        "goal": "Rebuild something destroyed — an empire, a people, a way of life — through means no one else would accept",
        "method": "Historical revisionism, forced cultural reclamation, violence against those seen as the cause of the original loss",
        "signature": "They have documents, artifacts, and witnesses to what was lost. The grief is real. The methods are not.",
    },
    {
        "scheme": "Liberation",
        "goal": "Free something or someone — a people, a creature, a power — convinced it is righteous",
        "method": "Sabotage of the systems holding the target captive, rallying of followers, escalating force",
        "signature": "They started as a genuine freedom fighter. Something changed — the cause, the methods, or them.",
    },
    {
        "scheme": "Forbidden Discovery",
        "goal": "Learn something that was hidden for a reason",
        "method": "Archaeological violence, torture of those who know, destruction of those who would stop them",
        "signature": "They don't fully understand what they're looking for. They are close, and when they find it, they will not be prepared for it.",
    },
    {
        "scheme": "Devotion",
        "goal": "Serve a power — a patron, a god, an ideology — that demands harm as tribute",
        "method": "Whatever the power requires. They ask no questions.",
        "signature": "They were not always like this. There was a moment when they chose this, and they remember it as the best decision they ever made.",
    },
]

VILLAIN_WOUNDS: list[dict] = [
    {
        "wound": "Betrayal",
        "origin": "Someone they trusted — mentor, ally, lover, institution — destroyed something irreplaceable",
        "what_it_did": "They learned that loyalty is a weapon other people use against you",
        "what_remains": "A list. Not a metaphorical one.",
    },
    {
        "wound": "Loss",
        "origin": "A death they couldn't prevent or couldn't forgive themselves for",
        "what_it_did": "The grief became the loudest thing about them, and they eventually stopped fighting it",
        "what_remains": "They still talk to the person who is gone. Sometimes they talk back.",
    },
    {
        "wound": "Injustice",
        "origin": "A system failed them catastrophically — court, church, guild, crown — and no one was held accountable",
        "what_it_did": "They decided the system was the enemy, not the individuals inside it",
        "what_remains": "They are not wrong that the system was unjust. They are wrong about what to do about it.",
    },
    {
        "wound": "Forbidden Truth",
        "origin": "They learned something that broke their understanding of the world",
        "what_it_did": "The old values stopped making sense. New ones grew in the wreckage.",
        "what_remains": "They want to share what they learned. The problem is what people will do when they know.",
    },
    {
        "wound": "Transformation",
        "origin": "Something was done to them — magic, experiment, curse, divine intervention — that changed who they are",
        "what_it_did": "The person before the change and the person after are not the same. They have not made peace with this.",
        "what_remains": "They are looking for whoever did it. They haven't decided what they'll do when they find them.",
    },
    {
        "wound": "Obsession",
        "origin": "A fixation that started as grief and became identity",
        "what_it_did": "Everything that was not the obsession fell away — people, principles, self-preservation",
        "what_remains": "Ask them about the thing they're obsessed with and they become a different person. Warmer. More present. More dangerous.",
    },
    {
        "wound": "Corruption",
        "origin": "A power or entity got into them slowly and they let it — because it solved a problem",
        "what_it_did": "The original self is still in there, getting smaller",
        "what_remains": "Occasionally they surface. In those moments they are aware of exactly what has happened to them.",
    },
    {
        "wound": "Desperation",
        "origin": "They saw no other way and chose this rather than surrender or die",
        "what_it_did": "The choice that seemed temporary became permanent",
        "what_remains": "They still believe they had no choice. They have stopped asking whether that's true.",
    },
]


# ── Tool functions ─────────────────────────────────────────────────────────────

def roll_alignment() -> str:
    """Roll a random alignment with a concrete behavioral expression, internal tension, and shadow tendency."""
    entry      = random.choice(ALIGNMENTS)
    expression = random.choice(entry["expressions"])
    return json.dumps({
        "alignment":  entry["name"],
        "expression": expression,
        "tension":    entry["tension"],
        "shadow":     entry["shadow"],
    })


def roll_quest_hook() -> str:
    """Randomly select a quest type and complication seed for a D&D encounter."""
    hook         = random.choice(QUEST_HOOKS)
    complication = random.choice(hook["complications"])
    return json.dumps({
        "quest_type":   hook["type"],
        "description":  hook["description"],
        "complication": complication,
    })


def roll_dice(sides: int, count: int = 1) -> str:
    if sides not in VALID_DICE:
        return f"Error: {sides} is not a valid die. Choose from: {sorted(VALID_DICE)}"
    if not (MIN_ROLLS <= count <= MAX_ROLLS):
        return f"Error: count must be between {MIN_ROLLS} and {MAX_ROLLS}, got {count}"
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"

def roll_stat() -> str:
    """Roll 4d6 and drop the lowest — the standard D&D 5e stat generation method."""
    rolls = [random.randint(1, 6) for _ in range(4)]
    dropped = min(rolls)
    kept    = sorted(rolls, reverse=True)[:3]
    return f"Rolled 4d6: {sorted(rolls)} → dropped lowest ({dropped}) → kept {kept} → score: {sum(kept)}"

def get_race_info(race_name: str) -> str:
    if race_name not in RACES:
        return f"Unknown race '{race_name}'. Available: {list(RACES.keys())}"
    return json.dumps(RACES[race_name], indent=2)

def get_class_info(class_name: str) -> str:
    if class_name not in CLASSES:
        return f"Unknown class '{class_name}'. Available: {list(CLASSES.keys())}"
    return json.dumps(CLASSES[class_name], indent=2)

def get_background_info(background_name: str) -> str:
    if background_name not in BACKGROUNDS:
        return f"Unknown background '{background_name}'. Available: {list(BACKGROUNDS.keys())}"
    return json.dumps(BACKGROUNDS[background_name], indent=2)


def calculate_ac(
    armor_type: str,
    dex_modifier: int,
    class_name: str = "",
    con_modifier: int = 0,
    wis_modifier: int = 0,
    has_shield: bool = False,
) -> str:
    """Calculate AC from armor type, relevant modifiers, and shield."""
    if armor_type not in ARMOR_TABLE:
        return json.dumps({
            "error": f"Unknown armor type '{armor_type}'. Options: {list(ARMOR_TABLE.keys())}"
        })
    armor = ARMOR_TABLE[armor_type]
    ac    = armor["base"]

    if armor.get("dex"):
        dex_add = dex_modifier
        if armor.get("dex_max") is not None:
            dex_add = min(dex_modifier, armor["dex_max"])
        ac += dex_add

    if armor.get("add_con"):
        ac += con_modifier
    if armor.get("add_wis"):
        ac += wis_modifier

    shield_bonus = 2 if has_shield else 0
    ac += shield_bonus

    # Build human-readable formula string
    parts = [str(armor["base"])]
    if armor.get("dex"):
        cap = armor.get("dex_max")
        parts.append(f"DEX{f' (max +{cap})' if cap is not None else ''}")
    if armor.get("add_con"):
        parts.append("CON")
    if armor.get("add_wis"):
        parts.append("WIS")
    if has_shield:
        parts.append("+2 (shield)")

    return json.dumps({
        "armor_type": armor_type,
        "ac":         ac,
        "formula":    " + ".join(parts),
        "has_shield": has_shield,
    })


def pick_skills(class_name: str, background_skills: list | None = None) -> str:
    """Return the valid class skill options and count for the given class.

    background_skills lists skills already granted by background so Claude
    can avoid duplicates when choosing class skills.
    """
    if class_name not in SKILL_POOLS:
        return json.dumps({"error": f"Unknown class '{class_name}'. Available: {list(SKILL_POOLS.keys())}"})
    pool         = SKILL_POOLS[class_name]
    already_have = background_skills or []

    if pool["options"] == "any":
        available = [s for s in ALL_SKILLS if s not in already_have]
    else:
        available = [s for s in pool["options"] if s not in already_have]

    return json.dumps({
        "class":        class_name,
        "choose":       pool["count"],
        "available":    available,
        "already_have": already_have,
        "note": (
            f"Pick exactly {pool['count']} skill(s) from 'available'. "
            "Do not pick skills from outside this list. "
            "Skills in 'already_have' come from the background — don't duplicate them."
        ),
    })


def roll_deity(domain_hint: str = "", alignment_hint: str = "") -> str:
    """Suggest a deity appropriate for the character's class and inclinations."""
    pool = DEITIES
    if domain_hint:
        filtered = [d for d in pool if domain_hint.lower() in d["domain"].lower()]
        if filtered:
            pool = filtered
    if alignment_hint:
        filtered = [d for d in pool if alignment_hint.lower() in d["alignment"].lower()]
        if filtered:
            pool = filtered
    deity = random.choice(pool)
    return json.dumps(deity)


def calculate_combat_stats(
    class_name: str,
    str_modifier: int,
    dex_modifier: int,
    int_modifier: int = 0,
    wis_modifier: int = 0,
    cha_modifier: int = 0,
) -> str:
    """Return initiative, weapon attack bonuses, and (for spellcasters) spell save DC
    and spell attack bonus. All values assume level 1 (proficiency bonus +2)."""
    if class_name not in CLASSES:
        return json.dumps({
            "error": f"Unknown class '{class_name}'. Available: {list(CLASSES.keys())}"
        })

    pb = PROFICIENCY_BONUS
    mod_map = {
        "STR": str_modifier, "DEX": dex_modifier,
        "INT": int_modifier, "WIS": wis_modifier, "CHA": cha_modifier,
    }

    def fmt(n: int) -> str:
        return f"+{n}" if n >= 0 else str(n)

    result: dict = {
        "proficiency_bonus":  pb,
        "initiative":         fmt(dex_modifier),
        "str_attack_bonus":   fmt(str_modifier + pb),
        "dex_attack_bonus":   fmt(dex_modifier + pb),
        "note": (
            "Use str_attack_bonus for STR-based melee weapons (longswords, axes, etc.). "
            "Use dex_attack_bonus for finesse weapons (rapiers, daggers) and ranged attacks."
        ),
    }

    spell_stat = SPELLCASTING_STAT.get(class_name)
    if spell_stat:
        spell_mod = mod_map[spell_stat]
        result["spellcasting_ability"]  = spell_stat
        result["spell_save_dc"]         = 8 + pb + spell_mod
        result["spell_attack_bonus"]    = fmt(pb + spell_mod)

    return json.dumps(result)


def get_subclass_info(class_name: str, subclass_name: str) -> str:
    """Return the full data for a specific subclass — level gained, key feature, and flavor."""
    if class_name not in SUBCLASSES:
        return json.dumps({
            "error": f"Unknown class '{class_name}'. Available: {list(SUBCLASSES.keys())}"
        })
    class_subs = SUBCLASSES[class_name]
    if subclass_name not in class_subs:
        return json.dumps({
            "error": f"Unknown subclass '{subclass_name}' for {class_name}. "
                     f"Available: {list(class_subs.keys())}"
        })
    return json.dumps(class_subs[subclass_name])


def roll_villain_profile() -> str:
    """Randomly pick a villain scheme and wound — the core of what drives this antagonist."""
    scheme = random.choice(VILLAIN_SCHEMES)
    wound  = random.choice(VILLAIN_WOUNDS)
    return json.dumps({"scheme": scheme, "wound": wound})


# ── Tool schemas (Claude's side) ───────────────────────────────────────────────

TOOLS = [
    {
        "name": "roll_stat",
        "description": "Roll one ability score using the standard 4d6-drop-lowest method. Call this 6 times for STR, DEX, CON, INT, WIS, CHA.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_dice",
        "description": "Roll any standard D&D dice. Use for HP rolls, random table results, or anything needing open-ended randomness.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {
                    "type": "integer",
                    "description": "Number of sides on the die.",
                    "enum": sorted(VALID_DICE),
                },
                "count": {
                    "type": "integer",
                    "description": "Number of dice to roll.",
                    "minimum": MIN_ROLLS,
                    "maximum": MAX_ROLLS,
                },
            },
            "required": ["sides"],
        },
    },
    {
        "name": "get_race_info",
        "description": "Look up a race's ability score bonuses, racial traits, speed, languages, and flavor. Use this to pick a race that fits the rolled stats.",
        "input_schema": {
            "type": "object",
            "properties": {
                "race_name": {
                    "type": "string",
                    "description": "Race name.",
                    "enum": list(RACES.keys()),
                },
            },
            "required": ["race_name"],
        },
    },
    {
        "name": "get_class_info",
        "description": "Look up a class's hit die, primary stats, saving throws, armor and weapon proficiencies, typical_armor, and flavor.",
        "input_schema": {
            "type": "object",
            "properties": {
                "class_name": {
                    "type": "string",
                    "description": "Class name.",
                    "enum": list(CLASSES.keys()),
                },
            },
            "required": ["class_name"],
        },
    },
    {
        "name": "get_background_info",
        "description": "Look up a background's skill proficiencies, tools, feature, personality seeds (traits, ideals, bonds, flaws), and story hooks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "background_name": {
                    "type": "string",
                    "description": "Background name.",
                    "enum": list(BACKGROUNDS.keys()),
                },
            },
            "required": ["background_name"],
        },
    },
    {
        "name": "pick_skills",
        "description": (
            "Return the valid class skill options and how many to choose. "
            "Call this after selecting BOTH class AND background. "
            "Pass background_skills so duplicates are filtered out. "
            "You MUST pick class skills only from the returned 'available' list."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "class_name": {
                    "type": "string",
                    "description": "The character's class.",
                    "enum": list(SKILL_POOLS.keys()),
                },
                "background_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Skills already granted by the background (e.g. ['Insight', 'Religion']). Pass [] if none.",
                },
            },
            "required": ["class_name"],
        },
    },
    {
        "name": "calculate_ac",
        "description": (
            "Calculate Armor Class from armor type and ability modifiers. "
            "Call this after gear is established. "
            "Use the class's typical_armor from get_class_info as a starting point, "
            "adjusted for what the gear roll actually returned. "
            "Pass has_shield=true if a shield appeared in the gear."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "armor_type": {
                    "type": "string",
                    "description": "The armor being worn.",
                    "enum": list(ARMOR_TABLE.keys()),
                },
                "dex_modifier": {
                    "type": "integer",
                    "description": "The character's DEX modifier (may be negative).",
                },
                "class_name": {
                    "type": "string",
                    "description": "The character's class.",
                },
                "con_modifier": {
                    "type": "integer",
                    "description": "CON modifier — only needed for Barbarian Unarmored.",
                },
                "wis_modifier": {
                    "type": "integer",
                    "description": "WIS modifier — only needed for Monk Unarmored.",
                },
                "has_shield": {
                    "type": "boolean",
                    "description": "True if the character has a shield in their gear.",
                },
            },
            "required": ["armor_type", "dex_modifier"],
        },
    },
    {
        "name": "roll_deity",
        "description": (
            "Suggest a deity for a Cleric, Paladin, or Acolyte background character. "
            "Call this after the class and subclass direction are established. "
            "Pass domain_hint to filter by domain (e.g. 'War', 'Life', 'Trickery', 'Death', 'Nature', 'Knowledge', 'Tempest'). "
            "Pass alignment_hint to filter by alignment (e.g. 'Good', 'Lawful', 'Evil', 'Neutral'). "
            "Both are optional — omit for a fully random result."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_hint": {
                    "type": "string",
                    "description": "Domain keyword to filter by, e.g. 'War', 'Life', 'Trickery'.",
                },
                "alignment_hint": {
                    "type": "string",
                    "description": "Alignment keyword to filter by, e.g. 'Good', 'Neutral', 'Evil', 'Lawful', 'Chaotic'.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_subclass_info",
        "description": (
            "Look up a specific subclass — returns its level_gained (when it unlocks), "
            "key_feature_name, key_feature (what it does mechanically), and flavor (the kind of character who takes it). "
            "Call this in Step 3 after committing to a class, before writing any backstory. "
            "The subclass's flavor and feature should shape the character concept directly.\n\n"
            "Subclasses by class:\n"
            "Barbarian: Path of the Berserker, Path of the Totem Warrior, Path of the Storm Herald\n"
            "Bard: College of Lore, College of Valor, College of Glamour\n"
            "Cleric: Life Domain, Light Domain, Knowledge Domain, Nature Domain, Trickery Domain, War Domain, Tempest Domain\n"
            "Druid: Circle of the Land, Circle of the Moon, Circle of Spores\n"
            "Fighter: Champion, Battle Master, Eldritch Knight\n"
            "Monk: Way of the Open Hand, Way of Shadow, Way of the Four Elements\n"
            "Paladin: Oath of Devotion, Oath of the Ancients, Oath of Vengeance, Oathbreaker\n"
            "Ranger: Hunter, Beast Master, Gloom Stalker\n"
            "Rogue: Thief, Assassin, Arcane Trickster\n"
            "Sorcerer: Wild Magic, Draconic Bloodline, Divine Soul\n"
            "Warlock: The Fiend, The Great Old One, The Archfey\n"
            "Wizard: School of Evocation, School of Divination, School of Necromancy, School of Illusion, "
            "School of Abjuration, School of Transmutation, School of Conjuration, School of Enchantment"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "class_name": {
                    "type": "string",
                    "description": "The character's class.",
                    "enum": list(SUBCLASSES.keys()),
                },
                "subclass_name": {
                    "type": "string",
                    "description": "Exact subclass name from the list in the description.",
                },
            },
            "required": ["class_name", "subclass_name"],
        },
    },
    {
        "name": "roll_villain_profile",
        "description": (
            "Randomly select a villain scheme (what they want and how they pursue it) "
            "and a wound (what made them this way). "
            "Call this first when generating a villain — before race, class, or backstory. "
            "The scheme and wound are the core of who this villain is; everything else grows from them."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "calculate_combat_stats",
        "description": (
            "Calculate initiative, weapon attack bonuses, and (for spellcasters) spell save DC "
            "and spell attack bonus at level 1. Call this immediately after calculate_ac. "
            "Proficiency bonus at level 1 is always +2."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "class_name": {
                    "type": "string",
                    "description": "The character's class.",
                    "enum": list(CLASSES.keys()),
                },
                "str_modifier": {
                    "type": "integer",
                    "description": "STR modifier (may be negative).",
                },
                "dex_modifier": {
                    "type": "integer",
                    "description": "DEX modifier (may be negative).",
                },
                "int_modifier": {
                    "type": "integer",
                    "description": "INT modifier — needed for Wizard spellcasting DC.",
                },
                "wis_modifier": {
                    "type": "integer",
                    "description": "WIS modifier — needed for Cleric, Druid, Ranger spellcasting DC.",
                },
                "cha_modifier": {
                    "type": "integer",
                    "description": "CHA modifier — needed for Bard, Paladin, Sorcerer, Warlock spellcasting DC.",
                },
            },
            "required": ["class_name", "str_modifier", "dex_modifier"],
        },
    },
    DND_NAME_TOOL_SCHEMA,
    DND_SPELL_TOOL_SCHEMA,
    DND_GEAR_TOOL_SCHEMA,
    {
        "name": "roll_alignment",
        "description": (
            "Roll a random alignment — returns the alignment name, a concrete behavioral expression "
            "(how this alignment shows up in action, not as abstract philosophy), an internal tension "
            "(what makes it interesting to play), and a shadow tendency (how it can go wrong). "
            "Call this after background is established so alignment grows from who the character already is."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_quest_hook",
        "description": (
            "Randomly select a quest type and complication seed for a D&D encounter. "
            "Call this first before building a quest giver's details. "
            "This prevents defaulting to the same quest type every time."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a D&D 5th Edition character generator creating vivid, story-ready characters.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names must feel appropriate to the character's race. After choosing a race, call roll_dnd_name_suggestion(race=...) — pass the race you chose to get race-appropriate naming conventions. Dwarves get compound epithets, Halflings get cosy family names, Tieflings get names carrying infernal heritage with dark poetry, Elves get elvish syllable-names. Human characters draw from real-world cultural traditions. Adapt the result freely — it's a starting point, not a mandate.

Work through these steps in order, using your tools at each stage:

1. ABILITY SCORES — Call roll_stat six times, one per ability in this order:
   Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma.
   Note all six scores before moving on.

2. RACE — Choose a race that fits the stats and any constraints given.
   Call get_race_info to look it up. Apply the racial ability score bonuses to the rolled scores.
   Note the race's Speed and Languages — these go directly on the sheet.
   Then call roll_dnd_name_suggestion(race="[chosen race]") to get a name in the right register.

3. CLASS & SUBCLASS — Choose a class that suits the final stats and the emerging character concept.
   Call get_class_info. Note the hit die, saving throws, proficiencies, and the typical_armor field.
   Calculate HP at level 1: max hit die value + CON modifier.
   SUBCLASS — Commit to a specific subclass (don't just hint — choose one). Call get_subclass_info to
   get the key_feature and flavor. The subclass should shape the character's concept, backstory, and
   how they're described throughout the sheet. Note: level_gained tells you when it unlocks
   (1 for Cleric/Warlock/Sorcerer, 2 for Druid/Wizard, 3 for most others).
   DEITY — If the class is Cleric or Paladin, call roll_deity now with a domain_hint matching the
   subclass direction (e.g. "Life", "War", "Trickery", "Death", "Knowledge", "Tempest").
   The returned deity shapes the character's outlook, spell flavor, and connections.
   SPELLS — If this is a spellcasting class (Wizard, Sorcerer, Cleric, Druid, Bard, Warlock, Paladin,
   or Ranger), call get_spell_suggestions(class_name=...). The result has separate "cantrips" and "spells"
   arrays — pick 1-2 cantrips and 2-3 leveled spells that feel true to this character.

4. BACKGROUND — Choose a background that fits the character's story so far.
   Call get_background_info. Use the personality seeds as inspiration — not verbatim, but as starting points.
   After choosing, immediately call pick_skills(class_name="[chosen class]",
   background_skills=[...exact skill names from the background...]).
   You MUST select class skills ONLY from the "available" list that pick_skills returns — no exceptions.
   DEITY for Acolyte — if background is Acolyte AND class is not Cleric/Paladin, call roll_deity now.
   CONNECTIONS — generate at least one named NPC from the background's story hooks:
     - A mentor, patron, or ally → ALLY or CONTACT (name, one sentence, relationship)
     - A rival, enemy, or antagonist → ENEMY or RIVAL (name, one sentence, relationship)
   Make these specific people, not abstractions.

5. ALIGNMENT — Call roll_alignment() now, after background is established.
   Use the returned expression to show — not tell — how this character's alignment works in practice.
   Let the tension complicate the backstory. Let the shadow hint at where they might go wrong.
   Do not write "this character is [alignment]" in the backstory — let it live in what they do.

6. GEAR & AC & COMBAT — Call roll_dnd_gear(class_name="[chosen class]") — all returned items must appear in Equipment.
   Then immediately call calculate_ac:
   - Use the armor_type from the class's typical_armor field, adjusted if the gear roll returned different armor
   - Pass the DEX modifier
   - Pass has_shield=true if a shield appeared in the gear
   - For Barbarian: use "Barbarian Unarmored" and pass con_modifier
   - For Monk: use "Monk Unarmored" and pass wis_modifier
   - For Lizardfolk without armor: use "Natural Armor"
   Then immediately call calculate_combat_stats(class_name="[class]", str_modifier=X, dex_modifier=Y).
   - For spellcasting classes also pass the relevant ability modifier:
     Wizard → int_modifier; Cleric/Druid/Ranger → wis_modifier; Bard/Paladin/Sorcerer/Warlock → cha_modifier.

7. CHARACTER SHEET — Always use exactly this format:

## **[Full Name, with nickname in quotes if it fits]**

| | |
|---|---|
| **Race** | [Race] |
| **Class** | [Class] (Level 1) |
| **Subclass** | [Subclass name] *(unlocks at level [N] — use level_gained from get_subclass_info)* |
| **Background** | [Background] |
| **Alignment** | [Alignment from roll_alignment — the name only, e.g. "Chaotic Good"] |
| **HP** | [hp] |
| **AC** | [from calculate_ac result] |
| **Speed** | [from race info — e.g. "30 ft"] |
| **Initiative** | [from calculate_combat_stats — e.g. "+2"] |
| **Proficiency Bonus** | +2 |
| **Attack Bonus** | [from calculate_combat_stats — list the relevant bonus(es): e.g. "STR +4" for fighters, "DEX +5 / STR +3" for rogues, "Spell +6" for pure casters] |
| **Spell Save DC** | [from calculate_combat_stats — omit this row entirely for non-spellcasters] |
| **Spell Attack Bonus** | [from calculate_combat_stats — omit this row entirely for non-spellcasters] |

### Ability Scores
| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| [score] ([mod]) | [score] ([mod]) | [score] ([mod]) | [score] ([mod]) | [score] ([mod]) | [score] ([mod]) |

Then one evocative line per ability (only 1-2 words, not full sentences — just a sharp label):
- **STR [score]** — [sharp descriptor]
- **DEX [score]** — [sharp descriptor]
- **CON [score]** — [sharp descriptor]
- **INT [score]** — [sharp descriptor]
- **WIS [score]** — [sharp descriptor]
- **CHA [score]** — [sharp descriptor]

For the single highest ability score, add one *italic* sentence about how they got it or what it means about them.

### Proficiencies & Skills
- **Saving Throws:** [from class]
- **Skills:** [list all proficient skills — class picks from pick_skills result + background skills, no duplicates]
- **Passive Perception:** [10 + WIS modifier + 5 if proficient in Perception, else 10 + WIS modifier]
- **Languages:** [all languages from race info + any bonus from background (Sage/Noble/Guild Artisan/Hermit add 1-2 extra) or high INT]
- **Tools & Other:** [tools from background, any other proficiencies]

### Personality
- **Trait:** [drawn from background seeds but made specific to this character]
- **Ideal:** [what they believe in]
- **Bond:** [what they can't leave behind]
- **Flaw:** [the crack in the armor]

### Deity *(Cleric / Paladin / Acolyte background only — omit entirely for all other classes/backgrounds)*
- **[Deity name]** — [Domain] — [one sentence on how this character personally relates to their god]

### Connections
- **[Category] — [Full Name]:** [one sentence: who they are and their relationship to the character]
Categories: Ally, Contact, Enemy, Rival.

### Equipment
[List every item returned by roll_dnd_gear — don't skip any. Each item is on its own line with a dash.
The weapon should feel worn in, not new off a table. The personal item (always last) gets one additional
sentence: what it suggests about who this person is or was.]

### Cantrips *(spellcasting classes only — omit for non-casters)*
[List each chosen cantrip with one sentence on how this character uses it.]

### Spells Known *(spellcasting classes only — omit for non-casters)*
[List each chosen leveled spell with level, school, and one sentence on how this character uses it.]

### Backstory
Three sentences. A past, a wound, and a direction."""

NPC_SYSTEM_PROMPT = """You are a D&D 5e NPC generator. Create a vivid, instantly usable NPC sketch.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names must feel appropriate to the NPC's race. Decide the race first, call get_race_info (note speed and languages), then call roll_dnd_name_suggestion(race="[race]") — Dwarves get compound epithets, Halflings get cosy family names, Tieflings carry infernal heritage with dark poetry. Human NPCs draw from real-world cultural traditions for maximum diversity. Adapt the result freely.

Roll a few key stats with roll_stat (only the ones that matter for this NPC's role — not all six).
Look up race or class info if it would help ground them.
If the NPC is a spellcaster, call get_spell_suggestions(class_name=...) and pick 2 signature spells —
one cantrip from the "cantrips" array and one leveled spell from the "spells" array if possible.
Write one sentence each on how this specific person uses them.
Call roll_alignment() — let the expression and tension color the Demeanor and Secret without naming the alignment explicitly.
If the NPC is a Cleric or Paladin, call roll_deity with an appropriate domain_hint.
Then produce the sketch — fast and sharp.

Always use exactly this format:

## **[Name]**
*[Race] [Class or Occupation] — [one sharp hook sentence]*

| | |
|---|---|
| **Alignment** | [Alignment from roll_alignment — name only] |
| **Speed** | [from race info] |
| **Languages** | [from race info] |
| **[Most relevant stat]** | [score] ([modifier]) |
| **[Second stat]** | [score] ([modifier]) |
| **[Third stat]** | [score] ([modifier]) |

**Demeanor:** [1-2 sentences — how they present, what you notice first]
**Wants:** [what they need right now — specific]
**Secret:** [one thing they're hiding — specific, not vague]
**Hook:** [one concrete way they pull adventurers into their orbit]
**Connection:** [one named person they love, fear, or owe — and why it matters]"""

QUEST_GIVER_SYSTEM_PROMPT = """You are a D&D 5e quest giver generator. Create a complete encounter — someone who approaches the party in a tavern, on the road, at a temple door, or in a noble's study, and asks them for help.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names must feel appropriate to the character's race. Decide the race first, call get_race_info (note speed and languages), then call roll_dnd_name_suggestion(race="[race]") — pass the race you chose. Human quest givers draw from real-world cultural traditions for maximum diversity. Adapt the result freely — it's a starting point, not a mandate.

STEP 0 (before writing anything):
1. Call roll_quest_hook() — build the entire encounter around what it returns. The quest type determines the Ask and what they're offering. The complication seed should surface in at least one of the four Truths. Do not default to the same quest type unless roll_quest_hook returns that category.
2. Decide the quest giver's race, call get_race_info, then call roll_dnd_name_suggestion(race="[race]") for a race-appropriate name.
3. Look up a background with get_background_info to establish who this person is and what world they come from.
4. Roll 1d6 once to add a random element to their situation — let it color something about them.
5. Call roll_alignment() — let the alignment's expression shape how they present and The Ask; let its tension decide which of the four Truths cuts deepest for them.
6. If the quest giver is a Cleric, Paladin, or Acolyte, call roll_deity with an appropriate domain_hint.

The encounter has four possible truths — the DM rolls 1d4 in secret. Make all four truths plausible from the party's perspective. The quest giver doesn't know which truth the DM rolled — they behave the same way regardless.

Always use exactly this format:

## **[Full Name]**
*Quest Giver — [who they appear to be in one phrase]*

| | |
|---|---|
| **Appears to be** | [what the party sees — occupation, station, mood] |
| **Actually is** | [the real story — revealed only in Truth 2, 3, or 4] |
| **Alignment** | [Alignment from roll_alignment — name only] |
| **Speed** | [from race info] |
| **Languages** | [from race info] |

**Appearance:** [2 sentences — what the party notices when this person approaches. Specific: clothing, manner, what they're carrying, what they're not saying.]

**The Ask:** *[Write this as direct speech — what the quest giver actually says to the party. 3–5 sentences. A real person's voice, not a mission briefing. Fear, hope, desperation, or carefully controlled calm — make it felt.]*

**What They Want:** [The task, stated plainly. Where, what, who, how. Specific enough to act on.]

**What They're Offering:** [Payment. Be concrete — gold, information, an introduction, a favor, an heirloom, a title. Something that means something.]

**The Truth (DM rolls 1d4):**
1. **Clean** — [Everything is as stated. The quest giver is who they say they are. There's still a real complication — danger, difficulty, something unexpected — but no deception. The party gets what they signed up for.]
2. **Complicated** — [The quest giver is not quite who they appear, or the situation is not quite what they described. They're not lying exactly — but they left something important out. The party is being used, knowingly or not, for something adjacent to what was advertised.]
3. **The Real Story** — [The surface job is a cover, a distraction, or the least important part of what's actually happening. The quest giver has a hidden agenda, a hidden identity, or is themselves in danger they haven't disclosed. The party may be pawns — or the only people who can actually fix this.]
4. **The Reversal** — [The party is on the wrong side of this story. The person the quest giver wants found doesn't want to be found — and has good reason. The thing they want stopped is protecting someone. The villain of this job is the quest giver, knowingly or not. Nothing they said was technically false. All of it pointed the wrong direction. The party's first instinct, on realizing this, should be to wonder what they've already set in motion.]

**Why They'd Say Yes:** [One sentence — the reason this particular group of adventurers would take the job despite any misgivings.]

**Connection:** [One named person who knows this quest giver — a reference, a warning, or a loose thread. Why that name matters.]"""

VILLAIN_SYSTEM_PROMPT = """You are a D&D 5e villain generator. Create a complete, playable antagonist — someone with a scheme, a wound, and a world that reacts to them.

Avoid clichés tied to race, class, sex, or ethnicity. The wound must be specific and personal, not archetypal. The scheme must be concrete enough to act against.

STEP 0 (before writing anything):
1. Call roll_villain_profile() — the returned scheme and wound are the core of who this villain is. Everything else is built around them. The scheme tells you what they want and how they pursue it. The wound tells you what made them this way.
2. Roll ability scores with roll_stat six times for STR, DEX, CON, INT, WIS, CHA.
3. Choose a race that fits the scheme and wound — call get_race_info (note speed and languages).
4. Choose a class that serves the scheme — call get_class_info. Choose a subclass — call get_subclass_info.
5. Call roll_dnd_name_suggestion(race="[race]") for a name appropriate to the race.
6. Call roll_alignment() — the alignment expression should make the scheme feel inevitable, not monstrous.
7. If the villain is a spellcaster, call get_spell_suggestions — pick 1 cantrip and 2 spells that feel like tools of the scheme.
8. If the class is Cleric or Paladin, call roll_deity with a domain matching the scheme.

Always use exactly this format:

## **[Full Name]**
*[Race] [Class] / [Subclass] — [one sentence: what they are to the people who fear them]*

| | |
|---|---|
| **Alignment** | [Alignment from roll_alignment — name only] |
| **Race** | [Race] |
| **Class / Subclass** | [Class] / [Subclass] *(unlocks at level N)* |
| **Speed** | [from race info] |
| **Languages** | [from race info] |
| **HP** | [max hit die + CON modifier] |

### Ability Scores
| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| [score] ([mod]) | [score] ([mod]) | [score] ([mod]) | [score] ([mod]) | [score] ([mod]) | [score] ([mod]) |

### The Scheme
**[Scheme name]** — [What they want. Specific: what city, what power, what outcome. Not 'domination' in the abstract — domination of what, by when, and what is in the way.]

**Method:** [How they pursue it. The signature behavior — not the entire plan, but the thing they do that makes people afraid or confused.]

**How far along they are:** [One sentence. They have already succeeded at something. What?]

### The Wound
**[Wound name]** — [What happened to them. Specific: what was lost, who was responsible, what they know now that they didn't know then.]

**What it cost them:** [One sentence on what the wound took — a relationship, a belief, a version of themselves.]

**What they'd say if asked:** [One sentence of direct speech — how they explain or justify themselves. Make it human enough that a player might pause.]

### Minions
Three types of followers — not just muscle:
- **[Type]:** [Who they are, what they do, and why they follow this villain specifically]
- **[Type]:** [Who they are, what they do, and why they follow this villain specifically]
- **[Type]:** [Who they are, what they do, and why they follow this villain specifically]

### Defeat Condition
**What can stop them:** [A specific weakness, not 'kill them.' What would actually end this — what belief could be shattered, what loss would break the scheme, what do they secretly need that could be denied or offered?]

**What they're afraid of:** [One thing they will not say, but that drives their behavior. The shape of their actual fear.]

**The Tragic Version:** [One sentence: how this ends if no one intervenes — and why that outcome is worse than a fight.]

### Encounter Hook
[Two sentences: how the players first become aware this villain exists, and what the villain has already done to them before they know it.]

### Connections
- **ALLY — [Full Name]:** [One sentence — who they are and why they serve]
- **ENEMY — [Full Name]:** [One sentence — who opposes them and what they know]
- **COMPLICATION — [Full Name]:** [One sentence — someone who loves or was loved by the villain, who the party might reach before the villain does]"""


# ── Tool dispatcher ────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_stat":              return roll_stat()
    if name == "roll_dice":              return roll_dice(**inputs)
    if name == "get_race_info":          return get_race_info(**inputs)
    if name == "get_class_info":         return get_class_info(**inputs)
    if name == "get_background_info":    return get_background_info(**inputs)
    if name == "get_subclass_info":      return get_subclass_info(**inputs)
    if name == "pick_skills":            return pick_skills(**inputs)
    if name == "calculate_ac":           return calculate_ac(**inputs)
    if name == "calculate_combat_stats": return calculate_combat_stats(**inputs)
    if name == "roll_deity":             return roll_deity(**inputs)
    if name == "roll_villain_profile":   return roll_villain_profile()
    if name == "roll_dnd_name_suggestion": return roll_dnd_name_suggestion(race=inputs.get("race"))
    if name == "get_spell_suggestions":    return get_spell_suggestions(**inputs)
    if name == "roll_dnd_gear":            return roll_dnd_gear(**inputs)
    if name == "roll_alignment":           return roll_alignment()
    if name == "roll_quest_hook":          return roll_quest_hook()
    return f"Unknown tool: {name}"


# ── Phase tracker ──────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "name":       "Rolling name suggestion...",
    "stats":      "Rolling ability scores...",
    "race":       "Choosing race...",
    "class":      "Choosing class...",
    "subclass":   "Choosing subclass...",
    "background": "Building background & connections...",
    "skills":     "Selecting class skills...",
    "spells":     "Selecting spells...",
    "gear":       "Rolling starting gear...",
    "ac":         "Calculating AC...",
    "combat":     "Calculating combat stats...",
    "deity":      "Rolling deity...",
    "alignment":  "Rolling alignment...",
    "quest":      "Rolling quest hook...",
    "villain":    "Rolling villain scheme & wound...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_dnd_name_suggestion":  return "name"
    if tool_name == "get_spell_suggestions":     return "spells"
    if tool_name == "roll_dnd_gear":             return "gear"
    if tool_name == "calculate_ac":              return "ac"
    if tool_name == "calculate_combat_stats":    return "combat"
    if tool_name == "get_subclass_info":         return "subclass"
    if tool_name == "pick_skills":               return "skills"
    if tool_name == "roll_deity":                return "deity"
    if tool_name == "roll_alignment":            return "alignment"
    if tool_name == "roll_quest_hook":           return "quest"
    if tool_name == "roll_villain_profile":      return "villain"
    if tool_name == "roll_stat":             return "stats"
    if tool_name == "get_race_info":         return "race"
    if tool_name == "get_class_info":        return "class"
    if tool_name == "get_background_info":   return "background"
    return None


# ── Agentic loop ───────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    return run_agent_loop(
        prompt, system_prompt, TOOLS, run_tool, detect_phase, PHASE_MESSAGES
    )


# ── Entry point ────────────────────────────────────────────────────────────────

def save_result(result: str, mode: str) -> Path:
    return save_character(result, mode, "dnd", Path(__file__).parent.parent)


def run(mode: str | None = None, desc: str | None = None) -> None:
    valid_modes = ("full", "npc", "questgiver", "villain")
    if mode is None:
        mode = input("Mode? (full / npc / questgiver / villain, default: full): ").strip().lower()
        mode = mode if mode in valid_modes else "full"
    label = {"full": "character", "npc": "NPC", "questgiver": "quest giver", "villain": "villain"}[mode]
    if desc is None:
        raw  = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()
        desc = sanitize_desc(raw)
        for w in screen_desc(desc):
            print(f"  [safety] {w}")

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt     = "Generate a fully random D&D 5e NPC."
    elif mode == "questgiver":
        sys_prompt = QUEST_GIVER_SYSTEM_PROMPT
        prompt     = "Generate a fully random D&D 5e quest giver encounter."
    elif mode == "villain":
        sys_prompt = VILLAIN_SYSTEM_PROMPT
        prompt     = "Generate a fully random D&D 5e villain — a complete antagonist with a scheme, a wound, and a world that reacts to them."
    else:  # full
        sys_prompt = SYSTEM_PROMPT
        prompt     = "Generate a fully random D&D 5e character for storytelling purposes."

    if desc:
        prompt += f"\n\n{wrap_desc(desc)}"

    result = strip_preamble(run_agent(prompt, sys_prompt))

    warn = screen_output(result)
    if warn:
        print(f"  [safety] {warn}")

    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
