"""
Main entry point — game-first interactive menu.

Pick your game, then pick what you want to build. Each agent can also be
run directly (python traveller_agent.py, etc.) to skip the menu entirely.
"""

import dnd_agent
import traveller_agent
import firefly_agent
import scum_villainy_agent
import party_agent
import npc_cluster_agent
import encounter_agent
import ship_agent
from utils import pick


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
    ],
    "traveller": [
        ("full",        "Full character sheet"),
        ("npc",         "NPC sketch"),
        ("patron",      "Patron encounter"),
        ("party",       "Crew"),
        ("cluster",     "NPC cluster"),
        ("encounter",   "Encounter"),
        ("ship",        "Ship"),
    ],
    "firefly": [
        ("full",        "Full character sheet"),
        ("npc",         "NPC sketch"),
        ("jobcontact",  "Job contact"),
        ("party",       "Crew"),
        ("cluster",     "NPC cluster"),
        ("encounter",   "Encounter"),
        ("ship",        "Ship"),
    ],
    "scum": [
        ("full",        "Full character sheet"),
        ("npc",         "NPC sketch"),
        ("scorecontact","Score contact"),
        ("party",       "Crew"),
        ("cluster",     "NPC cluster"),
        ("encounter",   "Encounter"),
        ("ship",        "Ship"),
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
    "full":         "character",
    "npc":          "NPC",
    "questgiver":   "quest giver",
    "patron":       "patron",
    "jobcontact":   "job contact",
    "scorecontact": "score contact",
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

    # ── Character / NPC / hook encounter ──────────────────────────────────────
    label = MODE_LABELS[action]
    desc  = input(f"\nDescribe the {label} you want (or press Enter for fully random):\n> ").strip()

    print()
    CHARACTER_RUNNERS[game](mode=action, desc=desc)


if __name__ == "__main__":
    main()
