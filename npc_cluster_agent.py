"""
NPC Cluster Generator
Generates a group of connected NPCs for any supported game system,
then synthesizes a web of connections and GM hooks.

Run with: python npc_cluster_agent.py
Or invoked from main.py.
"""

import re
from pathlib import Path

import anthropic

import dnd_agent
import firefly_agent
import scum_villainy_agent
import traveller_agent
from utils import pick

client = anthropic.Anthropic()


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


# ── NPC generation loop (with tools) ──────────────────────────────────────────

def _run_npc_agent(prompt: str, system: str, tools: list, tool_runner) -> str:
    """Generic agentic loop for a single NPC — no phase printing."""
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            system=system,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = tool_runner(block.name, block.input)
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result,
                    })
            messages.append({"role": "user", "content": tool_results})


def _strip_preamble(text: str) -> str:
    """Remove any introductory text before the first ## heading."""
    lines = text.strip().splitlines()
    idx   = next((i for i, l in enumerate(lines) if l.startswith("##")), 0)
    return "\n".join(lines[idx:])


def generate_npc(game: str, relationship: str, context_hint: str, desc: str, index: int) -> str:
    """Generate one NPC using the game's NPC system prompt and tools."""
    config = GAME_AGENTS[game]
    label  = config["label"]
    rel_label = dict(RELATIONSHIP_TYPES).get(relationship, relationship)

    prompt_parts = [
        f"Generate a {label} NPC.",
        f"This NPC is part of a group whose relationship is: {rel_label}.",
        f"Context for this cluster: {context_hint}" if context_hint else "",
        f"NPC #{index} specific direction: {desc}" if desc else f"NPC #{index}: fully random.",
        "Keep names culturally diverse and distinct from each other.",
    ]
    prompt = " ".join(p for p in prompt_parts if p)

    raw    = _run_npc_agent(prompt, config["npc_prompt"], config["tools"], config["run_tool"])
    return _strip_preamble(raw)


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
    """One no-tools call to produce a title, connection web, and GM hooks."""
    rel_label = dict(RELATIONSHIP_TYPES).get(relationship, relationship)
    label     = GAME_AGENTS[game]["label"]

    npc_block = "\n\n---\n\n".join(npcs)
    user_msg  = (
        f"Game: {label}\n"
        f"Relationship type: {rel_label}\n\n"
        f"NPC sketches:\n\n{npc_block}"
    )

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=_SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    for block in response.content:
        if hasattr(block, "text"):
            return block.text.strip()
    return ""


# ── Save ───────────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def save_cluster(synthesis: str, npcs: list[str], game: str, relationship: str) -> Path:
    """
    Assemble and save the full cluster document.

    Filename: parties/{game}-npc-{relationship}-{title_slug}-party.md
    The title slug is extracted from the synthesis header (before the colon).
    """
    # Extract title from first line of synthesis: "# Title: ..."
    first_line = synthesis.strip().splitlines()[0]
    title_text = re.sub(r"^#+\s*", "", first_line).strip()
    title_slug = _slug(title_text.split(":")[0])

    filename = f"{game}-npc-{relationship}-{title_slug}-party.md"

    output_dir = Path(__file__).parent / "parties"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    if filepath.exists():
        stem    = filepath.stem
        counter = 2
        while filepath.exists():
            filepath = output_dir / f"{stem}-{counter}.md"
            counter  += 1

    # Assemble document: synthesis header + individual NPC blocks
    divider   = "\n\n---\n\n"
    npc_block = divider.join(f"## **{_extract_name(npc)}**\n" + _strip_heading(npc) for npc in npcs)

    # synthesis already has # title + connection web + hooks
    # insert the NPC bodies between the title block and the connection web
    synth_lines = synthesis.strip().splitlines()
    web_start   = next(
        (i for i, l in enumerate(synth_lines) if l.startswith("## Web")),
        len(synth_lines),
    )
    pre_web  = "\n".join(synth_lines[:web_start]).strip()
    post_web = "\n".join(synth_lines[web_start:]).strip()

    content = f"{pre_web}\n\n---\n\n{npc_block}\n\n---\n\n{post_web}\n"

    filepath.write_text(content)
    return filepath


def _extract_name(npc_text: str) -> str:
    """Pull the character name from the ## heading line."""
    for line in npc_text.splitlines():
        if line.startswith("##"):
            return re.sub(r"[#*]", "", line).strip()
    return "Unknown"


def _strip_heading(npc_text: str) -> str:
    """Remove the first ## heading line so we don't double-print it."""
    lines = npc_text.strip().splitlines()
    start = next((i + 1 for i, l in enumerate(lines) if l.startswith("##")), 0)
    return "\n".join(lines[start:]).strip()


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
            "Any shared context for the cluster? (e.g. 'post-war veterans', 'heist crew', or press Enter): "
        ).strip()

    rel_label = dict(RELATIONSHIP_TYPES).get(relationship, relationship)
    label     = GAME_AGENTS[game]["label"]

    print(f"\nGenerating {count} {label} NPCs ({rel_label})...\n")

    npcs: list[str] = []
    for i in range(1, count + 1):
        print(f"  [{i}/{count}] Generating NPC...")
        desc = input(f"    Direction for NPC {i} (or press Enter for random): ").strip()
        npc  = generate_npc(game, relationship, context_hint, desc, i)
        npcs.append(npc)
        print(f"    ✓ {_extract_name(npc)}")

    print("\nSynthesizing connection web and GM hooks...")
    synthesis = synthesize_cluster(npcs, game, relationship)

    filepath = save_cluster(synthesis, npcs, game, relationship)
    print(f"\nSaved → {filepath.relative_to(Path(__file__).parent)}\n")


if __name__ == "__main__":
    run()
