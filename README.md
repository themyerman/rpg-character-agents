# Tabletop Character Generators

AI-powered character and NPC generators for tabletop RPGs, built with the Anthropic Claude API. Each generator runs an agentic loop — Claude calls dice-rolling and rules-lookup tools, gets real random results back, and uses them to build characters that feel like they actually lived through something.

Currently supports **D&D 5e** and **Mongoose Traveller 2e**.

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
- `character` — Full character sheet with ability scores (4d6 drop lowest), race, class, background, personality, connections, equipment, and backstory
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
- `character` — Full character with rolled UPP, homeworld (complete UWP), career history (2–6 terms), mishaps, connections, muster out benefits, and backstory. Ship shares are treated as story hooks, not line items.
- `npc` — Quick NPC sketch in Traveller format: UPP, career, demeanor, want, secret, hook
- `patron` — Classic Traveller patron encounter: the job, the pitch (in direct speech), the payment, and four possible truths. The referee rolls 1d4 in secret — Truth 4 is always The Reversal, where the crew is on the wrong side of the job.

Output saves to `traveller_characters/` as `character-name-full.md`, `character-name-npc.md`, or `character-name-patron.md`.

**Example characters generated:**
- Séverine "Sev" Aldenberg-Vey — Navy, 4 terms, ship shares and unfinished business
- Korven "Half-Lung" Drask — Drifter, 6 terms, Cr105k he shouldn't have
- Nasrin "Nas" al-Qadeer — Scout, 2 terms, her own ship and four languages
- Halvar Czeszko — Patron encounter, cargo job that's probably not a cargo job

---

## Party & Crew Builder — `party_agent.py`

```bash
python party_agent.py
```

GM prep tool that assembles a party (D&D) or crew (Traveller) with connective tissue — shared history, fault lines, secrets, and a first session hook. Works with your saved characters, generates fresh ones, or mixes both.

**Interactive flow:**
1. D&D or Traveller
2. Party size (default: 4)
3. Mode: `folder` (pick from saved characters) / `generate` (all fresh) / `mix` (some of each)
4. If folder or mix: pick characters by number from a displayed list
5. Optional: generate a tailored quest giver or patron hook at the end

Output saves to `parties/` as `game-party-name-party.md`. Opening hooks save to the appropriate characters folder.

**Example output sections:** Members roster with roles → How They Met → What Holds Them Together → The Fault Line → Shared Secret → First Session Hook

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
agents/
├── main.py                  # Stage 1 reference — bare API call
├── dnd_agent.py             # D&D 5e generator
├── traveller_agent.py       # Mongoose Traveller 2e generator
├── party_agent.py           # Party / crew builder
├── tests/                   # Unit tests (pure Python logic — no API calls)
│   ├── test_dnd.py
│   ├── test_traveller.py
│   └── test_party.py
├── dnd_characters/          # D&D output
├── traveller_characters/    # Traveller output
└── parties/                 # Party brief output
```
