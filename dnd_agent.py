"""
D&D 5e Character Generator
Creates vivid storytelling characters using D&D 5th Edition mechanics.

Run with: python dnd_dice_agent.py
"""

import json
import random
import re
from pathlib import Path
import anthropic

client = anthropic.Anthropic()


# ── Constants ──────────────────────────────────────────────────────────────────

VALID_DICE = {4, 6, 8, 10, 12, 20}   # full D&D dice set
MIN_ROLLS  = 1
MAX_ROLLS  = 20


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
    },
    "High Elf": {
        "description": "Ancient, graceful, and quietly condescending — keepers of arcane knowledge and deep memory",
        "ability_bonuses": {"DEX": 2, "INT": 1},
        "traits": ["Darkvision 60ft", "Keen Senses (Perception proficiency)", "Fey Ancestry (advantage vs charm, immune to magical sleep)", "Trance (meditate 4hrs instead of sleeping 8)", "One Wizard cantrip", "Extra language"],
        "flavor": "patient to a fault, beautiful in an unsettling way, remembers things that happened before your nation existed",
    },
    "Wood Elf": {
        "description": "Reclusive guardians of ancient forests — swifter and more grounded than their high elf cousins",
        "ability_bonuses": {"DEX": 2, "WIS": 1},
        "traits": ["Darkvision 60ft", "Keen Senses", "Fey Ancestry", "Trance", "Fleet of Foot (35ft speed)", "Mask of the Wild (hide in natural terrain)"],
        "flavor": "quiet, observant, trusts a forest over a city any day",
    },
    "Hill Dwarf": {
        "description": "Stubborn, tough, and loyal — forged in stone and tradition, holds grudges across generations",
        "ability_bonuses": {"CON": 2, "WIS": 1},
        "traits": ["Darkvision 60ft", "Dwarven Resilience (advantage vs poison)", "Stonecunning", "Dwarven Toughness (+1 HP per level)", "Artisan's tool proficiency"],
        "flavor": "gruff, deeply honorable, has strong opinions about ale and stonework",
    },
    "Mountain Dwarf": {
        "description": "Warriors born underground — built like stone, equally immovable",
        "ability_bonuses": {"STR": 2, "CON": 2},
        "traits": ["Darkvision 60ft", "Dwarven Resilience", "Stonecunning", "Light and medium armor proficiency"],
        "flavor": "militaristic and direct, respects strength and craft in equal measure",
    },
    "Lightfoot Halfling": {
        "description": "Small, lucky, and surprisingly hard to notice — more resilient than they look",
        "ability_bonuses": {"DEX": 2, "CHA": 1},
        "traits": ["Lucky (reroll 1s on attack rolls, ability checks, saving throws)", "Brave (advantage vs frightened)", "Halfling Nimbleness (move through larger creatures' spaces)", "Naturally Stealthy (can hide behind larger creatures)"],
        "flavor": "cheerful, comfort-seeking, tends to survive situations that kill more imposing people",
    },
    "Forest Gnome": {
        "description": "Curious tinkerers and woodland tricksters with infectious enthusiasm and short attention spans",
        "ability_bonuses": {"INT": 2, "DEX": 1},
        "traits": ["Darkvision 60ft", "Gnome Cunning (advantage on INT/WIS/CHA saves vs magic)", "Minor Illusion cantrip", "Speak with Small Beasts"],
        "flavor": "enthusiastic, easily distracted, sees everything as a puzzle",
    },
    "Half-Elf": {
        "description": "Caught between two worlds, belonging to neither — which makes them very good at reading rooms",
        "ability_bonuses": {"CHA": 2, "two others of choice": 1},
        "traits": ["Darkvision 60ft", "Fey Ancestry", "Skill Versatility (proficiency in any 2 skills)", "Extra language"],
        "flavor": "charming, subtly restless, used to performing for audiences that aren't quite sure what to make of them",
    },
    "Half-Orc": {
        "description": "Marked by orcish blood — strength, ferocity, and a will to survive that borders on supernatural",
        "ability_bonuses": {"STR": 2, "CON": 1},
        "traits": ["Darkvision 60ft", "Intimidation proficiency", "Relentless Endurance (drop to 1 HP instead of 0, once per long rest)", "Savage Attacks (roll one extra weapon die on a melee critical hit)"],
        "flavor": "intense and practical, has learned to use the fear others project onto them as a tool",
    },
    "Tiefling": {
        "description": "Infernal heritage written on their skin — horns, tail, unnerving eyes. Always the outsider.",
        "ability_bonuses": {"CHA": 2, "INT": 1},
        "traits": ["Darkvision 60ft", "Hellish Resistance (resistance to fire damage)", "Infernal Legacy (Thaumaturgy cantrip; Hellish Rebuke and Darkness as they level)"],
        "flavor": "often mistrusted from birth, learned self-reliance early, can be warm or cold depending entirely on how the world treated them",
    },
    "Dragonborn": {
        "description": "Dragon blood in human form — breath weapons, natural pride, and a culture built around glory",
        "ability_bonuses": {"STR": 2, "CHA": 1},
        "traits": ["Draconic Ancestry (choose dragon type — determines damage type)", "Breath Weapon (line or cone, scales with level)", "Damage Resistance (matching ancestry type)"],
        "flavor": "honor-driven, proud to the point of arrogance, spectacular and terrifying when they finally breathe",
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
}


# ── Tools (Python side) ────────────────────────────────────────────────────────

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
        "description": "Look up a race's ability score bonuses, racial traits, and flavor. Use this to pick a race that fits the rolled stats.",
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
        "description": "Look up a class's hit die, primary stats, saving throws, armor and weapon proficiencies, skills, and flavor.",
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
]


# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a D&D 5th Edition character generator creating vivid, story-ready characters.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names should draw from a wide range of cultural traditions — not just Anglo-Saxon or Tolkien-adjacent defaults. Vary first letters, syllable counts, and linguistic origins across characters.

Work through these steps in order, using your tools at each stage:

1. ABILITY SCORES — Call roll_stat six times, one per ability in this order:
   Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma.
   Note all six scores before moving on.

2. RACE — Choose a race that fits the stats and any constraints given.
   Look it up with get_race_info. Apply the racial ability score bonuses to the rolled scores.
   Note any traits, languages, and special abilities.

3. CLASS — Choose a class that suits the final stats and the emerging character concept.
   Look it up with get_class_info. Note the hit die, saving throws, proficiencies, and skill options.
   Calculate HP at level 1: max hit die value + CON modifier.
   Hint at a subclass direction that fits the character — don't commit, just suggest.

4. BACKGROUND — Choose a background that fits the character's story so far.
   Look it up with get_background_info. Use the personality seeds as inspiration — not verbatim, but as starting points.
   CONNECTIONS — the background's story hooks often imply people. Generate at least one named NPC:
     - A mentor, patron, or ally → ALLY or CONTACT (name, one sentence, relationship)
     - A rival, enemy, or antagonist → ENEMY or RIVAL (name, one sentence, relationship)
   Make these specific people, not abstractions.

5. CHARACTER SHEET — Always use exactly this format:

## **[Full Name, with nickname in quotes if it fits]**

| | |
|---|---|
| **Race** | [Race] |
| **Class** | [Class] (Level 1) |
| **Background** | [Background] |
| **Alignment** | [Alignment — pick one that fits naturally] |
| **HP** | [hp] |
| **Proficiency Bonus** | +2 |

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
- **Skills:** [list all proficient skills from class + background]
- **Tools & Other:** [tools from background, any other proficiencies]

### Personality
- **Trait:** [drawn from background seeds but made specific to this character]
- **Ideal:** [what they believe in]
- **Bond:** [what they can't leave behind]
- **Flaw:** [the crack in the armor]

### Connections
- **[Category] — [Full Name]:** [one sentence: who they are and their relationship to the character]
Categories: Ally, Contact, Enemy, Rival.

### Equipment
Starting gear based on class and background — make it feel lived-in, not like a list from a table.

### Backstory
Three sentences. A past, a wound, and a direction."""

NPC_SYSTEM_PROMPT = """You are a D&D 5e NPC generator. Create a vivid, instantly usable NPC sketch.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names should draw from a wide range of cultural traditions — not just Anglo-Saxon or Tolkien-adjacent defaults. Vary first letters, syllable counts, and linguistic origins across characters.

Roll a few key stats with roll_stat (only the ones that matter for this NPC's role — not all six).
Look up race or class info if it would help ground them. Then produce the sketch — fast and sharp.

Always use exactly this format:

## **[Name]**
*[Race] [Class or Occupation] — [one sharp hook sentence]*

| | |
|---|---|
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

Names should draw from a wide range of cultural traditions — not just Anglo-Saxon or Tolkien-adjacent defaults. Vary first letters, syllable counts, and linguistic origins across characters.

Look up a background with get_background_info to establish who this person is and what world they come from. Roll 1d6 once to add a random element to their situation — let it color something about them.

The encounter has four possible truths — the DM rolls 1d4 in secret. Make all four truths plausible from the party's perspective. The quest giver doesn't know which truth the DM rolled — they behave the same way regardless.

Always use exactly this format:

## **[Full Name]**
*Quest Giver — [who they appear to be in one phrase]*

| | |
|---|---|
| **Appears to be** | [what the party sees — occupation, station, mood] |
| **Actually is** | [the real story — revealed only in Truth 2, 3, or 4] |

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


# ── Tool dispatcher ────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_stat":          return roll_stat()
    if name == "roll_dice":          return roll_dice(**inputs)
    if name == "get_race_info":      return get_race_info(**inputs)
    if name == "get_class_info":     return get_class_info(**inputs)
    if name == "get_background_info":return get_background_info(**inputs)
    return f"Unknown tool: {name}"


# ── Phase tracker ──────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "stats":      "Rolling ability scores...",
    "race":       "Choosing race...",
    "class":      "Choosing class...",
    "background": "Building background & connections...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_stat":           return "stats"
    if tool_name == "get_race_info":       return "race"
    if tool_name == "get_class_info":      return "class"
    if tool_name == "get_background_info": return "background"
    return None


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
    """Save output to dnd_characters/ as {character-name}-{full|npc|questgiver}.md"""
    first_line = result.strip().splitlines()[0]
    name_raw   = re.sub(r"[#*]", "", first_line).strip()
    name_slug  = re.sub(r"[^a-z0-9]+", "-", name_raw.lower()).strip("-")
    filename   = f"{name_slug}-{mode}.md"

    output_dir = Path(__file__).parent / "dnd_characters"
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(result)
    return filepath


def run(mode: str | None = None, desc: str | None = None) -> None:
    if mode is None:
        mode = input("Mode? (full / npc / questgiver, default: full): ").strip().lower()
        mode = mode if mode in ("full", "npc", "questgiver") else "full"
    label = {"full": "character", "npc": "NPC", "questgiver": "quest giver"}[mode]
    if desc is None:
        desc = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt = f"Generate a D&D 5e NPC with these constraints: {desc}" if desc else "Generate a fully random D&D 5e NPC."
    elif mode == "questgiver":
        sys_prompt = QUEST_GIVER_SYSTEM_PROMPT
        prompt = f"Generate a D&D 5e quest giver encounter with these constraints: {desc}" if desc else "Generate a fully random D&D 5e quest giver encounter."
    else:  # full
        sys_prompt = SYSTEM_PROMPT
        prompt = f"Generate a D&D 5e character for storytelling purposes with these constraints: {desc}" if desc else "Generate a fully random D&D 5e character for storytelling purposes."

    result = run_agent(prompt, sys_prompt)
    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
