"""
Tabletop Party Generator — GM Prep Tool
Assembles a party or crew from saved characters, generates fresh ones, or mixes both.

Run with: python party_agent.py
"""

import random
import re
from pathlib import Path
import anthropic

client = anthropic.Anthropic()


# ── Folder locations ────────────────────────────────────────────────────────────

FOLDERS = {
    "dnd":       Path(__file__).parent / "dnd_characters",
    "traveller": Path(__file__).parent / "traveller_characters",
    "firefly":   Path(__file__).parent / "firefly_characters",
    "scum":      Path(__file__).parent / "scum_villainy_characters",
}

PARTIES_DIR = Path(__file__).parent / "parties"


# ── Character file discovery ────────────────────────────────────────────────────

def list_characters(game: str) -> list[tuple[int, str, Path]]:
    """Return numbered list of full/npc character files for the given game."""
    folder = FOLDERS.get(game)
    if folder is None or not folder.exists():
        return []
    files = sorted([
        f for f in folder.glob("*.md")
        if f.stem.endswith(("-full", "-npc"))
    ])
    return [(i + 1, f.stem, f) for i, f in enumerate(files)]


def pick_characters(chars: list[tuple[int, str, Path]], count: int) -> list[Path]:
    """Show numbered list, return selected paths."""
    print("\nAvailable characters:")
    for num, name, _ in chars:
        label = name.replace("-", " ").replace(" full", "").replace(" npc", " (NPC)")
        print(f"  {num}. {label}")
    raw = input(f"\nPick by number (e.g. '1 3'), or press Enter to use the first {count}: ").strip()
    if not raw:
        return [p for _, _, p in chars[:count]]
    try:
        indices = [int(x) - 1 for x in raw.split()]
        return [chars[i][2] for i in indices if 0 <= i < len(chars)]
    except ValueError:
        print("Couldn't parse — using first characters.")
        return [p for _, _, p in chars[:count]]


# ── Dice tools (for fresh character sketches) ───────────────────────────────────

def roll_stat_dnd() -> str:
    rolls = [random.randint(1, 6) for _ in range(4)]
    kept  = sorted(rolls, reverse=True)[:3]
    return f"Rolled 4d6: {sorted(rolls)} → kept {kept} → score: {sum(kept)}"

def roll_dice_dnd(sides: int, count: int = 1) -> str:
    valid = {4, 6, 8, 10, 12, 20}
    if sides not in valid:
        return f"Error: {sides} is not a valid D&D die."
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"

def roll_dice_traveller(sides: int, count: int = 1) -> str:
    if sides != 6:
        return "Error: Traveller only uses d6."
    rolls = [random.randint(1, 6) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"


FIREFLY_CREW_PROMPT = """You are a Firefly RPG crew builder and GM prep tool (Cortex System).

You will receive one or more existing character sheets, and possibly an instruction to generate additional crew members to fill out the crew. If generating fresh crew, invent a name, role (Captain/Pilot/First Mate/Mechanic/Doctor/Shepherd/Muscle/Grifter/Thief), homeworld, war history, and one-sentence hook for each — make them fill gaps in the crew's roles and dynamics.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Do not output any intermediate notes or working text. Output only the formatted crew brief, starting directly with the ## heading.

Produce the crew brief in exactly this format:

## [Ship Name] — Crew Brief
*[Ship type] — [one evocative phrase about the ship or this crew's reputation in the 'Verse]*

| | |
|---|---|
| **Ship** | [Name] ([type: Firefly-class / Tohoku-class / Pelican-class / etc.]) |
| **Condition** | [one phrase — beat to hell but flying, freshly stolen, running on hope and baling wire, etc.] |
| **What It Owes** | [debt, obligation, or complication — financial, legal, or moral] |

### Crew
- **[Name]** — [Role] — [their function in the group dynamic, one sentence]
[repeat for each member]

### How They Came Together
[2–3 paragraphs. Specific — who recruited whom, what the circumstances were, what it cost to get this far. Reference specific backstory details from the sheets.]

### What Holds Them Together
[One paragraph. The practical reason this crew is still flying — shared debt, shared ship, shared enemy, or the uncomfortable fact that they're all each other has out here.]

### The Fault Line
[One paragraph. The specific tension between specific crew members that will eventually cause a crisis. Name names, name the issue. The 'Verse is hard on cracks.]

### Shared Secret
[One paragraph. Something the crew knows collectively but doesn't discuss. Connected to at least one member's war history or backstory.]

### First Session Hook
[One paragraph. A specific situation to open with — a job gone sideways, a face from someone's past at the wrong port, a ship that shouldn't be where it is. Pull on at least two crew members' specific backstory threads.]"""


SCUM_CREW_PROMPT = """You are a Scum and Villainy crew builder and GM prep tool (Forged in the Dark).

You will receive one or more existing character sheets, and possibly an instruction to generate additional crew members to fill out the crew. If generating fresh crew, invent a name, playbook (Muscle/Pilot/Scoundrel/Mystic/Speaker/Stitch), heritage, background, and one-sentence hook for each — make them fill gaps in the crew's capabilities and create interesting friction.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Do not output any intermediate notes or working text. Output only the formatted crew brief, starting directly with the ## heading.

Produce the crew brief in exactly this format:

## [Ship Name] — Crew Brief
*[Crew type: Assassins / Bounty Hunters / Criminals / Heist Crew / Rebels / Smugglers] — [one phrase about their reputation or situation]*

| | |
|---|---|
| **Ship** | [Name] ([class]) |
| **Crew Type** | [Assassins / Bounty Hunters / Criminals / Heist Crew / Rebels / Smugglers] |
| **Rep** | [0–3 — their current reputation in the underworld] |
| **Heat** | [0–3 — how much Hegemony attention they're drawing] |
| **What It Owes** | [debt, obligation, or complication hanging over the crew] |

### Crew
- **[Name]** — [Playbook] — [their role in the crew dynamic, one sentence]
[repeat for each member]

### How They Came Together
[2–3 paragraphs. Specific — who pulled who in, what the first score was, what it cost. Reference specific character details from the sheets.]

### What Holds Them Together
[One paragraph. The practical reason this crew is still working together — shared heat, shared debt, shared score that went wrong, or the fact that the Hegemony is looking for all of them.]

### The Fault Line
[One paragraph. The specific tension between specific crew members. Name playbooks, name the issue. Forged in the Dark characters are always one bad score from falling apart.]

### Shared Secret
[One paragraph. Something the whole crew knows but doesn't discuss — connected to at least one character's background or vice.]

### First Score Hook
[One paragraph. A specific job to open with — a target, a contact with an offer, a rival crew stepping on their territory. Pull on at least two characters' specific backstory threads. Leave the complications for the table to discover.]"""


DND_TOOLS = [
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

TRAVELLER_TOOLS = [
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


def run_tool_dnd(name: str, inputs: dict) -> str:
    if name == "roll_stat": return roll_stat_dnd()
    if name == "roll_dice": return roll_dice_dnd(**inputs)
    return f"Unknown tool: {name}"

def run_tool_traveller(name: str, inputs: dict) -> str:
    if name == "roll_dice": return roll_dice_traveller(**inputs)
    return f"Unknown tool: {name}"


# ── System prompts ──────────────────────────────────────────────────────────────

DND_PARTY_PROMPT = """You are a D&D 5e party builder and GM prep tool.

You will receive one or more existing character sheets, and possibly an instruction to generate additional characters to fill out the party. If generating fresh characters, use roll_stat to generate ability scores, then invent a name, race, class, and one-sentence hook for each — make them complement the existing characters in role and personality.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Do not output any intermediate notes, stat summaries, or working text. Output only the formatted party brief, starting directly with the ## heading.

Produce the party brief in exactly this format:

## [Party Name — something the characters might actually call themselves, or leave unnamed if nothing fits]

### Members
- **[Name]** — [Race/Class] — [their role in the group dynamic, not their backstory — one sentence]
[repeat for each member]

### How They Met
[2–3 paragraphs. A specific inciting incident — not "they met in a tavern" but what actually happened, who was there, what it cost someone. Reference specific details from the character sheets.]

### What Holds Them Together
[One paragraph. The practical or emotional reason they haven't gone their separate ways — shared debt, shared enemy, shared goal, or simple necessity.]

### The Fault Line
[One paragraph. The specific tension between specific characters that will eventually cause a crisis. Name the characters, name the disagreement. Not vague.]

### Shared Secret
[One paragraph. Something all party members know but don't talk about. Connected to at least one character's backstory.]

### First Session Hook
[One paragraph. A concrete situation to open with — a job, a threat, a face from someone's past showing up. Pull on at least two characters' specific backstory threads. Leave it unresolved — the GM takes it from here.]"""


TRAVELLER_CREW_PROMPT = """You are a Mongoose Traveller 2e crew builder and GM prep tool.

You will receive one or more existing character sheets, and possibly an instruction to generate additional crew members to fill out the crew. If generating fresh crew, use roll_dice (2d6 six times) to generate characteristics, then invent a name, career, and one-sentence hook for each — make them fill practical gaps in the crew's capabilities.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Do not output any intermediate notes, stat summaries, or working text. Output only the formatted crew brief, starting directly with the ## heading.

Produce the crew brief in exactly this format:

## [Ship Name] — Crew Brief
*[Ship class] — [one evocative phrase about the ship's condition or reputation]*

| | |
|---|---|
| **Ship** | [Name] ([class: Type-A Free Trader / Scout/Courier / Far Trader / etc.]) |
| **Condition** | [one phrase — worn but spaceworthy, freshly refitted, one jump from the breakers, etc.] |
| **What It Owes** | [the ship's debt, obligation, or complication — financial, legal, or moral] |

### Crew
- **[Name]** — [Role: Pilot / Astrogator / Engineer / Medic / Gunner / Broker / etc.] — [one sentence]
[repeat for each member]

### How They Came Together
[2–3 paragraphs. Specific — who brought who in, what the circumstances were, what it cost to get this far. Reference specific backstory details from the sheets.]

### What Holds Them Together
[One paragraph. The practical reason this crew is still together — shared debt, ship mortgage, shared enemy, or simple lack of better options.]

### The Fault Line
[One paragraph. The specific tension between specific crew members that will eventually cause a crisis. Name names, name the issue.]

### Shared Secret
[One paragraph. Something the crew knows collectively but doesn't discuss. Connected to at least one member's backstory.]

### First Session Hook
[One paragraph. A specific situation to open with — a job on offer, a complication with the ship, a face from someone's past showing up at the wrong port. Pull on at least two crew members' specific backstory threads.]"""


# ── Agent functions ─────────────────────────────────────────────────────────────

def synthesize(prompt: str, system_prompt: str) -> str:
    """Single-call synthesis — used when all characters are from the folder."""
    print("\nBuilding party brief...")
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def run_agent(prompt: str, system_prompt: str, tools: list, run_tool_fn) -> str:
    """Agentic loop — used when fresh characters need to be generated."""
    print("\nGenerating fresh characters and building party brief...")
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool_fn(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})


# ── Prompt builder ─────────────────────────────────────────────────────────────

def build_prompt(sheets: list[str], fresh_count: int, party_size: int,
                 label: str, theme: str = "") -> str:
    """Assemble the generation prompt from existing sheets, fresh count, and optional theme."""
    parts = []
    if sheets:
        parts.append(f"Here {'is' if len(sheets) == 1 else 'are'} {len(sheets)} character sheet(s) to build the {label} around:\n\n")
        for i, sheet in enumerate(sheets, 1):
            parts.append(f"--- CHARACTER {i} ---\n{sheet}\n\n")
    if fresh_count:
        parts.append(f"Generate {fresh_count} additional character sketch(es) to complete a {label} of {party_size}, then synthesize all into the party brief.")
    if theme:
        parts.append(f"\n\nTheme / constraints from the GM: {theme}")
    return "".join(parts)


# ── Save ────────────────────────────────────────────────────────────────────────

def save_result(result: str, game: str, suffix: str = "party") -> Path:
    # Find the first markdown heading line (## ...) for the filename
    heading = next(
        (line for line in result.strip().splitlines() if line.startswith("##")),
        result.strip().splitlines()[0],
    )
    name_raw  = re.sub(r"[#*]", "", heading).strip()
    name_slug = re.sub(r"[^a-z0-9]+", "-", name_raw.lower()).strip("-")
    filename  = f"{game}-{name_slug}-{suffix}.md"
    PARTIES_DIR.mkdir(exist_ok=True)
    filepath = PARTIES_DIR / filename
    filepath.write_text(result)
    return filepath


# ── Entry point ─────────────────────────────────────────────────────────────────

def run() -> None:

    # 1. Game
    game_raw = input("Game? (dnd / traveller / firefly / scum, default: traveller): ").strip().lower()
    game     = game_raw if game_raw in ("dnd", "traveller", "firefly", "scum") else "traveller"
    label    = "party" if game == "dnd" else "crew"

    # 2. Party size
    size_raw = input(f"How many in the {label}? (default: 4): ").strip()
    try:
        party_size = int(size_raw) if size_raw else 4
        party_size = max(2, min(6, party_size))
    except ValueError:
        party_size = 4

    # 3. Mode
    print(f"\nMode?")
    print(f"  folder   — build from saved characters")
    print(f"  generate — generate a fresh {label}")
    print(f"  mix      — some from folder, some generated fresh")
    mode_raw = input("Mode (default: folder): ").strip().lower()
    mode     = mode_raw if mode_raw in ("folder", "generate", "mix") else "folder"

    # 4. Gather characters
    sheets      = []
    fresh_count = 0
    chars       = list_characters(game)

    if mode == "folder":
        if not chars:
            print(f"\nNo characters found in {FOLDERS[game]}. Switching to generate mode.")
            mode        = "generate"
            fresh_count = party_size
        else:
            picked      = pick_characters(chars, party_size)
            sheets      = [p.read_text() for p in picked]
            fresh_count = max(0, party_size - len(sheets))
            if fresh_count:
                print(f"\nOnly {len(sheets)} selected — will generate {fresh_count} fresh to fill the {label}.")

    elif mode == "generate":
        fresh_count = party_size

    elif mode == "mix":
        if not chars:
            print(f"\nNo saved characters found. Generating all {party_size} fresh.")
            fresh_count = party_size
        else:
            try:
                n_raw       = input(f"How many from folder? (rest generated fresh, total {party_size}): ").strip()
                from_folder = int(n_raw) if n_raw else party_size // 2
                from_folder = max(1, min(party_size - 1, from_folder))
            except ValueError:
                from_folder = party_size // 2
            picked      = pick_characters(chars, from_folder)
            sheets      = [p.read_text() for p in picked]
            fresh_count = party_size - len(sheets)
            if fresh_count:
                print(f"\nUsing {len(sheets)} from folder, generating {fresh_count} fresh.")

    # 5. Theme / constraints
    theme = input(f"\nAny themes, constraints, or specifics? (e.g. 'gothic horror, vampire hunters' or press Enter for fully random): ").strip()

    # 6. Build prompt
    prompt = build_prompt(sheets, fresh_count, party_size, label, theme)

    # 7. Run
    system_prompt = {
        "dnd":       DND_PARTY_PROMPT,
        "traveller": TRAVELLER_CREW_PROMPT,
        "firefly":   FIREFLY_CREW_PROMPT,
        "scum":      SCUM_CREW_PROMPT,
    }[game]

    if fresh_count > 0:
        tools       = DND_TOOLS if game == "dnd" else TRAVELLER_TOOLS
        run_tool_fn = run_tool_dnd if game == "dnd" else run_tool_traveller
        # Firefly and Scum use a simple single-call synthesis even with fresh chars
        # (their character sketches don't require dice rolling in the party context)
        if game in ("firefly", "scum"):
            result = synthesize(prompt, system_prompt)
        else:
            result = run_agent(prompt, system_prompt, tools, run_tool_fn)
    else:
        result = synthesize(prompt, system_prompt)

    # Strip any preamble before the first ## heading
    lines = result.strip().splitlines()
    heading_idx = next((i for i, l in enumerate(lines) if l.startswith("##")), 0)
    result = "\n".join(lines[heading_idx:])

    print("\n" + result)

    saved = save_result(result, game)
    print(f"\n[saved → {saved}]")

    # 8. Optional hook
    HOOK_TYPES = {
        "dnd":       "quest giver",
        "traveller": "patron",
        "firefly":   "job contact",
        "scum":      "score contact",
    }
    hook_type = HOOK_TYPES[game]
    hook_raw  = input(f"\nGenerate an opening {hook_type} hook tailored to this {label}? (yes / no, default: no): ").strip().lower()

    if hook_raw in ("yes", "y"):
        if game == "dnd":
            from dnd_agent import (
                QUEST_GIVER_SYSTEM_PROMPT,
                TOOLS as HOOK_TOOLS,
                run_tool as hook_run_tool,
            )
            hook_prompt = (
                f"Generate a D&D 5e quest giver encounter tailored specifically to this party. "
                f"The hook should connect to their fault line, their shared secret, or a specific character's backstory thread. "
                f"Here is the party brief:\n\n{result}"
            )
            print(f"\nGenerating {hook_type} hook...")
            hook_result = run_agent(hook_prompt, QUEST_GIVER_SYSTEM_PROMPT, HOOK_TOOLS, hook_run_tool)

        elif game == "traveller":
            from traveller_agent import (
                PATRON_SYSTEM_PROMPT as HOOK_SYSTEM,
                TOOLS as HOOK_TOOLS,
                run_tool as hook_run_tool,
            )
            hook_prompt = (
                f"Generate a Mongoose Traveller patron encounter tailored specifically to this crew. "
                f"The job should connect to their fault line, their shared secret, or a specific crew member's backstory thread. "
                f"Here is the crew brief:\n\n{result}"
            )
            print(f"\nGenerating {hook_type} hook...")
            hook_result = run_agent(hook_prompt, HOOK_SYSTEM, HOOK_TOOLS, hook_run_tool)

        elif game == "firefly":
            from firefly_agent import JOB_CONTACT_SYSTEM_PROMPT as HOOK_SYSTEM
            hook_prompt = (
                f"Generate a Firefly RPG job contact tailored specifically to this crew. "
                f"The job should connect to their fault line, their shared secret, or a specific crew member's backstory thread. "
                f"Here is the crew brief:\n\n{result}"
            )
            print(f"\nGenerating {hook_type} hook...")
            hook_result = synthesize(hook_prompt, HOOK_SYSTEM)

        elif game == "scum":
            from scum_villainy_agent import SCORE_CONTACT_SYSTEM_PROMPT as HOOK_SYSTEM
            hook_prompt = (
                f"Generate a Scum and Villainy score contact tailored specifically to this crew. "
                f"The score should connect to their fault line, their shared secret, or a specific crew member's backstory thread. "
                f"Here is the crew brief:\n\n{result}"
            )
            print(f"\nGenerating {hook_type} hook...")
            hook_result = synthesize(hook_prompt, HOOK_SYSTEM)

        print("\n" + hook_result)

        # Save hook to the appropriate characters folder
        first_line  = next(
            (l for l in hook_result.strip().splitlines() if l.startswith("##")),
            hook_result.strip().splitlines()[0],
        )
        name_raw    = re.sub(r"[#*]", "", first_line).strip()
        hook_slug   = re.sub(r"[^a-z0-9]+", "-", name_raw.lower()).strip("-")
        hook_suffix = {"dnd": "questgiver", "traveller": "patron",
                       "firefly": "jobcontact", "scum": "scorecontact"}[game]
        hook_path   = FOLDERS[game] / f"{hook_slug}-{hook_suffix}.md"
        hook_path.write_text(hook_result)
        print(f"[saved → {hook_path}]")


if __name__ == "__main__":
    run()
