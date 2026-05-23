# Tabletop RPG Generators

AI-powered GM tools for tabletop RPGs, built with the Anthropic Claude API. Each generator runs an agentic tool-use loop — Claude calls dice rollers, rules lookups, name generators, and seed tables, gets real random results back, and uses them to produce output that feels like it actually lived through something.

Supports **D&D 5e**, **Mongoose Traveller 2e**, **Firefly RPG (Cortex System)**, and **Scum and Villainy (Forged in the Dark)**.

The `output/` folder contains examples generated during development — characters, NPCs, parties, encounters, ships, locations, rumors, and events ready to use or adapt.

---

## Setup

Requires Python 3.11+ and an [Anthropic API key](https://console.anthropic.com).

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your-key-here
```

Tests require no API key — they cover only pure Python logic:

```bash
pip install pytest
pytest tests/
```

---

## Running

```bash
python main.py
```

Two menus: pick your game, then pick what to build.

**Game:**
- D&D 5e
- Mongoose Traveller 2e
- Firefly RPG
- Scum and Villainy

**What to build:**
- Full character sheet
- NPC sketch
- Hook encounter (quest giver / patron / job contact / score contact)
- Party / crew
- NPC cluster
- Encounter
- Ship
- Location
- Rumor
- Event

Each agent can also be run directly:

```bash
python agents/dnd_agent.py
python agents/traveller_agent.py
python agents/firefly_agent.py
python agents/scum_villainy_agent.py
python agents/party_agent.py
python agents/npc_cluster_agent.py
python agents/encounter_agent.py
python agents/ship_agent.py
python agents/location_agent.py
python agents/rumor_agent.py
python agents/event_agent.py
```

Every generator accepts a plain English prompt — use it to add a concept, a constraint, or a swerve. You can be vague (`"someone with a secret"`) or precise (`"ex-navy medic, cashiered for something she still thinks was right"`). The dice still roll. The description just tilts the output.

---

## Character Generators

### D&D 5e — `dnd_agent.py`

**Modes:**
- `full` — Full character sheet: ability scores (4d6 drop lowest), race, class, background, personality, named connections, equipment, spells (for spellcasting classes), alignment, and backstory
- `npc` — Quick sketch: stat block, alignment, demeanor, want, secret, hook, and one named connection
- `questgiver` — Hook encounter: who approaches the party, the pitch in direct speech, what they want, what they're offering, and four possible truths (the DM rolls 1d4 in secret — Truth 4 is always The Reversal)

The `roll_alignment` tool rolls one of the nine D&D alignments with a concrete behavioral expression (how it shows in action), an internal tension (what makes it interesting to play), and a shadow tendency (how it can go wrong). The system prompt instructs the model to show alignment through behavior — never to write "this character is [alignment]" in the backstory.

Output saves to `output/dnd/characters/`.

**Examples:** Pip "Tallowfingers" Underbough (Halfling Rogue), Iyari Sael Tovenn-Saltbough (full character), Jelani Orriss (quest giver with a missing apprentice and a guild problem)

---

### Mongoose Traveller 2e — `traveller_agent.py`

**Modes:**
- `full` — Full character with rolled UPP, homeworld (complete UWP with atmosphere, hydrographics, law level, tech level, background skills), career history (2–6 terms), survival rolls, d66 events, mishaps, named connections, muster out benefits, pension, and equipment. Ship shares are treated as story hooks: a named vessel with a dangling thread, not a line item.
- `npc` — Quick sketch in Traveller format: UPP, career, demeanor, want, secret, hook
- `patron` — Classic Traveller patron encounter: the job, the pitch in direct speech, the payment, and four possible truths (referee rolls 1d4 in secret — Truth 4 is The Reversal)

Noble titles are awarded by Social Standing: SOC 11 = Knight (Sir/Dame), 12 = Baron/Baroness, 13 = Marquis/Marchioness, 14 = Count/Countess, 15 = Duke/Duchess.

Output saves to `output/traveller/characters/`.

**Examples:** Baroness Séverine "Sev" Aldenberg-Vey (Agent, 5 terms, SOC 12, vacc suit with family crest), Korven "Half-Lung" Drask (Drifter, 6 terms, Cr105k he shouldn't have), Nasrin "Nas" al-Qadeer (Scout, 2 terms, her own ship and four languages), Áine Kelly-Vorrhan "the Quiet Secretary" (Noble, 6 terms, Telekinesis talent, trained in secret and licensed on two subsectors)

---

### Firefly RPG — `firefly_agent.py`

Cortex System character generation for the 'Verse. Die sizes (d4–d12) replace numeric scores; Distinctions are story engines that help or hurt depending on the situation.

**Modes:**
- `full` — Full character: role, homeworld (Core/Border/Rim), Unification War history, six attributes with die ratings, 6–8 skills, three Distinctions with story notes, Signature Asset, Complications, ship name, equipment, and backstory
- `npc` — Quick sketch: role, homeworld, key attributes, distinctions, wants, secret, hook
- `jobcontact` — Hook encounter: who's hiring, the pitch in direct speech, what they want, what they're offering, and four possible truths (Truth 4 is always The Reversal)

Roles: Captain, Pilot, First Mate, Mechanic, Doctor, Shepherd, Muscle, Grifter, Thief.

Output saves to `output/firefly/characters/`.

**Examples:** Kezia "Halberd" Ramos (Captain, Beaumonde, Browncoat vet with a stolen ship), Liora Aldermere-Sato (Grifter, Osiris Core, Alliance-educated and running from it)

---

### Scum and Villainy — `scum_villainy_agent.py`

Forged in the Dark character generation for crews at the edge of the Hegemony. Action ratings (0–4 dots), playbook special abilities, stress/trauma tracks, and a vice with a named purveyor.

**Modes:**
- `full` — Full crew member: playbook, heritage, background, vice, action dots by attribute (Insight/Prowess/Resolve), one special ability, XP triggers, stress and trauma tracks, load (starting gear), ship name, and backstory
- `npc` — Quick sketch: playbook equivalent, heritage, background, key actions, wants, secret, hook
- `scorecontact` — Hook encounter: who's offering the score, the pitch in direct speech, what they want, what they're paying, and four possible truths (Truth 4 is always The Reversal)

Playbooks: Muscle, Pilot, Scoundrel, Mystic, Speaker, Stitch. Action dots use filled/empty circles (●○○○).

Output saves to `output/scum_villainy/characters/`.

**Examples:** Adaeze "Reins" Vukoja (Pilot, Iruvia, steady hands and a dangerous calm), Adesina Voss-Karim (full crew member), Wren Adeyemi-Vasque (NPC)

---

## Party & Crew Builder — `party_agent.py`

Assembles a party or crew with connective tissue — shared history, fault lines, secrets, and a first session hook. Works with your saved characters, generates fresh ones, or mixes both.

**Interactive flow:**
1. Game: `dnd` / `traveller` / `firefly` / `scum`
2. Party/crew size (default: 4)
3. Mode: `folder` (pick from saved characters) / `generate` (all fresh) / `mix` (some of each)
4. If folder or mix: pick characters by number from a displayed list
5. Optional theme or constraints in plain English
6. Optional: generate a tailored hook encounter (quest giver / patron / job contact / score contact)

**Output sections:** Members roster → How They Came Together → What Holds Them Together → The Fault Line → Shared Secret → First Session Hook

Output saves to `output/parties/{game}/`.

**Examples:** The Hannox Detour (D&D), Lost Causes (Traveller), La Drona del Río (Firefly), Quiet Verdict (Scum and Villainy)

---

## NPC Cluster — `npc_cluster_agent.py`

Generates a connected group of NPCs with relationships, overlapping agendas, and hooks — a faction, a household, a crew, a criminal organisation, a family. Designed for situations where a single NPC isn't enough but a full party isn't the right tool.

Clusters have internal structure: members know each other, have history together, and their secrets create pressure that the party can exploit or be caught between.

Output saves to `output/characters/{game}/`.

---

## Location Generator — `location_agent.py`

Generates vivid, GM-ready location profiles: atmosphere, notable NPCs, a situation (the GM's-eye view of what's actually going on), three hooks, and GM notes. Four seed elements per game (type, condition, complication, hook) prevent the model from defaulting to generic taverns or plain starports.

Saved location briefs can be loaded by the rumor and event generators to anchor output to a specific place.

**Output sections:** Atmosphere → Notable NPCs (2-3 named, with wants/secrets) → The Situation → Hooks (3) → GM Notes

Each game has 20 entries per seed category (80 seeds total per game):
- **D&D** — inns, market towns, noble estates, dwarven trading posts, ruins, guild fronts
- **Traveller** — Class C downports, megacorp extraction facilities, gas giant skimming stations, decommissioned Scout bases
- **Firefly** — Rim settlements, border moon agricultural communities, derelict transports, Core transit hubs
- **Scum and Villainy** — Hegemony transit hubs, fringe stations, Ur-ruin sites, Guild shipyard districts, Mystic enclaves

Output saves to `output/{game}/locations/`.

---

## Rumor Generator — `rumor_agent.py`

Generates GM-ready rumors with a spoken version (as someone would actually say it), the actual truth behind it, the danger of acting on it as stated, three hooks, and GM notes. Seeds use a game-specific subject pool combined with shared truth-angle and tone seeds.

**Optionally loads a saved location brief** to anchor the rumor to a specific place.

**Seed structure:**
- **Subject** (game-specific, ~18 per game) — what the rumor is fundamentally about: thieves' guild succession disputes, megacorp acquisitions, Alliance troop movements, Hegemony faction moves
- **Truth-angle** (shared, 6 options) — how the rumor relates to reality: mostly true / misunderstood / false but acted on / the wrong people know it / outdated / deliberate plant
- **Tone** (shared, 6 options) — how it's being told: urgently over a drink / offhand as old news / third-hand / as a warning / as an opportunity / whispered

**Output sections:** As Heard (in-character speech) → Source → What's Actually True → The Danger → Hooks (3) → GM Notes

Output saves to `output/{game}/rumors/`.

---

## Event Generator — `event_agent.py`

Generates GM-ready events that interrupt, escalate, or reframe what's already happening — not random encounter tables, but specific pressure that demands a response. Two seed elements per game (context — when it fires, and event — the specific thing that happens) produce combinations that feel purposeful rather than arbitrary. Fully game-specific: a Traveller event during jump transit is nothing like a D&D event during a long rest.

**Optionally loads a saved party brief and/or location brief** to tailor the event to a specific crew and place.

**Output sections:** When It Fires → What Happens → The Party's Position (what they know vs. don't) → Possible Responses (3) → Complications (2 escalating discoveries) → GM Notes

Each game has 15 contexts and 15 events (225 possible combinations per game):
- **D&D** — long rests, mid-negotiations, border crossings, funerals; backstory figures appearing, impossible bodies, legal requests with teeth, faction demands
- **Traveller** — jump transit, port inspections, patron meetings, gas giant refuelling; sensor anomalies, personal messages, comms log irregularities, rival crews
- **Firefly** — jobs in progress, ship laid up for repairs, Alliance patrols passing through; war veterans, Companion needs, cargo with extras, cortex records with convenient errors
- **Scum and Villainy** — score approaches, faction meetings, Hegemony checkpoints, Mystic consultations; neutral factions making moves, Ur artifacts surfacing, vice complications, old debts calling in

Output saves to `output/{game}/events/`.

---

## Encounter Generator — `encounter_agent.py`

Generates GM-ready encounter sketches seeded by randomised tables — four elements per game: context (setting), situation (what's happening), complication (what makes the obvious approach fail), and motivation (why the antagonist is doing this). The model does the creative work; the seeds prevent generic defaults.

**Optional:** Load a saved party brief to tailor the encounter to a specific crew's skills, history, and open hooks.

**Output sections:** Setting → Scene → Situation (full GM picture) → Key NPCs → Complication → Possible Outcomes (3) → Hooks → GM Notes

Each game has 20 entries per seed category (80 seeds total per game):
- **D&D** — fantasy locations, social conflicts, creatures behaving wrong, old wrongs surfacing
- **Traveller** — starports, derelict ships, faction entanglements, Imperial bureaucracy as weather
- **Firefly** — rim settlements, jobs that become something else, the war still casting a shadow
- **Scum and Villainy** — half-completed scores, faction intermediaries, Ur artifacts, things the crew wasn't told

Output saves to `output/encounters/{game}/`.

**Example:** Sundown on Verlayne — the Baroness Wants a Ride (Traveller)

---

## Ship Builder — `ship_agent.py`

Generates a complete ship profile: technical specifications, physical description, history, quirks, crew roles, current situation, and a GM hook. Three seed elements (history, quirk, current situation) prevent generic vessels.

**Stat generators by game:**
- **Traveller** — displacement (100t–1000t), jump rating, maneuver/power plant ratings, fuel capacity, cargo, staterooms, hardpoints
- **D&D** — hull points, damage threshold, speed in knots, crew min/max, cargo, weapon mounts; four size tiers (sloop to man-o-war)
- **Firefly** — Cortex dice (d4–d12) for Engines, Agility, Strength, Toughness; crew and cargo in narrative terms
- **Scum and Villainy** — FitD speed and hull tiers, cargo slots, optional special systems (cloaking plating, hardened vault, Hegemony transponder with unclear provenance, Ur-band receiver, etc.)

**Output sections:** Registry table → Description → History (with named former captains/owners) → Quirks → Crew Roles → Current Situation → GM Notes

Output saves to `output/ships/{game}/`.

---

## Shared Modules

### `names.py` — Name Generation

Two functions, each used by different generators to prevent cultural clustering.

**`roll_name_suggestion()`** — used by Traveller, Firefly, and Scum and Villainy. Draws from 15+ real-world cultural traditions and returns a first name, last name, and the tradition they come from. 25% chance of a cross-tradition blend (first name from one heritage, surname from another), flagged with `is_blend: True` and a note on the pairing.

Traditions include: West African, Arabic/Middle Eastern, East Asian, South Asian, Slavic, Spanish/Latin American, Norse/Scandinavian, Icelandic (with generated patronymics — Jónsson, Sigríðardóttir, etc.), Māori, North American Indigenous, Nahuatl/Maya, Andean/Mapuche, East African/Horn of Africa, Celtic/Irish/Welsh, Southeast Asian.

**`roll_dnd_name_suggestion(race=None)`** — used by D&D 5e. Draws from fantasy race-specific pools and requires a `race` parameter so the agent passes the character's chosen race before naming them. Races: Dwarf (compound epithets — Stronginthearm, Ironfoot), Halfling (warm compound family names — Warmhearth, Strongfeet), Elf (Elvish syllable-names with high-fantasy surnames), Tiefling (virtue names — Hope, Torment, Patience — with infernal surnames), Dragonborn (long Draconic clan names), Gnome (whimsical compound names), Half-Orc (earned epithets — Gorehand, Grimfang). Human redirects to the cultural tradition pools — the same 15+ real-world traditions as `roll_name_suggestion()` — so Human PCs get multi-cultural real-world names (Jelani Orriss, Iyari Sael Tovenn-Saltbough) rather than Anglo-generic fantasy defaults.

---

### `spells.py` — D&D Spell Suggestions

**`get_spell_suggestions(class_name, subclass=None)`** — story-first, not rules-complete. Returns 5–6 spells for a spellcasting class: one or two cantrips, two or three low-level spells (1–2), one higher-level signature. Each spell includes a one-line hook about what it says about the character who carries it — not a mechanical description.

Supports all eight 5e spellcasting classes: Wizard, Cleric, Druid, Bard, Sorcerer, Warlock, Paladin, Ranger (~20–35 spells per class, covering cantrips through level 9). Full casters (Wizard, Cleric, Druid, Bard, Sorcerer, Warlock) extend to level 9; Paladin covers levels 1–5; Ranger covers levels 1–5. Non-casters (Barbarian, Fighter, Monk, Rogue) return a clear skip message. Handles subclass flavour (School of Divination, The Fiend, etc.) as context without filtering the spell list.

Called by `dnd_agent.py` during full character and NPC generation for spellcasting classes. The agent picks 3–4 from the returned suggestions and writes a sentence per chosen spell about how *this character specifically* uses it.

---

### `gear.py` — Starting Equipment

**`roll_dnd_gear(class_name)`**, **`roll_traveller_gear(career)`**, **`roll_firefly_gear(role)`**, **`roll_scum_gear(playbook)`** — returns 4 items as JSON: a signature weapon or tool (always appropriate for the class/career/role), 2 supporting items drawn from a game-specific pool, and one personal item drawn from a shared pool that hints at history. Story-first — items have brief characterful descriptions, not stat blocks.

The personal item is always last. The system prompt instructs the model to give it one additional sentence about what it reveals about who the character is or was.

Traveller career lookup is case-insensitive with substring fallback — `"Navy (3rd Officer, 4 terms)"` resolves to the Navy kit correctly. Firefly role lookup is case-insensitive. Scum playbook lookup is exact, case-insensitive.

Each game has its own weapon pools, kit pools, and personal item list:
- **D&D** — 12 classes × 2–3 weapon options + 5 kit options; 15 shared personal items (letters, coins, portraits, keys)
- **Traveller** — 12 careers × 2–3 weapon options + 5 kit options; 12 shared personal items (star charts, data chips, hull-plating notes)
- **Firefly** — 9 roles × 1–3 weapon options + 5 kit options; 12 shared personal items ('Verse-specific: war medals, Cortex clippings, warranty cards)
- **Scum and Villainy** — 6 playbooks × 2–3 weapon options + 5 kit options; 12 shared personal items (data chips, faction tokens, Ur material)

---

### `psi.py` — Psionics, Mystics, and Readers

Story-first psionic ability profiles for the three sci-fi systems. Each game handles the gifted mind differently; this module provides the data pools, generation functions, rarity rolls, and tool schemas that let agents build psionic characters with mechanical grounding and narrative weight.

**Traveller — `get_traveller_psi_profile()`**
Returns a primary talent, 2–3 powers with PSI costs and story hooks, a discovery method, and the character's current social situation inside the Third Imperium. Six talents: Telepathy, Clairvoyance, Telekinesis, Teleportation, Awareness, Special. Weighted by setting rarity — Telepathy and Awareness are most common, Teleportation rare. Always includes the cheapest power from the chosen talent; samples 2 more from the rest.

**Scum & Villainy — `get_mystic_profile()`**
Returns how the character experiences the Ur-web (6 connection flavors: Resonance, Presence, Vision, Instinct, Echo, Wound), 3 ability suggestions from the Mystic playbook with story hooks, and one Ur artifact with its property and complication.

**Firefly — `get_reader_profile()`**
Returns a Reader Distinction (d8) with hinder hook, 2 mental Complications with triggers and expressions, an Alliance threat level, and 2 Signature Asset suggestions. Distinctions and assets are sampled without replacement so a single result is always internally consistent.

**Rarity rolls — canonical population probabilities**

Each game has a `roll_*_psi_chance(context)` function that rolls d100 against a threshold sourced from the rulebooks:

| System | Context | Chance |
|--------|---------|--------|
| Traveller | Imperial human | 3% |
| Traveller | Frontier world | 7% |
| Traveller | Zhodani prole | 15% |
| Traveller | Zhodani noble/intendant | 95% |
| Traveller | Droyne | 100% |
| S&V | General NPC | 5% |
| S&V | Notable NPC | 10% |
| Firefly | Any character | 2% |
| Firefly | Alliance Academy connection | 20% |

The result includes `has_ability` (bool), the raw roll, and — when true — a `next_step` string naming the profile function to call next. Agents call the chance roll first for every randomly generated character/NPC; they call the profile function only if `has_ability` is true. Explicitly requested psionic characters skip the chance roll.

For S&V player characters, playbook selection handles the choice — `roll_scum_psi_chance()` is for NPCs only. The Mystic playbook is 1 of 7, giving a ~14% base rate for random player characters.

---

### `ships.py` — Ship Names

**`roll_ship_name(game)`** — returns a name, class, and a one-line naming register note. Called by `ship_agent.py` and also by the character agents: Traveller calls it when ship shares appear during muster-out; Firefly and Scum call it to name the vessel the character flies on (included in the character sheet). Each game has its own pool of 30 names and 8–12 classes with a distinct naming character:

- **Traveller** — Imperial/formal: classical mythology, noble titles, navigation, and the quiet poetry of deep-space transit (*Empress Marava*, *March Harrier*, *Annic Nova*)
- **Firefly** — Personal, bittersweet: named for battles, lost ideals, second chances (*Serenity*, *Perdition's Flame*, *Borrowed Time*)
- **Scum and Villainy** — Criminal-poetic: dark elegance, sardonic irony, implied menace (*Pale Dreamer*, *Nothing Personal*, *Gentle Reminder*)
- **D&D** — Nautical/heroic: sea mythology, legendary creatures, weather and ocean imagery (*Kraken's Bane*, *Leviathan's Wake*, *Tidal Fury*)

---

### `dice.py` — Dice & Rules Lookups

Centralised dice rolling used by character and party generators.

- `roll_stat_dnd()` — 4d6 drop lowest, returns score and kept rolls
- `roll_dice_dnd(sides, count)` — any standard D&D die (d4/d6/d8/d10/d12/d20)
- `roll_dice_traveller(sides, count)` — d6 only (as per Mongoose 2e)
- `get_traveller_title(soc)` — SOC 11–15 → Knight/Baron/Marquis/Count/Duke with masculine and feminine forms

---

### `utils.py` — Shared Infrastructure

- `get_client()` — singleton Anthropic client
- `run_agent_loop()` — generic tool-use while loop with optional phase progress display
- `save_character()` — slugify heading → write to `output/{subdir}/characters/` with collision counter
- `strip_preamble()` — remove any text before the first `##` heading
- `slug()` — lowercase, collapse non-alphanumeric runs to dashes
- `pick()` — numbered terminal menu, returns selected key

---

## How it works

1. Claude receives a system prompt with the game's rules, design philosophy, and output format
2. It calls tools (dice rollers, name generators, seed tables, rules lookups) and gets real random results back
3. The tool-use loop continues until Claude writes the final output
4. The result is printed and saved to the appropriate `output/` subdirectory

The phase tracker prints plain-English progress as generation runs — you see `Rolling characteristics...` and `Naming key NPCs...` rather than raw tool calls.

Every generator is designed to prevent defaults: name tools push away from familiar clusters, seed tables force the model off the well-worn paths, and the system prompts name the specific clichés to avoid. A bad survival roll shouldn't be boring. A ship shouldn't just be a ship.

---

## Files

```
rpg-character-agents/
├── main.py                   # Top-level menu
│
├── agents/                   # AI agent runners — each calls Claude via tool-use loop
│   ├── dnd_agent.py          # D&D 5e — character, NPC, quest giver
│   ├── traveller_agent.py    # Mongoose Traveller 2e — character, NPC, patron
│   ├── firefly_agent.py      # Firefly RPG — character, NPC, job contact
│   ├── scum_villainy_agent.py# Scum and Villainy — character, NPC, score contact
│   ├── party_agent.py        # Party / crew builder (all four games)
│   ├── npc_cluster_agent.py  # Connected NPC group with internal relationships
│   ├── encounter_agent.py    # Encounter generator with seed tables
│   ├── ship_agent.py         # Ship builder with stats, history, quirks
│   ├── location_agent.py     # Location generator with atmosphere, NPCs, hooks
│   ├── rumor_agent.py        # Rumor generator with truth-angle and tone seeds
│   └── event_agent.py        # Event generator — interruptions that demand response
│
├── lib/                      # Pure Python — no API calls, fully tested
│   ├── dice.py               # Dice rolling and rules lookups
│   ├── gear.py               # Starting equipment — 4 games, class/career/role-specific
│   ├── names.py              # Name pools — 15+ traditions + D&D race pools
│   ├── psi.py                # Psionics/Mystic/Reader — 3 games, rarity rolls
│   ├── ships.py              # Ship name pools — 4 games, distinct registers
│   ├── spells.py             # D&D spell pools — 8 classes, story-first hooks
│   └── utils.py              # Shared infrastructure
│
├── tests/
│   ├── test_dnd.py
│   ├── test_traveller.py
│   ├── test_firefly.py
│   ├── test_scum.py
│   ├── test_party.py
│   ├── test_npc_cluster.py
│   ├── test_dice.py
│   ├── test_names.py
│   ├── test_ships.py
│   ├── test_gear.py
│   ├── test_spells.py
│   ├── test_psi.py
│   ├── test_encounter_agent.py
│   ├── test_ship_agent.py
│   ├── test_location_agent.py
│   ├── test_rumor_agent.py
│   ├── test_event_agent.py
│   └── test_utils.py
│
└── output/
    ├── dnd/
    │   ├── characters/
    │   ├── parties/
    │   ├── clusters/
    │   ├── encounters/
    │   ├── ships/
    │   ├── locations/
    │   ├── rumors/
    │   └── events/
    ├── traveller/
    │   ├── characters/
    │   ├── parties/
    │   ├── clusters/
    │   ├── encounters/
    │   ├── ships/
    │   ├── locations/
    │   ├── rumors/
    │   └── events/
    ├── firefly/
    │   ├── characters/
    │   ├── parties/
    │   ├── clusters/
    │   ├── encounters/
    │   ├── ships/
    │   ├── locations/
    │   ├── rumors/
    │   └── events/
    └── scum_villainy/
        ├── characters/
        ├── parties/
        ├── clusters/
        ├── encounters/
        ├── ships/
        ├── locations/
        ├── rumors/
        └── events/
```
