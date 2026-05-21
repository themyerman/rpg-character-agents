"""
Dice rolling utilities for all RPG game systems.

Provides roll functions, tool schemas, and run_tool dispatchers that can be
wired into any agent's tool list.  Currently supports D&D 5e and Mongoose
Traveller 2e; extend by adding a new roll_* function + tool schema pair.
"""

import json
import random


# ── Roll functions ─────────────────────────────────────────────────────────────

def roll_stat_dnd() -> str:
    """Roll 4d6, drop the lowest die — standard D&D ability score method."""
    rolls = [random.randint(1, 6) for _ in range(4)]
    kept  = sorted(rolls, reverse=True)[:3]
    return f"Rolled 4d6: {sorted(rolls)} → kept {kept} → score: {sum(kept)}"


def roll_dice_dnd(sides: int, count: int = 1) -> str:
    """Roll count dice with the given number of sides (d4/d6/d8/d10/d12/d20)."""
    valid = {4, 6, 8, 10, 12, 20}
    if sides not in valid:
        return f"Error: {sides} is not a valid D&D die. Valid: {sorted(valid)}"
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"


def roll_dice_traveller(sides: int, count: int = 1) -> str:
    """Roll count d6 dice for Traveller characteristics (d6 only)."""
    if sides != 6:
        return "Error: Traveller only uses d6."
    rolls = [random.randint(1, 6) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"


# SOC 11+ (hex B+) confers a noble title in Mongoose Traveller 2e.
_TRAVELLER_NOBLE_TITLES: dict[int, tuple[str, str, str]] = {
    11: ("Knight",  "Sir",     "Dame"),
    12: ("Baron",   "Baron",   "Baroness"),
    13: ("Marquis", "Marquis", "Marchioness"),
    14: ("Count",   "Count",   "Countess"),
    15: ("Duke",    "Duke",    "Duchess"),
}

def get_traveller_title(soc: int) -> str:
    """Return the noble title for a Traveller Social Standing score of 11+."""
    if soc < 11:
        return json.dumps({"soc": soc, "title": None,
                           "note": "No noble title — SOC must be 11 or higher."})
    entry = _TRAVELLER_NOBLE_TITLES.get(soc, _TRAVELLER_NOBLE_TITLES[15])
    return json.dumps({
        "soc":       soc,
        "rank":      entry[0],
        "masculine": entry[1],
        "feminine":  entry[2],
        "note": (
            f"SOC {soc} confers the rank of {entry[0]}. "
            f"Use '{entry[1]}' before a male character's name, "
            f"'{entry[2]}' before a female character's name."
        ),
    })


# ── Tool schemas ───────────────────────────────────────────────────────────────

DND_TOOLS: list[dict] = [
    {
        "name": "roll_stat",
        "description": "Roll 4d6 drop lowest for one D&D ability score.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_dice",
        "description": "Roll dice for D&D (d4, d6, d8, d10, d12, d20).",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {"type": "integer", "enum": [4, 6, 8, 10, 12, 20]},
                "count": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["sides"],
        },
    },
]

TRAVELLER_TOOLS: list[dict] = [
    {
        "name": "roll_dice",
        "description": "Roll d6 dice for Traveller characteristics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {"type": "integer", "enum": [6]},
                "count": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["sides"],
        },
    },
    {
        "name": "get_noble_title",
        "description": (
            "Look up the Mongoose Traveller 2e noble title for a Social Standing "
            "score of 11 or higher. Call this after rolling SOC if the total is 11+. "
            "Returns rank name plus the correct masculine and feminine honorifics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "soc": {
                    "type": "integer",
                    "minimum": 11,
                    "maximum": 15,
                    "description": "Social Standing characteristic score (11–15).",
                },
            },
            "required": ["soc"],
        },
    },
]


# ── Tool dispatchers ───────────────────────────────────────────────────────────

def run_tool_dnd(name: str, inputs: dict) -> str:
    if name == "roll_stat":  return roll_stat_dnd()
    if name == "roll_dice":  return roll_dice_dnd(**inputs)
    return f"Unknown tool: {name}"


def run_tool_traveller(name: str, inputs: dict) -> str:
    if name == "roll_dice":    return roll_dice_traveller(**inputs)
    if name == "get_noble_title": return get_traveller_title(**inputs)
    return f"Unknown tool: {name}"
