"""
Rumor Generator — all four RPG game systems.

Creates GM-ready rumors with a spoken version, the actual truth, the danger of
acting on bad information, and three hooks. Three seed elements per rumor (a
game-specific subject, a shared truth-angle, and a shared tone) prevent the
model from defaulting to generic "there's treasure in the dungeon" gossip.

Optionally loads a saved location brief to anchor the rumor to a specific place.

Saves to output/{game_subdir}/rumors/.

Run with: python rumor_agent.py
"""

import json
import os
import random
import re
from pathlib import Path

from names import roll_name_suggestion, NAME_TOOL_SCHEMA
from utils import get_client, run_agent_loop, slug, pick


# ── Output path ───────────────────────────────────────────────────────────────

_OUTPUT = Path(__file__).parent / "output"

GAME_SUBDIRS: dict[str, str] = {
    "dnd":       "dnd",
    "traveller": "traveller",
    "firefly":   "firefly",
    "scum":      "scum_villainy",
}


# ── Seed pools ────────────────────────────────────────────────────────────────

# Game-specific subjects — what the rumor is fundamentally about
RUMOR_SUBJECTS: dict[str, list[str]] = {

    "dnd": [
        "A thieves' guild internal succession dispute that's about to turn violent",
        "A noble who's been selling military passage rights through lands they don't control",
        "A merchant caravan route that's been disappearing — not robbed, just gone",
        "A temple that's been quietly excommunicating priests who ask the wrong questions",
        "A wizard conducting experiments on a nearby village's missing livestock",
        "A creature seen in three separate locations on the same night",
        "An artifact that passed through four hands in a month — each seller died shortly after",
        "A keep under new management whose previous lord was never officially declared dead",
        "A heist that went badly wrong last month — the crew is missing and so is the target",
        "A hidden passage beneath the city that connects buildings that shouldn't be connected",
        "A member of the town guard selling information to both the guild and the constabulary",
        "A crown appointee who hasn't been seen in public for six weeks but is still signing documents",
        "A cursed item in active circulation — people keep giving it away and getting it back",
        "A monster attack the survivors describe differently each time, in specific ways",
        "A long-standing trade agreement about to collapse, and both sides are already positioning",
        "A druid grove that's been blessing one family's crops at the expense of everyone else's",
        "A ship that arrived at the river docks and unloaded nothing — and left with something",
        "An old order of knights whose charter entitles them to things the current lord won't honor",
    ],

    "traveller": [
        "A megacorporation acquisition that officially closed but operationally hasn't changed anything",
        "An Imperial Scout who filed a falsified survey and is collecting fees on a claim that doesn't exist",
        "A ship in this system that isn't on the traffic registry and isn't showing a transponder",
        "A noble in financial difficulty selling access to something that isn't theirs to sell",
        "A smuggling ring that has protection from someone in the port authority",
        "A planet about to have its habitability classification changed — the locals don't know yet",
        "A IISS route that's been quietly closed without announcement, and traders are still using it",
        "A Vargr mercenary outfit hiring aggressively for a contract nobody's named yet",
        "A Zhodani-flagged vessel operating in Imperial space under a cover identity",
        "A derelict that local traffic has been avoiding — it was supposedly salvaged two years ago",
        "A medical quarantine on a nearby world that the official briefing doesn't fully explain",
        "A merchant house that backed the wrong faction in a local dispute and is now calling in favours",
        "A piracy ring with an inside source in at least one port authority's traffic system",
        "A jump route that one captain claims to know — they're asking a lot for the data",
        "A weapon cache from the last border conflict, officially recovered, possibly not entirely",
        "A crew that was hired for a routine job and hasn't been heard from since they jumped out",
        "A cargo shipment that arrived at its destination without its original bill of lading",
        "An Imperial warrant that was issued for a ship that's still operating openly in this region",
    ],

    "firefly": [
        "Alliance troop movements that don't match the stated humanitarian purpose",
        "A Blue Sun distribution operation nobody at the local level was told about",
        "A Browncoat supply cache from the war — weapons, medicine, or both — in a location someone knows",
        "A lawman taking fees from both the Alliance and the local criminal operation",
        "A Companion with a registered House ID working somewhere they wouldn't ordinarily be",
        "A doctor with an active Alliance warrant who's been practicing in Rim settlements for years",
        "A Shepherd who arrived six months ago and hasn't done anything a Shepherd would normally do",
        "A job that went wrong last month — the crew scattered and nobody's claiming responsibility",
        "A Reaver sighting close enough to matter that didn't make any official channel",
        "A settlement that paid a significant sum to someone to be left alone — and got left alone",
        "A ship whose hull markings don't match its registry and whose crew doesn't discuss it",
        "A supply run contracted by the Alliance that arrived short — by a lot — and was signed off anyway",
        "A black-market cortex relay that's been broadcasting on a channel the Alliance hasn't found",
        "Someone who died in the war, officially, showing up in a Rim settlement and not explaining themselves",
        "An Alliance deserter with something to sell — not weapons, something more inconvenient",
        "A terraforming contract that was awarded to a company that doesn't appear to exist",
        "A Border world town that's been entirely loyal to the Alliance since the war, which everyone finds strange",
        "A Companion House on the Rim that's been operating without licensing for longer than should be possible",
    ],

    "scum": [
        "A Guild contract that transferred without proper notification — both holders think it's active",
        "A Hegemony official running a side operation using official resources and official cover",
        "A schism in the Church of Stellar Flame that hasn't gone public yet but is already affecting decisions",
        "An Ur artifact being moved through this region — the movement itself is the thing being hidden",
        "A faction leader whose death has been suppressed for weeks while someone manages the transition",
        "A score that's been posted to multiple crews simultaneously — someone's running a competition",
        "A crew that took a high-paying job and hasn't been seen since — their ship has been spotted",
        "A Mystic consulting for a faction they publicly refuse to work with",
        "A traitor inside a faction passing information, and the faction knows there's a leak but not who",
        "A job that pays too well being shopped to too many people — someone wants something to happen",
        "A Hegemony warrant that may have been issued in error, or may have been issued very precisely",
        "A debt being collected in favors instead of currency — the favors are getting larger",
        "A ship with no transponder that's been spotted three times in two systems by different crews",
        "An ancient Ur site being quietly excavated under a Guild exploration license with unusual restrictions",
        "A faction war that both sides are still calling a negotiation while actively preparing for violence",
        "A Hegemony inspection team on a route that doesn't have anything worth inspecting — officially",
        "A crew being blackmailed with something they swear they didn't do, and the evidence is convincing",
        "A contact who has been dead for six months, whose name keeps appearing on recent documents",
    ],
}

# Shared truth-angle — how the rumor relates to reality
TRUTH_ANGLES: list[str] = [
    "Mostly true, but the person spreading it has an angle that the framing serves",
    "The facts are right but the interpretation is entirely wrong — the conclusion doesn't follow",
    "False, but believed by people who have already acted on it and are committed",
    "True — and the wrong people already know it, which is why it's in circulation",
    "True but outdated — the situation has moved on and the information is now misleading",
    "A deliberate plant — someone specific wants this rumor in circulation",
]

# Shared tone — how the rumor is being told
TONES: list[str] = [
    "Urgently, over a drink, to someone who wasn't supposed to hear it",
    "Offhand, as established fact, by someone who treats it as old news",
    "Third-hand, from someone who swears they know the original source personally",
    "As a warning — 'stay out of it, it's not your problem'",
    "Framed as an opportunity — 'there's something in this for someone who moves quickly'",
    "Whispered — the speaker keeps checking who's nearby",
]


# ── Seed rollers ──────────────────────────────────────────────────────────────

def _roll_seed(game: str) -> str:
    return json.dumps({
        "subject":      random.choice(RUMOR_SUBJECTS[game]),
        "truth_angle":  random.choice(TRUTH_ANGLES),
        "tone":         random.choice(TONES),
    })

def roll_dnd_rumor_seed()       -> str: return _roll_seed("dnd")
def roll_traveller_rumor_seed() -> str: return _roll_seed("traveller")
def roll_firefly_rumor_seed()   -> str: return _roll_seed("firefly")
def roll_scum_rumor_seed()      -> str: return _roll_seed("scum")


# ── Tool schemas ──────────────────────────────────────────────────────────────

_SEED_DESC = (
    "Roll a randomised rumor seed: a subject (what the rumor is about), a truth-angle "
    "(how the rumor relates to reality), and a tone (how it's being told). Call this "
    "first — build the entire rumor around what it returns. The truth-angle is your "
    "constraint for the GM section; the subject is your constraint for the content."
)
_SEED_INPUT = {"type": "object", "properties": {}, "required": []}

DND_RUMOR_SEED_SCHEMA: dict = {
    "name": "roll_dnd_rumor_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
TRAVELLER_RUMOR_SEED_SCHEMA: dict = {
    "name": "roll_traveller_rumor_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
FIREFLY_RUMOR_SEED_SCHEMA: dict = {
    "name": "roll_firefly_rumor_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
SCUM_RUMOR_SEED_SCHEMA: dict = {
    "name": "roll_scum_rumor_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}


# ── Output format ─────────────────────────────────────────────────────────────

_RUMOR_FORMAT = """
## **[Rumor Title — a short phrase that names what this is about, not what's true]**
*[One sentence: the nature of this rumor — what it concerns and why it's in circulation]*

### As Heard
> "[The exact rumor as someone would speak it. 2-3 sentences, in the voice of someone passing it on. Include the specific detail that makes it feel real and the conclusion the speaker draws. First person or reported speech."]"

*Source: [Who is saying this, how they heard it, and — crucially — why they're saying it now. One sentence.]*

### What's Actually True
[The GM's-eye view. What really happened, what's actually going on, who knows what. This should differ from the rumor in a specific and interesting way — not just "it's false" but *how* it's false or incomplete or being used. One short paragraph.]

### The Danger
[What happens if the party acts on the rumor as stated. What they get wrong, who they'll offend, what opportunity they'll miss, or what trap they'll walk into. Be specific. One short paragraph.]

### Hooks
Three ways the party can engage with this rumor:
1. [Hook — a specific thing that happens: an approach, an encounter, a discovery]
2. [Hook]
3. [Hook]

### GM Notes
[One or two sentences of practical advice. How to use this rumor, what to escalate if the party pursues it, and one element that should stay ambiguous.]"""


# ── System prompts ────────────────────────────────────────────────────────────

DND_SYSTEM_PROMPT = f"""You are a D&D 5e rumor generator creating GM-ready gossip with real texture.

Call roll_dnd_rumor_seed() first. Build everything around what it returns — the subject is your content, the truth-angle determines the GM section, and the tone shapes how the rumor is told.

A good rumor is specific. It has a name in it, a place, a recent event. It sounds like something a real person said — not a plot hook, but the kind of thing that spreads because it's interesting and slightly wrong. The "As Heard" section should read like overheard speech, not a story synopsis.

The truth-angle controls how real the rumor is: follow it precisely. If the angle is "deliberate plant," someone chose for this to be in circulation. If it's "mostly true but the source has an angle," the facts are real but the framing serves someone.

Call roll_name_suggestion() for each named NPC. Let the names push you away from Anglo-Saxon defaults — the world has many cultures.

Avoid: treasure-in-the-dungeon hooks, vague threats with no specifics, NPCs without a reason to be talking.

Do not output intermediate notes. Start directly with the ## heading.
{_RUMOR_FORMAT}"""

TRAVELLER_SYSTEM_PROMPT = f"""You are a Mongoose Traveller 2e rumor generator creating GM-ready gossip for the Third Imperium and beyond.

Call roll_traveller_rumor_seed() first. Build everything around what it returns.

In Traveller, information is commerce. Rumors travel through crew bars, port authorities, and merchant networks — always attached to a person, a ship, or a system. The most dangerous information is the kind someone is being paid to spread. Imperial bureaucracy is patient: a warrant doesn't expire, and a scout's falsified survey doesn't disappear.

The truth-angle is your GM constraint — follow it precisely. If it says "true but the wrong people know it," the Imperium or a megacorp already has this information and has been sitting on it.

Call roll_name_suggestion() for each named NPC. The Imperium draws from many cultural traditions.

Avoid: vague piracy threats, treasure maps, rumors that could apply to any system anywhere.

Do not output intermediate notes. Start directly with the ## heading.
{_RUMOR_FORMAT}"""

FIREFLY_SYSTEM_PROMPT = f"""You are a Firefly RPG rumor generator creating GM-ready gossip for the 'Verse.

Call roll_firefly_rumor_seed() first. Build everything around what it returns.

Rumors in the 'Verse travel by cortex relay, bar talk, and the kind of careful conversation people have when they're not sure who's listening. The war is still recent enough that any rumor touching Alliance or Browncoat history carries weight. The Rim doesn't trust the Core, and the Core doesn't think about the Rim enough.

The truth-angle shapes the GM section — follow it precisely. If the angle is "false but believed," someone has already moved on this and it's too late to correct them without creating new problems.

Call roll_name_suggestion() for each named NPC. The 'Verse reflects its multicultural Chinese-Western mix.

Avoid: generic smuggling jobs, Reaver sightings with no specifics, rumors that are just "the Alliance is bad."

Do not output intermediate notes. Start directly with the ## heading.
{_RUMOR_FORMAT}"""

SCUM_SYSTEM_PROMPT = f"""You are a Scum and Villainy rumor generator creating GM-ready gossip at the edges of the Hegemony.

Call roll_scum_rumor_seed() first. Build everything around what it returns.

In the Hegemony's margins, information is leverage. Rumors circulate because someone benefits from their circulation — or because someone lost control of something they were trying to keep quiet. Every rumor has a faction angle, even if that angle isn't obvious. The Church, the Guilds, and the Hegemony bureaucracy all treat information as a managed resource.

The truth-angle is your GM constraint — follow it precisely. If it says "deliberate plant," a faction specifically chose to put this in circulation and has a plan for what happens when someone acts on it.

Call roll_name_suggestion() for each named NPC. The Hegemony spans many cultures and naming traditions.

Avoid: vague faction conflict without specifics, Ur artifacts as simple treasure, rumors that don't implicate anyone.

Do not output intermediate notes. Start directly with the ## heading.
{_RUMOR_FORMAT}"""

GAME_SYSTEM_PROMPTS: dict[str, str] = {
    "dnd":       DND_SYSTEM_PROMPT,
    "traveller": TRAVELLER_SYSTEM_PROMPT,
    "firefly":   FIREFLY_SYSTEM_PROMPT,
    "scum":      SCUM_SYSTEM_PROMPT,
}


# ── Per-game tool lists ───────────────────────────────────────────────────────

GAME_TOOLS: dict[str, list] = {
    "dnd":       [DND_RUMOR_SEED_SCHEMA,       NAME_TOOL_SCHEMA],
    "traveller": [TRAVELLER_RUMOR_SEED_SCHEMA,  NAME_TOOL_SCHEMA],
    "firefly":   [FIREFLY_RUMOR_SEED_SCHEMA,    NAME_TOOL_SCHEMA],
    "scum":      [SCUM_RUMOR_SEED_SCHEMA,       NAME_TOOL_SCHEMA],
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def _run_tool(game: str, name: str, inputs: dict) -> str:
    if name == "roll_dnd_rumor_seed":       return roll_dnd_rumor_seed()
    if name == "roll_traveller_rumor_seed": return roll_traveller_rumor_seed()
    if name == "roll_firefly_rumor_seed":   return roll_firefly_rumor_seed()
    if name == "roll_scum_rumor_seed":      return roll_scum_rumor_seed()
    if name == "roll_name_suggestion":      return roll_name_suggestion()
    return f"Unknown tool: {name}"

def make_run_tool(game: str):
    def run_tool(name: str, inputs: dict) -> str:
        return _run_tool(game, name, inputs)
    return run_tool


# ── Phase tracker ─────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "seed": "Rolling rumor seed...",
    "name": "Naming sources and NPCs...",
}

def detect_phase(tool_name: str, seen: set | None = None) -> str | None:
    if tool_name.endswith("_rumor_seed"):     return "seed"
    if tool_name == "roll_name_suggestion":   return "name"
    return None


# ── Location brief loader ─────────────────────────────────────────────────────

def _list_location_files(game: str) -> list[Path]:
    """Return saved location briefs for the given game, newest first."""
    subdir    = GAME_SUBDIRS.get(game, game)
    loc_dir   = _OUTPUT / subdir / "locations"
    if not loc_dir.exists():
        return []
    return sorted(loc_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

def _load_location_brief(game: str) -> str | None:
    """Prompt the GM to pick a saved location brief, or skip."""
    files = _list_location_files(game)
    if not files:
        return None

    print("\nLoad a saved location brief? (adds context to the rumor)")
    print("  0. Skip — no location")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.name}")

    choice = input("> ").strip()
    if not choice.isdigit() or int(choice) == 0:
        return None
    idx = int(choice) - 1
    if 0 <= idx < len(files):
        return files[idx].read_text()
    return None


# ── Save helper ───────────────────────────────────────────────────────────────

def save_rumor(content: str, game: str) -> Path:
    """Save rumor to output/{subdir}/rumors/{name-slug}-rumor.md."""
    first_line = next(
        (l for l in content.strip().splitlines() if l.startswith("##")),
        content.strip().splitlines()[0],
    )
    title_raw  = re.sub(r"[#*]", "", first_line).strip()
    title_slug = slug(title_raw)
    subdir     = GAME_SUBDIRS.get(game, game)
    output_dir = _OUTPUT / subdir / "rumors"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{title_slug}-rumor.md"
    filepath = output_dir / filename
    counter  = 2
    while filepath.exists():
        filepath = output_dir / f"{title_slug}-rumor-{counter}.md"
        counter += 1

    filepath.write_text(content)
    return filepath


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run(game: str | None = None) -> None:
    GAMES = [
        ("dnd",       "D&D 5e"),
        ("traveller", "Mongoose Traveller 2e"),
        ("firefly",   "Firefly RPG"),
        ("scum",      "Scum and Villainy"),
    ]
    if game is None:
        game = pick("Which game?", GAMES)

    location_brief = _load_location_brief(game)
    desc = input("\nDescribe the rumor you want (or press Enter for fully random):\n> ").strip()

    system_prompt = GAME_SYSTEM_PROMPTS[game]
    tools         = GAME_TOOLS[game]
    run_tool      = make_run_tool(game)

    prompt = "Generate a rumor for the GM."
    if location_brief:
        prompt += f"\n\nThis rumor is set in or connected to the following location:\n\n{location_brief}"
    if desc:
        prompt += f"\n\nGM's concept or constraints: {desc}"

    print()
    result = run_agent_loop(
        prompt, system_prompt, tools, run_tool, detect_phase, PHASE_MESSAGES
    )

    path = save_rumor(result, game)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    run()
