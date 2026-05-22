"""
D&D 5e spell suggestions for spellcasting classes.

Story-first, not rules-complete. Each spell has a one-line hook about what
it says about the character who carries it. The goal is a handful of spells
that feel *specific* to this person, not an optimised loadout.

get_spell_suggestions(class_name) returns a curated selection of 5-6 spells:
one or two cantrips, two or three low-level spells, one higher-level signature.
"""

import json
import random


# ── Spell pools by class ──────────────────────────────────────────────────────
#
# Each entry: name, level (0 = cantrip), school, hook (what it says about them)

SPELL_POOLS: dict[str, list[dict]] = {
    "Wizard": [
        {"name": "Mage Hand",      "level": 0, "school": "Conjuration",   "hook": "Reaches for things they shouldn't touch — and often does anyway."},
        {"name": "Minor Illusion", "level": 0, "school": "Illusion",      "hook": "Learned young that the appearance of a thing matters as much as the thing itself."},
        {"name": "Fire Bolt",      "level": 0, "school": "Evocation",     "hook": "The first spell they mastered; still fall back on it when careful thinking fails."},
        {"name": "Prestidigitation","level": 0, "school": "Transmutation", "hook": "Used constantly for small conveniences — someone who learned magic for comfort as much as power."},
        {"name": "Ray of Frost",   "level": 0, "school": "Evocation",     "hook": "Prefers precision over force; would rather slow a problem than end it."},
        {"name": "Message",        "level": 0, "school": "Transmutation", "hook": "Secrets are currency, and they've always known how to move them quietly."},
        {"name": "Find Familiar",  "level": 1, "school": "Conjuration",   "hook": "The familiar has been with them longer than most relationships — and understands them better."},
        {"name": "Identify",       "level": 1, "school": "Divination",    "hook": "Can't leave an unknown thing alone; the compulsion to understand is older than the spell."},
        {"name": "Magic Missile",  "level": 1, "school": "Evocation",     "hook": "Reliable, unfussy, efficient — tells you something about how they solve problems."},
        {"name": "Shield",         "level": 1, "school": "Abjuration",    "hook": "The reflex of someone who's been hit before and learned from it."},
        {"name": "Unseen Servant", "level": 1, "school": "Conjuration",   "hook": "Never quite comfortable doing things themselves that they could delegate."},
        {"name": "Detect Magic",   "level": 1, "school": "Divination",    "hook": "The world is full of things pretending to be mundane. They've stopped being fooled."},
        {"name": "Sleep",          "level": 1, "school": "Enchantment",   "hook": "Doesn't like hurting things unless it's necessary. Sleep is usually enough."},
        {"name": "Misty Step",     "level": 2, "school": "Conjuration",   "hook": "The exit strategy of someone who plans for things going wrong."},
        {"name": "Invisibility",   "level": 2, "school": "Illusion",      "hook": "Uses it more than they admit — there's a reason they're comfortable being unseen."},
        {"name": "Mirror Image",   "level": 2, "school": "Illusion",      "hook": "The question of which one is real stopped bothering them years ago."},
        {"name": "Counterspell",   "level": 3, "school": "Abjuration",    "hook": "Spent years studying other wizards just to know how to stop them."},
        {"name": "Fireball",       "level": 3, "school": "Evocation",     "hook": "The spell that got them in trouble the first time, and probably will again."},
        {"name": "Fly",            "level": 3, "school": "Transmutation", "hook": "The reason they became a wizard, if they're honest."},
        {"name": "Arcane Eye",     "level": 4, "school": "Divination",    "hook": "Uncomfortable with not knowing what's in the next room — or the next decade."},
    ],

    "Cleric": [
        {"name": "Sacred Flame",     "level": 0, "school": "Divine",       "hook": "Not mercy, not patience — the god's will made visible."},
        {"name": "Guidance",         "level": 0, "school": "Divination",   "hook": "Given freely, even to people who didn't ask and probably should have."},
        {"name": "Spare the Dying",  "level": 0, "school": "Necromancy",   "hook": "Holds the line between life and death with a steady hand and no sentimentality."},
        {"name": "Toll the Dead",    "level": 0, "school": "Necromancy",   "hook": "A reminder that death comes for everything — they just sometimes speed the process."},
        {"name": "Thaumaturgy",      "level": 0, "school": "Transmutation","hook": "The small miracles that remind people exactly who they're talking to."},
        {"name": "Bless",            "level": 1, "school": "Enchantment",  "hook": "Believes in the people around them enough to spend divine favour on them."},
        {"name": "Cure Wounds",      "level": 1, "school": "Evocation",    "hook": "Given without hesitation, but they notice who never says thank you."},
        {"name": "Command",          "level": 1, "school": "Enchantment",  "hook": "One word. Not a request."},
        {"name": "Healing Word",     "level": 1, "school": "Evocation",    "hook": "The quick patch — practical and unglamorous about keeping people alive."},
        {"name": "Inflict Wounds",   "level": 1, "school": "Necromancy",   "hook": "They don't enjoy it. Much."},
        {"name": "Shield of Faith",  "level": 1, "school": "Abjuration",   "hook": "The conviction that some things are worth protecting, made physical."},
        {"name": "Spiritual Weapon", "level": 2, "school": "Evocation",    "hook": "The god fighting beside them — or more accurately, through them."},
        {"name": "Hold Person",      "level": 2, "school": "Enchantment",  "hook": "Used more as a conversation-starter than a weapon."},
        {"name": "Lesser Restoration","level": 2,"school": "Abjuration",   "hook": "What the god asks of them, they give without counting the cost."},
        {"name": "Revivify",         "level": 3, "school": "Necromancy",   "hook": "The most difficult thing they can do — and they feel the cost of it each time."},
        {"name": "Spirit Guardians", "level": 3, "school": "Conjuration",  "hook": "The dead they carry with them, finally made useful."},
        {"name": "Speak with Dead",  "level": 3, "school": "Necromancy",   "hook": "The conversations that never end, just pause."},
    ],

    "Druid": [
        {"name": "Druidcraft",       "level": 0, "school": "Transmutation","hook": "Used constantly, without thought — the way most people breathe."},
        {"name": "Shillelagh",       "level": 0, "school": "Transmutation","hook": "Wood that remembers being alive."},
        {"name": "Thorn Whip",       "level": 0, "school": "Transmutation","hook": "Pulling things toward them is a habit that goes beyond the spell."},
        {"name": "Produce Flame",    "level": 0, "school": "Conjuration",  "hook": "Fire is a tool, not a weapon — except when it needs to be."},
        {"name": "Guidance",         "level": 0, "school": "Divination",   "hook": "The forest always knew things before they did. They're just passing it on."},
        {"name": "Entangle",         "level": 1, "school": "Conjuration",  "hook": "The world is full of roots. They just ask nicely."},
        {"name": "Speak with Animals","level": 1,"school": "Divination",   "hook": "Finds animals more honest than most people they've met."},
        {"name": "Goodberry",        "level": 1, "school": "Transmutation","hook": "There's always food if you know where to look. The lesson matters more than the spell."},
        {"name": "Faerie Fire",      "level": 1, "school": "Evocation",    "hook": "Nothing can hide from the forest if the forest decides to look."},
        {"name": "Healing Word",     "level": 1, "school": "Evocation",    "hook": "Urgent and direct — save the tenderness for when there's time."},
        {"name": "Moonbeam",         "level": 2, "school": "Evocation",    "hook": "The light that reveals what things really are."},
        {"name": "Pass without Trace","level": 2,"school": "Abjuration",   "hook": "The forest doesn't announce itself. Neither do they."},
        {"name": "Barkskin",         "level": 2, "school": "Transmutation","hook": "Learned that softness is a choice, not an obligation."},
        {"name": "Call Lightning",   "level": 3, "school": "Conjuration",  "hook": "The storm has always been there. They just made it personal."},
        {"name": "Conjure Animals",  "level": 3, "school": "Conjuration",  "hook": "Never entirely alone — not since they learned this."},
        {"name": "Plant Growth",     "level": 3, "school": "Transmutation","hook": "Time is different when you think in seasons."},
    ],

    "Bard": [
        {"name": "Vicious Mockery",  "level": 0, "school": "Enchantment",  "hook": "Words as weapons — a skill they had long before they called it magic."},
        {"name": "Minor Illusion",   "level": 0, "school": "Illusion",     "hook": "The gap between what's real and what people will believe has always seemed exploitable."},
        {"name": "Dancing Lights",   "level": 0, "school": "Evocation",    "hook": "The first spell, learned in a theatre: make people look where you want them to look."},
        {"name": "Prestidigitation", "level": 0, "school": "Transmutation","hook": "Used to make things more dramatic. Which is to say: constantly."},
        {"name": "Mage Hand",        "level": 0, "school": "Conjuration",  "hook": "Getting things without being seen getting them — an old habit."},
        {"name": "Charm Person",     "level": 1, "school": "Enchantment",  "hook": "They tell themselves they only use it when they have to. This is not entirely true."},
        {"name": "Healing Word",     "level": 1, "school": "Evocation",    "hook": "The right words at the right moment have always had a way of saving people."},
        {"name": "Dissonant Whispers","level": 1,"school": "Enchantment",  "hook": "Knows exactly which fears to name."},
        {"name": "Faerie Fire",      "level": 1, "school": "Evocation",    "hook": "Impossible to resist pointing out what's been trying to hide."},
        {"name": "Heroism",          "level": 1, "school": "Enchantment",  "hook": "Believes in people, sometimes past the point of good judgment."},
        {"name": "Suggestion",       "level": 2, "school": "Enchantment",  "hook": "The most powerful thing they know: the idea you planted that the other person thinks was theirs."},
        {"name": "Invisibility",     "level": 2, "school": "Illusion",     "hook": "Sometimes the best performance is the one nobody sees you giving."},
        {"name": "Silence",          "level": 2, "school": "Illusion",     "hook": "The absence of sound is its own kind of statement."},
        {"name": "Hypnotic Pattern", "level": 3, "school": "Illusion",     "hook": "Understands that beauty can be a weapon."},
        {"name": "Major Image",      "level": 3, "school": "Illusion",     "hook": "At some point the distinction between the show and the truth stopped mattering."},
        {"name": "Modify Memory",    "level": 5, "school": "Enchantment",  "hook": "Used it once. Thinks about it more than they'd like to admit."},
    ],

    "Sorcerer": [
        {"name": "Fire Bolt",        "level": 0, "school": "Evocation",    "hook": "Came out wrong the first time. Still does, occasionally."},
        {"name": "Shocking Grasp",   "level": 0, "school": "Evocation",    "hook": "The power that was there before they knew what to call it."},
        {"name": "Prestidigitation", "level": 0, "school": "Transmutation","hook": "Controlling small things is practice for the days the big things threaten to slip."},
        {"name": "Ray of Frost",     "level": 0, "school": "Evocation",    "hook": "When fire is too obvious, or too obvious what it says about their bloodline."},
        {"name": "Mage Hand",        "level": 0, "school": "Conjuration",  "hook": "The gentlest expression of something that is rarely gentle."},
        {"name": "Chromatic Orb",    "level": 1, "school": "Evocation",    "hook": "The power choosing its own shape — they just decide the target."},
        {"name": "Magic Missile",    "level": 1, "school": "Evocation",    "hook": "No room for the power to go wrong. Useful on bad days."},
        {"name": "Thunderwave",      "level": 1, "school": "Evocation",    "hook": "The first time it happened accidentally. The second time too."},
        {"name": "Charm Person",     "level": 1, "school": "Enchantment",  "hook": "The bloodline wants things — this is the polite version of that."},
        {"name": "Misty Step",       "level": 2, "school": "Conjuration",  "hook": "The instinct to be somewhere else, given form."},
        {"name": "Scorching Ray",    "level": 2, "school": "Evocation",    "hook": "More control than a fireball. They are working on this."},
        {"name": "Mirror Image",     "level": 2, "school": "Illusion",     "hook": "Which one is real? The bloodline considers this a philosophical question."},
        {"name": "Fireball",         "level": 3, "school": "Evocation",    "hook": "Didn't choose it — it chose them."},
        {"name": "Counterspell",     "level": 3, "school": "Abjuration",   "hook": "Power recognising power. The bloodline knows its own kind."},
        {"name": "Fly",              "level": 3, "school": "Transmutation","hook": "The body already knows how to do this. The spell just gives it permission."},
        {"name": "Polymorph",        "level": 4, "school": "Transmutation","hook": "If power means anything, it means choosing what shape you wear."},
    ],

    "Warlock": [
        {"name": "Eldritch Blast",   "level": 0, "school": "Evocation",    "hook": "The patron's will, expressed through their hands. Every time."},
        {"name": "Chill Touch",      "level": 0, "school": "Necromancy",   "hook": "Death's cold, borrowed briefly. The patron finds this amusing."},
        {"name": "Minor Illusion",   "level": 0, "school": "Illusion",     "hook": "The patron taught them: reality is whatever you can make someone believe."},
        {"name": "Mage Hand",        "level": 0, "school": "Conjuration",  "hook": "The simplest thing they got in the bargain. They still use it constantly."},
        {"name": "Prestidigitation", "level": 0, "school": "Transmutation","hook": "Small tricks for a pact built on larger ones."},
        {"name": "Armor of Agathys", "level": 1, "school": "Abjuration",   "hook": "The price of touching them: you bleed too."},
        {"name": "Hex",              "level": 1, "school": "Enchantment",  "hook": "The patron's mark. They try not to think about what it means to carry it."},
        {"name": "Hellish Rebuke",   "level": 1, "school": "Evocation",    "hook": "Reflexive, instinctive, disproportionate. The patron approves."},
        {"name": "Witch Bolt",       "level": 1, "school": "Evocation",    "hook": "Once you have the connection, you keep it. In more ways than one."},
        {"name": "Misty Step",       "level": 2, "school": "Conjuration",  "hook": "The patron gave them an exit. They've needed it."},
        {"name": "Mirror Image",     "level": 2, "school": "Illusion",     "hook": "Which one made the deal? The patron never says."},
        {"name": "Shatter",          "level": 2, "school": "Evocation",    "hook": "Some things need to be broken before they can be fixed. Some don't need fixing after."},
        {"name": "Hunger of Hadar",  "level": 3, "school": "Conjuration",  "hook": "A window to where the patron lives. They don't look through it."},
        {"name": "Hypnotic Pattern", "level": 3, "school": "Illusion",     "hook": "The void is beautiful if you catch it at the right angle."},
        {"name": "Fear",             "level": 3, "school": "Illusion",     "hook": "Shows people what they already know is waiting for them."},
        {"name": "Banishment",       "level": 4, "school": "Abjuration",   "hook": "Sends things away to somewhere. They've learned not to ask where."},
    ],

    "Paladin": [
        {"name": "Bless",              "level": 1, "school": "Enchantment",  "hook": "The god's hand on the shoulder. Means something, even to people who don't believe it."},
        {"name": "Shield of Faith",    "level": 1, "school": "Abjuration",   "hook": "The conviction that some things are worth protecting, made physical."},
        {"name": "Wrathful Smite",     "level": 1, "school": "Evocation",    "hook": "Righteousness and anger are not always distinguishable."},
        {"name": "Heroism",            "level": 1, "school": "Enchantment",  "hook": "Gives courage to people who've forgotten they had it."},
        {"name": "Thunderous Smite",   "level": 1, "school": "Evocation",    "hook": "The oath made loud. Very loud."},
        {"name": "Divine Favour",      "level": 1, "school": "Evocation",    "hook": "The god fighting with them, not just through them."},
        {"name": "Zone of Truth",      "level": 2, "school": "Enchantment",  "hook": "The discomfort in the room when they cast it tells them what they need to know."},
        {"name": "Find Steed",         "level": 2, "school": "Conjuration",  "hook": "The horse knows them. That means something."},
        {"name": "Lesser Restoration", "level": 2, "school": "Abjuration",   "hook": "What the god asks of them, they give without counting the cost."},
        {"name": "Blinding Smite",     "level": 3, "school": "Evocation",    "hook": "Some truths are too bright to look at directly."},
        {"name": "Revivify",           "level": 3, "school": "Necromancy",   "hook": "The hardest thing the god grants them. Used sparingly. Always remembered."},
        {"name": "Crusader's Mantle",  "level": 3, "school": "Evocation",    "hook": "Not for themselves — always for the people beside them."},
    ],

    "Ranger": [
        {"name": "Hunter's Mark",      "level": 1, "school": "Divination",   "hook": "Once they've marked something, they don't let it go. This was true before the spell."},
        {"name": "Ensnaring Strike",   "level": 1, "school": "Conjuration",  "hook": "Patience and thorns. Mostly patience."},
        {"name": "Fog Cloud",          "level": 1, "school": "Conjuration",  "hook": "The wilderness gives advantages to those who know how to ask."},
        {"name": "Cure Wounds",        "level": 1, "school": "Evocation",    "hook": "Field medicine, practical and unglamorous. They've had a lot of practice."},
        {"name": "Speak with Animals", "level": 1, "school": "Divination",   "hook": "The birds knew about the ambush. They always know."},
        {"name": "Hail of Thorns",     "level": 1, "school": "Conjuration",  "hook": "The land defends its own, when asked."},
        {"name": "Pass without Trace", "level": 2, "school": "Abjuration",   "hook": "The forest forgets them. They've grown comfortable with that."},
        {"name": "Spike Growth",       "level": 2, "school": "Transmutation","hook": "Turning the terrain against the enemy is more satisfying than it has any right to be."},
        {"name": "Silence",            "level": 2, "school": "Illusion",     "hook": "The hunt requires it. So does everything else worth doing carefully."},
        {"name": "Conjure Barrage",    "level": 3, "school": "Conjuration",  "hook": "When patience runs out, volume works."},
        {"name": "Lightning Arrow",    "level": 3, "school": "Transmutation","hook": "The one that usually ends arguments."},
        {"name": "Freedom of Movement","level": 4, "school": "Abjuration",   "hook": "Nothing holds them. This was always true; the spell just makes it official."},
    ],
}

SPELLCASTING_CLASSES: list[str] = sorted(SPELL_POOLS.keys())

# Non-casting classes — return a clear message rather than an error
_NON_CASTERS = {
    "Barbarian", "Fighter", "Monk", "Rogue", "Thief",
    "Eldritch Knight", "Arcane Trickster",
}


# ── Spell selection ───────────────────────────────────────────────────────────

def get_spell_suggestions(class_name: str, subclass: str = None) -> str:
    """Return a curated selection of 5-6 spells for the given class.

    Selection is weighted: 1-2 cantrips, 2-3 low-level spells (1-2),
    1 higher-level signature spell. Each comes with a story hook.
    """
    # Handle non-casters cleanly
    if class_name in _NON_CASTERS:
        return json.dumps({
            "note": f"{class_name} is not a spellcasting class. Skip this tool.",
        })

    # Normalise common variants
    aliases = {
        "Eldritch Knight": "Wizard",
        "Arcane Trickster": "Wizard",
        "Oathbreaker": "Paladin",
        "Gloom Stalker": "Ranger",
    }
    lookup = aliases.get(class_name, class_name)

    if lookup not in SPELL_POOLS:
        known = ", ".join(SPELLCASTING_CLASSES)
        return json.dumps({"error": f"Unknown class {class_name!r}. Spellcasting classes: {known}"})

    pool = SPELL_POOLS[lookup]

    # Split by level tier
    cantrips = [s for s in pool if s["level"] == 0]
    low      = [s for s in pool if 1 <= s["level"] <= 2]
    high     = [s for s in pool if s["level"] >= 3]

    selected = []
    selected += random.sample(cantrips, min(2, len(cantrips)))
    selected += random.sample(low,      min(3, len(low)))
    if high:
        selected += random.sample(high, 1)

    random.shuffle(selected)

    result = {
        "class": class_name,
        "spells": [
            {
                "name":   s["name"],
                "level":  "Cantrip" if s["level"] == 0 else f"Level {s['level']}",
                "school": s["school"],
                "hook":   s["hook"],
            }
            for s in selected
        ],
        "note": (
            "Pick 3-4 of these that feel true to this character. "
            "Write one sentence per chosen spell about how *this person specifically* uses it — "
            "the hook is a starting point, not a mandate. "
            "A Cleric who uses Inflict Wounds reluctantly is different from one who doesn't."
        ),
    }
    if subclass:
        result["subclass"] = subclass

    return json.dumps(result)


# ── Tool schema ───────────────────────────────────────────────────────────────

DND_SPELL_TOOL_SCHEMA: dict = {
    "name": "get_spell_suggestions",
    "description": (
        "Get a curated spell selection for a D&D spellcasting character. "
        "Returns 5-6 spells — cantrips and levelled — each with a story hook "
        "about what it says about the character who carries it. "
        "Call this after choosing a spellcasting class (Wizard, Cleric, Druid, "
        "Bard, Sorcerer, Warlock, Paladin, or Ranger). Do NOT call for Barbarian, "
        "Fighter, Monk, or Rogue (unless Eldritch Knight / Arcane Trickster). "
        "Pick 3-4 from the returned list that feel true to this specific character."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "The character's class.",
                "enum": SPELLCASTING_CLASSES,
            },
            "subclass": {
                "type": "string",
                "description": (
                    "Optional subclass for flavour (e.g. 'School of Divination', "
                    "'Circle of the Moon', 'The Fiend'). Does not filter the spell list "
                    "but may be noted in the response."
                ),
            },
        },
        "required": ["class_name"],
    },
}
