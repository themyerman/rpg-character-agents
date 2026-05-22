"""
NPC Cluster Generator
Generates a group of connected NPCs for any supported game system,
then synthesizes a web of connections and GM hooks.

Run with: python npc_cluster_agent.py
Or invoked from main.py.
"""

import re
from pathlib import Path

import dnd_agent
import firefly_agent
import scum_villainy_agent
import traveller_agent
from utils import get_client, pick, run_agent_loop, strip_preamble


# ── Game registry ──────────────────────────────────────────────────────────────

GAME_AGENTS: dict[str, dict] = {
    "dnd": {
        "tools":       dnd_agent.TOOLS,
        "run_tool":    dnd_agent.run_tool,
        "npc_prompt":  dnd_agent.NPC_SYSTEM_PROMPT,
        "label":       "D&D 5e",
        "save_subdir": "dnd",
    },
    "traveller": {
        "tools":       traveller_agent.TOOLS,
        "run_tool":    traveller_agent.run_tool,
        "npc_prompt":  traveller_agent.NPC_SYSTEM_PROMPT,
        "label":       "Mongoose Traveller 2e",
        "save_subdir": "traveller",
    },
    "firefly": {
        "tools":       firefly_agent.TOOLS,
        "run_tool":    firefly_agent.run_tool,
        "npc_prompt":  firefly_agent.NPC_SYSTEM_PROMPT,
        "label":       "Firefly RPG",
        "save_subdir": "firefly",
    },
    "scum": {
        "tools":       scum_villainy_agent.TOOLS,
        "run_tool":    scum_villainy_agent.run_tool,
        "npc_prompt":  scum_villainy_agent.NPC_SYSTEM_PROMPT,
        "label":       "Scum and Villainy",
        "save_subdir": "scum_villainy",
    },
}


RELATIONSHIP_TYPES: list[tuple[str, str]] = [
    ("team",        "Team / Allies — working toward a shared goal"),
    ("rivals",      "Rivals — competing, with history between them"),
    ("family",      "Family — blood or chosen, with all the weight that carries"),
    ("complicated", "Complicated History — used to be something else, now it's this"),
    ("old_crew",    "Old Crew — they've worked together before; not everyone left clean"),
    ("strangers",   "Strangers with a Shared Secret — don't know each other yet, but they will"),
]


# ── NPC generation ─────────────────────────────────────────────────────────────

def generate_npc(game: str, relationship: str, context_hint: str,
                 modifier: str, index: int) -> str:
    """Generate one NPC silently (no phase printing) using the game's NPC prompt."""
    config    = GAME_AGENTS[game]
    rel_label = dict(RELATIONSHIP_TYPES).get(relationship, relationship)

    parts = [
        f"Generate a {config['label']} NPC.",
        f"This NPC is part of a group whose relationship is: {rel_label}.",
        f"Shared context: {context_hint}" if context_hint else "",
        f"Overall group direction: {modifier}" if modifier else "",
        f"This is NPC #{index} of the cluster — make them distinct from the others.",
        "Keep names culturally diverse and distinct from each other.",
    ]
    prompt = " ".join(p for p in parts if p)

    raw = run_agent_loop(
        prompt,
        config["npc_prompt"],
        config["tools"],
        config["run_tool"],
        max_tokens=2048,
    )
    return strip_preamble(raw)


# ── Synthesis call (no tools) ──────────────────────────────────────────────────

_SYNTHESIS_SYSTEM = """You are a narrative designer synthesizing a cluster of NPCs into a coherent ensemble.

You will receive several individual NPC sketches. Your job is to:
1. Write a short title and one-line description for the group as a whole.
2. Map the relationships between them — one sentence per pair, specific and evocative.
3. Provide exactly three GM hooks: concrete situations that would pull player characters into this group's orbit.

Output exactly this format — nothing else:

# [Evocative Group Title]: [Game Label] — [Relationship Type]
*[One-sentence description of what binds or divides them]*

## Web of Connections
- **[Name A] / [Name B]:** [One sentence about their relationship — specific, with texture]
(one bullet per pair)

## GM Hooks
1. [Concrete hook — a situation, not a vague summary]
2. [Concrete hook]
3. [Concrete hook]"""


def synthesize_cluster(npcs: list[str], game: str, relationship: str) -> str:
    """One no-tools call to produce a group title, connection web, and GM hooks."""
    rel_label = dict(RELATIONSHIP_TYPES).get(relationship, relationship)
    label     = GAME_AGENTS[game]["label"]
    npc_block = "\n\n---\n\n".join(npcs)

    response = get_client().messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=_SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": (
            f"Game: {label}\n"
            f"Relationship type: {rel_label}\n\n"
            f"NPC sketches:\n\n{npc_block}"
        )}],
    )
    for block in response.content:
        if hasattr(block, "text"):
            return block.text.strip()
    return ""


# ── Save ───────────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _extract_name(npc_text: str) -> str:
    """Pull the character name from the first ## heading."""
    for line in npc_text.splitlines():
        if line.startswith("##"):
            return re.sub(r"[#*]", "", line).strip()
    return "Unknown"


def _strip_heading(npc_text: str) -> str:
    """Remove the first ## heading line, keeping everything below it."""
    lines = npc_text.strip().splitlines()
    start = next((i + 1 for i, l in enumerate(lines) if l.startswith("##")), 0)
    return "\n".join(lines[start:]).strip()


def save_cluster(synthesis: str, npcs: list[str], game: str, relationship: str) -> Path:
    """
    Assemble and save the full cluster document.

    Filename: output/parties/{game_subdir}/{relationship}-{title_slug}-party.md
    Title slug comes from the synthesis header, before the first colon.
    """
    first_line = synthesis.strip().splitlines()[0]
    title_text = re.sub(r"^#+\s*", "", first_line).strip()
    title_slug = _slug(title_text.split(":")[0])
    filename   = f"{relationship}-{title_slug}-party.md"

    subdir     = GAME_AGENTS[game]["save_subdir"]
    output_dir = Path(__file__).parent / "output" / subdir / "clusters"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    if filepath.exists():
        stem    = filepath.stem
        counter = 2
        while filepath.exists():
            filepath = output_dir / f"{stem}-{counter}.md"
            counter  += 1

    # Build document: synthesis preamble + individual NPC blocks + connection web + hooks
    synth_lines = synthesis.strip().splitlines()
    web_start   = next(
        (i for i, l in enumerate(synth_lines) if l.startswith("## Web")),
        len(synth_lines),
    )
    pre_web  = "\n".join(synth_lines[:web_start]).strip()
    post_web = "\n".join(synth_lines[web_start:]).strip()

    divider   = "\n\n---\n\n"
    npc_block = divider.join(
        f"## **{_extract_name(npc)}**\n{_strip_heading(npc)}" for npc in npcs
    )
    content = f"{pre_web}\n\n---\n\n{npc_block}\n\n---\n\n{post_web}\n"

    filepath.write_text(content)
    return filepath


# ── Entry point ────────────────────────────────────────────────────────────────

def run(game: str | None = None, relationship: str | None = None,
        count: int | None = None, context_hint: str = "") -> None:

    if game is None:
        game = pick(
            "Which game system?",
            [(k, v["label"]) for k, v in GAME_AGENTS.items()],
        )

    if relationship is None:
        relationship = pick("What is their relationship?", RELATIONSHIP_TYPES)

    if count is None:
        raw = input("How many NPCs in this cluster? (2–6, default: 3): ").strip()
        try:
            count = max(2, min(6, int(raw)))
        except ValueError:
            count = 3

    if not context_hint:
        context_hint = input(
            "Shared context for the cluster? "
            "(e.g. 'post-war veterans on a mining station', or press Enter to skip): "
        ).strip()

    modifier = input(
        "Any overall direction for the group? "
        "(e.g. 'all hiding something', 'one of them is lying', or press Enter to skip): "
    ).strip()

    rel_label = dict(RELATIONSHIP_TYPES).get(relationship, relationship)
    label     = GAME_AGENTS[game]["label"]

    print(f"\nGenerating {count} {label} NPCs ({rel_label})...\n")

    npcs: list[str] = []
    for i in range(1, count + 1):
        print(f"  [{i}/{count}] Generating NPC...")
        npc = generate_npc(game, relationship, context_hint, modifier, i)
        npcs.append(npc)
        print(f"    ✓ {_extract_name(npc)}")

    print("\nSynthesizing connection web and GM hooks...")
    synthesis = synthesize_cluster(npcs, game, relationship)

    filepath = save_cluster(synthesis, npcs, game, relationship)
    print(f"\nSaved → {filepath.relative_to(Path(__file__).parent)}\n")


if __name__ == "__main__":
    run()
