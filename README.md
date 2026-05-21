# Tabletop Character Generators

AI-powered character and NPC generators for tabletop RPGs, built with the Anthropic Claude API. Each generator runs an agentic loop — Claude calls dice-rolling and rules-lookup tools, gets real random results back, and uses them to build characters that feel like they actually lived through something.

Supports **D&D 5e**, **Mongoose Traveller 2e**, **Firefly RPG (Cortex System)**, and **Scum and Villainy (Forged in the Dark)**.

The output folders contain example characters generated during development — ready to use as NPCs, inspiration, or starting points for your own sessions.

---

## Setup

Requires Python 3.11+ and an [Anthropic API key](https://console.anthropic.com).

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your-key-here
```

To run tests (no API key required — tests cover pure Python logic only):

```bash
pip install pytest
pytest tests/
```

---

## D&D 5e — `dnd_agent.py`

```bash
python dnd_agent.py
```

**Modes:**
- `full` — Full character sheet with ability scores (4d6 drop lowest), race, class, background, personality, connections, equipment, and backstory
- `npc` — Quick NPC sketch: stat block, demeanor, want, secret, hook, and one named connection
- `questgiver` — Hook encounter: who approaches the party, the pitch in direct speech, what they want, what they're offering, and four possible truths. The DM rolls 1d4 in secret — Truth 4 is always The Reversal, where the party is on the wrong side of the story.

You can describe what you want in plain English, or press Enter for fully random. Output saves to `dnd_characters/` as `character-name-full.md`, `character-name-npc.md`, or `character-name-questgiver.md`.

**Example characters generated:**
- Pip "Tallowfingers" Underbough — Lightfoot Halfling Rogue, hunting the gang boss who took her brother
- Halben Orriss — Quest giver, master glassblower with a missing apprentice and a problem he can't take to the guild

---

## Mongoose Traveller 2e — `traveller_agent.py`

```bash
python traveller_agent.py
```

**Modes:**
- `full` — Full character with rolled UPP, homeworld (complete UWP), career history (2–6 terms), mishaps, connections, muster out benefits, and backstory. Ship shares are treated as story hooks, not line items.
- `npc` — Quick NPC sketch in Traveller format: UPP, career, demeanor, want, secret, hook
- `patron` — Classic Traveller patron encounter: the job, the pitch (in direct speech), the payment, and four possible truths. The referee rolls 1d4 in secret — Truth 4 is always The Reversal, where the crew is on the wrong side of the job.

Output saves to `traveller_characters/` as `character-name-full.md`, `character-name-npc.md`, or `character-name-patron.md`.

**Example characters generated:**
- Séverine "Sev" Aldenberg-Vey — Navy, 4 terms, ship shares and unfinished business
- Korven "Half-Lung" Drask — Drifter, 6 terms, Cr105k he shouldn't have
- Nasrin "Nas" al-Qadeer — Scout, 2 terms, her own ship and four languages
- Halvar Czeszko — Patron encounter, cargo job that's probably not a cargo job

---

## Firefly RPG — `firefly_agent.py`

```bash
python firefly_agent.py
```

Cortex System character generation for the 'Verse. Die sizes (d4–d12) replace numeric scores; Distinctions are story engines that can help or hurt depending on the situation.

**Modes:**
- `full` — Full character sheet: role, homeworld (Core/Border/Rim), Unification War history, six attributes with die ratings, 6–8 skills, three Distinctions with story notes, Signature Asset, Complications, and backstory
- `npc` — Quick NPC sketch: role, homeworld, key attributes, distinctions, wants, secret, and one hook
- `jobcontact` — Hook encounter: who's hiring, the pitch in direct speech, what they want, what they're offering, and four possible truths. The GM rolls 1d4 in secret — Truth 4 is always The Reversal, where the crew is on the wrong side of the job.

The generator rolls war history randomly and distributes attribute dice (d4–d10) across the six Cortex attributes. Roles available: Captain, Pilot, First Mate, Mechanic, Doctor, Shepherd, Muscle, Grifter, Thief.

Output saves to `firefly_characters/` as `character-name-full.md`, `character-name-npc.md`, or `character-name-jobcontact.md`.

**Example characters generated:**
- Kezia "Halberd" Ramos — Captain, Beaumonde Border, Browncoat vet with a stolen ship and a score to settle
- Liora Aldermere-Sato — Grifter, Osiris Core, Alliance-educated and deliberately running from it

---

## Scum and Villainy — `scum_villainy_agent.py`

```bash
python scum_villainy_agent.py
```

Forged in the Dark character generation for crews operating at the edge of the Hegemony. Action ratings (0–4 dots), playbook special abilities, stress/trauma tracks, and a specific vice with a named purveyor.

**Modes:**
- `full` — Full crew member: playbook, heritage, background, vice, starting action dots grouped by attribute (Insight/Prowess/Resolve), one special ability, XP triggers, stress and trauma tracks, and backstory
- `npc` — Quick NPC sketch: playbook equivalent, heritage, background, key actions, wants, secret, and hook
- `scorecontact` — Hook encounter: who's offering the score, the pitch in direct speech, what they want, what they're paying, and four possible truths. The GM rolls 1d4 in secret — Truth 4 is always The Reversal, where the crew is on the wrong side of the job.

Playbooks: Muscle, Pilot, Scoundrel, Mystic, Speaker, Stitch. Action dots use filled/empty circles (●○○○). Pilot uses Helm instead of Skirmish; Stitch uses Patch instead of Tinker.

Output saves to `scum_villainy_characters/` as `character-name-full.md`, `character-name-npc.md`, or `character-name-scorecontact.md`.

**Example characters generated:**
- Adaeze "Reins" Vukoja — Pilot, Iruvia heritage, Skovlan background, steady hands and a dangerous calm
- Yusra "Vey" Okonkwo — Scoundrel, Severos heritage, Labor background, owes the wrong people too much

---

## Party & Crew Builder — `party_agent.py`

```bash
python party_agent.py
```

GM prep tool that assembles a party (D&D) or crew (Traveller, Firefly, Scum and Villainy) with connective tissue — shared history, fault lines, secrets, and a first session hook. Works with your saved characters, generates fresh ones, or mixes both.

**Interactive flow:**
1. Game: `dnd` / `traveller` / `firefly` / `scum`
2. Party/crew size (default: 4)
3. Mode: `folder` (pick from saved characters) / `generate` (all fresh) / `mix` (some of each)
4. If folder or mix: pick characters by number from a displayed list
5. Optional theme or constraints in plain English (e.g. "gothic horror, vampire hunters" or "crew stranded on the frontier with a broken drive")
6. Optional: generate a tailored opening hook at the end (quest giver / patron / job contact / score contact)

Output saves to `parties/` as `game-party-name-party.md`. Opening hooks save to the appropriate characters folder.

**Output sections:** Members roster with roles → How They Came Together → What Holds Them Together → The Fault Line → Shared Secret → First Session Hook

---

## How it works

`main.py` is the bare-bones reference — a single API call, nothing more. The agents build on that foundation:

1. Claude receives a system prompt with the game's rules and output format
2. It calls tools (dice rollers, rules lookups) and gets real random results back
3. The loop continues until Claude calls no more tools and writes the final character sheet
4. The result is printed and saved

The phase tracker prints plain-English progress as generation runs — you see "Rolling characteristics..." and "Mustering out..." rather than raw tool calls.

---

## Files

```
rpg-character-agents/
├── main.py                  # Stage 1 reference — bare API call
├── dnd_agent.py             # D&D 5e generator
├── traveller_agent.py       # Mongoose Traveller 2e generator
├── firefly_agent.py         # Firefly RPG (Cortex System) generator
├── scum_villainy_agent.py   # Scum and Villainy (Forged in the Dark) generator
├── party_agent.py           # Party / crew builder (all four games)
├── tests/                   # Unit tests (pure Python logic — no API calls)
│   ├── test_dnd.py
│   ├── test_traveller.py
│   ├── test_firefly.py
│   ├── test_scum.py
│   └── test_party.py
├── dnd_characters/          # D&D output
├── traveller_characters/    # Traveller output
├── firefly_characters/      # Firefly output
├── scum_villainy_characters/ # Scum and Villainy output
└── parties/                 # Party / crew brief output
```
