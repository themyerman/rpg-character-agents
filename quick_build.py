"""quick_build.py — Generate a full session starter without menus.

Usage:
    python quick_build.py <game>

Games: dnd | traveller | firefly | scum | alien | deadlands

Generates without prompting:
    • 3 full characters (cinematic pre-gens for Alien)
    • 1 NPC
    • 1 location
    • 1 hook (quest giver / patron / job contact / score contact / corporate contact)
    • 2 rumors

All files land in output/ exactly where the interactive agents would put them.
"""

import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from lib.utils import run_agent_loop, strip_preamble
from agents import dnd_agent, traveller_agent, firefly_agent, scum_villainy_agent
from agents import alien_agent, deadlands_agent
from agents import location_agent, rumor_agent


# ── Config ────────────────────────────────────────────────────────────────────

VALID_GAMES = {"dnd", "traveller", "firefly", "scum", "alien", "deadlands"}

GAME_LABELS = {
    "dnd":       "D&D 5e",
    "traveller": "Mongoose Traveller 2e",
    "firefly":   "Firefly RPG",
    "scum":      "Scum and Villainy",
    "alien":     "Alien RPG",
    "deadlands": "Deadlands: The Weird West",
}

CHARACTER_AGENTS = {
    "dnd":       dnd_agent,
    "traveller": traveller_agent,
    "firefly":   firefly_agent,
    "scum":      scum_villainy_agent,
    "alien":     alien_agent,
    "deadlands": deadlands_agent,
}

# Character mode for the 3 generated characters
CHARACTER_MODES = {
    "dnd":       "full",
    "traveller": "full",
    "firefly":   "full",
    "scum":      "full",
    "alien":     "cinematic",
    "deadlands": "full",
}

# System prompt to use for the 3 generated characters
CHARACTER_SYSTEM_PROMPTS = {
    "dnd":       lambda: dnd_agent.SYSTEM_PROMPT,
    "traveller": lambda: traveller_agent.SYSTEM_PROMPT,
    "firefly":   lambda: firefly_agent.SYSTEM_PROMPT,
    "scum":      lambda: scum_villainy_agent.SYSTEM_PROMPT,
    "alien":     lambda: alien_agent.SYSTEM_PROMPT,
    "deadlands": lambda: deadlands_agent.SYSTEM_PROMPT,
}

HOOK_MODES = {
    "dnd":       "questgiver",
    "traveller": "patron",
    "firefly":   "jobcontact",
    "scum":      "scorecontact",
    "alien":     "contact",
    "deadlands": "contact",
}

HOOK_PROMPTS = {
    "questgiver":   "Generate a fully random quest giver encounter.",
    "patron":       "Generate a fully random patron encounter.",
    "jobcontact":   "Generate a fully random job contact encounter.",
    "scorecontact": "Generate a fully random score contact encounter.",
    "contact":      "Generate a fully random contact encounter.",
}


def _hook_system_prompt(game: str) -> str:
    return {
        "dnd":       dnd_agent.QUEST_GIVER_SYSTEM_PROMPT,
        "traveller": traveller_agent.PATRON_SYSTEM_PROMPT,
        "firefly":   firefly_agent.JOB_CONTACT_SYSTEM_PROMPT,
        "scum":      scum_villainy_agent.SCORE_CONTACT_SYSTEM_PROMPT,
        "alien":     alien_agent.CONTACT_SYSTEM_PROMPT,
        "deadlands": deadlands_agent.CONTACT_SYSTEM_PROMPT,
    }[game]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _step(label: str) -> None:
    print(f"\n── {label} {'─' * max(1, 46 - len(label))}")


def _character_prompts(game: str, count: int = 3) -> list[str]:
    """Return `count` character generation prompts with distinct role/archetype seeds.

    For games with archetype/role tables (alien, deadlands) we pick distinct
    entries so back-to-back generations don't converge on the same character.
    Other games get plain "fully random" prompts — the model handles variety
    through its own tool-use seeding (stat rolls, background tables, etc.).
    """
    if game == "deadlands":
        archetypes = list(deadlands_agent.ARCHETYPES.keys())
        picks = random.sample(archetypes, min(count, len(archetypes)))
        return [f"Generate a fully random character. Archetype: {a}." for a in picks]

    if game == "alien":
        roles = list(alien_agent.ROLES.keys())
        picks = random.sample(roles, min(count, len(roles)))
        return [f"Generate a fully random character. Role: {r}." for r in picks]

    return ["Generate a fully random character."] * count


def _generate_location(game: str) -> Path:
    result = run_agent_loop(
        "Generate a location for the GM.",
        location_agent.GAME_SYSTEM_PROMPTS[game],
        location_agent.GAME_TOOLS[game],
        location_agent.make_run_tool(game),
        location_agent.detect_phase,
        location_agent.PHASE_MESSAGES,
    )
    return location_agent.save_location(strip_preamble(result), game)


def _generate_rumor(game: str) -> Path:
    result = run_agent_loop(
        "Generate a rumor for the GM.",
        rumor_agent.GAME_SYSTEM_PROMPTS[game],
        rumor_agent.GAME_TOOLS[game],
        rumor_agent.make_run_tool(game),
        rumor_agent.detect_phase,
        rumor_agent.PHASE_MESSAGES,
    )
    return rumor_agent.save_rumor(strip_preamble(result), game)


# ── Session build ─────────────────────────────────────────────────────────────

def build_session(game: str) -> None:
    agent      = CHARACTER_AGENTS[game]
    char_mode  = CHARACTER_MODES[game]
    char_sysprompt = CHARACTER_SYSTEM_PROMPTS[game]()
    paths: list[Path] = []

    char_label = "cinematic pre-gen" if char_mode == "cinematic" else "character"

    print(f"\n{'═' * 50}")
    print(f"  Quick Build — {GAME_LABELS[game]}")
    print(f"  3 {char_label}s · 1 NPC · 1 location · 1 hook · 2 rumors")
    print(f"{'═' * 50}")

    # 3 characters — varied prompts so the model can't converge on the same archetype
    char_prompts = _character_prompts(game)
    for i, prompt in enumerate(char_prompts, 1):
        _step(f"{char_label.capitalize()} {i} of 3")
        result = strip_preamble(agent.run_agent(prompt, char_sysprompt))
        path = agent.save_result(result, char_mode)
        paths.append(path)
        print(f"  → {path.name}")

    # 1 NPC
    _step("NPC")
    result = strip_preamble(agent.run_agent(
        "Generate a fully random NPC.", agent.NPC_SYSTEM_PROMPT
    ))
    path = agent.save_result(result, "npc")
    paths.append(path)
    print(f"  → {path.name}")

    # 1 location
    _step("Location")
    path = _generate_location(game)
    paths.append(path)
    print(f"  → {path.name}")

    # 1 hook encounter
    hook_mode = HOOK_MODES[game]
    _step(f"Hook — {hook_mode}")
    result = strip_preamble(agent.run_agent(
        HOOK_PROMPTS[hook_mode], _hook_system_prompt(game)
    ))
    path = agent.save_result(result, hook_mode)
    paths.append(path)
    print(f"  → {path.name}")

    # 2 rumors
    for i in range(1, 3):
        _step(f"Rumor {i} of 2")
        path = _generate_rumor(game)
        paths.append(path)
        print(f"  → {path.name}")

    # Summary
    print(f"\n{'═' * 50}")
    print(f"  Done — {len(paths)} files generated")
    print(f"{'═' * 50}")
    for p in paths:
        print(f"  {p}")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in VALID_GAMES:
        print(f"\nUsage: python quick_build.py <game>")
        print(f"Games: dnd | traveller | firefly | scum | alien | deadlands\n")
        sys.exit(1)

    build_session(sys.argv[1])


if __name__ == "__main__":
    main()
