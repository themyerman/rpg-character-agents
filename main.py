"""
Main entry point — game-first interactive menu.

Pick your game, then pick what you want to build. Each agent can also be
run directly (python agents/traveller_agent.py, etc.) to skip the menu entirely.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents import dnd_agent
from agents import traveller_agent
from agents import firefly_agent
from agents import scum_villainy_agent
from agents import party_agent
from agents import npc_cluster_agent
from agents import encounter_agent
from agents import ship_agent
from agents import location_agent
from agents import rumor_agent
from agents import event_agent
from lib.utils import pick
from lib.safety import sanitize_desc, screen_desc


# ── Per-game action menus ─────────────────────────────────────────────────────

# Each entry: (action_key, display_label)
# character modes are embedded directly so labels use game-appropriate terms

GAME_ACTIONS: dict[str, list[tuple[str, str]]] = {
    "dnd": [
        ("full",        "Full character sheet"),
        ("npc",         "NPC sketch"),
        ("questgiver",  "Quest giver"),
        ("party",       "Party"),
        ("cluster",     "NPC cluster"),
        ("encounter",   "Encounter"),
        ("ship",        "Ship"),
        ("location",    "Location"),
        ("rumor",       "Rumor"),
        ("event",       "Event"),
    ],
    "traveller": [
        ("full",          "Full character sheet"),
        ("npc",           "NPC sketch"),
        ("patron",        "Patron encounter"),
        ("alien",         "Alien character"),
        ("synthetic",     "Droid or AI NPC"),
        ("first_contact", "First contact encounter"),
        ("party",         "Crew"),
        ("cluster",       "NPC cluster"),
        ("encounter",     "Encounter"),
        ("ship",          "Ship"),
        ("location",      "Location"),
        ("rumor",         "Rumor"),
        ("event",         "Event"),
    ],
    "firefly": [
        ("full",        "Full character sheet"),
        ("npc",         "NPC sketch"),
        ("jobcontact",  "Job contact"),
        ("party",       "Crew"),
        ("cluster",     "NPC cluster"),
        ("encounter",   "Encounter"),
        ("ship",        "Ship"),
        ("location",    "Location"),
        ("rumor",       "Rumor"),
        ("event",       "Event"),
    ],
    "scum": [
        ("full",          "Full character sheet"),
        ("npc",           "NPC sketch"),
        ("scorecontact",  "Score contact"),
        ("stardancer",    "Stardancer character"),
        ("party",         "Crew"),
        ("cluster",       "NPC cluster"),
        ("encounter",     "Encounter"),
        ("ship",          "Ship"),
        ("location",      "Location"),
        ("rumor",         "Rumor"),
        ("event",         "Event"),
    ],
}

# Character agent runners — accept (mode, desc)
CHARACTER_RUNNERS: dict[str, callable] = {
    "dnd":       dnd_agent.run,
    "traveller": traveller_agent.run,
    "firefly":   firefly_agent.run,
    "scum":      scum_villainy_agent.run,
}

# Human-readable labels for the description prompt
MODE_LABELS: dict[str, str] = {
    "full":          "character",
    "npc":           "NPC",
    "questgiver":    "quest giver",
    "patron":        "patron",
    "jobcontact":    "job contact",
    "scorecontact":  "score contact",
    "alien":         "alien character",
    "synthetic":     "droid or AI NPC",
    "stardancer":    "Stardancer character",
    # first_contact is fully procedural — no desc prompt needed
}

GAMES: list[tuple[str, str]] = [
    ("dnd",       "D&D 5e"),
    ("traveller", "Mongoose Traveller 2e"),
    ("firefly",   "Firefly RPG"),
    ("scum",      "Scum and Villainy"),
]


def main() -> None:
    print("\nTabletop RPG Generator")
    print("=" * 30)

    game = pick("Which game?", GAMES)

    action = pick("What do you want to build?", GAME_ACTIONS[game])

    # ── Party / crew ──────────────────────────────────────────────────────────
    if action == "party":
        party_agent.run(game=game)
        return

    # ── NPC cluster ───────────────────────────────────────────────────────────
    if action == "cluster":
        npc_cluster_agent.run(game=game)
        return

    # ── Encounter ─────────────────────────────────────────────────────────────
    if action == "encounter":
        encounter_agent.run(game=game)
        return

    # ── Ship ──────────────────────────────────────────────────────────────────
    if action == "ship":
        ship_agent.run(game=game)
        return

    # ── Location ──────────────────────────────────────────────────────────────
    if action == "location":
        location_agent.run(game=game)
        return

    # ── Rumor ─────────────────────────────────────────────────────────────────
    if action == "rumor":
        rumor_agent.run(game=game)
        return

    # ── Event ─────────────────────────────────────────────────────────────────
    if action == "event":
        event_agent.run(game=game)
        return

    # ── First contact (fully procedural — no description prompt) ─────────────
    if action == "first_contact":
        CHARACTER_RUNNERS[game](mode=action, desc="")
        return

    # ── Character / NPC / hook encounter ──────────────────────────────────────
    label    = MODE_LABELS[action]
    raw_desc = input(f"\nDescribe the {label} you want (or press Enter for fully random):\n> ").strip()
    desc     = sanitize_desc(raw_desc)
    for warning in screen_desc(desc):
        print(f"  [safety] {warning}")

    print()
    CHARACTER_RUNNERS[game](mode=action, desc=desc)


if __name__ == "__main__":
    main()
