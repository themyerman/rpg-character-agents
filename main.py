"""
Main entry point — interactive menu that routes to the right generator.

Each agent can also be run directly:
  python dnd_agent.py
  python traveller_agent.py
  python firefly_agent.py
  python scum_villainy_agent.py
  python party_agent.py
"""

import dnd_agent
import traveller_agent
import firefly_agent
import scum_villainy_agent
import party_agent
from utils import pick


GAMES = [
    ("dnd",       "D&D 5e"),
    ("traveller", "Mongoose Traveller 2e"),
    ("firefly",   "Firefly RPG"),
    ("scum",      "Scum and Villainy"),
]

MODES: dict[str, list[tuple[str, str]]] = {
    "dnd":       [("full", "Full character sheet"), ("npc", "NPC sketch"),  ("questgiver",   "Quest giver")],
    "traveller": [("full", "Full character sheet"), ("npc", "NPC sketch"),  ("patron",       "Patron encounter")],
    "firefly":   [("full", "Full character sheet"), ("npc", "NPC sketch"),  ("jobcontact",   "Job contact")],
    "scum":      [("full", "Full character sheet"), ("npc", "NPC sketch"),  ("scorecontact", "Score contact")],
}

MODE_LABELS: dict[str, str] = {
    "full":        "character",
    "npc":         "NPC",
    "questgiver":  "quest giver",
    "patron":      "patron",
    "jobcontact":  "job contact",
    "scorecontact":"score contact",
}

RUNNERS = {
    "dnd":       dnd_agent.run,
    "traveller": traveller_agent.run,
    "firefly":   firefly_agent.run,
    "scum":      scum_villainy_agent.run,
}



def main() -> None:
    print("\nTabletop Character Generator")
    print("=" * 30)

    action = pick(
        "What do you want to do?",
        [("character", "Build a character or NPC"), ("party", "Build a party / crew")],
    )

    if action == "party":
        party_agent.run()
        return

    # --- character path ---
    game = pick("Which game?", GAMES)
    mode = pick("Which mode?", MODES[game])

    label = MODE_LABELS[mode]
    desc  = input(f"\nDescribe the {label} you want (or press Enter for fully random):\n> ").strip()

    print()
    RUNNERS[game](mode=mode, desc=desc)


if __name__ == "__main__":
    main()
