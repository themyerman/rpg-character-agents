"""
Firefly RPG Character Generator (Cortex System)
Creates vivid storytelling characters for the Firefly 'Verse.

Run with: python firefly_agent.py
"""

import json
import random
from pathlib import Path
from names import roll_name_suggestion, NAME_TOOL_SCHEMA
from ships import roll_ship_name, FIREFLY_SHIP_TOOL_SCHEMA
from utils import get_client, run_agent_loop, save_character, strip_preamble


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


# ── 'Verse worlds (expanded, for random assignment) ─────────────────────────────

VERSE_WORLDS = {
    "Core": [
        ("Londinium",   "Parliament's seat — wealth on every surface and surveillance underneath"),
        ("Sihnon",      "silk, scholarship, and the Academy; cultural capital the Alliance loves to display"),
        ("Ariel",       "premier medical center; white spires, perfect air, and hidden Blue Sun contracts"),
        ("Osiris",      "law, finance, and old money; where families like the Tams grew up and paid for it"),
        ("Bernadette",  "humanity's first foothold in the system; still carries that sense of arrival"),
        ("Liann Jiun",  "trade hub and cultural anchor; where Core Chinese traditions still run deep"),
        ("Caprial",     "manor estates and farming wealth; the Core's idea of pastoral, with fences"),
        ("Albion",      "heavy industry and Alliance fleet support; a world that works for the government"),
    ],
    "Border": [
        ("Persephone",  "gateway world; Eavesdown Docks see everything and ask nothing"),
        ("Beaumonde",   "factory city of New Dunsmuir; industrial heart of the Border, always hiring"),
        ("Greenleaf",   "pharmaceutical manufacturing under jungle canopy; the Alliance's medicine cabinet"),
        ("Pelorum",     "resort world for people with money and loose customs enforcement"),
        ("Santo",       "tropical and lawless; piracy's an industry, bribes are a currency"),
        ("Constance",   "quiet farming communities that mind their business and expect others to"),
        ("Boros",       "Alliance military staging ground and arms manufacturing; uniforms everywhere"),
        ("Dyton",       "mining colony with strong opinions and weaker safety standards"),
        ("Verbena",     "self-sufficient settlement; old traditions, tight community, suspicious of outsiders"),
        ("Whittier",    "rough industrial moon; people come for work and stay because they can't afford to leave"),
        ("Paquin",      "traveling performers, festivals, and entertainers; a world in motion"),
    ],
    "Rim": [
        ("Whitefall",     "Patience's territory; harsh, dry, and unwelcoming by design"),
        ("Jiangyin",      "isolated farming moon where the locals solve their problems their own way"),
        ("Shadow",        "Malcolm Reynolds' homeworld; burned during the war, still smoking in places"),
        ("Hera",          "Serenity Valley; where the war ended for everyone still alive"),
        ("Harvest",       "agricultural moon struggling to grow enough to pay the Alliance's new taxes"),
        ("Regina",        "mining world; Bowden's malady is a way of life here, not a footnote"),
        ("Higgins' Moon", "clay and Canton and mudder labor; company town, company rules, company law"),
        ("Deadwood",      "no law, no Alliance, no infrastructure; freedom with consequences attached"),
        ("Athens",        "Rim farming that actually works, barely; proud people with not much to show for it"),
        ("Ezra",          "outlaw territory; everyone here is running from something or hiding someone"),
        ("Silverhold",    "mining moon with Company towns and labor disputes that turn violent"),
        ("Aberdeen",      "sheep and open sky; pastoral life that looks peaceful until you know what's underneath"),
        ("Three Hills",   "small farming moon; the kind of place the war touched once and never left"),
        ("Triumph",       "primitive conditions by choice; folk traditions stronger than modern infrastructure"),
        ("Anson's World", "rugged settlers who don't want to be found and are very clear about it"),
    ],
}


# ── Job hooks ────────────────────────────────────────────────────────────────────

JOB_HOOKS = [
    {
        "type":        "Cargo Run",
        "description": "Legitimate goods with a paperwork problem — move them before inspectors arrive",
        "complications": ["the cargo is alive", "the owner lied about the weight", "someone else has a manifest with their name on it"],
    },
    {
        "type":        "Salvage Claim",
        "description": "Wartime wreck drifting in the black; legally ownerless, morally complicated, worth a fortune",
        "complications": ["another crew found it first", "the Alliance knows it's there", "there are survivors"],
    },
    {
        "type":        "Recovery",
        "description": "Find a missing person and bring them home — dead or alive, though nobody says it that way",
        "complications": ["they don't want to be found", "someone else is already looking", "home is the dangerous part"],
    },
    {
        "type":        "Extraction",
        "description": "Get someone out of somewhere they can't leave on their own — quietly",
        "complications": ["the someone is a fugitive", "there are guards who weren't mentioned", "more people need out than the contact said"],
    },
    {
        "type":        "Courier",
        "description": "Time-sensitive delivery that can't go through Cortex — documents, data, or a sealed case",
        "complications": ["someone knows what's being carried", "the recipient isn't who they said", "the contact said don't open it and that's not going to work"],
    },
    {
        "type":        "Escort",
        "description": "Ride along with cargo or a person expecting trouble — the trouble is real and already on its way",
        "complications": ["the threat is hired professionals", "the client is the reason for the threat", "the client is armed and paranoid"],
    },
    {
        "type":        "Land Job",
        "description": "Survey, settle, or defend a contested claim — settlers on one side, a company or government on the other",
        "complications": ["the deeds are forged", "the settlers are the problem", "the land is already occupied"],
    },
    {
        "type":        "War Relic",
        "description": "Find and retrieve Alliance or Independent hardware buried at a battle site — illegal, valuable, dangerous",
        "complications": ["it's booby-trapped", "a veteran has a different plan for it", "the Alliance is watching the site"],
    },
    {
        "type":        "Livestock Run",
        "description": "Transport animals, seed stock, or specialized agricultural goods to a settlement that needs them",
        "complications": ["the animals are not well-behaved", "quarantine regulations exist for a reason", "someone is intercepting these shipments"],
    },
    {
        "type":        "Prison Break",
        "description": "Get someone out who shouldn't be in — or someone in who absolutely should",
        "complications": ["inside help falls through", "extra people want out", "the prisoner knows something dangerous"],
    },
    {
        "type":        "Heist",
        "description": "Take something from a facility, estate, or ship that isn't theirs to give — clean and quiet",
        "complications": ["the security is better than the contact said", "another crew is running the same job", "it's not there"],
    },
    {
        "type":        "Intermediary",
        "description": "Stand between two parties who don't trust each other; the crew is the neutral ground",
        "complications": ["one side is lying", "both sides are lying", "the deal is a setup for the other party"],
    },
    {
        "type":        "Passenger Transport",
        "description": "Take someone from here to there, no questions asked — they have good reasons or very bad ones",
        "complications": ["Alliance is looking for them", "they brought something aboard", "there's more than one of them now"],
    },
    {
        "type":        "Supply Run",
        "description": "Deliver necessities to a struggling colony the Alliance doesn't service — food, medicine, parts",
        "complications": ["the route is watched", "there's not enough to go around", "the colony has a more urgent problem now"],
    },
]


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

def roll_homeworld(region: str) -> str:
    """
    Randomly assign a specific world from the given region.
    Returns the world name and its flavor text.
    Use the returned world name exactly — do not substitute another.
    """
    if region not in VERSE_WORLDS:
        return f"Unknown region '{region}'. Available: Core, Border, Rim"
    world, flavor = random.choice(VERSE_WORLDS[region])
    return json.dumps({"world": world, "region": region, "flavor": flavor})

def roll_job_hook() -> str:
    """
    Randomly select a job type and a complication seed for a 'Verse job encounter.
    Call this first, before building the contact's details.
    """
    hook         = random.choice(JOB_HOOKS)
    complication = random.choice(hook["complications"])
    return json.dumps({
        "job_type":    hook["type"],
        "description": hook["description"],
        "complication": complication,
    })


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
    {
        "name": "roll_homeworld",
        "description": "Randomly assign a specific world from a region of the 'Verse. Use the returned world name exactly — do not substitute a different world.",
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
        "name": "roll_job_hook",
        "description": "Randomly select a job type and complication seed for a 'Verse job encounter. Call this first before building the contact's details. This prevents defaulting to pharmaceutical runs.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    NAME_TOOL_SCHEMA,
    FIREFLY_SHIP_TOOL_SCHEMA,
]


# ── Tool dispatcher ─────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    if name == "roll_cortex_attributes": return roll_cortex_attributes()
    if name == "get_role_info":          return get_role_info(**inputs)
    if name == "get_location_info":      return get_location_info(**inputs)
    if name == "roll_dice":              return roll_dice(**inputs)
    if name == "roll_war_history":       return roll_war_history()
    if name == "roll_homeworld":         return roll_homeworld(**inputs)
    if name == "roll_job_hook":          return roll_job_hook()
    if name == "roll_name_suggestion":   return roll_name_suggestion()
    if name == "roll_ship_name":         return roll_ship_name("firefly")
    return f"Unknown tool: {name}"


# ── System prompts ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Firefly RPG character generator (Cortex System). Create vivid, story-ready characters for the 'Verse.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits, flaws, and wounds should be specific and individual — not cultural shorthand.

Names in the 'Verse reflect its multicultural mix — draw from Chinese, Spanish, Slavic, West African, Arabic, and other traditions, not just Anglo-European. Call roll_name_suggestion() as your very first action and use the result as a starting point. Adapt it freely, but let it push you away from familiar defaults. Vary first letters, syllable counts, and cultural origins. Do not default to soft English-sounding names that start with the same letters.

Do not output any intermediate notes, reasoning, or working text. Output only the formatted character sheet, starting directly with the ## heading.

Work through these steps using your tools:

1. ROLE — Choose a role that fits the story. Look it up with get_role_info.

2. HOMEWORLD — Choose a region (Core, Border, or Rim). Call get_location_info for regional flavor and background color, then call roll_homeworld(region) to get the specific assigned world. Use the world name returned by roll_homeworld exactly — do not substitute another. The region and world shape the character's worldview, accent, and expectations.

3. WAR HISTORY — Call roll_war_history to determine their relationship to the Unification War. Let it color the backstory without defining it entirely.

4. ATTRIBUTES — Call roll_cortex_attributes to get a die distribution. You may reassign up to two die sizes to better fit the role — note what you changed and why.

5. SKILLS — Assign die sizes to 6–8 relevant skills. Use the Cortex ladder: d4 (poor), d6 (fair), d8 (good), d10 (great), d12 (exceptional). Key role skills should be d8 or higher.

6. DISTINCTIONS — Write exactly three. Each is a short phrase (3–6 words) that captures something essential. They should create story, not just describe. A Distinction should be able to help you (d8) or hurt you (d4 for a Plot Point) depending on the situation.

7. SIGNATURE ASSET — One thing, relationship, or reputation worth d6. The one thing they'd grab in a fire.

8. COMPLICATIONS — One starting complication (d6) they're already carrying. Not a flaw — a situation.

9. SHIP — Call roll_ship_name() to get the name and class of the vessel this character currently serves on or calls home. Every character in the 'Verse is tied to a ship — this is what they'd die to protect or desperately want to escape.

Always use exactly this format:

## **[Full Name]**
*[Role] — [one sharp sentence that places them in the 'Verse]*

| | |
|---|---|
| **Role** | [Role] |
| **Homeworld** | [World] ([Region]) |
| **War** | [their relationship to the Unification War — one phrase] |
| **Ship** | [ship name] ([class]) |

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

Names in the 'Verse reflect its multicultural mix — draw from Chinese, Spanish, Slavic, West African, Arabic, and other traditions, not just Anglo-European. Call roll_name_suggestion() before naming anyone. Use the result as a starting point — adapt it freely, but let it push you away from familiar defaults.

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


JOB_CONTACT_SYSTEM_PROMPT = """You are a Firefly RPG job contact generator. Create a complete encounter — someone who approaches the crew with work. Jobs in the 'Verse always have a story underneath them, and someone is always not telling the whole truth.

Avoid clichés tied to race, class, sex, or ethnicity. Character traits and motives should be specific and individual — not cultural shorthand.

Names in the 'Verse reflect its multicultural mix — draw from Chinese, Spanish, Slavic, West African, Arabic, and other traditions, not just Anglo-European. Call roll_name_suggestion() before naming anyone. Use the result as a starting point — adapt freely.

Do not output any intermediate notes or working text. Output only the formatted contact, starting directly with the ## heading.

STEP 0 (before writing anything): Call roll_name_suggestion() for the contact's name, then call roll_job_hook() for the job type and complication seed. Build the entire contact and encounter around what this tool returns. The job type determines the pitch, the payment structure, and what the crew is actually being asked to do. The complication seed should surface in at least one of the four Truths. Do not default to pharmaceutical runs, medical cargo, or drug smuggling unless roll_job_hook explicitly returns that category.

The GM rolls 1d4 in secret to determine which truth is real — only one is. Truth 4 is always The Reversal, where the crew is on the wrong side of the job. Write all four so any one of them could be true; the others should feel plausible until they're contradicted.

Always use exactly this format:

## **[Name]**
*[Occupation or role] — [one sharp sentence that places them in the 'Verse]*

| | |
|---|---|
| **Appears to be** | [what they claim to be — their cover story] |
| **Actually is** | *(revealed only in Truth 2, 3, or 4 below)* |

**Appearance:** [what the crew notices — specific detail, not a list of features. One thing that's off.]

**The Pitch:** *"[The ask in their own voice — specific, pressured, casual, desperate, or smooth depending on who they are. At least three sentences. The crew should be able to hear this person.]"*

**The Job:** [Concrete description of what they want done — where, what, by when.]

**The Payment:** [What they're offering — coin, passage, information, a favor, safe harbor. Be specific about amounts and what it's worth to a crew running low.]

**The Truth (GM rolls 1d4 in secret — only one is real):**

1. **Straightforward** — [The job is basically what it seems. One real complication that has nothing to do with the contact — something the crew will encounter in the doing of it.]

2. **One Layer Down** — [Something the contact left out. Not a lie exactly — an omission that changes the shape of the job once the crew finds it.]

3. **The Real Story** — [The actual situation the contact is operating in. The job is real but it's part of something larger, more dangerous, or more personal than presented.]

4. **The Reversal** — [The crew is on the wrong side of this. What the contact called a job is actually harm being done to someone — and the crew is the instrument. The contact may not be a villain; they may believe their own story. But the people at the other end of this job did not deserve it.]

**Why They'd Take It:** [The practical reason — money, fuel, desperation, something one crew member specifically needs. Make it feel like a real calculation, not a setup.]

**Connection:** [One named person who knows this contact and what they'd tell the crew if asked — something useful, something that points toward whichever truth the dice chose.]"""


# ── Phase tracker ───────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "name":       "Rolling name suggestion...",
    "role":       "Choosing role...",
    "homeworld":  "Finding homeworld...",
    "war":        "Rolling war history...",
    "attributes": "Distributing attributes...",
    "job":        "Rolling job hook...",
    "ship":       "Naming the ship...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_name_suggestion":   return "name"
    if tool_name == "get_role_info":          return "role"
    if tool_name == "get_location_info":      return "homeworld"
    if tool_name == "roll_homeworld":         return "homeworld"
    if tool_name == "roll_war_history":       return "war"
    if tool_name == "roll_cortex_attributes": return "attributes"
    if tool_name == "roll_job_hook":          return "job"
    if tool_name == "roll_ship_name":         return "ship"
    return None


# ── Agentic loop ────────────────────────────────────────────────────────────────

def run_agent(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    return run_agent_loop(
        prompt, system_prompt, TOOLS, run_tool, detect_phase, PHASE_MESSAGES
    )


# ── Save ────────────────────────────────────────────────────────────────────────

def save_result(result: str, mode: str) -> Path:
    return save_character(result, mode, "firefly", __file__)


# ── Entry point ─────────────────────────────────────────────────────────────────

def run(mode: str | None = None, desc: str | None = None) -> None:
    if mode is None:
        mode = input("Mode? (full / npc / jobcontact, default: full): ").strip().lower()
        mode = mode if mode in ("full", "npc", "jobcontact") else "full"
    label = {"full": "character", "npc": "NPC", "jobcontact": "job contact"}[mode]
    if desc is None:
        desc = input(f"Describe the {label} you want (or press Enter for fully random): ").strip()

    if mode == "npc":
        sys_prompt = NPC_SYSTEM_PROMPT
        prompt = f"Generate a Firefly RPG NPC with these constraints: {desc}" if desc else "Generate a fully random Firefly RPG NPC."
    elif mode == "jobcontact":
        sys_prompt = JOB_CONTACT_SYSTEM_PROMPT
        prompt = f"Generate a Firefly RPG job contact encounter with these constraints: {desc}" if desc else "Generate a fully random Firefly RPG job contact encounter."
    else:
        sys_prompt = SYSTEM_PROMPT
        prompt = f"Generate a Firefly RPG character for storytelling purposes with these constraints: {desc}" if desc else "Generate a fully random Firefly RPG character for storytelling purposes."

    result = strip_preamble(run_agent(prompt, sys_prompt))

    print("\n" + result)

    saved = save_result(result, mode)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
