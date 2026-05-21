"""
Firefly RPG Character Generator (Cortex System)
Creates vivid storytelling characters for the Firefly 'Verse.

Run with: python firefly_agent.py
"""

import json
import random
import re
from pathlib import Path
import anthropic

client = anthropic.Anthropic()


# ── Constants ───────────────────────────────────────────────────────────────────

VALID_DICE_SIZES = {4, 6, 8, 10, 12}
CORTEX_LADDER    = [4, 6, 8, 10, 12]  # d4 → d12, worst to best


# ── Roles ───────────────────────────────────────────────────────────────────────

ROLES = {
    "Captain": {
        "description": "Leads the crew, makes the hard calls, usually the one who got everyone into this mess",
        "key_attributes": ["Willpower", "Alertness"],
        "key_skills":     ["Influence", "Discipline", "Perception"],
        "flavor":         "carries the weight, carries the guilt, keeps flying anyway",
        "distinction_seeds": ["Takes Responsibility", "Has a Code", "Earned Loyalty"],
    },
    "Pilot": {
        "description": "Flies the ship and everything else — boats, mules, shuttles, things that shouldn't fly",
        "key_attributes": ["Agility", "Alertness"],
        "key_skills":     ["Pilot", "Perception", "Mechanist"],
        "flavor":         "reads the black like weather, trusts the ship more than most people",
        "distinction_seeds": ["Born to Fly", "Talks to the Ship", "Never Lost a Passenger"],
    },
    "First Mate": {
        "description": "Keeps the crew together when the captain can't, the one everyone actually listens to",
        "key_attributes": ["Willpower", "Strength"],
        "key_skills":     ["Discipline", "Influence", "Unarmed Combat"],
        "flavor":         "the glue, the enforcer, the one who knows where the bodies are",
        "distinction_seeds": ["Gets Things Done", "Loyal to the End", "Harder Than They Look"],
    },
    "Mechanic": {
        "description": "Keeps the ship flying through miracles, duct tape, and sheer stubbornness",
        "key_attributes": ["Intelligence", "Agility"],
        "key_skills":     ["Mechanist", "Perception", "Craft"],
        "flavor":         "talks to engines the way other people talk to pets — and they answer",
        "distinction_seeds": ["The Ship Talks to Me", "Jury-Rigged and Proud", "Grew Up in the Guts of Things"],
    },
    "Doctor": {
        "description": "Keeps the crew alive against increasingly creative attempts on their lives",
        "key_attributes": ["Intelligence", "Alertness"],
        "key_skills":     ["Medical Expertise", "Knowledge", "Influence"],
        "flavor":         "trained for a world that no longer quite applies, adapting in real time",
        "distinction_seeds": ["First Do No Harm", "Seen Too Much", "Won't Leave Anyone Behind"],
    },
    "Shepherd": {
        "description": "A preacher, a wanderer, a person of faith — possibly also something else entirely",
        "key_attributes": ["Willpower", "Alertness"],
        "key_skills":     ["Discipline", "Influence", "Perception"],
        "flavor":         "more complicated than they appear, which is saying something",
        "distinction_seeds": ["Man of Faith", "Seen Both Sides", "Knows How to Handle a Gun for a Preacher"],
    },
    "Muscle": {
        "description": "The one you point at problems that need hitting — professional, reliable, expensive",
        "key_attributes": ["Strength", "Vitality"],
        "key_skills":     ["Unarmed Combat", "Firearms", "Athletics"],
        "flavor":         "doesn't start fights, finishes them — distinction matters",
        "distinction_seeds": ["Professional", "Has a Line They Won't Cross", "Loyal to Whoever's Paying"],
    },
    "Grifter": {
        "description": "Con artist, face, negotiator — the one who talks their way in and out of everything",
        "key_attributes": ["Alertness", "Intelligence"],
        "key_skills":     ["Influence", "Performance", "Covert"],
        "flavor":         "everybody's friend and nobody's ally, except when it counts",
        "distinction_seeds": ["Too Pretty to Shoot", "Always an Angle", "The Honest Liar"],
    },
    "Thief": {
        "description": "Gets in, gets what's needed, gets out — sometimes in that order",
        "key_attributes": ["Agility", "Alertness"],
        "key_skills":     ["Covert", "Athletics", "Perception"],
        "flavor":         "quiet hands, loud conscience",
        "distinction_seeds": ["Leaves No Trace", "Only Steals from People Who Deserve It", "Knows Every Lock"],
    },
}


# ── 'Verse locations ────────────────────────────────────────────────────────────

VERSE_LOCATIONS = {
    "Core": {
        "worlds":      ["Londinium", "Sihnon", "Ariel", "Osiris", "Bernadette", "Liann Jiun"],
        "flavor":      "Alliance heartland — wealth, surveillance, medicine, comfort, and control",
        "background":  "grew up with Alliance propaganda in the schools and food that didn't come in tins",
    },
    "Border": {
        "worlds":      ["Persephone", "Whittier", "Beaumonde", "Constance", "Pelorum", "Santo"],
        "flavor":      "where the Alliance and the frontier meet — trade, crime, and a bit of both",
        "background":  "grew up knowing how to read a room and which side of a deal to stand on",
    },
    "Rim": {
        "worlds":      ["Whitefall", "Jiangyin", "Triumph", "Athens", "Hera", "Shadow", "Harvest", "Persephone's moon Eavesdown"],
        "flavor":      "hard living, hard people, the war hit hardest here and never really stopped",
        "background":  "grew up knowing the Alliance as something that happened to you, not for you",
    },
}


# ── Alliance / Browncoat war history ───────────────────────────────────────────

WAR_HISTORY = {
    "Fought for the Alliance": "served the winning side, which doesn't feel like winning from up close",
    "Fought for the Independents": "Browncoat — lost the war, kept the opinion",
    "Too Young to Fight": "the war is history they lived through, not fought through",
    "Civilian on the Rim": "the war came to them; they didn't go to it",
    "Avoided It": "managed to be somewhere else — they have feelings about that",
    "No Comment": "they don't talk about the war",
}


# ── Tools ───────────────────────────────────────────────────────────────────────

def roll_cortex_attributes() -> str:
    """
    Distribute Cortex die sizes randomly across the six attributes.
    Standard spread: d4, d6, d6, d8, d8, d10 — capable but not exceptional.
    Returns a JSON object with attribute names and die sizes.
    """
    sizes = [4, 6, 6, 8, 8, 10]
    random.shuffle(sizes)
    attributes = ["Agility", "Alertness", "Intelligence", "Strength", "Vitality", "Willpower"]
    result = {attr: f"d{s}" for attr, s in zip(attributes, sizes)}
    return json.dumps(result, indent=2)

def get_role_info(role_name: str) -> str:
    if role_name not in ROLES:
        return f"Unknown role '{role_name}'. Available: {list(ROLES.keys())}"
    return json.dumps(ROLES[role_name], indent=2)

def get_location_info(region: str) -> str:
    if region not in VERSE_LOCATIONS:
        return f"Unknown region '{region}'. Available: Core, Border, Rim"
    return json.dumps(VERSE_LOCATIONS[region], indent=2)

def roll_dice(sides: int, count: int = 1) -> str:
    if sides not in VALID_DICE_SIZES:
        return f"Error: {sides} is not a valid Cortex die. Choose from: {sorted(VALID_DICE_SIZES)}"
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"

def roll_war_history() -> str:
    choice = random.choice(list(WAR_HISTORY.keys()))
    return json.dumps({"history": choice, "flavor": WAR_HISTORY[choice]})


# ── Tool schemas ────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "roll_cortex_attributes",
        "description": "Randomly distribute Cortex die sizes (d4–d10) across the six attributes: Agility, Alertness, Intelligence, Strength, Vitality, Willpower.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_role_info",
        "description": "Look up a character role's key attributes, skills, flavor, and distinction seeds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role_name": {
                    "type": "string",
                    "description": "Character role.",
                    "enum": list(ROLES.keys()),
                },
            },
            "required": ["role_name"],
        },
    },
    {
        "name": "get_location_info",
        "description": "Look up a region of the 'Verse (Core, Border, or Rim) for homeworld flavor and background color.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Region of the 'Verse.",
                    "enum": ["Core", "Border", "Rim"],
                },
            },
            "required": ["region"],
        },
    },
    {
        "name": "roll_dice",
        "description": "Roll Cortex dice (d4, d6, d8, d10, or d12) for random elements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {
                    "type": "integer",
                    "description": "Die size.",
                    "enum": [4, 6, 8, 10, 12],
                },
                "count": {
                    "type": "integer",
                    "description": "Number of dice.",
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["sides"],
        },
    },
    {
        "name": "roll_war_history",
        "description": "Randomly determine the character's relationship to the Unification War.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


# ── Tool dispatcher ─────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_cortex_attributes": return roll_cortex_attributes()
    if name == "get_role_info":          return get_role_info(**inputs)
    if name == "get_location_info":      return get_location_info(**inputs)
    if name == "roll_dice":              return roll_dice(**inputs)
    if name == "roll_war_history":       return roll_war_history()
    return f"Unknown tool: {name}"


# ── System prompts ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Firefly RPG character generator (Cortex System). Create vivid, story-ready characters for the 'Verse.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names in the 'Verse reflect its multicultural mix — draw from Chinese, Spanish, Slavic, West African, Arabic, and other traditions, not just Anglo-European. Vary first letters, syllable counts, and cultural origins. Do not default to soft English-sounding names that start with the same letters.

Do not output any intermediate notes, reasoning, or working text. Output only the formatted character sheet, starting directly with the ## heading.

Work through these steps using your tools:

1. ROLE — Choose a role that fits the story. Look it up with get_role_info.

2. HOMEWORLD — Choose a region (Core, Border, or Rim) with get_location_info. Pick a specific world from the list. The region shapes the character's worldview, accent, and expectations.

3. WAR HISTORY — Call roll_war_history to determine their relationship to the Unification War. Let it color the backstory without defining it entirely.

4. ATTRIBUTES — Call roll_cortex_attributes to get a die distribution. You may reassign up to two die sizes to better fit the role — note what you changed and why.

5. SKILLS — Assign die sizes to 6–8 relevant skills. Use the Cortex ladder: d4 (poor), d6 (fair), d8 (good), d10 (great), d12 (exceptional). Key role skills should be d8 or higher.

6. DISTINCTIONS — Write exactly three. Each is a short phrase (3–6 words) that captures something essential. They should create story, not just describe. A Distinction should be able to help you (d8) or hurt you (d4 for a Plot Point) depending on the situation.

7. SIGNATURE ASSET — One thing, relationship, or reputation worth d6. The one thing they'd grab in a fire.

8. COMPLICATIONS — One starting complication (d6) they're already carrying. Not a flaw — a situation.

Always use exactly this format:

## **[Full Name]**
*[Role] — [one sharp sentence that places them in the 'Verse]*

| | |
|---|---|
| **Role** | [Role] |
| **Homeworld** | [World] ([Region]) |
| **War** | [their relationship to the Unification War — one phrase] |

### Attributes
- **Agility** [dX] — [one phrase: what this looks like in practice]
- **Alertness** [dX] — [one phrase]
- **Intelligence** [dX] — [one phrase]
- **Strength** [dX] — [one phrase]
- **Vitality** [dX] — [one phrase]
- **Willpower** [dX] — [one phrase]

### Skills
List each skill with its die size. For the single highest-rated skill, add one italic sentence below it about how they got it or what it cost.
Example: `- Pilot d10` / `- Firearms d6`

### Distinctions
1. **[Distinction]** — [one sentence: how this creates story, both when it helps and when it doesn't]
2. **[Distinction]** — [one sentence]
3. **[Distinction]** — [one sentence]

### Signature Asset
**[Asset name]** d6 — [one sentence: what it is and why it matters to them specifically]

### Complications
**[Complication]** d6 — [one sentence: the situation they're already in]

### Backstory
Three sentences. A past, a wound, and a direction. The 'Verse is big and mostly empty and people end up on ships for reasons. Make this one feel earned."""

NPC_SYSTEM_PROMPT = """You are a Firefly RPG NPC generator (Cortex System). Create a vivid, instantly usable character sketch for the 'Verse.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names in the 'Verse reflect its multicultural mix — draw from Chinese, Spanish, Slavic, West African, Arabic, and other traditions, not just Anglo-European. Vary first letters, syllable counts, and cultural origins.

Call roll_cortex_attributes for a quick stat spread. Use get_role_info if it helps ground them. Skip the full chargen — this is a sketch.

Always use exactly this format:

## **[Name]**
*[Role or occupation] — [one sharp hook sentence]*

| | |
|---|---|
| **Role** | [what they do] |
| **Homeworld** | [world, region] |
| **Key Attributes** | [two or three notable die ratings] |

**Distinctions:** [two or three short phrases separated by / — the essence of who they are]

**Demeanor:** [1–2 sentences — how they come across, what you notice first]
**Wants:** [what they need right now — specific]
**Secret:** [one thing they're hiding — specific, not vague]
**Hook:** [one concrete way they pull the crew into their business]
**Connection:** [one named person they love, fear, or owe — and why it matters]"""


# ── Phase tracker ───────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "role":       "Choosing role...",
    "homeworld":  "Finding homeworld...",
    "war":        "Rolling war history...",
    "attributes": "Distributing attributes...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "get_role_info":          return "role"
    if tool_name == "get_location_info":      return "homeworld"
    if tool_name == "roll_war_history":       return "war"
    if tool_name == "roll_cortex_attributes": return "attributes"
    return None


# ── Agentic loop ────────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    messages = [{"role": "user", "content": prompt}]
    seen     = set()
    phase    = None

    print()

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
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
                    new_phase = detect_phase(block.name, seen)
                    if new_phase and new_phase != phase:
                        phase = new_phase
                        print(PHASE_MESSAGES[phase])

                    seen.add(block.name)
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})


# ── Save ────────────────────────────────────────────────────────────────────────

def save_result(result: str, mode: str) -> Path:
    first_line = next(
        (l for l in result.strip().splitlines() if l.startswith("##")),
        result.strip().splitlines()[0],
    )
    name_raw  = re.sub(r"[#*]", "", first_line).strip()
    name_slug = re.sub(r"[^a-z0-9]+", "-", name_raw.lower()).strip("-")
    filename  = f"{name_slug}-{mode}.md"

    output_dir = Path(__file__).parent / "firefly_characters"
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(result)
    return filepath


# ── Entry point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode  = input("Mode? (character / npc, default: character): ").strip().lower()
    mode  = mode if mode in ("character", "npc") else "character"
    label = "NPC" if mode == "npc" else "character"
    desc  = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt = f"Generate a Firefly RPG NPC with these constraints: {desc}" if desc else "Generate a fully random Firefly RPG NPC."
    else:
        sys_prompt = SYSTEM_PROMPT
        prompt = f"Generate a Firefly RPG character for storytelling purposes with these constraints: {desc}" if desc else "Generate a fully random Firefly RPG character for storytelling purposes."

    result = run_agent(prompt, sys_prompt)

    # Strip any preamble before the first ## heading
    lines = result.strip().splitlines()
    heading_idx = next((i for i, l in enumerate(lines) if l.startswith("##")), 0)
    result = "\n".join(lines[heading_idx:])

    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")
