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
        {"name": "Arcane Eye",        "level": 4, "school": "Divination",    "hook": "Uncomfortable with not knowing what's in the next room — or the next decade."},
        {"name": "Animate Objects",   "level": 5, "school": "Transmutation", "hook": "The workshop that fights back — control at its most literal and most petty."},
        {"name": "Telekinesis",       "level": 5, "school": "Transmutation", "hook": "Never quite comfortable using their hands for what the mind can do instead."},
        {"name": "Scrying",           "level": 5, "school": "Divination",    "hook": "They've watched more than they've admitted, and what they found changed how they ask questions."},
        {"name": "Disintegrate",      "level": 6, "school": "Transmutation", "hook": "Some problems deserve a final answer. They've drawn that conclusion twice."},
        {"name": "True Seeing",       "level": 6, "school": "Divination",    "hook": "What they saw the first time broke something they haven't finished putting back."},
        {"name": "Globe of Invulnerability", "level": 6, "school": "Abjuration", "hook": "The bubble of certainty — they live in it when they can and cast it when they can't."},
        {"name": "Forcecage",         "level": 7, "school": "Evocation",     "hook": "Preferred to killing — they like problems they can revisit."},
        {"name": "Simulacrum",        "level": 7, "school": "Illusion",      "hook": "The question of which one is the original stopped troubling them around the third casting."},
        {"name": "Plane Shift",       "level": 7, "school": "Conjuration",   "hook": "The place they're going couldn't possibly be worse than this one. Probably."},
        {"name": "Mind Blank",        "level": 8, "school": "Abjuration",    "hook": "Protecting something specific from something specific. They haven't said what."},
        {"name": "Maze",              "level": 8, "school": "Conjuration",   "hook": "Traps the problem elegantly, without having to look at it."},
        {"name": "Demiplane",         "level": 8, "school": "Conjuration",   "hook": "A room only they can open. Some things are better kept very far away."},
        {"name": "Wish",              "level": 9, "school": "Conjuration",   "hook": "The most honest thing they own. They haven't used it yet because they haven't decided what they want most."},
        {"name": "Time Stop",         "level": 9, "school": "Transmutation", "hook": "For when patience — which is usually sufficient — finally runs out."},
        {"name": "Imprisonment",      "level": 9, "school": "Abjuration",    "hook": "The permanent solution they keep hoping they won't need."},
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
        {"name": "Speak with Dead",     "level": 3, "school": "Necromancy",  "hook": "The conversations that never end, just pause."},
        {"name": "Banishment",          "level": 4, "school": "Abjuration",  "hook": "Returning things to where they came from — the question is whether they stay."},
        {"name": "Death Ward",          "level": 4, "school": "Abjuration",  "hook": "The spell they cast on themselves the night before Greenwatch. They haven't told anyone."},
        {"name": "Guardian of Faith",   "level": 4, "school": "Conjuration", "hook": "Not alone. Never alone. They're not sure if that's a comfort or a pressure."},
        {"name": "Flame Strike",        "level": 5, "school": "Evocation",   "hook": "The god's anger, expressed through them. Their own follows a moment later."},
        {"name": "Mass Cure Wounds",    "level": 5, "school": "Evocation",   "hook": "The reason they do this. The cost is worth it. They say this every time."},
        {"name": "Raise Dead",          "level": 5, "school": "Necromancy",  "hook": "More complicated than the scroll says. The returned are never quite the same, and neither are they."},
        {"name": "Harm",                "level": 6, "school": "Necromancy",  "hook": "The god's judgment, delivered personally. They feel it too."},
        {"name": "Planar Ally",         "level": 6, "school": "Conjuration", "hook": "Calling for help means admitting you need it. They've learned to make that call earlier."},
        {"name": "Blade Barrier",       "level": 6, "school": "Evocation",   "hook": "The line they hold. Consecrated, visible, absolute."},
        {"name": "Divine Word",         "level": 7, "school": "Evocation",   "hook": "Borrowed from the beginning of things. Using it costs them something each time."},
        {"name": "Resurrection",        "level": 7, "school": "Necromancy",  "hook": "The deep miracle. What it takes from them they can feel for weeks."},
        {"name": "Holy Aura",           "level": 8, "school": "Abjuration",  "hook": "Becoming a vessel — briefly, painfully, worthily."},
        {"name": "Antimagic Field",     "level": 8, "school": "Abjuration",  "hook": "Stripping the world back to what it actually is. Not everyone survives the honesty."},
        {"name": "True Resurrection",   "level": 9, "school": "Necromancy",  "hook": "The miracle they've been building toward. They're not sure they're worthy of it."},
        {"name": "Mass Heal",           "level": 9, "school": "Evocation",   "hook": "The day everything went wrong at once. It wasn't enough. It was close."},
        {"name": "Gate",                "level": 9, "school": "Conjuration", "hook": "The door to where the god actually lives. They've stood in the opening once and did not go through."},
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
        {"name": "Plant Growth",      "level": 3, "school": "Transmutation","hook": "Time is different when you think in seasons."},
        {"name": "Control Water",     "level": 4, "school": "Transmutation","hook": "The river decides — they just ask first, and they've learned the right questions."},
        {"name": "Dominate Beast",    "level": 4, "school": "Enchantment",  "hook": "The animal always forgives them. They're not sure they've earned it."},
        {"name": "Polymorph",         "level": 4, "school": "Transmutation","hook": "Not transformation — permission. The body remembers shapes it has never worn."},
        {"name": "Commune with Nature","level": 5, "school": "Divination",  "hook": "The world has opinions. They're not always good ones, and they're not always wrong."},
        {"name": "Awaken",            "level": 5, "school": "Transmutation","hook": "The tree started talking back. They hadn't expected that, and now they can't unlearn the habit of listening."},
        {"name": "Insect Plague",     "level": 5, "school": "Conjuration",  "hook": "Patience, and then — when patience runs out — this."},
        {"name": "Wall of Stone",     "level": 5, "school": "Transmutation","hook": "In a thousand years, no one will know who built it. The druid considers this adequate credit."},
        {"name": "Heal",              "level": 6, "school": "Evocation",    "hook": "Not a miracle — a correction. The body knew what it was supposed to be."},
        {"name": "Transport via Plants","level": 6,"school": "Conjuration", "hook": "The forest is always closer than it looks, if you know how to ask."},
        {"name": "Fire Storm",        "level": 7, "school": "Evocation",    "hook": "The world burning itself clean — they're just the one who says when."},
        {"name": "Regenerate",        "level": 7, "school": "Transmutation","hook": "The body remembers how to be whole. They just remind it."},
        {"name": "Animal Shapes",     "level": 8, "school": "Transmutation","hook": "The congregation, briefly. They always wonder if the animals remember it afterward."},
        {"name": "Earthquake",        "level": 8, "school": "Evocation",    "hook": "A last resort that never quite feels like one when they're standing at the edge."},
        {"name": "Shapechange",       "level": 9, "school": "Transmutation","hook": "Becoming something so far from human they sometimes forget the way back. Sometimes they don't try to remember."},
        {"name": "Foresight",         "level": 9, "school": "Divination",   "hook": "The gift and the weight of it — knowing what's coming and being unable to change most of it."},
        {"name": "Storm of Vengeance","level": 9, "school": "Conjuration",  "hook": "The world defending itself through them. They'll feel it for a month afterward."},
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
        {"name": "Modify Memory",       "level": 5, "school": "Enchantment", "hook": "Used it once. Thinks about it more than they'd like to admit."},
        {"name": "Compulsion",          "level": 4, "school": "Enchantment", "hook": "Making people move where they want while the room thinks it was their own idea. The power and the cruelty of it."},
        {"name": "Freedom of Movement", "level": 4, "school": "Abjuration",  "hook": "They make sure exits are available — always theirs first, others' second."},
        {"name": "Greater Invisibility","level": 4, "school": "Illusion",    "hook": "Staying in the scene while becoming unreachable — the performer's ideal."},
        {"name": "Otto's Irresistible Dance","level": 6,"school": "Enchantment","hook": "Making people dance while everyone laughs — they've never quite decided if it's joyful or awful."},
        {"name": "Mass Suggestion",     "level": 6, "school": "Enchantment", "hook": "One idea, spreading through a room like smoke from a good fire."},
        {"name": "Eyebite",             "level": 6, "school": "Necromancy",  "hook": "The look that stops people cold. They had a version of it before they learned the spell."},
        {"name": "Mirage Arcane",       "level": 7, "school": "Illusion",    "hook": "Reshaping the stage for the final act. The audience never sees the rigging."},
        {"name": "Power Word Pain",     "level": 7, "school": "Enchantment", "hook": "A word that does exactly what it says. They've performed worse things for smaller audiences."},
        {"name": "Feeblemind",          "level": 8, "school": "Enchantment", "hook": "The cruelest thing in their book. They've used it twice and don't talk about either time."},
        {"name": "Power Word Stun",     "level": 8, "school": "Enchantment", "hook": "Sometimes you need a moment of silence. This is the efficient version."},
        {"name": "True Polymorph",      "level": 9, "school": "Transmutation","hook": "The permanent version. They've thought about using it on themselves. They haven't decided."},
        {"name": "Power Word Kill",     "level": 9, "school": "Enchantment", "hook": "A word. Just one. They learned it hoping they'd never need it, and that hope is wearing thin."},
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
        {"name": "Polymorph",         "level": 4, "school": "Transmutation","hook": "If power means anything, it means choosing what shape you wear."},
        {"name": "Dominate Person",   "level": 5, "school": "Enchantment",  "hook": "The bloodline's clearest expression — other people's will just stops. They've decided this is fine."},
        {"name": "Cone of Cold",      "level": 5, "school": "Evocation",    "hook": "When fire is too obvious and the situation is still burning."},
        {"name": "Animate Objects",   "level": 5, "school": "Transmutation","hook": "The bloodline reaches for control in all directions. This is the literal version."},
        {"name": "Chain Lightning",   "level": 6, "school": "Evocation",    "hook": "Letting it jump to the next target — not entirely their choice, and they're making peace with that."},
        {"name": "Disintegrate",      "level": 6, "school": "Transmutation","hook": "The power that frightens them most, which is exactly why they haven't given it up."},
        {"name": "Mass Suggestion",   "level": 6, "school": "Enchantment",  "hook": "The bloodline's preference made efficient: one idea, many people, no negotiation."},
        {"name": "Finger of Death",   "level": 7, "school": "Necromancy",   "hook": "What happens when they stop rationing the power. They try not to let it get to this."},
        {"name": "Reverse Gravity",   "level": 7, "school": "Transmutation","hook": "The bloodline has opinions about which way is down. The world doesn't always agree."},
        {"name": "Power Word Stun",   "level": 8, "school": "Enchantment",  "hook": "One syllable, older than the bloodline. They don't know where it came from."},
        {"name": "Sunburst",          "level": 8, "school": "Evocation",    "hook": "The power wanting to be seen, finally, by everyone in the room at once."},
        {"name": "Wish",              "level": 9, "school": "Conjuration",  "hook": "The power the bloodline was always reaching toward. They haven't decided what to ask for."},
        {"name": "Meteor Swarm",      "level": 9, "school": "Evocation",    "hook": "The final conversation-ender. When it's time to stop arguing about whether sorcerers are dangerous."},
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
        {"name": "Hold Monster",      "level": 5, "school": "Enchantment",  "hook": "The patron's ability to stop things, borrowed for the duration. The patron finds this efficient."},
        {"name": "Synaptic Static",   "level": 5, "school": "Enchantment",  "hook": "The hum of the far realm given momentary shape — briefly, painfully, productively."},
        {"name": "Teleportation Circle","level": 5,"school": "Conjuration", "hook": "The door the patron left open. They've stopped wondering where it actually leads."},
        {"name": "Circle of Death",   "level": 6, "school": "Necromancy",   "hook": "The patron's preferred radius. They stopped arguing about scale."},
        {"name": "Scatter",           "level": 6, "school": "Conjuration",  "hook": "Moving people without asking. The patron considers consent a separate issue."},
        {"name": "Soul Cage",         "level": 6, "school": "Necromancy",   "hook": "What happens to the soul afterward is the patron's concern. They tell themselves this."},
        {"name": "Forcecage",         "level": 7, "school": "Evocation",    "hook": "The bar on everything — visible, undeniable, final. The patron approves of this one specifically."},
        {"name": "Plane Shift",       "level": 7, "school": "Conjuration",  "hook": "The patron can reach anywhere. This is the part where they demonstrate that."},
        {"name": "Finger of Death",   "level": 7, "school": "Necromancy",   "hook": "What the bargain looks like when they stop being polite about it."},
        {"name": "Demiplane",         "level": 8, "school": "Conjuration",  "hook": "A room built from borrowed power. They've started keeping things there they can't explain."},
        {"name": "Power Word Stun",   "level": 8, "school": "Enchantment",  "hook": "One word, older than the pact. The patron taught it to them without explaining where it came from."},
        {"name": "Glibness",          "level": 8, "school": "Transmutation","hook": "Every word becomes true when they say it. They've stopped distinguishing between the performance and themselves."},
        {"name": "True Polymorph",    "level": 9, "school": "Transmutation","hook": "The pact's deepest promise: you can become anything. The cost is the same as it always is."},
        {"name": "Wish",              "level": 9, "school": "Conjuration",  "hook": "The patron gave them access to this precisely once. They haven't used it. They're not sure they're allowed to want things."},
        {"name": "Imprisonment",      "level": 9, "school": "Abjuration",   "hook": "The forever solution. The patron calls it mercy. They've decided not to ask what it's called from inside."},
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
        {"name": "Aura of Life",       "level": 4, "school": "Abjuration",   "hook": "The field around them that keeps death at bay — they feel it most when it's needed most."},
        {"name": "Banishment",         "level": 4, "school": "Abjuration",   "hook": "Returning the wrong thing to where it belongs. They always make sure it's gone before they breathe again."},
        {"name": "Death Ward",         "level": 4, "school": "Abjuration",   "hook": "The promise they make to the people they can't afford to lose. They always cast it on someone else first."},
        {"name": "Dispel Evil and Good","level": 5, "school": "Abjuration",  "hook": "The oath made into a field — not asking, just ending."},
        {"name": "Holy Weapon",        "level": 5, "school": "Evocation",    "hook": "The god's radiance channeled through steel. For five minutes, they are exactly what they swore to be."},
        {"name": "Destructive Wave",   "level": 5, "school": "Evocation",    "hook": "The conviction that something must end — made loud, and made final."},
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
        {"name": "Locate Creature",    "level": 4, "school": "Divination",   "hook": "Once they've found something once, they can always find it again. This is not always a comfort."},
        {"name": "Grasping Vine",      "level": 4, "school": "Conjuration",  "hook": "The land reaching back. They asked nicely. It obliges."},
        {"name": "Guardian of Nature", "level": 4, "school": "Transmutation","hook": "Becoming the forest's instrument, briefly, entirely. They remember it more clearly than they'd like."},
        {"name": "Commune with Nature","level": 5, "school": "Divination",   "hook": "The wild has been watching. They ask it what it's seen, and the answer is never simple."},
        {"name": "Swift Quiver",       "level": 5, "school": "Transmutation","hook": "When there are too many targets and not enough time — which is always."},
        {"name": "Steel Wind Strike",  "level": 5, "school": "Conjuration",  "hook": "Five places at once — the wilderness doesn't wait for you to catch up."},
        {"name": "Tree Stride",        "level": 5, "school": "Conjuration",  "hook": "The forest is one place, if you know how to move through it. They do."},
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

    cantrip_list = [s for s in selected if s["level"] == 0]
    spell_list   = [s for s in selected if s["level"] >  0]

    result = {
        "class": class_name,
        "cantrips": [
            {"name": s["name"], "school": s["school"], "hook": s["hook"]}
            for s in cantrip_list
        ],
        "spells": [
            {
                "name":   s["name"],
                "level":  f"Level {s['level']}",
                "school": s["school"],
                "hook":   s["hook"],
            }
            for s in spell_list
        ],
        "note": (
            "Pick 3-4 of these that feel true to this character. "
            "Write one sentence per chosen spell about how *this person specifically* uses it — "
            "the hook is a starting point, not a mandate. "
            "List cantrips and leveled spells separately in the character sheet. "
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
