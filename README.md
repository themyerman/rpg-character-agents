# Tabletop RPG Generators

AI-powered GM tools for tabletop RPGs, built with the Anthropic Claude API. Each generator runs an agentic tool-use loop — Claude calls dice rollers, rules lookups, name generators, and seed tables, gets real random results back, and uses them to produce output that feels like it actually lived through something.

Supports **D&D 5e**, **Mongoose Traveller 2e**, **Firefly RPG (Cortex System)**, and **Scum and Villainy (Forged in the Dark)**.

The `output/` folder contains examples generated during development — characters, parties, encounters, and ships ready to use or adapt.

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

A numbered menu walks you through the options:

1. **Build a character or NPC**
2. **Build a party / crew**
3. **Build an NPC cluster**
4. **Generate an encounter**
5. **Build a ship**

Each agent can also be run directly:

```bash
python dnd_agent.py
python traveller_agent.py
python firefly_agent.py
python scum_villainy_agent.py
python party_agent.py
python npc_cluster_agent.py
python encounter_agent.py
python ship_agent.py
```

Every generator accepts a plain English prompt — use it to add a concept, a constraint, or a swerve. You can be vague (`"someone with a secret"`) or precise (`"ex-navy medic, cashiered for something she still thinks was right"`). The dice still roll. The description just tilts the output.

---

## Character Generators

### D&D 5e — `dnd_agent.py`

**Modes:**
- `full` — Full character sheet: ability scores (4d6 drop lowest), race, class, background, personality, named connections, equipment, and backstory
- `npc` — Quick sketch: stat block, demeanor, want, secret, hook, and one named connection
- `questgiver` — Hook encounter: who approaches the party, the pitch in direct speech, what they want, what they're offering, and four possible truths (the DM rolls 1d4 in secret — Truth 4 is always The Reversal)

Output saves to `output/characters/dnd/`.

**Examples:** Pip "Tallowfingers" Underbough (Halfling Rogue), Iyari Sael Tovenn-Saltbough (full character), Halben Orriss (quest giver with a missing apprentice and a guild problem)

---

### Mongoose Traveller 2e — `traveller_agent.py`

**Modes:**
- `full` — Full character with rolled UPP, homeworld (complete UWP with atmosphere, hydrographics, law level, tech level, background skills), career history (2–6 terms), survival rolls, d66 events, mishaps, named connections, muster out benefits, pension. Ship shares are treated as story hooks, not line items.
- `npc` — Quick sketch in Traveller format: UPP, career, demeanor, want, secret, hook
- `patron` — Classic Traveller patron encounter: the job, the pitch in direct speech, the payment, and four possible truths (referee rolls 1d4 in secret — Truth 4 is The Reversal)

Noble titles are awarded by Social Standing: SOC 11 = Knight (Sir/Dame), 12 = Baron/Baroness, 13 = Marquis/Marchioness, 14 = Count/Countess, 15 = Duke/Duchess.

Output saves to `output/characters/traveller/`.

**Examples:** Séverine "Sev" Aldenberg-Vey (Navy, 4 terms, ship shares and unfinished business), Korven "Half-Lung" Drask (Drifter, 6 terms, Cr105k he shouldn't have), Nasrin "Nas" al-Qadeer (Scout, 2 terms, her own ship and four languages)

---

### Firefly RPG — `firefly_agent.py`

Cortex System character generation for the 'Verse. Die sizes (d4–d12) replace numeric scores; Distinctions are story engines that help or hurt depending on the situation.

**Modes:**
- `full` — Full character: role, homeworld (Core/Border/Rim), Unification War history, six attributes with die ratings, 6–8 skills, three Distinctions with story notes, Signature Asset, Complications, and backstory
- `npc` — Quick sketch: role, homeworld, key attributes, distinctions, wants, secret, hook
- `jobcontact` — Hook encounter: who's hiring, the pitch in direct speech, what they want, what they're offering, and four possible truths (Truth 4 is always The Reversal)

Roles: Captain, Pilot, First Mate, Mechanic, Doctor, Shepherd, Muscle, Grifter, Thief.

Output saves to `output/characters/firefly/`.

**Examples:** Kezia "Halberd" Ramos (Captain, Beaumonde, Browncoat vet with a stolen ship), Liora Aldermere-Sato (Grifter, Osiris Core, Alliance-educated and running from it)

---

### Scum and Villainy — `scum_villainy_agent.py`

Forged in the Dark character generation for crews at the edge of the Hegemony. Action ratings (0–4 dots), playbook special abilities, stress/trauma tracks, and a vice with a named purveyor.

**Modes:**
- `full` — Full crew member: playbook, heritage, background, vice, action dots by attribute (Insight/Prowess/Resolve), one special ability, XP triggers, stress and trauma tracks, backstory
- `npc` — Quick sketch: playbook equivalent, heritage, background, key actions, wants, secret, hook
- `scorecontact` — Hook encounter: who's offering the score, the pitch in direct speech, what they want, what they're paying, and four possible truths (Truth 4 is always The Reversal)

Playbooks: Muscle, Pilot, Scoundrel, Mystic, Speaker, Stitch. Action dots use filled/empty circles (●○○○).

Output saves to `output/characters/scum_villainy/`.

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

Used by every generator to prevent cultural clustering. Two functions:

**`roll_name_suggestion()`** — draws from 15+ real-world cultural traditions and returns a first name, last name, and the tradition they come from. 25% chance of a cross-tradition blend (first name from one heritage, surname from another), flagged with `is_blend: True` and a note on the pairing.

Traditions include: West African, Arabic/Middle Eastern, East Asian, South Asian, Slavic, Spanish/Latin American, Norse/Scandinavian, Icelandic (with generated patronymics — Jónsson, Sigríðardóttir, etc.), Māori, North American Indigenous, Nahuatl/Maya, Andean/Mapuche, East African/Horn of Africa, Celtic/Irish/Welsh, Southeast Asian.

**`roll_dnd_name_suggestion(race=None)`** — draws from fantasy race-specific pools. Races: Dwarf (compound epithets — Stronginthearm, Ironfoot), Halfling (warm compound family names — Warmhearth, Strongfeet), Elf (Elvish syllable-names with high-fantasy surnames), Tiefling (virtue names — Hope, Torment, Patience — with infernal surnames), Dragonborn (long Draconic clan names), Gnome (whimsical compound names), Half-Orc (earned epithets — Gorehand, Grimfang). Human redirects to the cultural tradition pools.

---

### `ships.py` — Ship Names

**`roll_ship_name(game)`** — returns a name, class, and a one-line naming register note. Each game has its own pool of 30 names and 8–12 classes with a distinct naming character:

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
- `save_character()` — slugify heading → write to `output/characters/{subdir}/` with collision counter
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
├── dnd_agent.py              # D&D 5e — character, NPC, quest giver
├── traveller_agent.py        # Mongoose Traveller 2e — character, NPC, patron
├── firefly_agent.py          # Firefly RPG — character, NPC, job contact
├── scum_villainy_agent.py    # Scum and Villainy — character, NPC, score contact
│
├── party_agent.py            # Party / crew builder (all four games)
├── npc_cluster_agent.py      # Connected NPC group with internal relationships
├── encounter_agent.py        # Encounter generator with seed tables
├── ship_agent.py             # Ship builder with stats, history, quirks
│
├── dice.py                   # Dice rolling and rules lookups
├── names.py                  # Name pools — 15+ traditions + D&D race pools
├── ships.py                  # Ship name pools — 4 games, distinct registers
├── utils.py                  # Shared infrastructure
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
│   ├── test_encounter_agent.py
│   ├── test_ship_agent.py
│   └── test_utils.py
│
└── output/
    ├── characters/
    │   ├── dnd/
    │   ├── traveller/
    │   ├── firefly/
    │   └── scum_villainy/
    ├── parties/
    │   ├── dnd/
    │   ├── traveller/
    │   ├── firefly/
    │   └── scum_villainy/
    ├── encounters/
    │   ├── dnd/
    │   ├── traveller/
    │   ├── firefly/
    │   └── scum_villainy/
    └── ships/
        ├── dnd/
        ├── traveller/
        ├── firefly/
        └── scum_villainy/
```
