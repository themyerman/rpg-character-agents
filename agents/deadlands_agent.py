"""
Deadlands: The Weird West Character Generator (Savage Worlds / Pinnacle Entertainment)
Creates gunslingers, blessed, hucksters, and other survivors of the Weird West.

Run with: python deadlands_agent.py
"""

import json
import random
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.names import roll_name_suggestion, NAME_TOOL_SCHEMA
from lib.gear import roll_deadlands_gear, DEADLANDS_GEAR_TOOL_SCHEMA
from lib.utils import get_client, run_agent_loop, save_character, strip_preamble
from lib.safety import sanitize_desc, screen_desc, wrap_desc, screen_output


# ── Archetypes ─────────────────────────────────────────────────────────────────

ARCHETYPES: dict[str, dict] = {
    "Gunfighter": {
        "description": "The fastest draw in the territory, or trying to be. You've built a reputation on speed and accuracy, and now the reputation follows you everywhere you don't want it.",
        "key_attributes": ["Agility d10"],
        "key_skills": ["Shooting", "Fighting", "Intimidation", "Notice"],
        "typical_edges": ["Quick Draw", "Dead Shot", "Two-Fisted", "Marksman"],
        "typical_hindrances": ["Big Mouth", "Overconfident", "Wanted", "Vengeful"],
        "arcane_background": None,
        "flavor": "reputation is a target, and there's always someone who wants to collect it",
    },
    "Blessed": {
        "description": "Your faith isn't metaphor — it works. In a world where the dead walk and something is poisoning the land, genuine miracles are rarer than the preachers claim and you've got them.",
        "key_attributes": ["Spirit d10"],
        "key_skills": ["Faith", "Persuasion", "Healing", "Notice"],
        "typical_edges": ["Arcane Background (Blessed)", "Healer", "Holy Warrior", "Inspire"],
        "typical_hindrances": ["Vow", "Heroic", "Code of Honor", "Stubborn"],
        "arcane_background": "Blessed — miracles powered by genuine faith; power fades if you lose your way",
        "flavor": "the proof that something is still listening, out here in the dark",
    },
    "Huckster": {
        "description": "You gamble for power, dealing cards with literal demons to fuel hexes and tricks. Your luck has held so far. The demons are patient about the other kind of luck.",
        "key_attributes": ["Smarts d10", "Spirit d8"],
        "key_skills": ["Spellcasting", "Gambling", "Streetwise", "Notice"],
        "typical_edges": ["Arcane Background (Huckster)", "Luck", "Gambler", "Scholar"],
        "typical_hindrances": ["Poverty", "Habit", "Quirk", "Overconfident"],
        "arcane_background": "Huckster — hexes powered by gambling against a manitou; losing a hand has consequences",
        "flavor": "the one dealing from a deck that nobody else can read",
    },
    "Shaman": {
        "description": "The Great Spirits have given you power because the Reckoners are winning and something has to push back. You carry your people's history in one hand and whatever this land is becoming in the other.",
        "key_attributes": ["Spirit d10"],
        "key_skills": ["Focus", "Persuasion", "Survival", "Healing", "Notice"],
        "typical_edges": ["Arcane Background (Shaman)", "Beast Bond", "Danger Sense", "Woodsman"],
        "typical_hindrances": ["Outsider", "Vow", "Loyal", "Code of Honor"],
        "arcane_background": "Shaman — spirit powers tied to a specific nation and its sacred compact with the land",
        "flavor": "the memory of what this land was and the question of what it becomes",
        "note": "Shaman characters should be grounded in a specific nation (Sioux, Cheyenne, Apache, Comanche, etc.) with individual history. The Weird West has fractured the United States but strengthened many Native nations — the Sioux Confederacy holds the Hunting Grounds and its sovereignty is real. Avoid generic pan-Native stereotypes. This character has a specific community, specific obligations, and specific reasons for being far from home.",
    },
    "Mad Scientist": {
        "description": "Ghost rock fuels your inventions and slowly erodes your sanity. You build things that shouldn't work, powered by a mineral that shouldn't exist, and somewhere in the back of your mind the Reckoners are leaving you notes.",
        "key_attributes": ["Smarts d10"],
        "key_skills": ["Weird Science", "Repair", "Shooting", "Notice", "Knowledge (Science)"],
        "typical_edges": ["Arcane Background (Mad Scientist)", "McGyver", "Mr. Fix It", "Scholar"],
        "typical_hindrances": ["Habit (ghost rock fumes)", "Quirk", "Overconfident", "Phobia"],
        "arcane_background": "Mad Scientist — ghost rock powered gadgets; the more powerful the device, the more it costs the inventor",
        "flavor": "the proof that this new power comes with a price nobody budgeted for",
    },
    "Harrowed": {
        "description": "You died. Something came back. There's a manitou in there with you — an evil spirit that shares your body, sees through your eyes, and is learning your habits. You're on the same side, for now. The manitou is patient.",
        "key_attributes": ["Vigor d10"],
        "key_skills": ["Intimidation", "Shooting", "Fighting", "Notice"],
        "typical_edges": ["Harrowed", "Supernatural Powers", "Fearless", "Hard to Kill"],
        "typical_hindrances": ["Habit", "Mean", "Outsider", "Ugly"],
        "arcane_background": "Harrowed — undead with supernatural abilities; the manitou can seize control when the character is weak, unconscious, or loses a Spirit contest",
        "flavor": "the one who came back wrong and is trying to use that productively",
    },
    "Bounty Hunter": {
        "description": "You track people — and other things — for pay. Patient, methodical, and very good at finding what doesn't want to be found. The wanted posters get stranger every year and you've stopped asking questions about the ones that aren't entirely human.",
        "key_attributes": ["Agility d8", "Smarts d8"],
        "key_skills": ["Tracking", "Shooting", "Stealth", "Notice", "Streetwise"],
        "typical_edges": ["Investigator", "Danger Sense", "Tracker", "Level Headed"],
        "typical_hindrances": ["Vow", "Wanted", "Vengeful", "Code of Honor"],
        "arcane_background": None,
        "flavor": "the one who always finds what they're looking for and sometimes wishes they hadn't",
    },
    "Doc": {
        "description": "Frontier physician, which means you work with what's available in conditions that would make a city surgeon faint. You've seen wounds that shouldn't exist, patients who walk away from impossible things, and you've learned not to write down everything you observe.",
        "key_attributes": ["Smarts d10"],
        "key_skills": ["Healing", "Knowledge (Medicine)", "Persuasion", "Notice"],
        "typical_edges": ["Healer", "Scholar", "Steady Hands", "Connections"],
        "typical_hindrances": ["Habit (laudanum)", "Vow", "Poverty", "Pacifist"],
        "arcane_background": None,
        "flavor": "the one who keeps everyone alive and tries not to think too hard about how",
    },
    "Drifter": {
        "description": "No home, no roots, seen too much. You pass through towns like weather. You know how the West works — the real West, not the one in the dime novels — and you've stopped being surprised by the things that live in the dark places.",
        "key_attributes": ["Agility d8", "Smarts d6"],
        "key_skills": ["Streetwise", "Notice", "Stealth", "Survival", "Shooting"],
        "typical_edges": ["Luck", "Danger Sense", "Woodsman", "Improvisational Fighter"],
        "typical_hindrances": ["Habit", "Outsider", "Quirk", "Poverty"],
        "arcane_background": None,
        "flavor": "the one who has been everywhere and settled nowhere and carries both of those things",
    },
    "Cowboy": {
        "description": "You know cattle, horses, rope, and land. The range is home — or it was, before whatever's happening to the West started happening harder. You're practical, tough, and very good at staying alive in open country that wants to kill you.",
        "key_attributes": ["Strength d8", "Vigor d8"],
        "key_skills": ["Riding", "Shooting", "Survival", "Lasso", "Notice"],
        "typical_edges": ["Brawny", "Woodsman", "Beast Bond", "Quick"],
        "typical_hindrances": ["Loyal", "Code of Honor", "Stubborn", "Obligation"],
        "arcane_background": None,
        "flavor": "the one who knows the land better than anyone wants to know it right now",
    },
    "Lawman": {
        "description": "Sheriff, marshal, Texas Ranger, Pinkerton — you hold the line because somebody has to. The job keeps getting harder because the things crossing that line keep getting stranger. You've filed enough reports on things you can't explain that you've stopped filing them.",
        "key_attributes": ["Agility d8", "Spirit d8"],
        "key_skills": ["Shooting", "Fighting", "Intimidation", "Investigation", "Notice"],
        "typical_edges": ["Command", "Connections", "Level Headed", "Quick Draw"],
        "typical_hindrances": ["Code of Honor", "Vow", "Stubborn", "Obligation"],
        "arcane_background": None,
        "flavor": "the one still trying to make the old rules work in the new world",
    },
}


# ── Hindrances ─────────────────────────────────────────────────────────────────

HINDRANCES: list[dict] = [
    # Major hindrances (worth 2 character points each)
    {"name": "All Thumbs", "severity": "Major", "description": "Machines break in your hands. Tools misfire. Gadgets malfunction specifically when you touch them. This has been the story of your life."},
    {"name": "Big Mouth", "severity": "Major", "description": "You cannot keep a secret and you cannot keep your mouth shut. You have said the wrong thing at the wrong moment more times than you can count."},
    {"name": "Bloodthirsty", "severity": "Major", "description": "You don't take prisoners. You have your reasons. They are not good enough for some of the people who ride with you."},
    {"name": "Death Wish", "severity": "Major", "description": "You are looking for a death with meaning. You've been finding situations that might provide one. So far nothing has been quite enough."},
    {"name": "Doubting Thomas", "severity": "Major", "description": "Whatever the Weird West has done to you, you refuse to accept that what you're seeing is actually supernatural. You will find a rational explanation. This gets people killed, including occasionally you."},
    {"name": "Habit (Major)", "severity": "Major", "description": "Laudanum, whiskey, ghost rock fumes, or something worse. You need it to function and you need more of it than you should."},
    {"name": "Lame", "severity": "Major", "description": "An old wound, a bad fall, a doctor who did their best and it wasn't enough. You move slower than most. You've learned to compensate in ways that don't require running."},
    {"name": "Mean", "severity": "Major", "description": "You are not kind. You have not been kind in a long time. You're not sure you remember how."},
    {"name": "Vengeful (Major)", "severity": "Major", "description": "There is a name — or a face — that you will not stop hunting. You will risk everything for it. You have already risked most things."},
    {"name": "Wanted (Major)", "severity": "Major", "description": "There's real money on your head and active pursuit. The law, a gang, a railroad man, or something worse. They don't take you alive if they can help it."},
    # Minor hindrances (worth 1 character point each)
    {"name": "Bad Eyes", "severity": "Minor", "description": "Distance is a problem. You've borrowed enough people's spectacles to know what you're missing."},
    {"name": "Code of Honor", "severity": "Minor", "description": "There are things you will not do, regardless of how much it would help. You've paid for this standard more than once."},
    {"name": "Curious", "severity": "Minor", "description": "You cannot leave a mystery alone. This is why you're always the one who opens the wrong door."},
    {"name": "Hard of Hearing", "severity": "Minor", "description": "Too many gunshots, a sickness, a fight that went wrong. You miss things. You ask people to repeat themselves. You pretend sometimes that you heard when you didn't."},
    {"name": "Heroic", "severity": "Minor", "description": "You cannot refuse a call for help. This is not wisdom and you know it. You show up anyway."},
    {"name": "Loyal", "severity": "Minor", "description": "You don't leave people behind. This has made your life significantly more complicated than it needed to be."},
    {"name": "Obligation", "severity": "Minor", "description": "Someone or something has a claim on your time, your service, or your conscience. You cannot ignore it when it calls."},
    {"name": "Quirk", "severity": "Minor", "description": "A specific habit, ritual, or behavioral tic that marks you as unusual. It is harmless until it isn't."},
    {"name": "Stubborn", "severity": "Minor", "description": "You are right until proven wrong, and your standard of proof is higher than most. This has saved your life and cost you friendships."},
    {"name": "Ugly", "severity": "Minor", "description": "The West has not been kind to your face. People react before they think, and their first reaction is not favorable."},
    {"name": "Habit (Minor)", "severity": "Minor", "description": "Something you reach for too often — tobacco, a particular drink, a ritual that has to happen before you're ready. It's a distraction when you can't get it."},
    {"name": "Cautious", "severity": "Minor", "description": "You plan. You wait. You assess. Sometimes the situation needed someone to move three minutes ago."},
]


# ── Weird West patron hooks ────────────────────────────────────────────────────

WEIRD_WEST_HOOKS: list[dict] = [
    {
        "type": "Bounty Contract",
        "description": "A wanted poster for someone dangerous — or something. The money is real. The bounty office has stopped asking questions about whether you bring them back alive.",
        "complications": [
            "The wanted party isn't guilty of what's on the poster. Someone with money and connections arranged the paper on them and is watching to see if the job gets done.",
            "The mark has already been caught once and got out. Nobody explains how. The last bounty hunter who brought them in never filed a final report.",
            "The reward is posted by a private party, not a government. The private party's interest in this individual goes beyond whatever crime is printed on the paper.",
        ],
    },
    {
        "type": "Railroad Commission",
        "description": "One of the great rail lines has a job for capable hands — Stone's rail network, Kang's Celestial Railroad, Hellstromme Industries, or the Bayou Vermilion. The pay is generous. The reasons given for why they can't use their own people are vague.",
        "complications": [
            "The job puts the crew directly against one of the other rail companies. The railroad offering the contract knows this. They are using the crew to do something they don't want their name on.",
            "The site the crew is being sent to is on land with a prior claim — Native, Mexican, or homestead — that the railroad wants quietly ignored.",
            "The railroad's interest in this particular stretch of territory is not commercial. Something was found here during the survey. The survey crew didn't report back.",
        ],
    },
    {
        "type": "Agency Assignment",
        "description": "The Agency — Washington's secret arm for suppressing knowledge of the Reckoning — needs deniable operators for something that can't be on the official record. They're polite about it. The politeness doesn't cover what happens if you say no.",
        "complications": [
            "The Agency has been working this problem for three years. The crews they sent before didn't come back, or came back wrong. They're not telling you this.",
            "The assignment has civilian casualties baked into the acceptable outcome range. The Agency's calculus is cold. Yours may not be.",
            "Someone in the Agency is the reason this problem exists. The handler who briefed you is either the someone, or knows who is, and is watching to see if the crew figures it out.",
        ],
    },
    {
        "type": "Missing Person",
        "description": "Someone's family member, business partner, or old friend rode into the wrong territory and hasn't come back. The reward is everything the hirer has left. They know what they're asking.",
        "complications": [
            "The missing person went looking for something specific — a rumor, a map, a person. What they found is why they haven't come back, and now the crew knows the same direction.",
            "The missing person is not as missing as advertised. They went deliberately and they don't want to be found. Understanding why is more dangerous than not knowing.",
            "Someone else is also looking for the missing person. They have more resources and less concern for the missing person's wellbeing.",
        ],
    },
    {
        "type": "Haunted Territory",
        "description": "A ranch, a mine, a crossroads town — something is wrong with a piece of land and the people on it are dying or leaving or going mad. The landowner can pay. The preacher has already tried. The sheriff sent one deputy who came back with nothing useful to say.",
        "complications": [
            "The haunting is not accidental. Someone caused it — a wrong done to the land or its people that has been festering since before the crew was born.",
            "The thing haunting this land is not hostile. It is trying to communicate something that nobody has been willing to listen to. The violence is a symptom of the failure to listen.",
            "The landowner knows what caused this. They are the reason it started. Their money is guilt money and they have told the crew a version of events that exonerates them.",
        ],
    },
    {
        "type": "Texas Ranger Request",
        "description": "One Ranger. One county the size of a small country. Things happening in six places at once that require someone to ride toward them. The Ranger needs backup they can trust to keep quiet about what they find.",
        "complications": [
            "The Ranger's jurisdiction is being contested by a local power — a rancher, a railroad, a sheriff with a different boss. The crew's presence will be used as evidence of federal overreach.",
            "The Ranger knows more about the weird side of the West than they've shared. They've been classifying encounters as 'cattle rustling' and 'weather events' for two years. This one can't be filed that way.",
            "The thing the Ranger is tracking has been tracking them back. For longer than they know.",
        ],
    },
    {
        "type": "Ghost Rock Trouble",
        "description": "A ghost rock claim — mine, processing facility, or transport operation — has hit a problem that the investors want handled quietly before the press or the competition finds out about it.",
        "complications": [
            "The problem started when the ghost rock vein got deeper. What they found at the new depth is not ghost rock, and it has been there a very long time.",
            "The workers who found the problem are currently unaccounted for. The management is describing this as a labor dispute. The crew's job is to go in where the workers went and find out what a 'labor dispute' actually looked like.",
            "The ghost rock from this claim has been behaving differently from other deposits. Hellstromme's people have been asking questions about the source. The mine owner is not sure if Hellstromme is interested in buying or in burying.",
        ],
    },
    {
        "type": "Cattle Drive",
        "description": "Move a herd through difficult territory. The trail boss is short-handed, the route goes through land that's been problematic lately, and someone doesn't want these cattle to reach market.",
        "complications": [
            "The cattle are behaving strangely since the drive entered a particular stretch of territory. Animals don't spook like this without a reason, and the trail boss has been on enough drives to know this isn't weather.",
            "Someone already made an offer on this herd at below-market value and was refused. The refusal was a week ago. The trouble started five days ago.",
            "The route goes through land with a prior claim. The claimants knew the drive was coming. They sent someone to meet it and that someone hasn't returned to report.",
        ],
    },
]


# ── Tool functions ─────────────────────────────────────────────────────────────

def get_archetype_info(archetype_name: str) -> str:
    """Return full archetype details for a Deadlands character."""
    if archetype_name not in ARCHETYPES:
        return json.dumps({
            "error": f"Unknown archetype '{archetype_name}'.",
            "available": list(ARCHETYPES.keys()),
        })
    return json.dumps(ARCHETYPES[archetype_name])


def roll_hindrance() -> str:
    """Return a random Deadlands hindrance."""
    h = random.choice(HINDRANCES)
    return json.dumps(h)


def roll_weird_west_hook() -> str:
    """Return a random Weird West job type and complication seed."""
    hook         = random.choice(WEIRD_WEST_HOOKS)
    complication = random.choice(hook["complications"])
    return json.dumps({
        "job_type":    hook["type"],
        "description": hook["description"],
        "complication": complication,
    })


def roll_dice(sides: int, count: int = 1) -> str:
    valid = {4, 6, 8, 10, 12}
    if sides not in valid:
        return f"Error: Savage Worlds uses d4, d6, d8, d10, d12. Got d{sides}."
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"


# ── Tool schemas ───────────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    NAME_TOOL_SCHEMA,
    DEADLANDS_GEAR_TOOL_SCHEMA,
    {
        "name": "get_archetype_info",
        "description": (
            "Look up an archetype's key attributes, skills, edges, hindrances, and flavor. "
            "Call this immediately after committing to an archetype."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "archetype_name": {
                    "type": "string",
                    "description": "The character archetype.",
                    "enum": list(ARCHETYPES.keys()),
                },
            },
            "required": ["archetype_name"],
        },
    },
    {
        "name": "roll_hindrance",
        "description": (
            "Get a random Deadlands hindrance (Major or Minor character flaw). "
            "Call this 1–2 times per character — hindrances fund Edges and starting advances."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_weird_west_hook",
        "description": (
            "Get a random Weird West job type and complication seed for a patron encounter. "
            "Call this when generating a contact or patron."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_dice",
        "description": "Roll Savage Worlds dice (d4, d6, d8, d10, d12).",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {
                    "type": "integer",
                    "description": "Die type.",
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
]


# ── System prompts ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Deadlands: The Weird West character generator (Savage Worlds system / Pinnacle Entertainment). Create vivid, story-ready characters for the American West of 1876 — an alternate history where the Civil War ground to a bloody stalemate, the dead walk, and something is poisoning the land itself.

The tone is Gothic Western: grit, dust, moral weight, and genuine horror lurking at the edges of a world that's already hard enough. These are real people with real histories in a West that includes Black cowboys and soldiers, Mexican vaqueros and pistoleros, Native nations fighting for sovereignty with real power behind them, immigrants building lives alongside everyone else. Do not flatten this history to clichés. Every character should be specific: where they're from, what they've done, what it cost.

Avoid clichés tied to race, gender, or origin. Arcane backgrounds (Blessed, Huckster, Shaman, Mad Scientist, Harrowed) should be treated with the full weight they carry — they are not mere mechanics, they are relationships with the supernatural that cost something real.

Call roll_name_suggestion() before naming anyone. Use the result as a starting point — period-appropriate names from any American tradition of the 1870s: Anglo, Spanish, Scots-Irish, West African, Chinese, German, Native.

Do not output any intermediate notes. Output only the formatted character sheet, starting directly with the ## heading.

STEP 0 (before writing anything):
1. Choose an archetype (or use the user's request). Call get_archetype_info(archetype_name).
2. Call roll_hindrance() once or twice — these are the flaws that make the character human.
3. Call roll_name_suggestion() for the name.
4. Call roll_deadlands_gear(archetype_name) for equipment.

CHARACTER SHEET FORMAT — use exactly this structure:

## **[Full Name]**
*[Archetype] — [one sharp sentence about who this person is and what they carry into the West]*

| | |
|---|---|
| **Archetype** | [Archetype] |
| **Background** | [Occupation or origin — specific, not generic] |
| **Alignment** | [Good / Conflicted / Neutral / Complicated] |
| **Arcane Background** | [if applicable] |

### Attributes
Assign trait dice (d4–d12). Starting characters have 5 attribute points; each step costs 1 point. Arcane backgrounds and some edges modify these. Show the die size, not a number.

| Agility | Smarts | Spirit | Strength | Vigor |
|---------|--------|--------|----------|-------|
| [dX] | [dX] | [dX] | [dX] | [dX] |

### Skills
Skills are tied to an attribute and rated in die sizes. List 6–8 relevant skills. Key skills for this archetype should be d8 or higher.
- [Skill] d[X] ([Attribute])
- ...

### Edges
Choose 1–3 Edges appropriate to the archetype and backstory. Write each as what it means for this specific person, not just what it does mechanically.
- **[Edge]:** [What this means for this character — specific, personal]

### Hindrances
Use the rolls from roll_hindrance(). Write each as this character's specific version of the flaw — not the generic description, but what it looks like lived from the inside.
- **[Hindrance]** ([Major/Minor]): [This character's specific version]

### Wounds & Bennies
- **Wounds:** 0 (3 before Incapacitation; Harrowed may differ)
- **Bennies:** 3 per session (standard Wild Card allotment)

### Equipment
List every item from roll_deadlands_gear(). Make each item feel specific and worn-in — a tool with a history, a weapon with a story. The personal item is last; give it a sentence.

### Personality
- **Trait:** [One specific behavioral habit — how they act under stress, with strangers, in a fight]
- **Ideal:** [What they're trying to hold onto or build — even if it costs them]
- **Bond:** [A specific person or place they carry with them]
- **Flaw:** [What the Hindrance looks like from inside the character]

### Connections
- **Ally — [Name]:** [Who they trust and the specific reason]
- **Enemy — [Name]:** [Who they're in conflict with and why it's personal]

### Backstory
Two or three paragraphs. Start before the character entered the Weird West — what were they before? Then: what changed? The Reckoning needs a specific moment — a thing they saw, a thing they did, a thing that was done to them that cracked the ordinary world open and showed them what was underneath. End with where they are now and what they're looking for — not vaguely, but specifically: a name, a place, a debt."""


NPC_SYSTEM_PROMPT = """You are a Deadlands: The Weird West NPC generator (Savage Worlds / Pinnacle Entertainment). Create a vivid, instantly usable NPC sketch for a session in the Weird West.

These NPCs live in the same world: real people in a real 1876 with all its weight — racial tension, economic brutality, gender constraints, and the specific horror of a land that has been made worse by something supernatural. They should feel like people who have been surviving this, not characters who exist to serve a plot.

Avoid clichés tied to race, gender, or origin. Call roll_name_suggestion() before naming anyone.

Do not output intermediate notes. Output only the formatted NPC, starting directly with the ## heading.

STEP 0: Call roll_name_suggestion(). Call get_archetype_info() if the NPC has a clear archetype. Call roll_hindrance() for their defining flaw.

Always use exactly this format:

## **[Name]**
*[Occupation or role] — [one sharp sentence about who this person is in the Weird West]*

| | |
|---|---|
| **Alignment** | [Good / Conflicted / Neutral / Dangerous] |
| **Location** | [Where they're usually found] |

**Appearance:** [What someone notices — two details, one of which tells a story]

**Demeanor:** [How they present themselves — the gap between the surface and what's underneath]

**Wants:** [What they say they want — specific and credible]

**Secret:** [What they actually need, fear, or know — the real engine of their behavior]

**Hook:** [How they pull the player characters into their situation]

**Equipment:** [2–3 items — at least one that doesn't fit the stated identity or occupation]

**Connection:** [One named person or faction who links this NPC to something larger — and what that link costs them]"""


CONTACT_SYSTEM_PROMPT = """You are a Deadlands: The Weird West patron generator (Savage Worlds / Pinnacle Entertainment). Create a complete encounter — someone who walks into the right bar at the wrong time and offers the posse a job. In the Weird West, nobody who needs to hire strangers is telling the whole story. The money is always real. The reasons never are.

Avoid clichés tied to race, gender, or origin. Call roll_name_suggestion() before naming anyone.

Do not output intermediate notes. Output only the formatted contact, starting directly with the ## heading.

STEP 0 (before writing anything): Call roll_name_suggestion() for the contact's name. Call roll_weird_west_hook() for the job type and complication seed. Build everything around what these tools return. Do not default to a generic ranch hand or whiskey job unless roll_weird_west_hook explicitly returns that type.

The GM rolls 1d4 in secret to determine which truth is real — only one is. Truth 4 is always The Real West, where the posse is on the wrong side of history — working for the person or force that is doing the harm, willingly or not. Write all four so any one could be true until contradicted.

Always use exactly this format:

## **[Name]**
*[Occupation] — [one sharp sentence placing them in the Weird West]*

| | |
|---|---|
| **Appears to be** | [their stated identity and why they need outside help] |
| **Actually is** | *(revealed only in Truth 2, 3, or 4 below)* |

**Appearance:** [What the posse notices — two details. One is exactly what it looks like. One isn't.]

**The Pitch:** *"[The ask in their own voice — pressured, specific, shaped. At least three sentences. The posse should be able to hear the desperation or the calculation behind the words.]*"

**The Job:** [What they want done — where, who, what, by when. Concrete.]

**The Payment:** [What's on the table — dollars, information, horses, a deed, a favor from someone with a name. Specific amounts.]

**The Truth (GM rolls 1d4 in secret — only one is real):**

1. **Straightforward** — [The job is what it sounds like. One real complication that has nothing to do with the contact — something the posse will encounter in the doing of it, not a deception by the hirer.]

2. **One Layer Down** — [Something the contact left out. Not a lie — a shaped truth that changes the shape of the job once the posse finds it. The contact may think it's irrelevant. They are wrong about that.]

3. **The Real Story** — [What the contact is actually operating inside — a family situation, a factional war, a corporate play, a cover-up already in motion. The job is real but it's a piece of something larger that the contact either understands or is being used by.]

4. **The Real West** — [The posse is on the wrong side of this. The target deserved better; the contact is the source of the harm; what was called a job is actually the posse being used as instruments against people who have done nothing wrong. The contact may believe their own version of events. The land, and the people on it, will remember what the posse chose.]

**Why They'd Take It:** [The practical reason — money, information, something a specific member of the posse specifically needs. Make it feel like a real calculation, not a setup. It should be tempting even after the truth comes out.]

**Connection:** [One named person who knows this contact — what they'd say if the posse asked, and what it points toward without making it obvious which truth the dice chose.]"""


# ── Phase tracker ──────────────────────────────────────────────────────────────

PHASE_MESSAGES: dict[str, str] = {
    "name":       "Rolling name...",
    "archetype":  "Choosing archetype...",
    "hindrance":  "Rolling hindrance...",
    "hook":       "Rolling weird west hook...",
    "gear":       "Rolling gear...",
}


def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_name_suggestion":  return "name"
    if tool_name == "get_archetype_info":    return "archetype"
    if tool_name == "roll_hindrance":        return "hindrance"
    if tool_name == "roll_weird_west_hook":  return "hook"
    if tool_name == "roll_deadlands_gear":   return "gear"
    return None


# ── Run tool dispatcher ────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_name_suggestion":  return roll_name_suggestion()
    if name == "get_archetype_info":    return get_archetype_info(inputs["archetype_name"])
    if name == "roll_hindrance":        return roll_hindrance()
    if name == "roll_weird_west_hook":  return roll_weird_west_hook()
    if name == "roll_deadlands_gear":   return roll_deadlands_gear(inputs.get("archetype_name", ""))
    if name == "roll_dice":             return roll_dice(inputs["sides"], inputs.get("count", 1))
    return f"Unknown tool: {name}"


# ── Agentic loop ───────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    return run_agent_loop(
        prompt, system_prompt, TOOLS, run_tool, detect_phase, PHASE_MESSAGES
    )


# ── Save ───────────────────────────────────────────────────────────────────────

_OUTPUT_TYPES: dict[str, str] = {
    "full":    "characters",
    "npc":     "characters",
    "contact": "characters",
}

_VALID_MODES = set(_OUTPUT_TYPES.keys())


def save_result(result: str, mode: str) -> Path:
    output_type = _OUTPUT_TYPES.get(mode, "characters")
    return save_character(result, mode, "deadlands", Path(__file__).parent.parent, output_type)


# ── Entry point ────────────────────────────────────────────────────────────────

def run(mode: str | None = None, desc: str | None = None) -> None:
    if mode is None:
        mode = input(
            "Mode? (full / npc / contact, default: full): "
        ).strip().lower()
        mode = mode if mode in _VALID_MODES else "full"

    labels = {
        "full":    "character",
        "npc":     "NPC",
        "contact": "patron contact",
    }
    label = labels.get(mode, "character")

    if desc is None:
        raw  = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()
        desc = sanitize_desc(raw)
        for w in screen_desc(desc):
            print(f"  [safety] {w}")

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt     = "Generate a fully random Deadlands NPC for the Weird West."
    elif mode == "contact":
        sys_prompt = CONTACT_SYSTEM_PROMPT
        prompt     = "Generate a fully random Deadlands patron contact encounter."
    else:
        sys_prompt = SYSTEM_PROMPT
        prompt     = "Generate a fully random Deadlands character for the Weird West."

    if desc:
        prompt += f"\n\n{wrap_desc(desc)}"

    result = strip_preamble(run_agent(prompt, sys_prompt))

    warn = screen_output(result)
    if warn:
        print(f"  [safety] {warn}")

    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
