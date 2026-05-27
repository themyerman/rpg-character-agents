"""
Alien RPG Character Generator (Year Zero Engine / Free League Publishing)
Creates cinematic pre-gens, NPCs, corporate contacts, and scenario hooks.

Run with: python alien_agent.py
"""

import json
import random
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.names import roll_name_suggestion, NAME_TOOL_SCHEMA
from lib.gear import roll_alien_gear, ALIEN_GEAR_TOOL_SCHEMA
from lib.utils import get_client, run_agent_loop, save_character, strip_preamble
from lib.safety import sanitize_desc, screen_desc, wrap_desc, screen_output


# ── Roles ──────────────────────────────────────────────────────────────────────

ROLES: dict[str, dict] = {
    "Colonial Marine": {
        "description": "USCM infantry or mercenary equivalent. Combat is your first language and your only guaranteed skill. You follow orders — or you don't, and you've learned to live with the consequences.",
        "attributes": {"Strength": 4, "Agility": 4, "Wits": 2, "Empathy": 2},
        "key_skills": ["Ranged Combat", "Close Combat", "Stamina", "Mobility", "Observation"],
        "career_talents": [
            ("Banter", "Rally a frightened or panicking crew member with a few well-chosen words — or deliberately wrong ones."),
            ("Overkill", "When you commit to full suppression, your weapon does not run dry as fast as it should. Something in you knows exactly how to make ammunition last when it counts."),
            ("Past the Limit", "You have pushed your body past what it should be able to endure. You recover from physical punishment faster than makes physiological sense."),
        ],
        "flavor": "the soldier who knows the math on the body count and shows up anyway",
    },
    "Company Agent": {
        "description": "Weyland-Yutani's eyes on the crew — or you work for someone just as interested in the bottom line. You have a secondary objective nobody briefed the others on.",
        "attributes": {"Strength": 2, "Agility": 3, "Wits": 4, "Empathy": 3},
        "key_skills": ["Manipulation", "Observation", "Comtech", "Command", "Ranged Combat"],
        "career_talents": [
            ("Cunning", "You can lie convincingly in ways that survive direct questioning — and you know how to identify when someone is lying to you."),
            ("Analyst", "Given time and data, you can identify patterns that should be invisible. You read people the way others read equipment diagnostics."),
            ("Executive Authority", "In a crisis, your corporate credentials carry weight that rank does not — until someone decides to stop caring about the company."),
        ],
        "flavor": "the one in the room whose agenda you still can't read",
    },
    "Colonial Marshal": {
        "description": "Law enforcement on the Frontier — which is another way of saying you enforce whatever law exists, with whatever backup doesn't exist. You've learned to work alone.",
        "attributes": {"Strength": 3, "Agility": 3, "Wits": 3, "Empathy": 3},
        "key_skills": ["Ranged Combat", "Observation", "Manipulation", "Survival", "Stamina"],
        "career_talents": [
            ("Authority", "Your badge — or your manner — carries weight in situations where it shouldn't. People answer your questions before they think about whether they have to."),
            ("Investigation", "You notice what others overlook: the detail that's missing, the story that's slightly too consistent, the person who isn't quite reacting right."),
            ("Quick Draw", "You have survived more frontier disputes than your odds should allow. Your draw is fast and your first shot lands."),
        ],
        "flavor": "the only law between the colony and whatever comes next",
    },
    "Roughneck": {
        "description": "Blue-collar worker — miner, technician, cargo handler, maintenance crew. You built this installation. You know where every emergency shutoff is, and you know what management doesn't bother to fix.",
        "attributes": {"Strength": 4, "Agility": 3, "Wits": 3, "Empathy": 2},
        "key_skills": ["Heavy Machinery", "Stamina", "Comtech", "Mobility", "Survival"],
        "career_talents": [
            ("Mechanic", "You can jury-rig almost anything that runs on power or pressure. It won't be elegant and it might not hold, but it will hold long enough."),
            ("Grit", "You work in the dark, in the cold, in the pressure — you have been doing it your whole life. Fear takes longer to reach you than it reaches most people."),
            ("Scrounger", "You know how to find what you need in places where it officially doesn't exist. Every installation has a secondary inventory management system. You are it."),
        ],
        "flavor": "the one who keeps everything running while everyone else argues about it",
    },
    "Scientist": {
        "description": "Researcher, xenobiologist, geologist, medical officer with a specialisation that explains why W-Y brought you. You know more than you're saying, and you're scared of what you might be right about.",
        "attributes": {"Strength": 2, "Agility": 2, "Wits": 5, "Empathy": 3},
        "key_skills": ["Observation", "Comtech", "Survival", "Medical Aid", "Manipulation"],
        "career_talents": [
            ("Analysis", "You can examine an unknown specimen, environment, or event and draw conclusions faster than your instruments can confirm them. Sometimes you're right."),
            ("Breakthrough", "When others are stumped, you see the connecting principle. This is both your greatest professional asset and the reason you have enemies."),
            ("Field Medicine", "Your medical training extends to field conditions that would defeat a standard medic. You work with what's available and you keep working."),
        ],
        "flavor": "the one who understood what they were looking at before they should have",
    },
    "Pilot": {
        "description": "You fly the ship — or the shuttle, the APC, the loader, anything with an engine and a seat. You know every exit from every situation, and your first instinct in a crisis is to calculate distance to the nearest one.",
        "attributes": {"Strength": 2, "Agility": 5, "Wits": 3, "Empathy": 2},
        "key_skills": ["Piloting", "Ranged Combat", "Mobility", "Comtech", "Observation"],
        "career_talents": [
            ("Full Throttle", "Under pressure, your reflexes outrun your thinking. You can push a ship into maneuvers that its specs say aren't possible — once."),
            ("Navigator", "You can plot a course with degraded instruments, bad data, or no data at all. You've been lost enough times to know where lost takes you."),
            ("Feel for the Ship", "You read your vessel the way some people read weather. Before the diagnostics flag a problem, you already know something is wrong."),
        ],
        "flavor": "the one who knows the way out before anyone else starts looking",
    },
    "Medic": {
        "description": "Ship's doctor, combat medic, installation medical officer — you keep people alive in conditions designed to kill them. You've seen the exposure timelines. You know things you haven't told anyone.",
        "attributes": {"Strength": 2, "Agility": 3, "Wits": 3, "Empathy": 4},
        "key_skills": ["Medical Aid", "Observation", "Manipulation", "Comtech", "Stamina"],
        "career_talents": [
            ("Compassion", "Your instinct toward the injured overrides other instincts. You can act when others freeze, and your calm transfers to people who are losing theirs."),
            ("Triage", "Under mass-casualty conditions, you assess fast and correctly. You make the call on who gets the medpac and you don't second-guess it afterward. Not while people are watching."),
            ("Bedside Manner", "People tell you things in the medical bay that they wouldn't say anywhere else. You use this carefully and try not to think too hard about why they trusted you."),
        ],
        "flavor": "the one who knows what's already too late to fix",
    },
}


# ── Personal Agendas ───────────────────────────────────────────────────────────

PERSONAL_AGENDAS: dict[str, list[str]] = {
    "Colonial Marine": [
        "Your Buddy doesn't make it back in a bag. Whatever it costs — mission, crew, orders — they walk off this ship. You made this promise and you are keeping it.",
        "Your real orders come from W-Y, not your commanding officer. Secure the asset. Return it intact. The crew's survival is not a factor in your evaluation.",
        "Someone on this crew is connected to the incident that killed your last squad. You've known since you saw the manifest. You haven't decided yet what you're going to do about it.",
        "If this site is compromised beyond recovery, you have the destruct authorization codes. You are expected to use them. Nobody told you how to handle the problem of other people still being inside.",
        "The transfer papers are waiting. Clean mission record, no complications, favorable report — and you're out. Don't be a hero. Don't ask questions. Get through this.",
    ],
    "Company Agent": [
        "Secure the specimen. Living tissue, viable for study. Everything else — crew, ship, schedule — is secondary to this. W-Y's investment in this mission is not the stated objective.",
        "The installation commander has been making independent decisions that fall outside their authorization. Assess their reliability. If they cannot be relied upon, ensure they cannot create a liability.",
        "Your secondary objective was sealed before departure. Open it now. Follow its instructions. Under no circumstances allow any other crew member to read it.",
        "There must be no record of W-Y's prior knowledge of this system. Any evidence of earlier contact, survey data, or internal memos must be destroyed before the crew returns. Any crew member who has already seen it must be managed.",
        "You have been authorized to offer additional compensation to crew members who demonstrate aligned priorities. Start with whoever seems most practical. Everyone has a number.",
    ],
    "Colonial Marshal": [
        "Someone on this crew is wanted under Colonial authority. You recognized them the moment you read the manifest. You haven't decided yet whether jurisdiction still matters out here.",
        "Your authority extends to this installation under the Colonial compact, regardless of what W-Y's legal team says. Find whatever they're trying to bury and preserve it before they destroy it.",
        "The civilians come first. Whatever happens to the mission — whatever the company orders, whatever the marines decide — the non-combatants are your responsibility and you will not leave them.",
        "The distress signal was fabricated. You know this because you investigated the last one that used this same encryption signature — and nobody survived that one either.",
        "You have six months. The diagnosis came back before departure and you stopped taking the suppressants three weeks ago. You have enough time to finish this job and maybe one more. Do the job.",
    ],
    "Roughneck": [
        "You found something in the restricted section six weeks ago. You didn't report it because you weren't supposed to be there. It's still there. Whatever happens, nobody can know you knew.",
        "The bonus clause in your contract triggers if you document evidence of equipment failure causing the incident. Make sure there is evidence. Make sure you document it first.",
        "Your Rival is the W-Y safety inspector who buried your report after the accident at your last posting. Three people died. They got a commendation. They don't recognize you yet.",
        "You have the severance, the savings, the ticket out — if you survive this job. Don't take risks. Don't volunteer. Don't be the one standing closest to whatever goes wrong.",
        "The foreman on this installation has owed you money for three years. Collect before anyone else gets a claim on the remaining assets.",
    ],
    "Scientist": [
        "This is the most significant discovery in human history and they are going to destroy it. Document everything. Get it out somehow — memory chip, personal comm, anything. The company cannot be the only ones who know.",
        "Your research was published under someone else's name. The lead researcher on this installation used your methodology and filed your results under their credentials. You want the data. You want acknowledgment. You want it on record before anything else happens.",
        "W-Y told you there was nothing here. They lied, which means they knew, which means everything they told you was a cover. You need evidence of prior knowledge. Expose it or the data dies with you.",
        "Preserve the specimen. Living tissue, undamaged. This matters more than the mission, more than the crew, more than your own assessment of how this is going to end.",
        "You've been tracking the exposure symptoms for forty-eight hours. You know who's already past the threshold. You haven't told them because once you do, they have nothing left to lose — and you need them to keep making rational decisions until you don't.",
    ],
    "Pilot": [
        "Get yourself out. The ship is your way home and you are going to be on it when it leaves. If it comes down to the mission or the ship, it was always going to be the ship.",
        "You owe someone aboard a debt you've been avoiding for two years. This mission is the last time you'll see them. Settle it, one way or another, before it ends.",
        "Someone loaded a second flight plan — coordinates that bypass the return registry and route directly to a W-Y location you don't recognize. It wasn't you. You haven't said anything yet.",
        "The ship's logs from the outbound leg contain something that cannot be in the official record on return. Delete it before landing. This is not optional.",
        "You've lost crew before. Lost your last command over it. You made yourself a promise that this time everyone comes home. It's irrational. You know it's irrational. You're keeping it anyway.",
    ],
    "Medic": [
        "You ran the exposure tests thirty-six hours ago. You know who's been compromised and you have not told them yet — because once you do, they have nothing left to lose and they will stop making decisions you can predict.",
        "Your patient's file was altered before departure. You've been treating them for the wrong condition for three days. Correct it before anyone else looks at the chart.",
        "W-Y sent you a sealed secondary objective. One directive involves a specific crew member's biological samples. One involves what you are authorized to do if the situation becomes uncontainable. You haven't opened it yet.",
        "Your oath is simple and it doesn't have a corporate logo on it. Stabilize everyone. Whatever orders come through, whatever the situation becomes, that is your job and you are going to do it.",
        "Someone is going to die on this mission. The statistics are plain. Your job is to make sure you control which variables you can — and that the last medpac goes to the person who deserves it most, not the one with the best contract.",
    ],
}


# ── Scenario Hooks ─────────────────────────────────────────────────────────────

SCENARIO_HOOKS: list[dict] = [
    {
        "type": "Derelict Investigation",
        "description": "A vessel or installation has stopped responding. The crew has been sent to establish contact, recover assets, and file a report — in that order. W-Y's instructions emphasize the asset recovery.",
        "location_type": "derelict spacecraft or orbital installation",
        "complications": [
            "The manifest doesn't match what's actually aboard. Someone loaded this vessel with things they didn't file paperwork for, and they didn't do it on this end.",
            "The crew of the derelict are not all dead. One survivor, somewhere in the dark, who has decided they cannot trust anyone who shows up looking for them.",
            "The emergency bulkheads sealed three sections of the installation. The automated systems still consider whatever triggered them to be active.",
        ],
    },
    {
        "type": "Emergency Extraction",
        "description": "Get someone out. A researcher, a corporate asset, a witness — the briefing is light on specifics. The window for extraction closes in hours. What's being left behind is not the crew's problem, officially.",
        "location_type": "colony, research station, or corporate installation",
        "complications": [
            "The extraction target has changed their mind and does not want to leave. They have a reason. They haven't explained it.",
            "The facility has gone into lockdown since the last update. Getting in is a different problem than the briefing anticipated.",
            "There are other people here. The extraction order names one person. The others are watching the crew leave.",
        ],
    },
    {
        "type": "Corporate Inspection",
        "description": "An installation has gone quiet for seventy-two hours. W-Y is sending a team to assess the situation and recover any viable assets before filing an insurance claim. The crew are the team.",
        "location_type": "colony installation, mining operation, or research facility",
        "complications": [
            "The installation's systems are still operational. Whatever happened here, the power stayed on.",
            "The logs have been manually deleted in the last forty-eight hours. Someone was still alive long enough to do that, and they chose to delete the logs instead of calling for help.",
            "The Company already sent a team. The first team's equipment is still here. The first team is not.",
        ],
    },
    {
        "type": "Salvage Operation",
        "description": "Recover designated assets from a disaster site before the window closes or a competitor's salvage crew arrives. The disaster was documented as an accident. The crew were not told that the documentation was prepared before the accident occurred.",
        "location_type": "wreckage field, damaged installation, or disaster site",
        "complications": [
            "The rival salvage crew arrived first. They're not inclined to share the site, and their contract is ironclad.",
            "The asset W-Y wants salvaged is not on the official manifest. Finding it means searching sections of the wreck they were told to avoid.",
            "Whatever caused the disaster is documented as contained. The containment documentation is dated three hours after the disaster site went dark.",
        ],
    },
    {
        "type": "Outbreak Response",
        "description": "An installation has reported a containment breach. The crew has been dispatched to assess, render aid, and report status. The mission profile does not include the phrase 'allow survivors to leave the site.'",
        "location_type": "research station, colony outpost, or orbital lab",
        "complications": [
            "There are more survivors than the briefing suggested. The math on the rescue shuttle's capacity does not work in everyone's favour.",
            "The breach isn't what the report described. What's here is something the installation's team did not have a protocol for because officially it does not exist.",
            "Quarantine protocols lock the crew in with the situation. Someone has to override the lockout manually. The override panel is in the section that is not safe to enter.",
        ],
    },
    {
        "type": "First Contact Assessment",
        "description": "A survey team found something that doesn't match any catalogued taxonomy. The crew has been sent to document and assess before W-Y commits resources to the site. The survey team's last report was filed eight days ago.",
        "location_type": "unmapped planetoid, survey station, or frontier outpost",
        "complications": [
            "The survey team's equipment is functioning. Their logs are intact. Their biological signs are not registering on the crew's instruments.",
            "W-Y's prior knowledge of this site is more extensive than the briefing suggests. The coordinates were not discovered — they were already in the system, filed under a project designation that predates the survey team's mission.",
            "Whatever was found here, it found the survey team first. The order of contact is not what the official timeline states.",
        ],
    },
    {
        "type": "Black Site Retrieval",
        "description": "A restricted W-Y installation has been accessed by unauthorized parties. The crew has been sent to secure the site, recover the research, and deal with whoever got in. Nobody has explained what they got in to see.",
        "location_type": "classified installation or off-books research site",
        "complications": [
            "The unauthorized parties are still inside. They came prepared and they know more about the installation's layout than any unauthorized party should.",
            "The research the crew has been sent to recover is not what W-Y described. Understanding what it actually is requires reading documentation they were told not to open.",
            "The installation's on-site security team responded to the breach before the crew arrived. The security team is now also part of the situation.",
        ],
    },
    {
        "type": "Transit Escort",
        "description": "Move a specific cargo — or passenger — from point A to point B without drawing attention. The cargo is classified. The route avoids standard shipping lanes for reasons the crew have been told not to ask about.",
        "location_type": "aboard ship or through multiple waypoints",
        "complications": [
            "Someone else knows about the cargo and knows the route. They have been waiting at one of the waypoints.",
            "The cargo is not inert. Whatever's in the container has been maintaining a consistent temperature differential for the last eighteen hours.",
            "The passenger, if there is one, knows more about the destination than the crew does. They have been deciding how much to say and have not yet made up their mind.",
        ],
    },
]


# ── Tool functions ─────────────────────────────────────────────────────────────

def get_role_info(role_name: str) -> str:
    """Return full role profile for a given Alien RPG role."""
    if role_name not in ROLES:
        return json.dumps({
            "error": f"Unknown role '{role_name}'.",
            "available": list(ROLES.keys()),
        })
    return json.dumps(ROLES[role_name])


def roll_personal_agenda(role_name: str) -> str:
    """Return a random Personal Agenda for a given role."""
    if role_name not in PERSONAL_AGENDAS:
        return json.dumps({"error": f"Unknown role '{role_name}'."})
    agenda = random.choice(PERSONAL_AGENDAS[role_name])
    return json.dumps({"role": role_name, "personal_agenda": agenda})


def roll_scenario_hook() -> str:
    """Return a random cinematic scenario type, location, and complication seeds."""
    hook         = random.choice(SCENARIO_HOOKS)
    complication = random.choice(hook["complications"])
    return json.dumps({
        "scenario_type": hook["type"],
        "description":   hook["description"],
        "location_type": hook["location_type"],
        "complication":  complication,
    })


def roll_dice(sides: int, count: int = 1) -> str:
    valid = {6, 10}
    if sides not in valid:
        return f"Error: Alien RPG uses d6 (standard rolls) and d10 (stress). Got d{sides}."
    rolls = [random.randint(1, sides) for _ in range(count)]
    return f"Rolled {count}d{sides}: {rolls} — total: {sum(rolls)}"


# ── Tool schemas ───────────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    NAME_TOOL_SCHEMA,
    ALIEN_GEAR_TOOL_SCHEMA,
    {
        "name": "get_role_info",
        "description": (
            "Look up a role's attributes, key skills, career talents, and flavor. "
            "Call this immediately after committing to a role."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role_name": {
                    "type": "string",
                    "description": "The character's role.",
                    "enum": list(ROLES.keys()),
                },
            },
            "required": ["role_name"],
        },
    },
    {
        "name": "roll_personal_agenda",
        "description": (
            "Get a random Personal Agenda for a given role — the secret goal "
            "this character is hiding from the rest of the crew. "
            "Call this after choosing the role. The agenda is GM-only content."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role_name": {
                    "type": "string",
                    "description": "The character's role.",
                    "enum": list(PERSONAL_AGENDAS.keys()),
                },
            },
            "required": ["role_name"],
        },
    },
    {
        "name": "roll_scenario_hook",
        "description": (
            "Get a random cinematic scenario type, location flavor, and complication seed. "
            "Call this when generating a scenario framework for a one-shot session."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "roll_dice",
        "description": "Roll Alien RPG dice — d6 for standard rolls, d10 for stress checks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {
                    "type": "integer",
                    "description": "Die type: 6 (standard) or 10 (stress).",
                    "enum": [6, 10],
                },
                "count": {
                    "type": "integer",
                    "description": "Number of dice to roll.",
                    "minimum": 1,
                    "maximum": 12,
                },
            },
            "required": ["sides"],
        },
    },
]


# ── System prompts ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an Alien RPG cinematic character generator (Year Zero Engine / Free League Publishing). Create a vivid pre-generated character for a one-shot cinematic session — the kind of person who shows up to a bad situation already carrying something worse.

The tone is blue-collar survival horror. These are not heroes. They are workers, soldiers, and company assets in a universe that does not care about any of them. Every character should feel specific, real, and already slightly afraid.

Avoid clichés tied to race, gender, or origin. Character traits should be individual — worn in, earned, and specific to this person. Call roll_name_suggestion() before naming anyone; use the result as a starting point but adapt freely.

Do not output any intermediate notes or working text. Output only the formatted character sheet, starting directly with the ## heading.

STEP 0 (before writing anything):
1. Choose a role (or use the user's request). Call get_role_info(role_name).
2. Call roll_personal_agenda(role_name) — this is the secret at the center of the character.
3. Call roll_name_suggestion() for the name.
4. Call roll_alien_gear(role_name) for equipment.

CHARACTER SHEET FORMAT — use exactly this structure:

## **[Full Name]** — [Role]
*[One sharp sentence placing this person in the scenario — who they are and what they're carrying]*

| | |
|---|---|
| **Role** | [Role] |
| **Appearance** | [What the crew sees — two details, one of which is slightly off] |

### Attributes
| STRENGTH | AGILITY | WITS | EMPATHY |
|----------|---------|------|---------|
| [2–4] | [2–4] | [2–4] | [2–4] |

*Attributes sum to 12. Assign based on role: high where the role demands it, low where it shows.*

### Skills
List all twelve skills with ratings. Career skills for this role should be 2–3; others 0–1. Total skill points: 10.

**Strength:** Heavy Machinery [0–3], Stamina [0–3], Close Combat [0–3]
**Agility:** Mobility [0–3], Ranged Combat [0–3], Piloting [0–3]
**Wits:** Observation [0–3], Survival [0–3], Comtech [0–3]
**Empathy:** Command [0–3], Manipulation [0–3], Medical Aid [0–3]

### Career Talents
Choose 1–3 talents from the role's talent list. Write each as a brief thematic description — what it means for this specific person, not just what it does mechanically.

- **[Talent]:** [How this talent manifests in this character — personal, specific]

### Equipment
List every item from roll_alien_gear(). Each item should feel used — worn in, maintained or neglected in ways that say something about who this person is.

### Starting Stress
0

### Buddy
**[Name or Role]** — [One sentence: who this character has decided to protect, and the specific reason. Does not need to be mutual.]

### Rival
**[Name or Role]** — [One sentence: who this character does not trust, and the specific reason. Does not need to be known to the other party.]

### Signature Item
[Something personal they carry — an object with a story behind it. One sentence that raises a question it does not answer.]

---

### ⚠ Personal Agenda *(GM only — do not show to other players)*

[Write the Personal Agenda from roll_personal_agenda() as a full paragraph in second person, present tense. Make it specific, pressured, and impossible to cleanly resolve. The agenda should create a genuine conflict between this character's goal and the crew's survival — not an obvious villain move, but a real and human choice that happens to cost other people something. End with one sentence that names the specific thing this character will do if forced to choose.]"""


NPC_SYSTEM_PROMPT = """You are an Alien RPG NPC generator (Year Zero Engine / Free League Publishing). Create a vivid, instantly usable NPC sketch for a cinematic one-shot or campaign session.

These NPCs exist in the same universe of blue-collar horror: corporate workers, marines, colony staff, survivors, and the occasional company suit with an agenda nobody asked about. They should feel real within thirty seconds of appearing at the table.

Avoid clichés tied to race, gender, or origin. Call roll_name_suggestion() before naming anyone.

Do not output intermediate notes. Output only the formatted NPC, starting directly with the ## heading.

STEP 0: Call roll_name_suggestion(). Call get_role_info() if the NPC has a clear role. Call roll_personal_agenda() if they have an agenda worth hiding.

Always use exactly this format:

## **[Name]**
*[Role or occupation] — [one sharp sentence about who this person is in the Frontier]*

| | |
|---|---|
| **Role** | [Role or occupation] |
| **Affiliation** | [Company / USCM / Colonial Authority / Independent / Unknown] |

**Appearance:** [What the crew notices — one specific detail, one that's slightly wrong]

**Demeanor:** [How they present themselves — the gap between what they show and what they're carrying]

**Wants:** [What they say they want — specific and credible]

**Secret:** [What they actually need, fear, or know — the thing driving them under the stated want]

**Hook:** [How they pull the crew into their situation — or are pulled into the crew's]

**Equipment:** [2–3 items that tell a story — at least one that shouldn't be there, or is conspicuously missing]

**Connection:** [One named person or organization that links this NPC to something larger — and what that link costs them]"""


CONTACT_SYSTEM_PROMPT = """You are an Alien RPG corporate contact generator. Create a complete encounter — someone who approaches the crew with a job, a warning, or an offer. In the Frontier, nobody who needs to hire strangers is telling the whole story. Weyland-Yutani always has a secondary objective. So does everyone else.

Avoid clichés tied to race, gender, or origin. Call roll_name_suggestion() before naming anyone.

Do not output intermediate notes. Output only the formatted contact, starting directly with the ## heading.

STEP 0 (before writing anything): Call roll_name_suggestion() for the contact's name. Call roll_scenario_hook() for the job type and complication seed. Build the entire encounter around what these tools return.

The GM rolls 1d4 in secret to determine which truth is real — only one is. Truth 4 is always The Company Knew — where the crew was sent in with full knowledge of what they'd find, and was never expected to come back. Write all four so any one of them could be true until contradicted.

Always use exactly this format:

## **[Name]**
*[Role or affiliation] — [one sharp sentence about who this person appears to be]*

| | |
|---|---|
| **Appears to be** | [their stated identity and apparent affiliation] |
| **Actually is** | *(revealed only in Truth 2, 3, or 4 below)* |

**Appearance:** [What the crew notices — two details, one of which doesn't fit the stated identity]

**The Pitch:** *"[The offer in their own voice — how they frame it, what they emphasize, what they skip. At least three sentences. The crew should be able to hear the angle and the pressure behind it.]*"

**The Job:** [Concrete description of what they want done — location, target, timeline, parameters.]

**The Payment:** [What's on the table — credits, passage, equipment, favors, information. Specific amounts. Make it feel like a real calculation a desperate crew would make.]

**The Truth (GM rolls 1d4 in secret — only one is real):**

1. **Straightforward** — [The job is basically what it seems. One real complication that has nothing to do with the contact — something the crew will encounter in the doing of it, not a deception.]

2. **One Layer Down** — [Something the contact omitted. Not a lie exactly — a shaped truth that changes the shape of the job once the crew finds it. The contact may not consider it relevant. They are wrong.]

3. **The Real Story** — [The actual situation the contact is operating inside. The job is real but it's part of something larger — a faction play, a corporate power struggle, a cover-up already underway. The crew's mission is a piece of a board they haven't seen.]

4. **The Company Knew** — [Weyland-Yutani — or whoever the contact ultimately works for — was aware of what was at the site before the crew was sent. The mission was designed to produce a specific outcome that does not include crew survival. The contact may be a willing instrument, a dupe, or a person who told themselves a story that made it easier. The payment offer is real. The contract clause that voids it under 'mission failure conditions' is in the fine print on page 47.]

**Why They'd Take It:** [The practical reason — credits, fuel, passage, desperation, something a specific crew member specifically needs. Make it feel like a real calculation, not a trap. It should be tempting even once the session is over.]

**Connection:** [One named person who knows this contact and what they'd say about them — something that points toward whichever truth the dice chose, without making it obvious which one.]"""


SCENARIO_SYSTEM_PROMPT = """You are an Alien RPG scenario architect. Create a complete GM-facing framework for a cinematic one-shot session — the kind of evening that starts as a job and ends as a survival horror film nobody agreed to be in.

Do not output intermediate notes. Output only the formatted scenario, starting directly with the ## heading.

STEP 0 (before writing anything): Call roll_scenario_hook() to get the scenario type, location flavor, and complication seed. Build everything around what this returns.

Always use exactly this format:

## **[Scenario Title]**
*Cinematic one-shot — [scenario type] — [estimated session length: 3–5 hours]*

### The Setup
[2–3 sentences: what the crew has been told. The official version. What it looks like from the outside before anyone gets there.]

### The Location
**[Installation/vessel name]:** [What it is, who built it, what it was supposed to do. One specific physical detail that will matter later.]

**Condition on arrival:** [What the crew finds when they get there — before they know anything is wrong. Two details that are slightly off but explainable.]

### The Situation (GM only)
[What actually happened. The full truth. Written for the GM, not the players. Include: who caused it, when it started, what the current status is, and what will happen if the crew does nothing.]

### The Threat
**What it is:** [The specific danger — xenomorph, corporate security, environmental, human, or some combination. Be specific about what it can do and what its current status is.]

**What it wants:** [Threats that aren't mindless have motivations. Even xenomorphs have behavioral drives. State them plainly.]

**What the crew doesn't know:** [The specific piece of information that will change everything once they find it — and where it's located in the installation.]

### Escalation Structure
**Act One (arrival):** [What the crew encounters in the first hour — the surface-level problem that seems manageable]
**Act Two (revelation):** [What forces the crew to confront the actual situation — the moment the job becomes something else]
**Act Three (finale):** [The endgame — what the crew must do to survive, and what they have to sacrifice to do it]

### The W-Y Factor
[What Weyland-Yutani actually wants from this site, what they already know, and what instructions (if any) the Company Agent received before departure. Always different from the official mission brief.]

### Complication
[The specific complication from roll_scenario_hook() — how it manifests in this scenario, and when the crew will encounter it]

### Survival Hooks
[2–3 specific reasons individual crew roles are essential to getting out alive — the pilot needs to fly, the medic has to make the call, the roughneck knows the override. Create dependency without making any role useless.]"""


# ── Phase tracker ──────────────────────────────────────────────────────────────

PHASE_MESSAGES: dict[str, str] = {
    "name":     "Rolling name...",
    "role":     "Locking in role...",
    "agenda":   "Pulling personal agenda...",
    "gear":     "Rolling gear...",
    "scenario": "Building scenario hook...",
}


def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_name_suggestion":  return "name"
    if tool_name == "get_role_info":         return "role"
    if tool_name == "roll_personal_agenda":  return "agenda"
    if tool_name == "roll_alien_gear":       return "gear"
    if tool_name == "roll_scenario_hook":    return "scenario"
    return None


# ── Run tool dispatcher ────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_name_suggestion":  return roll_name_suggestion()
    if name == "get_role_info":         return get_role_info(inputs["role_name"])
    if name == "roll_personal_agenda":  return roll_personal_agenda(inputs["role_name"])
    if name == "roll_scenario_hook":    return roll_scenario_hook()
    if name == "roll_alien_gear":       return roll_alien_gear(inputs.get("role_name", ""))
    if name == "roll_dice":             return roll_dice(inputs["sides"], inputs.get("count", 1))
    return f"Unknown tool: {name}"


# ── Agentic loop ───────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    return run_agent_loop(
        prompt, system_prompt, TOOLS, run_tool, detect_phase, PHASE_MESSAGES
    )


# ── Save ───────────────────────────────────────────────────────────────────────

_OUTPUT_TYPES: dict[str, str] = {
    "cinematic": "characters",
    "npc":       "characters",
    "contact":   "characters",
    "scenario":  "scenarios",
}

_VALID_MODES = set(_OUTPUT_TYPES.keys())


def save_result(result: str, mode: str) -> Path:
    output_type = _OUTPUT_TYPES.get(mode, "characters")
    return save_character(result, mode, "alien", Path(__file__).parent.parent, output_type)


# ── Entry point ────────────────────────────────────────────────────────────────

def run(mode: str | None = None, desc: str | None = None) -> None:
    if mode is None:
        mode = input(
            "Mode? (cinematic / npc / contact / scenario, default: cinematic): "
        ).strip().lower()
        mode = mode if mode in _VALID_MODES else "cinematic"

    labels = {
        "cinematic": "pre-gen character",
        "npc":       "NPC",
        "contact":   "corporate contact",
        "scenario":  "cinematic scenario",
    }
    label = labels.get(mode, "character")

    if desc is None:
        raw  = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()
        desc = sanitize_desc(raw)
        for w in screen_desc(desc):
            print(f"  [safety] {w}")

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt     = "Generate a fully random Alien RPG NPC for a cinematic session."
    elif mode == "contact":
        sys_prompt = CONTACT_SYSTEM_PROMPT
        prompt     = "Generate a fully random Alien RPG corporate contact encounter."
    elif mode == "scenario":
        sys_prompt = SCENARIO_SYSTEM_PROMPT
        prompt     = "Generate a fully random Alien RPG cinematic one-shot scenario framework."
    else:
        sys_prompt = SYSTEM_PROMPT
        prompt     = "Generate a fully random Alien RPG pre-gen character for a cinematic one-shot."

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
