"""
Psionic / psychic ability profiles for sci-fi RPG systems.

Story-first, not rules-complete. Each system handles the gifted mind
differently — this file provides the data pools and generation functions
that let agents build psionic characters with mechanical grounding
and narrative weight.

  traveller — PSI characteristic, psionic talents (Telepathy, Clairvoyance,
               Telekinesis, Teleportation, Awareness, Special), Institute
               training, social stigma inside the Third Imperium.

  scum      — Mystic playbook, Attune action, Ur-web connection flavor,
               ability suggestions, Ur artifacts and their costs.

  firefly   — Reader Distinction, mental Complications, Alliance threat
               level, Signature Asset suggestions for specific abilities.

Each game exports a get_*_profile() function and a tool schema for the
agent's TOOLS list. All three can be imported individually or via the
shared get_psi_profile(game) dispatcher.
"""

import json
import random


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — PSI talents, powers, discovery, and stigma
# ═══════════════════════════════════════════════════════════════════════════════

TRAVELLER_TALENTS: dict[str, dict] = {
    "Telepathy": {
        "description": (
            "The talent of mind-to-mind contact — reading surface thoughts, "
            "probing deeper, sending silent words, or striking directly at another's mind."
        ),
        "powers": [
            {
                "name": "Life Detection",
                "psi_cost": 1,
                "hook": "Feels living minds like heat — the difference between a crowded room and an empty one, even through hull plating.",
            },
            {
                "name": "Telempathy",
                "psi_cost": 1,
                "hook": "Reads emotional states rather than words; has spent a lifetime knowing when people lie without being able to explain how.",
            },
            {
                "name": "Read Surface Thoughts",
                "psi_cost": 2,
                "hook": "The words people are almost saying. It took years to stop answering questions that were never spoken aloud.",
            },
            {
                "name": "Send Thoughts",
                "psi_cost": 2,
                "hook": "Plants words in other minds; still uncomfortable with how easy it is to make someone think an idea was their own.",
            },
            {
                "name": "Probe",
                "psi_cost": 4,
                "hook": "Deep memory access — what someone knows, not just what they're thinking. Has never done it without feeling worse afterward.",
            },
            {
                "name": "Assault",
                "psi_cost": 8,
                "hook": "Mental violence, direct and devastating. Used it once. Knows what it felt like from both sides.",
            },
        ],
    },
    "Clairvoyance": {
        "description": (
            "Remote sensing — sight, sound, and presence beyond line of sight "
            "and, in some cases, beyond the present moment."
        ),
        "powers": [
            {
                "name": "Sense",
                "psi_cost": 1,
                "hook": "A general awareness of what occupies a distant location — like a map that updates when something moves.",
            },
            {
                "name": "Clairvoyance",
                "psi_cost": 2,
                "hook": "Full remote vision — can be anywhere they've been, or anywhere they can picture clearly enough.",
            },
            {
                "name": "Clairaudience",
                "psi_cost": 2,
                "hook": "Hears conversations through walls, across vacuum, in rooms that haven't been entered in years.",
            },
            {
                "name": "Clairsentience",
                "psi_cost": 3,
                "hook": "All remote senses simultaneously — overwhelming without focus. The trick is knowing which room to look in.",
            },
        ],
    },
    "Telekinesis": {
        "description": (
            "Moving matter without physical contact — delicate manipulation "
            "to crushing force, at distances proportional to PSI spent."
        ),
        "powers": [
            {
                "name": "Telekinesis",
                "psi_cost": 2,
                "hook": "Moves objects through concentration. From the outside it looks like nothing, which is half the value.",
            },
            {
                "name": "Enhanced Telekinesis",
                "psi_cost": 3,
                "hook": "Heavier loads, higher speed — once used it to stop a hatch closing on someone's hand and it became a reflex.",
            },
            {
                "name": "Pyrokinesis",
                "psi_cost": 3,
                "hook": "Generates or suppresses heat at range. Controlled. Useful. Not something discussed at refuelling stops.",
            },
            {
                "name": "Telekinetic Punch",
                "psi_cost": 5,
                "hook": "Concussive force at range. Unambiguous. The kind of ability that makes first impressions.",
            },
        ],
    },
    "Teleportation": {
        "description": (
            "Instantaneous spatial displacement — consciousness routing through "
            "jump-space to reappear elsewhere, with or without passengers."
        ),
        "powers": [
            {
                "name": "Teleport Self",
                "psi_cost": 3,
                "hook": "Blink-displacement — must know the destination, which makes it a better exit strategy than an entrance.",
            },
            {
                "name": "Teleport Other",
                "psi_cost": 4,
                "hook": "Can take one person or object along. The first time was an accident. The recipient has forgiven them, mostly.",
            },
            {
                "name": "Distant Teleport",
                "psi_cost": 6,
                "hook": "Greater range with greater cost — theoretically unlimited, bounded in practice by how much PSI they're willing to spend to land somewhere alive.",
            },
        ],
    },
    "Awareness": {
        "description": (
            "Mastery of one's own body — healing, enhancement, metabolic control, "
            "and the ability to treat the self as a system to be administered."
        ),
        "powers": [
            {
                "name": "Suspended Animation",
                "psi_cost": 0,
                "hook": "Enters a sleep so deep it reads as death. Used it once, in transit, because there was no food. Still dreams about it.",
            },
            {
                "name": "Enhanced Awareness",
                "psi_cost": 1,
                "hook": "Heightened senses, accelerated perception — the world goes slow and specific.",
            },
            {
                "name": "Psionically Enhanced Strength",
                "psi_cost": 2,
                "hook": "Temporary augmentation; the body that emerges when the PSI flows in.",
            },
            {
                "name": "Regeneration",
                "psi_cost": 3,
                "hook": "Heals damage from within — leaves no scars. Some people find this unsettling. They've stopped caring what people find unsettling.",
            },
            {
                "name": "Body Mastery",
                "psi_cost": 5,
                "hook": "Complete physiological control — heartbeat, bleeding, toxin resistance. The body treated as a ship with the right crew.",
            },
        ],
    },
    "Special": {
        "description": (
            "Rare or alien abilities that fall outside standard Imperial psionic classifications — "
            "sometimes Droyne-influenced, sometimes a function of unusual genetics, "
            "sometimes simply unexplained."
        ),
        "powers": [
            {
                "name": "Psionic Invisibility",
                "psi_cost": 3,
                "hook": "Not true invisibility — makes attention slide off, perception register 'nothing here.' Works better on people than sensors.",
            },
            {
                "name": "Temporal Awareness",
                "psi_cost": 4,
                "hook": "Flickering sense of the near future — not prophecy, just the half-second edge. Still gets surprised sometimes.",
            },
            {
                "name": "Matter Sense",
                "psi_cost": 2,
                "hook": "Feels the composition and history of materials through contact — what it is, how old, whether it's been altered.",
            },
        ],
    },
}


TRAVELLER_DISCOVERY_HOOKS: list[dict] = [
    {
        "method": "Psionic Institute",
        "description": "Tested and trained by a licensed Institute — hidden, expensive, operating in legal gray zone inside the Imperium.",
        "hook": "The Institute reduced their PSI through months of testing before training began; they paid in strength to gain control, and they've never been sure it was a fair trade.",
    },
    {
        "method": "Wild Talent",
        "description": "No training, no testing — ability emerged on its own under extreme stress.",
        "hook": "It came in a bad moment — a crash, an ambush, a grief that had nowhere else to go — and it's been there ever since: inconsistent, undertrained, not entirely under control.",
    },
    {
        "method": "Zhodani Contact",
        "description": "Encountered the Zhodani Consulate, where psionics are normal, valued, and structured.",
        "hook": "The Zhodani treated their ability as unremarkable, which was stranger than any hostility would have been; came back changed, mostly in how they think about hiding it.",
    },
    {
        "method": "Alien Exposure",
        "description": "Contact with an alien artifact, world, or species triggered latent psionic ability.",
        "hook": "They don't know exactly what woke it up; something on that world, in that ruin, responded to something in them — and neither has been dormant since.",
    },
    {
        "method": "Research Incident",
        "description": "Involved in or affected by psionic research — official, unofficial, or very much illegal.",
        "hook": "Someone ran an experiment that wasn't supposed to work, and it did — they weren't the one who designed it, but they were in the room, and the results followed them out.",
    },
]


TRAVELLER_STIGMA_HOOKS: list[str] = [
    "Keeps it completely hidden — no one who currently knows them is aware, and they have a cover story for every incident that has gotten smoother with use.",
    "Known to exactly one trusted person who has never spoken of it and expects the same silence in return.",
    "Had one semi-public incident years ago — filed as a medical episode, never investigated, but they remember every face that was in the room.",
    "Holds documentation as a 'licensed psionic technician' issued by an Institute — legally recognized in two subsectors and a serious complication everywhere else.",
    "Actively wanted by a planetary government for unlicensed psionic activity; the warrant uses a former name and a three-year-old description, which buys time but not safety.",
    "Has operated openly in Zhodani or frontier space long enough that concealment within the Imperium now feels like a second skill — maintained with effort, noticed when it slips.",
]


def get_traveller_psi_profile() -> str:
    """
    Return a psionic profile for a Traveller character: one primary talent,
    2-3 powers from it, a discovery hook, and a stigma situation.

    Talent weights follow approximate rarity in the setting:
    Telepathy and Awareness are most common; Teleportation is rare.
    """
    weights = {
        "Telepathy":     4,
        "Clairvoyance":  3,
        "Awareness":     4,
        "Telekinesis":   2,
        "Teleportation": 1,
        "Special":       1,
    }
    talent_name = random.choices(
        list(weights.keys()), weights=list(weights.values()), k=1
    )[0]
    talent = TRAVELLER_TALENTS[talent_name]

    # Always include the lowest-cost power; sample 2 more from the rest
    pool = talent["powers"]
    cheapest = min(pool, key=lambda p: p["psi_cost"])
    rest = [p for p in pool if p is not cheapest]
    extras = random.sample(rest, min(2, len(rest)))
    selected_powers = [cheapest] + extras

    discovery = random.choice(TRAVELLER_DISCOVERY_HOOKS)
    stigma    = random.choice(TRAVELLER_STIGMA_HOOKS)

    result = {
        "talent": talent_name,
        "talent_description": talent["description"],
        "powers": [
            {"name": p["name"], "psi_cost": p["psi_cost"], "hook": p["hook"]}
            for p in selected_powers
        ],
        "discovery": discovery,
        "social_situation": stigma,
        "note": (
            "PSI is a hidden seventh characteristic, typically 2d6 minus terms served (min 0). "
            "Characters spend PSI points to activate powers; they recover at 1 point per hour. "
            "Psionic ability is illegal or heavily stigmatized in most of the Third Imperium. "
            "Add a PSI section to the character sheet after Equipment, as a final layer."
        ),
    }
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# SCUM & VILLAINY — Ur-web, Mystic abilities, artifacts
# ═══════════════════════════════════════════════════════════════════════════════

SCUM_UR_WEB_CONNECTIONS: list[dict] = [
    {
        "flavor": "Resonance",
        "description": "The Ur-web comes as vibration in metal — hull plates, station struts, anything that's been in space long enough.",
        "hook": "Feels Ur artifacts before seeing them; the older the object, the louder it gets. Stations older than the Hegemony are nearly deafening.",
    },
    {
        "flavor": "Presence",
        "description": "Experiences the Ur as a secondary awareness — a vast, dim consciousness at the edge of their own.",
        "hook": "Never entirely alone; the Ur-web's presence is constant and familiar, and occasionally responds when they're not asking questions.",
    },
    {
        "flavor": "Vision",
        "description": "Receives the Ur as flashes of image and memory — not their own, not quite anyone's.",
        "hook": "Has seen things that haven't happened yet; also things that happened before humans reached the stars. Doesn't always know which is which.",
    },
    {
        "flavor": "Instinct",
        "description": "Doesn't experience the Ur consciously — it surfaces as unexplained certainty, decisions made before reasoning catches up.",
        "hook": "Trusts their gut in ways that unsettle the crew, because they're right more often than the gut should allow.",
    },
    {
        "flavor": "Echo",
        "description": "Hears voices — fragments, not full speech, from minds that are no longer present.",
        "hook": "Populated, empty space always sounds inhabited to them; derelict stations are the worst.",
    },
    {
        "flavor": "Wound",
        "description": "The Ur-web connection came through trauma — an artifact, a near-death experience, an exposure that left something behind.",
        "hook": "The ability and the damage arrived together; they've learned to use one without letting the other use them.",
    },
]


SCUM_UR_ARTIFACTS: list[dict] = [
    {
        "name": "A shard of something not metal and not glass",
        "property": "Warm to the touch, always, regardless of ambient temperature. Sharpens Attune rolls near Ur sites.",
        "complication": "Hegemony artifact scanners at checkpoints will flag it; they've learned to declare it as a 'personal religious object.'",
    },
    {
        "name": "A resonance coin, pre-Hegemony",
        "property": "Hums audibly when a Mystic or Ur-touched individual is within twenty meters. Inaudible to non-Attune users.",
        "complication": "It also hums near Hegemony Ur-monitors, which is useful information and a significant problem.",
    },
    {
        "name": "An anchor — a small carved figure of unknown origin",
        "property": "Reduces stress from failed Attune rolls by 1 when held. Grounding. Quiet.",
        "complication": "Someone else wants it, with the kind of persistence that means they know exactly what it is.",
    },
    {
        "name": "A fragment of Ur script, tattooed",
        "property": "Not an object — the artifact is on their skin. Grants +1d when performing Rituals.",
        "complication": "What it actually says is disputed among the three people in the galaxy who can read it, and one of those people works for the Hegemony.",
    },
    {
        "name": "A sealed container of Ur provenance",
        "property": "Has never been opened. Resonates strongly near ley lines and Ur sites. Something inside responds when they Attune.",
        "complication": "They don't know what's inside and have decided, for now, that this is safer.",
    },
]


SCUM_MYSTIC_ABILITY_HOOKS: list[dict] = [
    {
        "ability": "Arcane Sight",
        "hook": "Sees what others miss without trying — spirits at the edge of vision, ether flows in ship corridors. The crew has learned not to ask what they're looking at.",
    },
    {
        "ability": "Ghost Walker",
        "hook": "Can push through solid matter — walls, hulls, locked doors — but emerges wracked. The cost is always worth it and never comfortable.",
    },
    {
        "ability": "Heritage",
        "hook": "Something in their lineage or history connects directly to the Ur; spirits and echoes respond to them as though they recognize something.",
    },
    {
        "ability": "Ritual",
        "hook": "Knows the old forms — the arcana that predate the Hegemony by millennia. Slow, deliberate, and terrifyingly effective.",
    },
    {
        "ability": "Tempest",
        "hook": "When they unleash rather than direct — wide-area, violent, chaotic — the Ur-web amplifies it. Not a precise tool. Useful anyway.",
    },
    {
        "ability": "The Sight",
        "hook": "Pushes into the near future at the cost of stress. What they see is accurate. What it costs them builds each time.",
    },
    {
        "ability": "Warded",
        "hook": "Has learned to turn the Ur-web into armor against its own effects — and against those who would use it against them.",
    },
    {
        "ability": "Whispers",
        "hook": "Spirits warn them. Not clearly, not kindly, but reliably — a chill, a sound, a pressure behind the eyes. They are never caught sleeping.",
    },
]


def get_mystic_profile() -> str:
    """
    Return a Scum & Villainy Mystic profile: Ur-web connection flavor,
    3 ability suggestions, one Ur artifact, and stress/cost notes.
    """
    connection = random.choice(SCUM_UR_WEB_CONNECTIONS)
    artifact   = random.choice(SCUM_UR_ARTIFACTS)
    abilities  = random.sample(SCUM_MYSTIC_ABILITY_HOOKS, 3)

    result = {
        "playbook": "Mystic",
        "ur_web_connection": connection,
        "suggested_abilities": abilities,
        "artifact": artifact,
        "note": (
            "The Mystic's primary action is Attune (starts at 2 dots). "
            "Abilities that 'push yourself' cost 2 stress. Special armor absorbs "
            "one supernatural consequence per score. The Ur-web is ancient, vast, "
            "and not entirely benign — treat connection flavor as texture, not power level."
        ),
    }
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# FIREFLY — Reader Distinctions, Complications, Alliance threat, Assets
# ═══════════════════════════════════════════════════════════════════════════════

FIREFLY_READER_DISTINCTIONS: list[dict] = [
    {
        "name": "Reads the Room",
        "description": "Senses emotional currents in a space without trying — baseline noise, not invasive reach.",
        "hinder_hook": "Can't turn it off in crowds; sometimes the noise is louder than the conversation happening in front of them.",
    },
    {
        "name": "Hears What Isn't Said",
        "description": "Catches the gap between words and thought — liars, concealers, people holding something back.",
        "hinder_hook": "Unsettles people who sense they're being read, even when nothing is said.",
    },
    {
        "name": "Knows Things They Shouldn't",
        "description": "Information surfaces without a source — faces they've never seen, facts they were never told.",
        "hinder_hook": "Can't always separate knowledge from memory; sometimes acts on a certainty they can't justify.",
    },
    {
        "name": "The Alliance Made Them",
        "description": "Product of the Academy's program — trained, augmented, and escaped. The gift is real and so is the damage.",
        "hinder_hook": "Conditioned responses surface under stress; the Alliance's triggers are still there, buried.",
    },
    {
        "name": "Sees the Shape of Things",
        "description": "Perceives the probable arc of events — not prophecy, pattern recognition at a level that feels like the former.",
        "hinder_hook": "Occasionally certain about things that haven't happened yet, which is more unsettling than useful.",
    },
]


FIREFLY_READER_COMPLICATIONS: list[dict] = [
    {
        "name": "The Noise",
        "description": "Unfiltered input from too many minds at once — crowds, high-stress situations, chaotic environments trigger it.",
        "trigger": "Any scene with more than a handful of people in strong emotional distress.",
        "expression": "Withdrawal, pain, sensory overload — they go somewhere inside until it passes.",
    },
    {
        "name": "The Episodes",
        "description": "Academy conditioning surfaces as dissociation or involuntary action — rare, unpredictable, very specific triggers.",
        "trigger": "Particular words, codes, or sensory combinations left by the Alliance program.",
        "expression": "Absence — they're present but not there — or a controlled, precise action that isn't theirs.",
    },
    {
        "name": "The Cost of Reaching",
        "description": "Deep reads or strong projections leave them exhausted, disoriented, temporarily diminished.",
        "trigger": "Pushing ability past passive use into active reach.",
        "expression": "Physical collapse, confusion, lost time — proportional to how far they pushed.",
    },
    {
        "name": "Bleeds",
        "description": "Absorbs emotions from others and loses track of which ones are theirs.",
        "trigger": "Extended proximity to someone in strong emotional states.",
        "expression": "Behavioral shifts — grief, rage, elation — that don't match their situation and take time to clear.",
    },
    {
        "name": "The Nightmares",
        "description": "Sleep is where control lapses; what they've read surfaces, unfiltered.",
        "trigger": "Sleep, usually — but extreme stress can bring it while waking.",
        "expression": "Screaming, sleep-talking specifics that trouble the crew, waking with others' memories in their mouth.",
    },
]


FIREFLY_ALLIANCE_THREAT_LEVELS: list[dict] = [
    {
        "level": "Quiet Flag",
        "description": "Name is on a low-priority list — flagged if encountered, not actively hunted.",
        "risk": "Routine identity checks at Alliance checkpoints will return a yellow flag. Manageable with false papers.",
    },
    {
        "level": "Active File",
        "description": "A case officer has their file; periodic sweeps check for activity.",
        "risk": "Can't use their real name in Core worlds. Someone at every major port may be authorized to detain them.",
    },
    {
        "level": "Specialist Asset",
        "description": "An operative is assigned to their recovery — not openly, but persistently.",
        "risk": "The operative knows their patterns and has resources. The goal is retrieval, not punishment, which is not necessarily better.",
    },
    {
        "level": "Academy Priority",
        "description": "What they carry in their mind is valuable enough that the Academy wants them back urgently.",
        "risk": "Ships have been diverted, agents embedded in civilian roles. The crew has probably already met someone without knowing it.",
    },
]


FIREFLY_READER_ASSETS: list[dict] = [
    {
        "name": "Surface Read",
        "description": "Passive awareness of immediate emotional states and surface intentions.",
        "hook": "Knows who in the room means harm before they've decided on it themselves.",
    },
    {
        "name": "Deep Pull",
        "description": "Active reach into specific memory or knowledge — exhausting, invasive.",
        "hook": "Has found things people didn't know they knew; also things they desperately wanted forgotten.",
    },
    {
        "name": "Projected Calm",
        "description": "Can transmit a sense of safety or trust outward — not control, not compulsion, just warmth.",
        "hook": "Useful in negotiations, tense standoffs, anyone about to do something they'll regret. Works on animals.",
    },
    {
        "name": "Danger Sense",
        "description": "Ambient awareness of threat — weapons, intent, structural failure — in range.",
        "hook": "Has saved the crew more times than they've been told about. The crew suspects. They haven't confirmed.",
    },
    {
        "name": "The Voice",
        "description": "Can project a single word or phrase directly into someone's mind.",
        "hook": "Used it twice. Both times it worked perfectly. Won't discuss either occasion.",
    },
]


def get_reader_profile() -> str:
    """
    Return a Firefly Reader profile: one Distinction, two mental Complications,
    an Alliance threat level, and 2 Signature Asset suggestions.
    """
    distinction   = random.choice(FIREFLY_READER_DISTINCTIONS)
    complications = random.sample(FIREFLY_READER_COMPLICATIONS, 2)
    threat        = random.choice(FIREFLY_ALLIANCE_THREAT_LEVELS)
    assets        = random.sample(FIREFLY_READER_ASSETS, 2)

    result = {
        "reader_distinction": distinction,
        "complications": complications,
        "alliance_threat": threat,
        "signature_assets": assets,
        "note": (
            "The Reader Distinction is d8. Invoke it when the psychic ability clearly helps; "
            "Hinder it (earn a Plot Point) when it creates trouble. "
            "Complications start at d6 and can be stepped up by the GM. "
            "Signature Assets start at d6 and can be stepped up through play. "
            "The Alliance threat level is off-screen pressure, not a stat — "
            "it determines how aggressively they're being sought right now."
        ),
    }
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# Shared dispatcher
# ═══════════════════════════════════════════════════════════════════════════════

def get_psi_profile(game: str) -> str:
    """Dispatch to the correct psi/psychic profile generator for the given game."""
    if game == "traveller":
        return get_traveller_psi_profile()
    if game == "scum":
        return get_mystic_profile()
    if game == "firefly":
        return get_reader_profile()
    return json.dumps({
        "error": f"No psi profile for game '{game}'. Valid: traveller, scum, firefly."
    })


# ═══════════════════════════════════════════════════════════════════════════════
# Tool schemas (one per game, imported into each agent's TOOLS list)
# ═══════════════════════════════════════════════════════════════════════════════

TRAVELLER_PSI_TOOL_SCHEMA: dict = {
    "name": "get_traveller_psi_profile",
    "description": (
        "Get a psionic talent profile for a Traveller character. "
        "Returns a primary talent (Telepathy, Clairvoyance, Telekinesis, "
        "Teleportation, Awareness, or Special), 2-3 powers with PSI costs "
        "and narrative hooks, a discovery method, and the character's current "
        "social situation inside the Third Imperium. "
        "Call this when generating a psionic Traveller character — before writing the sheet."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

SCUM_MYSTIC_TOOL_SCHEMA: dict = {
    "name": "get_mystic_profile",
    "description": (
        "Get an Ur-web connection profile for a Scum & Villainy Mystic. "
        "Returns how the character experiences the Ur-web, 3 ability suggestions "
        "from the Mystic playbook with narrative hooks, and one Ur artifact with "
        "its property and complication. "
        "Call this when generating a Mystic character — before writing the sheet."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

FIREFLY_READER_TOOL_SCHEMA: dict = {
    "name": "get_reader_profile",
    "description": (
        "Get a Reader (psychic) profile for a Firefly character. "
        "Returns a Reader Distinction with hinder hook, two mental Complications "
        "with triggers and expressions, an Alliance threat level, and two Signature "
        "Asset suggestions with hooks. "
        "Call this when generating a Reader character — before writing the sheet."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


# ═══════════════════════════════════════════════════════════════════════════════
# RARITY ROLLS — canonical population probabilities per system
# ═══════════════════════════════════════════════════════════════════════════════
#
# Sources:
#   Traveller: Mongoose 2e Core Rulebook + Alien Modules (Zhodani, Droyne)
#   Scum & Villainy: Playbook distribution (1 of 7) for PCs; setting tone for NPCs
#   Firefly: Setting canon (Academy program scale); RPG corebook (Distinction rarity)

# ── Traveller thresholds (d100 roll-under) ────────────────────────────────────
#
# imperial        — Standard Imperial human space. Psionics are stigmatized and
#                   suppressed; Institutes operate underground. Wild talents exist
#                   but rarely surface. ~3% of the population.
#
# frontier        — Low-law, low-Imperial-oversight worlds beyond the coreward
#                   trade lanes. Less suppression, more wild talents going untested.
#                   ~7% of the population.
#
# zhodani_prole   — Zhodani working class. Latent ability is present but the Consulate
#                   doesn't train proles; most never know what they have. ~15%.
#
# zhodani_noble   — Zhodani noble or intendant. Psionic ability is required for caste
#                   status; all are tested and trained. Effectively 95% (the rare
#                   5% who test negative are quietly reassigned). ~95%.
#
# droyne          — All Droyne have psionic ability; it is biologically fundamental
#                   to caste determination. 100%.

TRAVELLER_PSI_THRESHOLDS: dict[str, int] = {
    "imperial":       3,
    "frontier":       7,
    "zhodani_prole":  15,
    "zhodani_noble":  95,
    "droyne":         100,
}

# ── Scum & Villainy thresholds ────────────────────────────────────────────────
#
# npc             — General NPC in Hegemony space. Ur-touched individuals exist
#                   but are uncommon outside specific roles. ~5%.
#
# notable_npc     — Named, story-relevant NPC. Selection bias: interesting people
#                   in the Hegemony's margins are more likely to have unusual
#                   abilities. ~10%.
#
# Note: For *player characters*, the Mystic is 1 of 7 playbooks (~14%). This is
# handled by playbook selection, not by a chance roll — use get_mystic_profile()
# directly when the Mystic playbook is chosen.

SCUM_PSI_THRESHOLDS: dict[str, int] = {
    "npc":          5,
    "notable_npc":  10,
}

# ── Firefly thresholds ────────────────────────────────────────────────────────
#
# character           — Any character in the 'Verse. The Academy program was
#                       secret, small-scale, and mostly failed. Readers are
#                       nearly unique. ~2%.
#
# academy_connection  — Character has known Alliance Academy ties (student,
#                       staff, family of a subject). Meaningfully higher but
#                       still rare. ~20%.

FIREFLY_PSI_THRESHOLDS: dict[str, int] = {
    "character":           2,
    "academy_connection":  20,
}


# ── Roll functions ────────────────────────────────────────────────────────────

def roll_traveller_psi_chance(context: str = "imperial") -> str:
    """
    Roll to determine if a Traveller character has psionic ability.
    Uses canonical Mongoose 2e population rates. Returns has_ability and
    next_step instruction so the agent knows whether to call
    get_traveller_psi_profile().
    """
    if context not in TRAVELLER_PSI_THRESHOLDS:
        return json.dumps({
            "error": f"Unknown context '{context}'.",
            "valid_contexts": list(TRAVELLER_PSI_THRESHOLDS.keys()),
        })
    threshold = TRAVELLER_PSI_THRESHOLDS[context]
    roll = random.randint(1, 100)
    has_ability = roll <= threshold

    result: dict = {
        "has_ability": has_ability,
        "rolled": roll,
        "threshold": f"{threshold}%",
        "context": context,
    }
    if context == "zhodani_noble":
        result["context_note"] = (
            "Zhodani nobles and intendants are tested and trained by the Consulate. "
            "Psionic ability is required for caste status."
        )
    elif context == "droyne":
        result["context_note"] = (
            "All Droyne have psionic ability — it is biologically fundamental "
            "to caste determination."
        )
    elif context == "frontier":
        result["context_note"] = (
            "Frontier worlds have less Imperial suppression; wild talents go "
            "untested more often, but also surface more freely."
        )

    if has_ability:
        result["note"] = (
            f"Rolled {roll} against {threshold}% threshold — "
            "this character has psionic potential."
        )
        result["next_step"] = (
            "Call get_traveller_psi_profile() to generate their talent, "
            "powers, discovery method, and social situation."
        )
    else:
        result["note"] = (
            f"Rolled {roll} against {threshold}% threshold — "
            "this character has no psionic ability. Do not add a PSI section."
        )
    return json.dumps(result, indent=2)


def roll_scum_psi_chance(context: str = "npc") -> str:
    """
    Roll to determine if a Scum & Villainy NPC is Ur-touched / Mystic-adjacent.
    Use only for NPCs — player character Mystics are determined by playbook choice,
    not by this roll. Returns has_ability and next_step.
    """
    if context not in SCUM_PSI_THRESHOLDS:
        return json.dumps({
            "error": f"Unknown context '{context}'.",
            "valid_contexts": list(SCUM_PSI_THRESHOLDS.keys()),
        })
    threshold = SCUM_PSI_THRESHOLDS[context]
    roll = random.randint(1, 100)
    has_ability = roll <= threshold

    result: dict = {
        "has_ability": has_ability,
        "rolled": roll,
        "threshold": f"{threshold}%",
        "context": context,
    }
    if has_ability:
        result["note"] = (
            f"Rolled {roll} against {threshold}% threshold — "
            "this NPC has Ur-web sensitivity or Mystic-adjacent ability."
        )
        result["next_step"] = (
            "Call get_mystic_profile() to get Ur-web connection flavor and "
            "weave it into the NPC's Demeanor or Secret."
        )
    else:
        result["note"] = (
            f"Rolled {roll} against {threshold}% threshold — "
            "this NPC has no Ur-web connection. Do not add Mystic elements."
        )
    return json.dumps(result, indent=2)


def roll_firefly_psi_chance(context: str = "character") -> str:
    """
    Roll to determine if a Firefly character or NPC is a Reader.
    Readers are vanishingly rare in the 'Verse — products of a secret,
    small-scale Alliance Academy program. Returns has_ability and next_step.
    """
    if context not in FIREFLY_PSI_THRESHOLDS:
        return json.dumps({
            "error": f"Unknown context '{context}'.",
            "valid_contexts": list(FIREFLY_PSI_THRESHOLDS.keys()),
        })
    threshold = FIREFLY_PSI_THRESHOLDS[context]
    roll = random.randint(1, 100)
    has_ability = roll <= threshold

    result: dict = {
        "has_ability": has_ability,
        "rolled": roll,
        "threshold": f"{threshold}%",
        "context": context,
    }
    if context == "academy_connection":
        result["context_note"] = (
            "Alliance Academy ties meaningfully raise the odds, but the program "
            "was small and mostly failed. Most Academy-connected characters are "
            "not Readers."
        )

    if has_ability:
        result["note"] = (
            f"Rolled {roll} against {threshold}% threshold — "
            "this character is a Reader. This is genuinely exceptional."
        )
        result["next_step"] = (
            "Call get_reader_profile() to generate their Distinction, "
            "Complications, Alliance threat level, and Signature Assets."
        )
    else:
        result["note"] = (
            f"Rolled {roll} against {threshold}% threshold — "
            "this character is not a Reader. Do not add Reader elements."
        )
    return json.dumps(result, indent=2)


# ── Rarity tool schemas ───────────────────────────────────────────────────────

TRAVELLER_PSI_CHANCE_TOOL_SCHEMA: dict = {
    "name": "roll_traveller_psi_chance",
    "description": (
        "Roll to determine if a randomly generated Traveller character or NPC "
        "has psionic ability, using canonical Mongoose 2e population rates. "
        "Call this for every randomly generated character/NPC unless psionics "
        "were explicitly requested. If has_ability is true, call "
        "get_traveller_psi_profile() next. "
        "Context guide: 'imperial' = standard Imperial human (3%); "
        "'frontier' = low-law non-Imperial world (7%); "
        "'zhodani_prole' = Zhodani working class (15%); "
        "'zhodani_noble' = Zhodani noble/intendant (95%); "
        "'droyne' = any Droyne (100%)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "enum": list(TRAVELLER_PSI_THRESHOLDS.keys()),
                "description": "The character's cultural/racial context — determines probability.",
            },
        },
        "required": ["context"],
    },
}

SCUM_PSI_CHANCE_TOOL_SCHEMA: dict = {
    "name": "roll_scum_psi_chance",
    "description": (
        "Roll to determine if a randomly generated Scum & Villainy NPC is "
        "Ur-touched or Mystic-adjacent, using setting-appropriate rates. "
        "Call this for randomly generated NPCs only — player character Mystics "
        "are determined by playbook choice, not this roll. "
        "If has_ability is true, call get_mystic_profile() next and weave "
        "the Ur-web flavor into the NPC's Demeanor or Secret. "
        "Context guide: 'npc' = general NPC (5%); "
        "'notable_npc' = named story-relevant NPC (10%)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "enum": list(SCUM_PSI_THRESHOLDS.keys()),
                "description": "NPC prominence — determines probability.",
            },
        },
        "required": ["context"],
    },
}

FIREFLY_PSI_CHANCE_TOOL_SCHEMA: dict = {
    "name": "roll_firefly_psi_chance",
    "description": (
        "Roll to determine if a randomly generated Firefly character or NPC "
        "is a Reader, using setting-canonical rates. Readers are vanishingly "
        "rare — products of a secret Alliance Academy program. "
        "Call this for every randomly generated character/NPC unless a Reader "
        "was explicitly requested. If has_ability is true, call "
        "get_reader_profile() next. "
        "Context guide: 'character' = any character in the 'Verse (2%); "
        "'academy_connection' = known Alliance Academy ties (20%)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "enum": list(FIREFLY_PSI_THRESHOLDS.keys()),
                "description": "Character's relationship to the Alliance Academy.",
            },
        },
        "required": ["context"],
    },
}
