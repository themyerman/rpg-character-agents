"""
Ship name pools for all RPG game systems.

Each game has a distinct naming register:

  traveller — Imperial/formal. Classical mythology, noble titles, navigation,
               honest commerce. Ships sound like they were named by accountants
               who occasionally read poetry.

  firefly   — Personal, bittersweet, meaning-laden. Named for battles, lost
               ideals, second chances. The crew named her, and it shows.

  scum      — Criminal-poetic. Dark elegance, sardonic irony, implied menace.
               Often carries "The" as a quiet definite article of intimidation.

  dnd       — Nautical/heroic. Sea mythology, legendary creatures, weather
               and ocean imagery. Names carved into wood and cursed at in storms.

Call roll_ship_name(game) before naming any ship to prevent the model from
defaulting to generic sci-fi vessel names. The returned JSON includes the
ship's class/type and a one-line note on the naming register.

Tool schemas are per-game (no game parameter — each agent hardcodes its game
in its run_tool dispatcher).
"""

import json
import random


# ── Ship pools ────────────────────────────────────────────────────────────────

SHIP_POOLS: dict[str, dict] = {

    "traveller": {
        "register": (
            "Imperial/formal — classical mythology, noble titles, navigation, "
            "and the quiet poetry of someone who has spent a lot of time in jump space."
        ),
        "names": [
            "Persephone", "Annic Nova", "March Harrier", "Empress Marava",
            "Far Horizon", "Bold Venture", "Distant Shores", "Spinward Star",
            "Iron Meridian", "Deep Passage", "Golden Promise", "Swift Venture",
            "Prometheus Rising", "Long Way Round", "Vagrant Star", "Honest Profit",
            "Ardent Pilgrim", "Second Sunrise", "Pale Wanderer", "Drifting Light",
            "Steady Bearing", "Waypoint", "Coreward Reach", "Duchess of Mora",
            "Faithful Servant", "Bright Passage", "Outer Reach", "Silver Comet",
            "Trade Wind", "Perihelion",
        ],
        "classes": [
            "Type-A Free Trader", "Type-A2 Far Trader", "Type-S Scout/Courier",
            "Type-R Subsidized Merchant", "Type-C Corsair", "Type-T Patrol Cruiser",
            "Beowulf-class Free Trader", "Empress Marava-class Far Trader",
            "Gazelle-class Close Escort", "Broadsword-class Mercenary Cruiser",
            "Safari Ship", "Seeker Mining Vessel",
        ],
    },

    "firefly": {
        "register": (
            "Personal, bittersweet, meaning-laden — named for battles, lost ideals, "
            "or second chances. The crew named her, and it shows in every dent."
        ),
        "names": [
            "Serenity", "Deliverance", "Persistence", "Endurance", "Defiance",
            "Absolution", "Second Chance", "Perdition's Flame", "Providence",
            "Valor", "Last Light", "Wayward Sun", "Bitter Season", "Fortunate Son",
            "Hard Passage", "Burning Bright", "Far From Home", "Lost Cause",
            "Long Passage", "Narrow Escape", "Dusty Mile", "Iron Will",
            "Fallen Star", "Breaking Dawn", "Last Dance", "Vagrant Son",
            "New Beginning", "Borrowed Time", "True Meridian", "Wayward Star",
        ],
        "classes": [
            "Firefly-class", "Tohoku-class", "Pelican-class", "Mobius-class",
            "Dragonfly-class", "Aught-class", "Trace Compression Block-class",
            "Series 3 Firefly", "Wren-class",
        ],
    },

    "scum": {
        "register": (
            "Criminal-poetic — dark elegance, sardonic irony, implied menace. "
            "The name is a warning, a joke, or both."
        ),
        "names": [
            "Pale Dreamer", "Void Witch", "Iron Hand", "Quiet Ruin",
            "Dark Meridian", "Shadow's Edge", "Honest Mistake", "Nothing Personal",
            "Careful Lie", "Velvet Hand", "Long Silence", "Patient Zero",
            "Iron Lullaby", "Borrowed Time", "Empty Threat", "The Contingency",
            "Calculated Risk", "Last Impression", "Gentle Reminder", "Quiet Exit",
            "Clean Hands", "The Exception", "Narrow Margin", "Necessary Evil",
            "Best Intentions", "Patient Hunter", "Pale Justice", "The Arrangement",
            "Burning Bridge", "The Oversight",
        ],
        "classes": [
            "Stardancer-class", "Lamprey-class", "Cerberus-class", "Firedrake-class",
            "Specter-class", "Warden-class", "Jackal-class", "Nightsong-class",
        ],
    },

    "dnd": {
        "register": (
            "Nautical/heroic — sea mythology, legendary creatures, weather and ocean "
            "imagery. Names carved into wood, then cursed at during every storm."
        ),
        "names": [
            "Storm Chaser", "Sea Serpent", "Gilded Prow", "Iron Tide",
            "Maiden's Breath", "Leviathan's Wake", "Tempest's Daughter",
            "Kraken's Bane", "Wave Dancer", "Tidal Fury", "Sea Witch",
            "Mermaid's Song", "Saltborn", "Stormrunner", "Deep Horizon",
            "Dragon's Tooth", "Ironkeel", "Black Current", "Wayward Wind",
            "Silver Gull", "Sea Drake", "Undertow", "Tide's Edge",
            "Corsair's Pride", "Lucky Anchor", "Brinewind", "The Tempest",
            "Mariner's Hope", "Brazen Gull", "Windrunner",
        ],
        "classes": [
            "Sloop", "Brigantine", "Carrack", "Galleon", "Caravel",
            "Keelboat", "Warship", "Longship", "Galley", "Drakkar",
        ],
    },

    "alien": {
        "register": (
            "Corporate/utilitarian — Weyland-Yutani commercial and USCM military vessels. "
            "Names drawn from mythology, geography, and the company's quiet sense of irony. "
            "Every hull registry is on file somewhere. The company knows exactly where each ship is."
        ),
        "names": [
            "Nostromo", "Sulaco", "Narcissus", "Prometheus", "Covenant",
            "Patna", "Anesidora", "Montero", "Marlow", "Gaspar",
            "Yelena", "Cronus", "Auriga", "Lorelei", "Legato",
            "Sotillo", "Torrens", "Kutner", "Maginot", "Hadley",
            "Heracles", "Rigel", "Arcturus", "Cygnus", "Perihelion",
            "Fury", "Shoshone", "Long Passage", "Iron Meridian", "Pale Horizon",
        ],
        "classes": [
            "USCSS Class M Commercial Hauler",
            "USCSS Class C Commercial Transport",
            "USCM Conestoga-class Troopship",
            "USCM Bougainville-class Assault Transport",
            "Weyland-Yutani Survey Vessel",
            "Colonial Administration Transport",
            "Independent Deep-Space Salvage Vessel",
            "Lockmart CM-88B Bison Medium Utility Transport",
            "Deep Orbit Science Platform",
            "Class 3 Work Tug",
        ],
    },
}


# ── Function ──────────────────────────────────────────────────────────────────

def roll_ship_name(game: str) -> str:
    """Return a ship name and class appropriate to the given game.

    Args:
        game: One of 'traveller', 'firefly', 'scum', 'dnd'.

    Returns:
        JSON string with keys: name, ship_class, register.
    """
    if game not in SHIP_POOLS:
        return json.dumps({
            "error": f"Unknown game {game!r}. Valid: {sorted(SHIP_POOLS.keys())}",
        })
    pool = SHIP_POOLS[game]
    return json.dumps({
        "name":       random.choice(pool["names"]),
        "ship_class": random.choice(pool["classes"]),
        "register":   pool["register"],
    })


# ── Tool schemas (one per game — agents hardcode their game in run_tool) ──────

TRAVELLER_SHIP_TOOL_SCHEMA: dict = {
    "name": "roll_ship_name",
    "description": (
        "Get a Mongoose Traveller 2e ship name and class. Call this when naming "
        "the crew's ship or any vessel they encounter. Names follow the Imperial "
        "register — classical, formal, with a hint of deep-space poetry."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

FIREFLY_SHIP_TOOL_SCHEMA: dict = {
    "name": "roll_ship_name",
    "description": (
        "Get a Firefly RPG ship name and class. Call this when naming the crew's "
        "ship or any vessel in the 'Verse. Names are personal and meaning-laden — "
        "the crew named her, and it shows."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

SCUM_SHIP_TOOL_SCHEMA: dict = {
    "name": "roll_ship_name",
    "description": (
        "Get a Scum and Villainy ship name and class. Call this when naming the "
        "crew's ship or any vessel they deal with. Names carry dark elegance, "
        "sardonic irony, or implied menace — often all three."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

DND_SHIP_TOOL_SCHEMA: dict = {
    "name": "roll_ship_name",
    "description": (
        "Get a D&D ship name and class for a nautical campaign. Call this when "
        "naming any vessel. Names draw on sea mythology, legendary creatures, "
        "and the ocean's indifference to human ambition."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

ALIEN_SHIP_TOOL_SCHEMA: dict = {
    "name": "roll_ship_name",
    "description": (
        "Get an Alien RPG ship name and class. Call this when naming the crew's "
        "vessel or any ship they encounter. Names follow the Weyland-Yutani and "
        "USCM registers — corporate, utilitarian, with mythology underneath."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}
