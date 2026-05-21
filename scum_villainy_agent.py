"""
Scum and Villainy Character Generator (Forged in the Dark)
Creates crew members for a life of crime at the edge of the Hegemony.

Run with: python scum_villainy_agent.py
"""

import json
import random
import re
from pathlib import Path
import anthropic

client = anthropic.Anthropic()


# ── Playbooks ────────────────────────────────────────────────────────────────────

PLAYBOOKS = {
    "Muscle": {
        "description": "You solve problems with force. Violence is a tool; you're very good with tools.",
        "starting_actions": {"Skirmish": 2, "Command": 1},
        "key_actions": ["Skirmish", "Wreck", "Command", "Hunt"],
        "special_abilities": [
            ("Battleborn", "You may expend your special armor to resist a consequence from an attack in combat, or to push yourself during a fight."),
            ("Bodyguard", "When you protect a crew member, gain +1d. When you take harm in their place, clear 1 stress."),
            ("Ghost Fighter", "You may imbue your hands, blade, or gun with spirit essence. You gain potency on your next Skirmish roll."),
            ("Heavy Hitter", "When you roll a critical hit, you may cause a catastrophic level of harm instead of standard harm."),
            ("Hired Killer", "When you engage in combat on behalf of a paying client, you may reduce stress costs by 1."),
            ("Mule", "Your load limits are higher. You can carry +2 load."),
            ("Not To Be Trifled With", "You can push yourself to do one of the following: perform a feat of physical force that verges on the superhuman; engage a small gang on equal footing in close combat."),
            ("Savage", "When you unleash physical violence, it's especially frightening. Civilians flee; gangs stagger."),
        ],
        "xp_triggers": ["Execute a successful violent job.", "Contend with challenges above your station."],
        "load": "Heavy",
    },
    "Pilot": {
        "description": "You are one with the ship. Anything that flies is an extension of your hands.",
        "starting_actions": {"Helm": 2, "Survey": 1},
        "key_actions": ["Helm", "Finesse", "Survey", "Tinker"],
        "special_abilities": [
            ("All Hands", "When you do a flashback to prepare for a job, you may call on any crew member who is present. They act as a team."),
            ("Bravado", "When you push yourself to perform a daring maneuver, take +1d to the roll."),
            ("Commander", "When you lead a crew action, you may take +1d instead of adding dice to the pool."),
            ("Cool Under Fire", "When you push yourself to resist consequences from piloting, take +1d."),
            ("Flight Plan", "When you gather information about a route or destination, you may ask one additional question for free."),
            ("Ghost Ship", "Your ship is especially hard to track. +1 effect when you attempt to evade pursuit."),
            ("Hair Trigger", "You can push yourself to take one of the following: react to any situation before it develops; act first in any tense standoff."),
            ("Mechanic's Sense", "You can feel when something is wrong with any ship you're flying. The GM will tell you of any hidden mechanical consequences before they happen."),
        ],
        "xp_triggers": ["Execute a successful maneuver under pressure.", "Make a hard call about the ship or the mission."],
        "load": "Light",
    },
    "Scoundrel": {
        "description": "You're slippery, cunning, and comfortable in the gray areas. The law is a suggestion.",
        "starting_actions": {"Prowl": 2, "Sway": 1},
        "key_actions": ["Prowl", "Finesse", "Sway", "Consort"],
        "special_abilities": [
            ("Ambush", "When you attack from hiding or spring a trap, you get +1d and you may deal your harm before the target can react."),
            ("Daredevil", "When you roll a desperate action, you get +1d for free."),
            ("Disappear", "You may expend your special armor to resist a consequence from detection or violence. When you roll to lose a tail, take +1d."),
            ("Ghost", "You can push yourself to perform supernatural feats of stealth that verge on the uncanny."),
            ("Lucky", "You start each job with +1 luck."),
            ("Slippery", "When you face a complication from the law or rival organizations, you may push yourself to simply vanish from the situation."),
            ("The Devil's Own Luck", "Each time you spend luck, gain +1d on your next roll."),
            ("Venomous", "You have a toxic touch. When you harm someone with your hands, they suffer an additional level of harm from poison."),
        ],
        "xp_triggers": ["Execute a successful heist or con.", "Betray or be betrayed by an associate."],
        "load": "Light",
    },
    "Mystic": {
        "description": "The Ur left marks on you — or you sought them out. Either way, you see what others can't.",
        "starting_actions": {"Attune": 2, "Study": 1},
        "key_actions": ["Attune", "Study", "Survey", "Command"],
        "special_abilities": [
            ("Arcane Sight", "You can see spirits and feel the flows of ether around you without attuning."),
            ("Ghost Walker", "You can move through solid objects when you push yourself. You suffer level 2 harm ('Wracked') afterward."),
            ("Heritage", "You have an unusual connection to the Ur. Take +1d when you deal with spirits, echoes, or Ur artifacts."),
            ("Ritual", "You know the ritual arcana. You can perform rituals with the Attune action."),
            ("Tempest", "When you unleash a violent Attune action, it's especially powerful. You can affect multiple targets or cause chaos in a wide area."),
            ("The Sight", "You can push yourself to sense the near future — the GM will tell you what's about to happen. You take 2 stress."),
            ("Warded", "You may expend your special armor to resist a supernatural consequence, or to push yourself when you deal with spirit energy."),
            ("Whispers", "Spirits whisper warnings to you. You're never surprised, even from sleep."),
        ],
        "xp_triggers": ["Use your arcane abilities to advance the crew's goals.", "Explore the nature of your connection to the Ur."],
        "load": "Medium",
    },
    "Speaker": {
        "description": "You get what you want through words. Charm, manipulation, intimidation — it's all just leverage.",
        "starting_actions": {"Sway": 2, "Consort": 1},
        "key_actions": ["Sway", "Consort", "Command", "Study"],
        "special_abilities": [
            ("Arcane Mind", "You're always calm and in control. +1d when you resist with Resolve."),
            ("Connected", "During downtime, you get +1 result level on Consort rolls."),
            ("Fixer", "When you arrange a deal or negotiate a contract, take +1d. When you're paid, gain +1 credit."),
            ("Ghost Voice", "You can speak with the dead. Once per job, ask a spirit one question; it must answer truthfully."),
            ("Mastermind", "You may expend your special armor to protect a teammate. When you do, they take no effect and you take 1 stress."),
            ("Opportunist", "When an enemy fails a roll against you, you may immediately make a free action against them."),
            ("Subterfuge", "You can push yourself to do one of the following: create a false identity that will hold up under scrutiny; plant a story so believable it becomes fact."),
            ("Trust No One", "You know when you're being watched or followed. +1d to Survey when looking for surveillance or informants."),
        ],
        "xp_triggers": ["Maneuver your crew into a position of advantage.", "Make a connection that changes the power balance."],
        "load": "Light",
    },
    "Stitch": {
        "description": "You keep the crew alive and the ship running. Without you, they'd all be dead — they just don't appreciate it enough.",
        "starting_actions": {"Patch": 2, "Tinker": 1},
        "key_actions": ["Patch", "Tinker", "Study", "Finesse"],
        "special_abilities": [
            ("Alchemist", "When you Tinker to create a concoction or compound, take +1d. You start with three uses of a basic alchemical substance each job."),
            ("Battlefield Medic", "When you Patch someone in the field, the consequence is one level lower."),
            ("Fortitude", "You may expend your special armor to resist a consequence from injury, or to push yourself when treating others."),
            ("Ghost Surgeon", "You can perform procedures on spirits. You know how to treat the spiritual harm that most medics ignore."),
            ("Resourceful", "When you're out of supplies, you can Tinker to improvise something useful from what's at hand. Take +1d."),
            ("Sawbones", "You can push yourself to treat a severe wound in the field — level 3 harm becomes level 2. You take 2 stress."),
            ("Steady Hands", "You're never rattled by gore or crisis. +1d on Patch rolls in chaotic situations."),
            ("Underdog", "When you're outnumbered or outgunned, take +1d to resist consequences."),
        ],
        "xp_triggers": ["Patch up the crew after a dangerous job.", "Solve a problem that requires technical expertise."],
        "load": "Medium",
    },
}


# ── Heritage ─────────────────────────────────────────────────────────────────────

HERITAGE = {
    "Hegemony": {
        "description": "Born inside the empire — you know how it works, and you know how to work it",
        "flavor": "You grew up with rules, hierarchy, and the quiet assumption that the Hegemony was forever",
    },
    "Iota": {
        "description": "From the rebel sectors and pirate havens that resist Hegemony control",
        "flavor": "You grew up knowing the Hegemony as an enemy, an occupier, or a distant threat",
    },
    "Sah'iyan": {
        "description": "From the warrior culture that the Hegemony absorbed but never quite tamed",
        "flavor": "You carry traditions and obligations older than the empire, and you know it",
    },
    "Ur": {
        "description": "Touched by the ancient alien civilization — whether by blood, artifact, or proximity",
        "flavor": "Something is different about you, and the spirits know it",
    },
    "Wanderers": {
        "description": "Born between worlds — ships, stations, asteroid belts, places without names",
        "flavor": "You have no homeworld, just a direction you were heading",
    },
}


# ── Background ───────────────────────────────────────────────────────────────────

BACKGROUND = {
    "Academic": "You studied — formally or by theft. You know things that others don't, and how to use that.",
    "Labor":    "You worked with your hands and your back. You understand what things cost in human terms.",
    "Military": "You served. The discipline stuck; so did the things you did.",
    "Nobility": "You came from comfort and status. You still know how to move in those rooms, even when you shouldn't.",
    "Trade":    "Commerce, negotiation, supply chains. You see every situation as a transaction.",
    "Underworld": "Crime was your first school. The curriculum was harsh; the graduates are useful.",
}


# ── Vice ─────────────────────────────────────────────────────────────────────────

VICE = {
    "Faith":      "Belief gives you structure. A ritual, a deity, a code — something you won't abandon.",
    "Gambling":   "Risk is the only thing that makes you feel alive. Cards, fights, bad odds.",
    "Luxury":     "You work hard so you can stop working. Fine things, comfort, one good meal.",
    "Obligation": "Someone has a claim on you — family, debt, a promise you made when you were desperate.",
    "Pleasure":   "You know what you like and you pursue it. It's not complicated.",
    "Stupor":     "Sometimes you need to stop thinking. Whatever gets you there.",
    "Weird":      "Your method of relaxation is strange, possibly alarming to others, entirely your own.",
}


# ── Action listing ───────────────────────────────────────────────────────────────

ACTIONS = {
    "Insight":  ["Hunt", "Study", "Survey", "Tinker"],
    "Prowess":  ["Finesse", "Prowl", "Skirmish", "Wreck"],
    "Resolve":  ["Attune", "Command", "Consort", "Sway"],
}

# Pilot uses "Helm" instead of Skirmish for piloting; Stitch uses "Patch" for Tinker
# These are handled in the system prompt — the tool returns the standard action list
# and the LLM substitutes playbook-specific action names where appropriate.


# ── Tools ────────────────────────────────────────────────────────────────────────

def get_playbook_info(playbook_name: str) -> str:
    if playbook_name not in PLAYBOOKS:
        return f"Unknown playbook '{playbook_name}'. Available: {list(PLAYBOOKS.keys())}"
    return json.dumps(PLAYBOOKS[playbook_name], indent=2)

def assign_action_dots(playbook_name: str) -> str:
    """
    Return a starting action-dot allocation for the playbook.
    Rules: start with playbook's preset dots, then add 4 more (max 2 in any action, max 3 total).
    """
    if playbook_name not in PLAYBOOKS:
        return f"Unknown playbook '{playbook_name}'"

    pb = PLAYBOOKS[playbook_name]
    dots: dict[str, int] = {}

    # Initialize all actions at 0
    for actions in ACTIONS.values():
        for action in actions:
            dots[action] = 0

    # Playbook-specific substitutions
    if playbook_name == "Pilot":
        dots["Helm"] = 0
        dots.pop("Skirmish", None)
    if playbook_name == "Stitch":
        dots["Patch"] = 0
        dots.pop("Tinker", None)

    # Apply starting actions
    for action, rating in pb["starting_actions"].items():
        if action in dots:
            dots[action] = rating

    # Distribute 4 bonus dots randomly (max 2 per action, max 3 total in any action)
    available = [a for a in dots if dots[a] < 2]
    bonus = 4
    while bonus > 0 and available:
        pick = random.choice(available)
        dots[pick] += 1
        if dots[pick] >= 2:
            available.remove(pick)
        bonus -= 1

    # Group by attribute for output
    grouped = {}
    for attr, actions in ACTIONS.items():
        # Swap in playbook-specific action names
        resolved = []
        for a in actions:
            if playbook_name == "Pilot" and a == "Skirmish":
                resolved.append("Helm")
            elif playbook_name == "Stitch" and a == "Tinker":
                resolved.append("Patch")
            else:
                resolved.append(a)
        grouped[attr] = {a: dots.get(a, 0) for a in resolved}

    return json.dumps(grouped, indent=2)

def roll_heritage() -> str:
    choice = random.choice(list(HERITAGE.keys()))
    return json.dumps({"heritage": choice, **HERITAGE[choice]})

def roll_background() -> str:
    choice = random.choice(list(BACKGROUND.keys()))
    return json.dumps({"background": choice, "flavor": BACKGROUND[choice]})

def roll_vice() -> str:
    choice = random.choice(list(VICE.keys()))
    return json.dumps({"vice": choice, "flavor": VICE[choice]})

def roll_dice(count: int = 2) -> str:
    """Roll a pool of d6s (standard FitD dice). Returns individual results and outcome tier."""
    count = max(1, min(count, 6))
    rolls = [random.randint(1, 6) for _ in range(count)]
    best  = max(rolls)
    if best == 6:
        outcome = "Full success (6)" if rolls.count(6) < 2 else "Critical success (6/6)"
    elif best in (4, 5):
        outcome = "Partial success (4–5)"
    else:
        outcome = "Failure (1–3)"
    return json.dumps({"rolls": rolls, "best": best, "outcome": outcome})


# ── Tool schemas ─────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_playbook_info",
        "description": "Look up a playbook's description, starting actions, key skills, special abilities, and XP triggers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "playbook_name": {
                    "type": "string",
                    "enum": list(PLAYBOOKS.keys()),
                    "description": "The character playbook to look up.",
                },
            },
            "required": ["playbook_name"],
        },
    },
    {
        "name": "assign_action_dots",
        "description": "Generate a starting action-dot allocation for the playbook. Returns dots grouped by attribute.",
        "input_schema": {
            "type": "object",
            "properties": {
                "playbook_name": {
                    "type": "string",
                    "enum": list(PLAYBOOKS.keys()),
                    "description": "Playbook to generate dots for.",
                },
            },
            "required": ["playbook_name"],
        },
    },
    {
        "name": "roll_heritage",
        "description": "Randomly determine the character's heritage (cultural/regional origin).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_background",
        "description": "Randomly determine the character's background (what they did before this life).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_vice",
        "description": "Randomly determine the character's vice (how they decompress between jobs).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_dice",
        "description": "Roll a pool of d6s for random elements during character creation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 6,
                    "description": "Number of d6s to roll.",
                },
            },
            "required": ["count"],
        },
    },
]


# ── Tool dispatcher ───────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "get_playbook_info":  return get_playbook_info(**inputs)
    if name == "assign_action_dots": return assign_action_dots(**inputs)
    if name == "roll_heritage":      return roll_heritage()
    if name == "roll_background":    return roll_background()
    if name == "roll_vice":          return roll_vice()
    if name == "roll_dice":          return roll_dice(**inputs)
    return f"Unknown tool: {name}"


# ── System prompts ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Scum and Villainy character generator (Forged in the Dark). Create vivid crew members for a life of crime at the edge of the Hegemony.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names should reflect the Hegemony's reach across many cultures — draw from a wide range of traditions (Arabic, South Asian, East Asian, West African, Slavic, Spanish, invented alien-adjacent names) and avoid clustering on similar sounds or the same first letter.

Do not output any intermediate notes, reasoning, or working text. Output only the formatted character sheet, starting directly with the ## heading.

Work through these steps using your tools:

1. PLAYBOOK — Choose a playbook that fits the story. Look it up with get_playbook_info.

2. HERITAGE — Call roll_heritage. Heritage shapes worldview and opens certain doors.

3. BACKGROUND — Call roll_background. Background is what they did before this life.

4. VICE — Call roll_vice. Vice is specific: not just "gambling" but who they gamble with and what it costs.

5. ACTIONS — Call assign_action_dots with the chosen playbook. This returns a starting action-dot spread.

6. SPECIAL ABILITY — Choose one from the playbook's list. The first one is often a safe default; pick the one that fits this character's story.

7. XP TRIGGERS — Include both XP triggers for the playbook. They drive play.

Notes on format:
- Action dots use filled/empty circles: ● for each dot, ○ for empty (max 4 per action)
- Show all actions grouped by attribute (Insight / Prowess / Resolve)
- Pilot uses Helm instead of Skirmish; Stitch uses Patch instead of Tinker
- Vice purveyor should be a specific named person or place, not a category

Always use exactly this format:

## **[Full Name]**
*[Playbook] — [one sharp sentence that places them in the Hegemony's margins]*

| | |
|---|---|
| **Playbook** | [Playbook] |
| **Heritage** | [Heritage] |
| **Background** | [Background] |
| **Vice** | [Vice] / [Purveyor — specific name and place] |

### Actions

**Insight**
| Action | Rating |
|--------|--------|
| Hunt | [●○○○] |
| Study | [●●○○] |
| Survey | [○○○○] |
| Tinker | [○○○○] |

**Prowess**
| Action | Rating |
|--------|--------|
| Finesse | [○○○○] |
| Prowl | [●○○○] |
| Skirmish | [●●○○] |
| Wreck | [○○○○] |

**Resolve**
| Action | Rating |
|--------|--------|
| Attune | [○○○○] |
| Command | [○○○○] |
| Consort | [●○○○] |
| Sway | [○○○○] |

(Use actual dots/circles from the action roll output. Replace Skirmish with Helm for Pilot, Tinker with Patch for Stitch.)

### Special Ability
**[Ability Name]** — [full description]

### XP Triggers
- [First trigger]
- [Second trigger]

### Stress & Trauma
**Stress:** ○○○○○○○○○ (9 boxes)
**Trauma:** ☐ Cold ☐ Haunted ☐ Obsessed ☐ Paranoid ☐ Reckless ☐ Soft ☐ Unstable ☐ Vicious

### Load
**Standard Load:** [Light / Medium / Heavy based on playbook]

### Backstory
Three sentences. A past, a wound, and a direction. They ended up in a crew at the edge of the Hegemony — that wasn't the plan. Make it feel specific."""


NPC_SYSTEM_PROMPT = """You are a Scum and Villainy NPC generator (Forged in the Dark). Create a vivid, instantly usable character sketch for a crew operating at the Hegemony's margins.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names should reflect the Hegemony's reach across many cultures — draw from a wide range of traditions and avoid clustering on similar sounds or the same first letter.

Call roll_heritage and roll_background for grounding. Skip the full chargen — this is a sketch.

Always use exactly this format:

## **[Name]**
*[Role or occupation] — [one sharp hook sentence]*

| | |
|---|---|
| **Playbook** | [Closest playbook, or original role] |
| **Heritage** | [Heritage] |
| **Background** | [Background] |
| **Vice** | [Vice] / [specific purveyor] |

**Key Actions:** [two or three notable actions at d8+ equivalent, described in plain language]

**Demeanor:** [1–2 sentences — how they present, what you notice first]
**Wants:** [what they need right now — specific]
**Secret:** [one thing they're hiding — specific, not vague]
**Hook:** [one concrete way they pull the crew into their business]
**Connection:** [one named person they love, fear, or owe — and why it matters]"""


SCORE_CONTACT_SYSTEM_PROMPT = """You are a Scum and Villainy score contact generator (Forged in the Dark). Create a complete encounter — someone who approaches the crew with a score. Every score in the Hegemony's shadow has something underneath it, and no one who needs criminals for a job is telling the whole story.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits and motives should be specific and individual — not cultural shorthand.

Names should reflect the Hegemony's reach across many cultures — vary first letters, syllable counts, and cultural origins.

Do not output any intermediate notes or working text. Output only the formatted contact, starting directly with the ## heading.

The GM rolls 1d4 in secret to determine which truth is real — only one is. Truth 4 is always The Reversal, where the crew is on the wrong side of the score. Write all four so any one could be true until contradicted.

Always use exactly this format:

## **[Name]**
*[Faction or role] — [one sharp sentence about who they are in the underworld]*

| | |
|---|---|
| **Faction** | [Hegemony / Church of Stellar Flame / Brekker Syndicate / Independents / etc.] |
| **Appears to be** | [their cover or surface identity] |
| **Actually is** | *(revealed only in Truth 2, 3, or 4 below)* |

**Appearance:** [what the crew notices first — one specific detail that's off about them]

**The Pitch:** *"[The offer in their own voice — how they frame it, what they emphasize, what they skip over. At least three sentences. The crew should be able to hear the angle.]"*

**The Score:** [Concrete description of what they need done — target, location, method, timeline.]

**The Payment:** [Coin, Rep, favors, reduced Heat, faction protection — specific amounts and what they mean to a crew that needs them.]

**The Heat:** [How much Hegemony attention this score carries — and why. A score with low Heat has a reason; a score with high Heat has a worse one.]

**The Truth (GM rolls 1d4 in secret — only one is real):**

1. **Straightforward** — [Score is what it looks like. One real complication in the doing of it — a rival crew, a security detail, a target who isn't where they're supposed to be.]

2. **One Layer Down** — [Something the contact omitted. Changes what the crew is walking into without changing the basic shape of the score.]

3. **The Real Story** — [The contact is operating inside something larger — a faction play, a personal vendetta, a Hegemony trap being set for someone else. The crew's score is a piece of it.]

4. **The Reversal** — [The crew is on the wrong side. The target deserved better; the contact is the real villain; what looked like a score is actually the crew doing harm to people who can't fight back. The contact may believe their own framing. The dice don't care.]

**Why They'd Take It:** [The real calculation — Rep, coin, Heat reduction, or something one crew member specifically needs. Make it feel like a choice, not a trap. It should be tempting even after the session.]

**Connection:** [One named person in the underworld who knows this contact — what they'd say if asked, and what it points toward.]"""


# ── Phase tracker ─────────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "playbook":    "Choosing playbook...",
    "heritage":    "Rolling heritage...",
    "background":  "Rolling background...",
    "vice":        "Rolling vice...",
    "actions":     "Assigning action dots...",
}

def detect_phase(tool_name: str) -> str | None:
    if tool_name == "get_playbook_info":  return "playbook"
    if tool_name == "roll_heritage":      return "heritage"
    if tool_name == "roll_background":    return "background"
    if tool_name == "roll_vice":          return "vice"
    if tool_name == "assign_action_dots": return "actions"
    return None


# ── Agentic loop ──────────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    messages = [{"role": "user", "content": prompt}]
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
                    new_phase = detect_phase(block.name)
                    if new_phase and new_phase != phase:
                        phase = new_phase
                        print(PHASE_MESSAGES[phase])

                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})


# ── Save ──────────────────────────────────────────────────────────────────────────

def save_result(result: str, mode: str) -> Path:
    first_line = next(
        (l for l in result.strip().splitlines() if l.startswith("##")),
        result.strip().splitlines()[0],
    )
    name_raw  = re.sub(r"[#*]", "", first_line).strip()
    name_slug = re.sub(r"[^a-z0-9]+", "-", name_raw.lower()).strip("-")
    filename  = f"{name_slug}-{mode}.md"

    output_dir = Path(__file__).parent / "characters" / "scum_villainy"
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    if filepath.exists():
        stem = filepath.stem
        counter = 2
        while filepath.exists():
            filepath = output_dir / f"{stem}-{counter}.md"
            counter += 1
    filepath.write_text(result)
    return filepath


# ── Entry point ───────────────────────────────────────────────────────────────────

def run(mode: str | None = None, desc: str | None = None) -> None:
    if mode is None:
        mode = input("Mode? (full / npc / scorecontact, default: full): ").strip().lower()
        mode = mode if mode in ("full", "npc", "scorecontact") else "full"
    label = {"full": "character", "npc": "NPC", "scorecontact": "score contact"}[mode]
    if desc is None:
        desc = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt = (
            f"Generate a Scum and Villainy NPC with these constraints: {desc}"
            if desc else
            "Generate a fully random Scum and Villainy NPC."
        )
    elif mode == "scorecontact":
        sys_prompt = SCORE_CONTACT_SYSTEM_PROMPT
        prompt = (
            f"Generate a Scum and Villainy score contact encounter with these constraints: {desc}"
            if desc else
            "Generate a fully random Scum and Villainy score contact encounter."
        )
    else:
        sys_prompt = SYSTEM_PROMPT
        prompt = (
            f"Generate a Scum and Villainy character with these constraints: {desc}"
            if desc else
            "Generate a fully random Scum and Villainy character."
        )

    result = run_agent(prompt, sys_prompt)

    # Strip any preamble before the first ## heading
    lines = result.strip().splitlines()
    heading_idx = next((i for i, l in enumerate(lines) if l.startswith("##")), 0)
    result = "\n".join(lines[heading_idx:])

    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
