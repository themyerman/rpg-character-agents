"""
Dice rolling utilities for all RPG game systems.

Provides roll functions, tool schemas, and run_tool dispatchers that can be
wired into any agent's tool list.  Currently supports D&D 5e and Mongoose
Traveller 2e; extend by adding a new roll_* function + tool schema pair.
"""

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
]


# ── Tool dispatchers ───────────────────────────────────────────────────────────

def run_tool_dnd(name: str, inputs: dict) -> str:
    if name == "roll_stat":  return roll_stat_dnd()
    if name == "roll_dice":  return roll_dice_dnd(**inputs)
    return f"Unknown tool: {name}"


def run_tool_traveller(name: str, inputs: dict) -> str:
    if name == "roll_dice":  return roll_dice_traveller(**inputs)
    return f"Unknown tool: {name}"
