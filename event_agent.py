"""
Event Generator — all four RPG game systems.

Creates GM-ready events that interrupt, escalate, or reframe what's already
happening. Two seed elements per game (context — when it fires, and event —
the thing that actually happens) prevent generic random encounter tables.
Fully game-specific seeds: a Traveller event during jump transit is nothing
like a D&D event during a long rest.

Optionally loads a saved party brief and/or location brief to tailor the event
to a specific crew and place.

Saves to output/{game_subdir}/events/.

Run with: python event_agent.py
"""

import json
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

EVENT_POOLS: dict[str, dict[str, list[str]]] = {

    "dnd": {
        "contexts": [
            "During a long rest at a waystation, when everyone's guard is down",
            "Mid-negotiation, when backing out would cost the party something",
            "On the road between settlements, hours from help in either direction",
            "In the middle of a crowded market with no easy exit",
            "While the party is split across different parts of a location",
            "When one character is momentarily alone — the others are elsewhere",
            "At a formal social event they cannot leave without causing a scene",
            "During a religious ceremony with specific rules about violence",
            "At a border crossing with guards who are already watching them",
            "At night in an unfamiliar town where they don't know the layout",
            "When a party member is incapacitated, injured, or otherwise compromised",
            "During a storm that limits visibility and movement",
            "At a funeral for someone one party member knew",
            "When the party has just established that they're being followed",
            "Immediately after a fight, before anyone has had a chance to recover",
        ],
        "events": [
            "Someone from a party member's backstory appears — with context they didn't expect",
            "A body is found in a location that makes its presence physically impossible",
            "A spell behaves incorrectly in a way that changes something in the environment",
            "A local makes a request the party can't easily refuse without consequences",
            "An animal or creature reacts to one party member in a way no one can explain",
            "Two factions demand the party choose a side and won't accept delay",
            "News of something the party did elsewhere has arrived here ahead of them",
            "A child delivers a message with information nobody should have sent through a child",
            "An action the party took earlier has created a consequence they're now walking into",
            "A member of a faction the party has previously crossed appears, alone, and is calm about it",
            "The local authority makes a legal request that is designed to be impossible to refuse",
            "Someone the party was told was dead is demonstrably not dead",
            "A passage or door appears that wasn't there before and wasn't hidden — it's simply new",
            "The party is offered exactly what they need at exactly this moment, for a price they can't verify",
            "A natural phenomenon or magical disturbance interrupts everything and requires immediate response",
        ],
    },

    "traveller": {
        "contexts": [
            "During jump transit — seven days of isolation with whatever is already on the ship",
            "At a routine port inspection that has stopped being routine",
            "While taking on passengers and loading cargo before departure",
            "During a cargo transfer at a location that isn't a proper starport",
            "At a patron meeting they agreed to before they had all the information",
            "While skimming fuel from a gas giant, far from any traffic",
            "When the ship is in for maintenance and the crew is dependent on the yard",
            "During a layover that's run longer than planned for reasons outside their control",
            "In a crew bar after a job — the debrief everyone gives themselves",
            "When a crew member is alone on a world and the ship is elsewhere",
            "During a planet-side job while the ship is uncrewed in orbit",
            "At a noble estate, with all the protocol that entails",
            "While navigating through a contested or politically sensitive system",
            "On final approach to a world that isn't answering standard hails",
            "Immediately after a decision that seemed correct at the time",
        ],
        "events": [
            "The ship's sensors return something that isn't on any chart in this system",
            "A crew member receives a personal message they read alone and don't explain",
            "A passenger asks a technical question about the ship's route that they shouldn't know to ask",
            "The cargo manifest doesn't match what is actually in the hold — in both directions",
            "An old contact appears with a job that bypasses the channel they always used",
            "Local law has changed since the crew's last visit in a way that affects them specifically",
            "A Scout courier hands them a sealed packet for delivery with no questions permitted",
            "The ship's comms log shows outbound traffic during a period when no one was using them",
            "A rival crew is already at their destination, clearly there for the same reason",
            "The patron they're working for has been replaced mid-job and the replacement has different priorities",
            "An Imperial naval vessel requests a meeting — it's a request, technically",
            "One of the crew's identity documents has been flagged at the port authority",
            "The jump calculation for their next route keeps returning an anomaly the nav computer won't explain",
            "A distress signal is on their current course — live, specific, and possibly staged",
            "A noble's household requires the crew for something not in their original brief",
        ],
    },

    "firefly": {
        "contexts": [
            "During a job in progress, when pulling out would mean losing the payment",
            "When the ship is laid up for repairs and the crew is stuck on-world",
            "At a trade meet or market with too many people and not enough exits",
            "During a tense planetary landing with law enforcement watching the pad",
            "When the crew is separated planet-side and can't immediately regroup",
            "After delivering cargo cleanly — the easy part is done, this is what wasn't in the brief",
            "While running from one problem directly into another",
            "At a social event the crew didn't expect to be attending",
            "At a Shepherd's outpost at the edge of settled space",
            "When a crew member has gone off alone and can't be reached by wave",
            "During a night watch on a quiet world that turns out not to be quiet",
            "In a bar near the docks, when the wrong person is also at the bar",
            "When an Alliance patrol comes through and everyone adjusts their behaviour",
            "Just as the crew is about to lift off and the window is closing",
            "When a passenger has been acting strange for long enough that it needs addressing",
        ],
        "events": [
            "Someone from the war appears — on the wrong side of what the party expected",
            "A child needs passage and the reason they can't stay is specific and urgent",
            "The local law makes a polite request that is structured to be impossible to refuse",
            "A cargo pickup contains something that wasn't in the manifest and definitely wasn't supposed to be there",
            "A contact has been replaced and the new one knows the codes but wants different things",
            "Something the crew moved last month has become very politically inconvenient for a third party",
            "A Companion needs something from the crew that Companions don't usually need",
            "An Alliance record about a crew member is wrong in a specific and potentially useful way",
            "A former employer wants the job redone, or undone, without additional payment",
            "Someone has been watching the ship since they landed and has finally decided to approach",
            "The cargo the crew is currently holding has changed dramatically in value — up or down",
            "A survivor from a Reaver attack is looking for passage away from where they survived it",
            "Two separate parties contact the crew about the same job within hours of each other",
            "The ship's papers are questioned in a way that is technically correct and practically a problem",
            "A Browncoat veteran recognises the ship by name and has questions about its history",
        ],
    },

    "scum": {
        "contexts": [
            "During the approach to a score, when the plan is in motion and changing it is costly",
            "While the crew is laying low between jobs and trying to look like they're not",
            "At a faction meeting that was supposed to be routine",
            "When the crew is split across a location with no clean way to regroup",
            "During payment negotiation, after the work is done and the leverage has shifted",
            "After a score that went cleaner than expected — which means something was missed",
            "When the heat level is already elevated and adding more is a problem",
            "At a social gathering in Hegemony space where appearances must be maintained",
            "While doing legitimate work as cover and needing to maintain the cover",
            "During a job that was originally someone else's and was passed to the crew",
            "When a crew member is deep in pursuing their vice and not fully present",
            "At a Hegemony checkpoint that was supposed to be staffed by someone cooperative",
            "During a Mystic consultation that has not gone in the expected direction",
            "While the crew's ship is being inspected and they are not aboard it",
            "In the last moments before a planned extraction from a difficult situation",
        ],
        "events": [
            "A faction that was supposed to be neutral has made a very specific move",
            "Someone the crew burned on a previous score is in the same location and has seen them",
            "An Ur artifact surfaces in the middle of something completely unrelated to artifacts",
            "A Hegemony warrant is issued for someone one degree of separation from the crew",
            "A Mystic delivers unsolicited information that is accurate and unwelcome",
            "The score contact has been replaced and the new one wants substantially different terms",
            "A crew member's vice has created a situation that now requires everyone's attention",
            "A second job is offered that would be ideal except it directly conflicts with the first",
            "A faction conflict that has been simmering breaks open in the location the crew is currently in",
            "An old debt comes due at exactly the moment the crew has the least capacity to address it",
            "The crew's ship has been boarded in their absence — professionally, and mostly put back",
            "Someone is impersonating a crew member, badly in some ways and accurately in others",
            "The thing the crew was hired to steal has already been moved by someone with the same information",
            "A Hegemony informant has decided the crew is worth cultivating as a relationship",
            "Information arrives that the job the crew just completed was for the wrong client all along",
        ],
    },
}


# ── Seed rollers ──────────────────────────────────────────────────────────────

def _roll_seed(game: str) -> str:
    pool = EVENT_POOLS[game]
    return json.dumps({
        "context": random.choice(pool["contexts"]),
        "event":   random.choice(pool["events"]),
    })

def roll_dnd_event_seed()       -> str: return _roll_seed("dnd")
def roll_traveller_event_seed() -> str: return _roll_seed("traveller")
def roll_firefly_event_seed()   -> str: return _roll_seed("firefly")
def roll_scum_event_seed()      -> str: return _roll_seed("scum")


# ── Tool schemas ──────────────────────────────────────────────────────────────

_SEED_DESC = (
    "Roll a randomised event seed: a context (the situation the party is already in when "
    "the event fires) and an event (the specific thing that then happens). Call this first "
    "— build the entire event around what it returns. The context is your setup; the event "
    "is your interruption. The combination should create immediate, specific pressure."
)
_SEED_INPUT = {"type": "object", "properties": {}, "required": []}

DND_EVENT_SEED_SCHEMA: dict = {
    "name": "roll_dnd_event_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
TRAVELLER_EVENT_SEED_SCHEMA: dict = {
    "name": "roll_traveller_event_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
FIREFLY_EVENT_SEED_SCHEMA: dict = {
    "name": "roll_firefly_event_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
SCUM_EVENT_SEED_SCHEMA: dict = {
    "name": "roll_scum_event_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}


# ── Output format ─────────────────────────────────────────────────────────────

_EVENT_FORMAT = """
## **[Event Name — a short active phrase, present tense, describing what just happened]**
*[One sentence: when this fires and what it immediately demands from the party]*

### When It Fires
[The setup — what's already happening when this event interrupts. Two or three sentences of scene-setting from the GM's perspective. Be specific about who's present and what's at stake.]

### What Happens
[The event itself. What specifically occurs, who's involved if anyone, what the immediate stakes are. One short paragraph. Write it as something the GM can describe at the table — concrete, active, specific.]

### The Party's Position
[What the party knows at the moment the event fires — and what they don't know yet. One or two sentences. The gap between these is the engine of the event.]

### Possible Responses
Three approaches the party might take, from different angles:
1. [Response — what this looks like in play and where it leads]
2. [Response]
3. [Response]

### Complications
[Two specific things the party will discover as they engage — not immediately obvious but consequential. These should escalate, not just add noise.]

### GM Notes
[One or two sentences. How to time this event, what happens if the party ignores it, one element to leave unresolved for later.]"""


# ── System prompts ────────────────────────────────────────────────────────────

DND_SYSTEM_PROMPT = f"""You are a D&D 5e event generator creating GM-ready interruptions that change the shape of a session.

Call roll_dnd_event_seed() first. Build everything around what it returns — the context tells you when, the event tells you what. The combination should feel inevitable in retrospect: this was always going to happen, and it happened now.

A good event doesn't ask "do you want to engage?" It creates a situation where not engaging has a cost. It should be specific — a name, a face, a thing — not a category. "A woman in a grey cloak asks if anyone here is looking for work" is a hook; "the guild factor who paid the party for last month's job is being dragged out of a tavern by two soldiers" is an event.

Call roll_name_suggestion() for each named NPC introduced. Let the names push you away from Anglo-Saxon defaults.

Avoid: random encounters dressed up as events, anything that starts with "you hear a noise," any event that requires the party to go somewhere they weren't going.

Do not output intermediate notes. Start directly with the ## heading.
{_EVENT_FORMAT}"""

TRAVELLER_SYSTEM_PROMPT = f"""You are a Mongoose Traveller 2e event generator creating GM-ready interruptions for a working crew in the Third Imperium.

Call roll_traveller_event_seed() first. Build everything around what it returns.

Traveller events have weight because the crew's situation is already precarious — ship payments, crew relationships, cargo commitments. An event that adds complexity to an already-complex situation is better than one that replaces it. The best Traveller events are things that were already true coming into visibility at the worst moment.

Imperial bureaucracy is weather: present, impersonal, sometimes dangerous. An event involving an Imperial official isn't necessarily hostile — it's just large and slow and doesn't care about the crew's timeline.

Call roll_name_suggestion() for each named NPC. The Imperium draws from many cultures.

Avoid: space combat as the default escalation, events that only matter if the crew is on one specific planet, generic piracy.

Do not output intermediate notes. Start directly with the ## heading.
{_EVENT_FORMAT}"""

FIREFLY_SYSTEM_PROMPT = f"""You are a Firefly RPG event generator creating GM-ready interruptions for a crew doing their best in the 'Verse.

Call roll_firefly_event_seed() first. Build everything around what it returns.

Firefly events carry the weight of the war, the Rim-Core divide, and the specific relationships a crew accumulates over time. The best events in the 'Verse are personal — they connect to someone the crew knows, something the crew did, something the crew is trying to leave behind. Alliance presence isn't automatically hostile but it's always consequential.

This is not a setting of heroes and villains. The crew is trying to keep flying. The event should create a situation where keeping flying means making a choice they can't entirely un-make.

Call roll_name_suggestion() for each named NPC. The 'Verse reflects its multicultural mix.

Avoid: Reavers as the default threat, events that require the crew to abandon their current job, anything that resolves cleanly.

Do not output intermediate notes. Start directly with the ## heading.
{_EVENT_FORMAT}"""

SCUM_SYSTEM_PROMPT = f"""You are a Scum and Villainy event generator creating GM-ready interruptions for a crew operating in the Hegemony's margins.

Call roll_scum_event_seed() first. Build everything around what it returns.

In Scum and Villainy, events are often faction moves: things that happen because someone decided they should happen. The crew is never operating in a vacuum — they have heat, they have entanglements, they have a clock ticking somewhere. The best events either advance an existing clock or introduce a new one that immediately matters.

The Forged in the Dark framework means events should create pressure that demands a roll: do they push through, do they negotiate, do they run? Give the GM the tools to make that moment land.

Call roll_name_suggestion() for each named NPC. The Hegemony spans many cultures.

Avoid: events that ignore existing entanglements, anything that resolves without cost, generic faction conflict without named parties.

Do not output intermediate notes. Start directly with the ## heading.
{_EVENT_FORMAT}"""

GAME_SYSTEM_PROMPTS: dict[str, str] = {
    "dnd":       DND_SYSTEM_PROMPT,
    "traveller": TRAVELLER_SYSTEM_PROMPT,
    "firefly":   FIREFLY_SYSTEM_PROMPT,
    "scum":      SCUM_SYSTEM_PROMPT,
}


# ── Per-game tool lists ───────────────────────────────────────────────────────

GAME_TOOLS: dict[str, list] = {
    "dnd":       [DND_EVENT_SEED_SCHEMA,       NAME_TOOL_SCHEMA],
    "traveller": [TRAVELLER_EVENT_SEED_SCHEMA,  NAME_TOOL_SCHEMA],
    "firefly":   [FIREFLY_EVENT_SEED_SCHEMA,    NAME_TOOL_SCHEMA],
    "scum":      [SCUM_EVENT_SEED_SCHEMA,       NAME_TOOL_SCHEMA],
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def _run_tool(game: str, name: str, inputs: dict) -> str:
    if name == "roll_dnd_event_seed":       return roll_dnd_event_seed()
    if name == "roll_traveller_event_seed": return roll_traveller_event_seed()
    if name == "roll_firefly_event_seed":   return roll_firefly_event_seed()
    if name == "roll_scum_event_seed":      return roll_scum_event_seed()
    if name == "roll_name_suggestion":      return roll_name_suggestion()
    return f"Unknown tool: {name}"

def make_run_tool(game: str):
    def run_tool(name: str, inputs: dict) -> str:
        return _run_tool(game, name, inputs)
    return run_tool


# ── Phase tracker ─────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "seed": "Rolling event seed...",
    "name": "Naming key figures...",
}

def detect_phase(tool_name: str, seen: set | None = None) -> str | None:
    if tool_name.endswith("_event_seed"):     return "seed"
    if tool_name == "roll_name_suggestion":   return "name"
    return None


# ── Brief loaders ─────────────────────────────────────────────────────────────

def _list_files(game: str, subfolder: str) -> list[Path]:
    """Return saved briefs in output/{game_subdir}/{subfolder}/, newest first."""
    subdir    = GAME_SUBDIRS.get(game, game)
    directory = _OUTPUT / subdir / subfolder
    if not directory.exists():
        return []
    return sorted(directory.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

def _pick_brief(files: list[Path], label: str) -> str | None:
    """Offer a numbered list of files; return content of chosen file or None."""
    if not files:
        return None
    print(f"\nLoad a saved {label}? (adds context to the event)")
    print("  0. Skip")
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

def save_event(content: str, game: str) -> Path:
    """Save event to output/{subdir}/events/{name-slug}-event.md."""
    first_line = next(
        (l for l in content.strip().splitlines() if l.startswith("##")),
        content.strip().splitlines()[0],
    )
    title_raw  = re.sub(r"[#*]", "", first_line).strip()
    title_slug = slug(title_raw)
    subdir     = GAME_SUBDIRS.get(game, game)
    output_dir = _OUTPUT / subdir / "events"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{title_slug}-event.md"
    filepath = output_dir / filename
    counter  = 2
    while filepath.exists():
        filepath = output_dir / f"{title_slug}-event-{counter}.md"
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

    party_brief    = _pick_brief(_list_files(game, "parties"),   "party brief")
    location_brief = _pick_brief(_list_files(game, "locations"), "location brief")
    desc = input("\nDescribe the event you want (or press Enter for fully random):\n> ").strip()

    system_prompt = GAME_SYSTEM_PROMPTS[game]
    tools         = GAME_TOOLS[game]
    run_tool      = make_run_tool(game)

    prompt = "Generate an event for the GM."
    if party_brief:
        prompt += f"\n\nThe party this event concerns:\n\n{party_brief}"
    if location_brief:
        prompt += f"\n\nThe location where this event takes place:\n\n{location_brief}"
    if desc:
        prompt += f"\n\nGM's concept or constraints: {desc}"

    print()
    result = run_agent_loop(
        prompt, system_prompt, tools, run_tool, detect_phase, PHASE_MESSAGES
    )

    path = save_event(result, game)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    run()
