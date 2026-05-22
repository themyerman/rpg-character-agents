"""
Ship Builder — all four RPG game systems.

Generates a complete GM-ready ship profile: technical specs, physical
description, history, quirks, crew roles, current situation, and a hook.

Ships are seeded by three randomised elements — history, quirk, situation —
to prevent the model from defaulting to generic vessels. Stats are generated
per-game with appropriate mechanical weight (Traveller tonnage and jump
ratings, D&D hull points and crew, Firefly Cortex dice, Scum FitD tiers).

Saves to output/{game_subdir}/ships/.

Run with: python ship_agent.py
"""

import json
import random
import re
from pathlib import Path

from names import roll_name_suggestion, NAME_TOOL_SCHEMA
from ships import (
    roll_ship_name,
    TRAVELLER_SHIP_TOOL_SCHEMA,
    FIREFLY_SHIP_TOOL_SCHEMA,
    SCUM_SHIP_TOOL_SCHEMA,
    DND_SHIP_TOOL_SCHEMA,
)
from utils import get_client, run_agent_loop, slug, pick, strip_preamble


# ── Directory helpers ─────────────────────────────────────────────────────────

_OUTPUT = Path(__file__).parent / "output"

GAME_SUBDIRS: dict[str, str] = {
    "dnd":       "dnd",
    "traveller": "traveller",
    "firefly":   "firefly",
    "scum":      "scum_villainy",
}


# ── Ship seed tables ──────────────────────────────────────────────────────────

SHIP_SEED_POOLS: dict[str, dict[str, list[str]]] = {

    "dnd": {
        "histories": [
            "built for a merchant house that went bankrupt before the first voyage; the creditors sold her to cover a fraction of the debt",
            "she carried soldiers in a war that ended badly; the victors claimed her, then sold her off when she became inconvenient to explain",
            "originally a pirate vessel, legitimised by a letter of marque that was quietly voided two years later",
            "she's changed names at least three times; the old name is still visible under the paint on the stern if you know to look",
            "built by a noble family as a pleasure yacht; sold after the disgrace, sold again after the fire, sold a third time for reasons no one will say",
            "her first voyage discovered something that hasn't been officially acknowledged; the crew was sworn to silence and the logs were sealed",
            "she survived a storm that sank every other ship in the convoy; the crew has theories about why",
            "she was a smuggling vessel for twenty years before someone cleaned her up and filed new papers; the hidden compartments are still there",
            "she was built for a wizard who only sailed her once before disappearing; the commission was paid in full and the ship was never collected",
            "her former captain died aboard and was buried at sea; certain crew are particular about which cabin is used for storage",
            "she was taken as a prize three times; she has outlasted every crew that tried to claim her permanently",
            "she was built to a design that hasn't been used in fifty years; finding parts requires someone who knows the old ways",
            "she ran humanitarian supplies during a siege and became something of a symbol; that has complicated her subsequent owners' preferred business",
            "the original manifest lists a cargo that was never delivered and never recovered; the consignee has been trying to locate it for years",
            "she passed through a reef that charted ships have no business navigating; nobody on the current crew was there when it happened",
        ],
        "quirks": [
            "she makes no sound at all in certain winds — not less sound, no sound — which unnerves the crew",
            "the compass in the pilot house reads slightly off magnetic north; experienced sailors have learned to account for it",
            "fish do not follow her wake; local fishermen notice when she comes into port",
            "the captain's cabin door will not stay latched at night regardless of how it's secured",
            "she sits oddly in the water — slightly bow-heavy — for reasons the shipwright who inspected her could not explain",
            "her figurehead was replaced at some point with something that doesn't quite match the rest of the carving style",
            "she accelerates in the last hour before a storm better than she does in fair weather",
            "the same rope keeps working loose regardless of how carefully it's secured; the crew has superstitions about which knot to use",
            "certain crew members have reported hearing singing from below the waterline in deep water; others have heard nothing",
            "she heels to port in calm conditions and starboard in rough; experienced hands say she's always been this way",
            "she has survived damage that should have sunk her at least twice; the shipwright who patched her the last time refused to say what he found",
            "barnacles do not accumulate on her hull the way they should; she's never had to be careened",
            "birds avoid landing on her; gulls will follow her for miles without ever touching the rigging",
            "the lantern at the prow goes out in safe harbours and burns brightly in dangerous ones; whether this is meaningful or coincidence is debated",
            "she smells of cedar below decks, which is not what she was built from",
        ],
        "situations": [
            "in dry dock for repairs that have taken twice as long as the estimate, with a crew eating into their pay while they wait",
            "currently impounded by the harbour authority over a paperwork dispute that her owner insists is political",
            "for sale at a price that's either a bargain or a warning",
            "moored at a dock that doesn't officially exist, offloading cargo in the middle of the night",
            "sailing under sealed orders that only the captain has seen, with a crew that has started asking questions",
            "anchored off a coast nobody likes, waiting for a signal that's three days overdue",
            "making port with a hold full of something the crew insists is legitimate and a harbour master who isn't sure",
            "sailing with a skeleton crew after half the hands left at the last port without explanation",
            "being used as accommodation for people who can't afford the inn and have nowhere else to go",
            "running a route everyone else has abandoned after three ships disappeared on it this year",
            "sitting at anchor in a disputed harbour where two navies both consider her their lawful prize",
            "sailing with a passenger who paid triple the asking price and whose luggage is locked and very heavy",
            "making an unscheduled stop at a port not on the manifest, with no explanation logged",
            "under charter to a merchant house for a delivery that was supposed to take two weeks and is now in its fifth",
            "docked at a quiet harbour with a crew that arrived, unloaded nothing, loaded nothing, and is waiting",
        ],
    },

    "traveller": {
        "histories": [
            "she was a subsidised merchant on the Spinward Main for twelve years; the subsidy was withdrawn when the route became unprofitable and she was sold to pay debts",
            "she served with the Imperial Navy as a tender, then was decommissioned and sold — twice — before becoming what she is now",
            "she was built to spec for a free trader who died before taking delivery; the shipyard sold her to the highest bidder",
            "she's been flagged under five different registries in the last decade, each change made during a legal dispute that ended badly",
            "her original drive was replaced at a scout base twelve years ago; the replacement was better but had no paperwork",
            "she survived a misjump that put her six parsecs off course; the insurance claim was disputed and the matter was eventually dropped",
            "she was used as a long-term courier for an organisation that no longer officially exists; certain cargo locks have codes that nobody has changed",
            "a previous owner used her to move something they shouldn't have; the authorities closed the case but the file wasn't purged",
            "she was impounded at Rhylanor for eighteen months over a licensing dispute; whoever bought her at auction got a bargain if they didn't ask why",
            "she ran the same route for twenty years under the same captain, then the captain died and the heirs sold her immediately",
            "she was donated to a charitable foundation that promptly went insolvent; she's been in private hands since the liquidation",
            "she misjumped once and emerged in a system that isn't on any chart; nobody talks about what they saw there",
            "she was the site of a crime that was never solved to anyone's satisfaction; the current owner bought her specifically because the price reflected that",
            "she has more staterooms than a ship her tonnage should; something was removed from the cargo deck to make room, and nobody documented it",
            "she served a noble family for thirty years and was sold when the family's fortunes turned; the crest is still on the airlock panel",
        ],
        "quirks": [
            "the jump drive produces a harmonic at jump entry that sounds faintly like voices; the crew has stopped trying to identify words",
            "she runs cold — the life support requires higher settings than her specs suggest; engineers have checked and found nothing wrong",
            "the port sensor array has a blind spot in a specific arc that no calibration has corrected",
            "one of the cargo locks opens to a code that none of the current crew set; it's never been changed because nobody can decide whose job that is",
            "she consistently arrives at the edge of a jump window — never early, never more than six hours late",
            "the gravity plates on deck 2 cycle at a frequency that makes some people mildly nauseated after extended stays",
            "her transponder occasionally transmits a secondary ID that isn't registered to any known vessel",
            "she accelerates harder than her rated M-drive should allow; nobody has investigated this closely",
            "the ship's computer has a personality quirk that manifests as specific kinds of file organisation; new crew find it unnerving",
            "the captain's locker contains a personal log from a previous owner that nobody has read and nobody throws away",
            "she is consistently rated one condition better than her apparent age would suggest; the previous owners clearly spent money on her",
            "the emergency beacon has never needed to be used; the crew considers this unlucky rather than fortunate",
            "the drive room has a smell that comes and goes with no identifiable source; the mechanic has checked everything",
            "certain atmospheric readings taken aboard her are slightly off in ways that no calibration corrects; the sensors work fine on bench tests",
            "she has more fuel capacity than her original specs; a previous owner made a modification that was never filed with the shipyard",
        ],
        "situations": [
            "in dock at a Class D starport, waiting for parts that are two weeks overdue and a mechanic who hasn't shown up",
            "in transit with sealed cargo and a passenger who asked three questions in the first hour and hasn't spoken since",
            "moored at a freeport station under a flag of convenience while something aboard is resolved",
            "for sale, with a price that includes the ship and whatever complications she comes with",
            "running a route that recently lost two ships to causes the authorities haven't determined",
            "under charter to a patron who has changed the destination twice without explanation",
            "berthed at a highport under a lien filed by a party the current crew has never met",
            "in jump with a crew that recently became aware of something in the cargo manifest they weren't told about",
            "conducting a survey run in a system that doesn't appear on commercial charts",
            "parked in a belter camp doing nothing obvious while her crew waits for something",
            "impounded at an Imperial installation over a paperwork dispute that seems disproportionate to the paperwork",
            "making an emergency stop at a world whose starport rating makes that very uncomfortable",
            "currently crewed by people who weren't the original crew when she last made port",
            "operating in a system where the local authorities have her flagged for reasons nobody aboard can explain",
            "sitting at anchor in a system with no inhabited worlds, running on minimal power, with no departure filed",
        ],
    },

    "firefly": {
        "histories": [
            "she was built for a merchant family that sided with the Independents; what happened to the family is the kind of thing people on the rim don't ask about",
            "she ran supply lines during the Unification War on the Independent side; the hull is patched in twelve places from things that happened before the current crew joined",
            "she was Alliance-contracted freight for seven years before her captain decided that wasn't a liveable arrangement",
            "she's been the same ship for fifteen years and the same crew for most of that time; the crew has outlasted every attempt to separate them from her",
            "she was stripped to the frame at Persephone and rebuilt over two years by people who were very particular about what she became",
            "her previous captain sold her to cover a debt that shouldn't have been that large; the new crew knows better than to ask",
            "she ran medical supplies to worlds the Alliance medical corps didn't reach; the people who depended on those runs haven't forgotten",
            "she was impounded by Alliance customs three years ago and held for eleven months over a charge that was eventually dropped with no apology",
            "she was involved in something at Hera that none of the crew who were there talk about, and none of the crew who weren't don't ask about",
            "her engine was rebuilt by a mechanic who had opinions about how it should sound; it does sound different now, and the performance reflects it",
            "she's been passed between rim families for twenty years; half the crew consider themselves the rightful owners by relationship if not by law",
            "she was briefly famous, in a small way, for something she did during a crisis; that fame occasionally creates problems",
            "she was used as a hospital ship during something the Alliance's official record doesn't mention; some of the medical equipment is still aboard",
            "she survived a Reaver encounter that should have been fatal; the crew doesn't discuss it and newcomers are advised not to bring it up",
            "her original name was something else; the current name was given by the crew who bought her out of an impound lot with money they'd spent three years saving",
        ],
        "quirks": [
            "her engine has a specific sound at full burn that the mechanic calls singing; crew who've been aboard long enough can hear when she's unhappy",
            "she runs about ten percent hotter than she should on atmo entry; nobody has found the cause, and the shields have always held",
            "the galley has a smell nobody can identify and nobody has been able to eliminate; it's not unpleasant, which is why it's survived",
            "she receives signals on a frequency the Alliance stopped using in 2508; nobody knows if this is significant",
            "the port thruster takes longer to warm up in cold; the pilot accounts for this automatically without thinking",
            "she has a room that's always slightly colder than the rest of the ship; it's used for storage now",
            "the night mode lights in the crew quarters are dimmer than spec on the starboard side; it's been this way for years",
            "she can be coaxed to burn quieter on the atmo approach — quieter than she should be — if the pilot knows the throttle trick",
            "one of the external panels is welded shut; nobody aboard knows what's behind it or who welded it",
            "her cargo crane makes a sound the crew considers lucky; they're aware this is irrational and they don't care",
            "she carries considerably more weight than a ship her size should comfortably manage; nobody's quite sure how",
            "the backup navigation system has a set of coordinates pre-loaded that don't correspond to any registered world",
            "she has more hidden compartments than the current crew has found; they know this because they keep finding new ones",
            "the ship's clock runs two minutes fast; the crew runs their schedules against it and adjusts when they make contact with outside timekeeping",
            "she's survived three things that should have killed her; the crew considers this a personality trait rather than luck",
        ],
        "situations": [
            "sitting in a berth at a rim station, between jobs, with a crew that's starting to do the math on how long they can afford to wait",
            "in transit with a job that was described one way and is becoming clear is another way",
            "making port at a world the crew has reasons to avoid, because they have no other option right now",
            "for sale, nominally — but the asking price includes something the current crew isn't ready to let go of",
            "under watch by an Alliance officer who keeps showing up where they dock and calling it coincidence",
            "running a supply route to a settlement that the Alliance has stopped servicing and hasn't announced it's stopped servicing",
            "docked at a station run by people the captain owes a debt to, waiting to see what that debt costs",
            "making an emergency landing on a world that wasn't the destination, with a crew and passenger list that makes this complicated",
            "in transit with a passenger who paid in advance, in full, in cash, and asked no questions",
            "sitting with a hold full of legitimate cargo and an escort of questions about the hold full of cargo before this one",
            "running dark near the edge of the system, waiting for a contact that was supposed to arrive yesterday",
            "docked for what was supposed to be two days, now on day eleven, while something is resolved",
            "carrying a crew member's family member somewhere they very badly need to go",
            "making a run to a world that the crew knows is more complicated than the job description allowed for",
            "between jobs and between ports, technically adrift in one of those gaps that exists between deciding and doing",
        ],
    },

    "scum": {
        "histories": [
            "she was a Hegemony customs runner before someone with connections and no patience acquired her; the tracking package was mostly removed",
            "she was built for a Guild courier contract that fell through; the contractor sold her at a loss to someone who had uses for a fast ship with no obvious affiliation",
            "she's changed crew, flag, and name twice in the last three years; the current crew is the third to operate her under the current name",
            "she was part of a fleet that ran afoul of a Hegemony action; she's the only one that made it out; the current crew knows two different versions of why",
            "she was built by an Ur artifact salvage operation that went dark; someone acquired her from the estate",
            "she operated as a Forgotten Gods courier for six years; that association was severed, officially, under circumstances that benefited everyone to keep quiet",
            "she was confiscated by the Hegemony, sold at auction, confiscated again, sold again, and is currently operating under a registration that technically belongs to a shipping company that was dissolved",
            "her previous captain disappeared mid-run and the crew delivered the cargo, split the pay, and voted to keep operating",
            "she was used as a test platform for something the Ur salvage crews found; what they were testing is not documented",
            "she ran the same circuit for a Guild factor for eight years; when the factor retired, she was gifted to the crew in lieu of back pay",
            "she was operated by the Hegemony intelligence apparatus as a listening post under commercial cover; that arrangement ended badly for most of the people involved",
            "a noble family commissioned her and never explained why; when the commission was paid, they asked for certain modifications and then never took delivery",
            "she's been in the Procyon Sector for twenty years and has had more lives than the people who've crewed her",
            "she carries equipment from three previous operators, none of whom documented what they installed or why; the current crew is still finding things",
            "she was used in a score that became a legend in certain circles; the crew who ran it is mostly dead or scattered; the ship is the only survivor with a clear record",
        ],
        "quirks": [
            "the drive has a signature that Hegemony sensors struggle to distinguish from background radiation; whether this is engineered or accidental has never been determined",
            "she has more cargo space than her external dimensions should allow; nobody has successfully mapped the discrepancy",
            "the sensor package picks up Ur-band frequencies that no standard installation should receive; the readings are not always interpretable",
            "she runs cold — cooler than life support requires — which makes her difficult to track on thermal",
            "the ship's manifest system has been replaced so many times that the current version occasionally surfaces records from previous operators",
            "her reactor has a suppressed harmonic that only becomes audible in very specific conditions; the crew knows what those conditions are",
            "she has a panic configuration — a specific power state — that the previous crew clearly used regularly; the current crew discovered it by accident",
            "the lockdown sequence for the cargo bay is on a separate system from everything else, with a code that predates the current crew",
            "she handles differently in tight spaces than her profile suggests — better, specifically, and in ways the pilot has stopped questioning",
            "there is a compartment accessible only from outside the hull that none of the current crew put there",
            "the ship's AI assistant has an unusual pattern of what it remembers between sessions; certain conversations are apparently not logged",
            "she accelerates to escape velocity faster than her rated drive should allow; nobody has investigated this too closely",
            "certain Hegemony inspection systems have difficulty categorising her; she's been waved through three times on what should have been a hard stop",
            "the internal temperature in the hold fluctuates in a pattern that doesn't correspond to any mechanical cycle the engineer can identify",
            "she has an extremely specific reputation in certain port circles — not for what she's done but for what she's survived",
        ],
        "situations": [
            "docked at an independent station with a job offer on the table that needs an answer within twelve hours",
            "in transit with cargo that was described accurately and is still a problem",
            "holding position in a ghost sector while a situation on a nearby station resolves itself",
            "running hot — elevated heat from the last score — and looking for a low-profile layover",
            "for sale, technically, though the crew hasn't confirmed they're willing to make this real",
            "moored at a Hegemony-licensed station while the crew handles something that requires them to be somewhere they're not obviously connected to",
            "operating under a charter that pays exceptionally well and comes from a source the crew can't fully verify",
            "running a circuit that three other crews have recently declined for reasons they haven't shared",
            "docked with a crew member receiving treatment from someone who expects something in return",
            "carrying an Ur artifact that wasn't in the manifest and that nobody is currently claiming ownership of",
            "in a system that's become significantly more crowded with Hegemony presence in the last week",
            "waiting for a signal that will indicate whether a plan succeeded or failed; they'll know which by what the signal says",
            "making an unscheduled stop at a world because something aboard required it, and the crew is managing the fallout from that decision",
            "between scores, between ports, technically off the books, and running lower on options than they expected",
            "crewed by a mix of people who've worked together for years and two new additions who came aboard under time pressure and haven't fully explained themselves",
        ],
    },
}


# ── Seed roller functions ─────────────────────────────────────────────────────

def _roll_ship_seed(game: str) -> str:
    pool = SHIP_SEED_POOLS[game]
    return json.dumps({
        "history":   random.choice(pool["histories"]),
        "quirk":     random.choice(pool["quirks"]),
        "situation": random.choice(pool["situations"]),
    })


def roll_dnd_ship_seed() -> str:
    """Roll a D&D ship seed (history, quirk, current situation)."""
    return _roll_ship_seed("dnd")


def roll_traveller_ship_seed() -> str:
    """Roll a Traveller ship seed."""
    return _roll_ship_seed("traveller")


def roll_firefly_ship_seed() -> str:
    """Roll a Firefly ship seed."""
    return _roll_ship_seed("firefly")


def roll_scum_ship_seed() -> str:
    """Roll a Scum and Villainy ship seed."""
    return _roll_ship_seed("scum")


SEED_ROLLERS: dict[str, callable] = {
    "dnd":       roll_dnd_ship_seed,
    "traveller": roll_traveller_ship_seed,
    "firefly":   roll_firefly_ship_seed,
    "scum":      roll_scum_ship_seed,
}


# ── Stat generators ───────────────────────────────────────────────────────────

def roll_traveller_ship_stats() -> str:
    """Generate Mongoose Traveller 2e ship statistics."""
    tonnage = random.choices(
        [100, 200, 400, 800, 1000],
        weights=[30, 30, 20, 15, 5],
    )[0]

    jump    = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
    m_drive = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
    p_plant = max(jump, m_drive)

    # Fuel: jump fuel + 4-week power plant reserve
    jump_fuel = int(tonnage * jump * 0.1)
    pp_fuel   = int(tonnage * 0.02)

    # Cargo: subtract drives, fuel, and staterooms
    drive_overhead = int(tonnage * random.uniform(0.18, 0.28))
    staterooms     = max(2, tonnage // random.choice([20, 25, 30]))
    cargo          = max(0, tonnage - drive_overhead - (staterooms * 4) - jump_fuel - pp_fuel)

    hardpoints = max(1, tonnage // 100)

    age_years = random.choices(
        [3, 7, 12, 18, 25, 35],
        weights=[10, 20, 30, 20, 15, 5],
    )[0]
    condition = random.choices(
        ["Pristine", "Well-maintained", "Worn but reliable", "Showing her age", "Barely spaceworthy"],
        weights=[5, 20, 40, 25, 10],
    )[0]

    return json.dumps({
        "displacement":    f"{tonnage}t",
        "jump_rating":     f"J-{jump}",
        "maneuver_rating": f"M-{m_drive}",
        "power_plant":     f"P-{p_plant}",
        "fuel_capacity":   f"{jump_fuel}t (one jump) + {pp_fuel}t (power plant, 4 weeks)",
        "cargo_capacity":  f"{cargo}t",
        "staterooms":      staterooms,
        "hardpoints":      hardpoints,
        "age":             f"~{age_years} years",
        "condition":       condition,
    })


def roll_dnd_ship_stats() -> str:
    """Generate D&D 5e naval ship statistics."""
    size = random.choices(
        ["small", "medium", "large", "great"],
        weights=[25, 35, 25, 15],
    )[0]

    if size == "small":
        hull_hp    = random.randint(50, 100)
        speed      = f"{random.choice([8, 9, 10])} knots"
        crew_min   = random.randint(3, 8)
        crew_max   = random.randint(8, 15)
        cargo_tons = random.randint(5, 30)
        mounts     = random.randint(2, 6)
    elif size == "medium":
        hull_hp    = random.randint(100, 200)
        speed      = f"{random.choice([7, 8, 9])} knots"
        crew_min   = random.randint(8, 15)
        crew_max   = random.randint(15, 25)
        cargo_tons = random.randint(25, 80)
        mounts     = random.randint(6, 14)
    elif size == "large":
        hull_hp    = random.randint(200, 400)
        speed      = f"{random.choice([6, 7, 8])} knots"
        crew_min   = random.randint(15, 25)
        crew_max   = random.randint(25, 50)
        cargo_tons = random.randint(80, 200)
        mounts     = random.randint(12, 24)
    else:  # great — flagship, man-o-war
        hull_hp    = random.randint(400, 700)
        speed      = f"{random.choice([5, 6, 7])} knots"
        crew_min   = random.randint(40, 80)
        crew_max   = random.randint(80, 150)
        cargo_tons = random.randint(150, 400)
        mounts     = random.randint(24, 40)

    damage_threshold = hull_hp // 10

    age_years = random.choices(
        [2, 8, 15, 25, 40, 60],
        weights=[10, 20, 30, 20, 15, 5],
    )[0]
    condition = random.choices(
        ["Freshly fitted", "Sound", "Serviceable", "Weathered", "Barely seaworthy"],
        weights=[5, 20, 40, 25, 10],
    )[0]

    return json.dumps({
        "hull_points":        hull_hp,
        "damage_threshold":   damage_threshold,
        "speed":              speed,
        "crew_minimum":       crew_min,
        "crew_maximum":       crew_max,
        "cargo_capacity":     f"{cargo_tons} tons",
        "weapon_mounts":      mounts,
        "age":                f"~{age_years} years",
        "condition":          condition,
    })


_CORTEX_DICE = ["d4", "d6", "d8", "d10", "d12"]

def roll_firefly_ship_stats() -> str:
    """Generate Firefly RPG (Cortex System) ship statistics."""
    engines = random.choices(_CORTEX_DICE, weights=[5, 20, 35, 25, 15])[0]
    agility = random.choices(_CORTEX_DICE, weights=[10, 25, 35, 20, 10])[0]
    strength = random.choices(_CORTEX_DICE, weights=[5, 15, 35, 30, 15])[0]

    # Toughness roughly tracks Strength + 1 step
    strength_idx = _CORTEX_DICE.index(strength)
    toughness_idx = min(4, strength_idx + random.choice([0, 1, 1]))
    toughness = _CORTEX_DICE[toughness_idx]

    crew_capacity = random.choices(
        ["2 (very tight)", "4", "6", "8", "12+"],
        weights=[10, 30, 30, 20, 10],
    )[0]
    cargo_capacity = random.choices(
        ["minimal (2 tons)", "modest (8 tons)", "comfortable (25 tons)", "heavy (50+ tons)"],
        weights=[10, 25, 40, 25],
    )[0]

    age_years = random.choices(
        [3, 8, 15, 20, 30, 40],
        weights=[5, 15, 30, 25, 20, 5],
    )[0]
    condition = random.choices(
        ["Practically new", "Good working order", "Well-worn", "Beat up but flying", "One hard burn from dead"],
        weights=[5, 20, 40, 25, 10],
    )[0]

    return json.dumps({
        "engines":        engines,
        "agility":        agility,
        "strength":       strength,
        "toughness":      toughness,
        "crew_capacity":  crew_capacity,
        "cargo_capacity": cargo_capacity,
        "age":            f"~{age_years} years",
        "condition":      condition,
    })


_SCUM_SPECIALS = [
    "Sensor package (military grade, technically decommissioned)",
    "Cloaking plating (partial — kills the drive signature, not the mass)",
    "Hardened cargo vault (rated for Hegemony-class contraband)",
    "Medical bay (small but equipped)",
    "Remote piloting suite",
    "Extended fuel reservoir (+2 range)",
    "Concealed weapon mount (one hardpoint, unregistered)",
    "False hull plates (4 tons of hidden space)",
    "Emergency ejection pods",
    "Hegemony transponder (authentic — provenance unclear)",
    "Ur-band receiver (passive only, officially not installed)",
    "Armoured cockpit (separately sealed from the rest of the ship)",
    "Signal dampener (active — detectable at close range)",
    "Secondary airlock (not on the registry manifest)",
]

def roll_scum_ship_stats() -> str:
    """Generate Scum and Villainy (Forged in the Dark) ship statistics."""
    speed = random.choices(
        ["Slow (1)", "Average (2)", "Fast (3)", "Blazing (4)"],
        weights=[15, 35, 35, 15],
    )[0]
    hull = random.choices(
        ["Light (4 hull)", "Medium (6 hull)", "Heavy (8 hull)"],
        weights=[30, 40, 30],
    )[0]
    crew_capacity = random.choices(
        ["2-person", "4-person", "6-person", "10-person"],
        weights=[15, 35, 35, 15],
    )[0]
    cargo = random.choices(
        ["1 slot (very light)", "3 slots", "5 slots", "8 slots (heavy hauler)"],
        weights=[10, 30, 40, 20],
    )[0]

    n_specials = random.choices([0, 1, 2], weights=[15, 50, 35])[0]
    specials   = random.sample(_SCUM_SPECIALS, n_specials) if n_specials else []

    age_years = random.choices(
        [2, 6, 12, 20, 30],
        weights=[10, 20, 35, 25, 10],
    )[0]
    condition = random.choices(
        ["Fresh off the line", "Maintained", "Working order", "Rough", "Held together by spite"],
        weights=[5, 20, 40, 25, 10],
    )[0]

    return json.dumps({
        "speed":           speed,
        "hull":            hull,
        "crew_capacity":   crew_capacity,
        "cargo":           cargo,
        "special_systems": specials if specials else ["None on record"],
        "age":             f"~{age_years} years",
        "condition":       condition,
    })


STAT_ROLLERS: dict[str, callable] = {
    "dnd":       roll_dnd_ship_stats,
    "traveller": roll_traveller_ship_stats,
    "firefly":   roll_firefly_ship_stats,
    "scum":      roll_scum_ship_stats,
}


# ── Tool schemas ──────────────────────────────────────────────────────────────

_EMPTY_SCHEMA = {"type": "object", "properties": {}, "required": []}

DND_SHIP_SEED_SCHEMA: dict = {
    "name": "roll_dnd_ship_seed",
    "description": (
        "Roll a D&D ship seed: a history (how she got here), a quirk "
        "(what makes her distinctive), and a current situation. "
        "Call this before writing anything to prevent generic vessels."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

TRAVELLER_SHIP_SEED_SCHEMA: dict = {
    "name": "roll_traveller_ship_seed",
    "description": (
        "Roll a Traveller ship seed: a history (how she got here), a quirk "
        "(what makes her distinctive), and a current situation. "
        "Call this before writing to prevent generic free traders."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

FIREFLY_SHIP_SEED_SCHEMA: dict = {
    "name": "roll_firefly_ship_seed",
    "description": (
        "Roll a Firefly ship seed: a history (how she got here), a quirk "
        "(what makes her distinctive), and a current situation. "
        "Call this before writing to prevent generic Firefly-class clichés."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

SCUM_SHIP_SEED_SCHEMA: dict = {
    "name": "roll_scum_ship_seed",
    "description": (
        "Roll a Scum and Villainy ship seed: a history (how she got here), "
        "a quirk (what makes her distinctive), and a current situation. "
        "Call this before writing to prevent predictable crime-ship defaults."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

DND_SHIP_STATS_SCHEMA: dict = {
    "name": "roll_dnd_ship_stats",
    "description": (
        "Roll D&D 5e ship statistics: hull points, damage threshold, speed, "
        "crew requirements, cargo capacity, weapon mounts, age, and condition."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

TRAVELLER_SHIP_STATS_SCHEMA: dict = {
    "name": "roll_traveller_ship_stats",
    "description": (
        "Roll Mongoose Traveller 2e ship statistics: displacement, jump rating, "
        "maneuver drive, power plant, fuel capacity, cargo capacity, staterooms, "
        "hardpoints, age, and condition."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

FIREFLY_SHIP_STATS_SCHEMA: dict = {
    "name": "roll_firefly_ship_stats",
    "description": (
        "Roll Firefly RPG (Cortex) ship statistics: Engines die, Agility die, "
        "Strength die, Toughness die, crew capacity, cargo capacity, age, and condition."
    ),
    "input_schema": _EMPTY_SCHEMA,
}

SCUM_SHIP_STATS_SCHEMA: dict = {
    "name": "roll_scum_ship_stats",
    "description": (
        "Roll Scum and Villainy (FitD) ship statistics: speed tier, hull rating, "
        "crew capacity, cargo slots, special systems, age, and condition."
    ),
    "input_schema": _EMPTY_SCHEMA,
}


DND_SHIP_TOOLS: list[dict] = [
    DND_SHIP_TOOL_SCHEMA,
    DND_SHIP_SEED_SCHEMA,
    DND_SHIP_STATS_SCHEMA,
    NAME_TOOL_SCHEMA,
]

TRAVELLER_SHIP_TOOLS: list[dict] = [
    TRAVELLER_SHIP_TOOL_SCHEMA,
    TRAVELLER_SHIP_SEED_SCHEMA,
    TRAVELLER_SHIP_STATS_SCHEMA,
    NAME_TOOL_SCHEMA,
]

FIREFLY_SHIP_TOOLS: list[dict] = [
    FIREFLY_SHIP_TOOL_SCHEMA,
    FIREFLY_SHIP_SEED_SCHEMA,
    FIREFLY_SHIP_STATS_SCHEMA,
    NAME_TOOL_SCHEMA,
]

SCUM_SHIP_TOOLS: list[dict] = [
    SCUM_SHIP_TOOL_SCHEMA,
    SCUM_SHIP_SEED_SCHEMA,
    SCUM_SHIP_STATS_SCHEMA,
    NAME_TOOL_SCHEMA,
]

GAME_TOOLS: dict[str, list[dict]] = {
    "dnd":       DND_SHIP_TOOLS,
    "traveller": TRAVELLER_SHIP_TOOLS,
    "firefly":   FIREFLY_SHIP_TOOLS,
    "scum":      SCUM_SHIP_TOOLS,
}


# ── System prompts ────────────────────────────────────────────────────────────

_SHIP_FORMAT = """
Always use exactly this format:

## [Ship Name]
*[Class] — [one evocative phrase about what kind of ship she is]*

### Registry

| | |
|---|---|
| **Name** | [name] |
| **Class** | [class] |
[include all relevant stats as table rows]
| **Age** | [age] |
| **Condition** | [condition] |

### Description
[What you see from outside. What you notice in the first moments aboard. Specific sensory details — not generic "worn but sturdy." What is specific to this ship. 3–4 sentences.]

### History
[How she got here. Former owners or commanders with full names. Significant events in her life. What she was built for versus what she's become. Two paragraphs, written as story not as summary.]

### Quirks
Three to five specific quirks as bullets. Each quirk gets a bold name and a sentence of description. Make them specific and evocative — not "the engine runs loud" but what about the sound is specific and what the crew has made of it.

- **[Quirk Name]:** [description]

### Crew Roles
What positions this ship needs filled. Each role on its own line with a note about what that role means specifically on this vessel — what's unusual, what the ship demands of this particular crewmember.

### Current Situation
One paragraph. Where she is right now. What she needs. What she represents — to someone looking to buy her, hire her, or take her. What she's carrying, hiding, or waiting for.

### GM Notes
*One paragraph. The hook. One secret or complication that travels with this ship and will eventually surface — and what happens when it does.*
"""

DND_SYSTEM_PROMPT = f"""You are a D&D 5e ship designer creating vivid, immediately usable nautical vessels for GM prep.

Call tools in this order:
1. roll_ship_name() — to name and class the ship
2. roll_dnd_ship_stats() — to generate her mechanical profile
3. roll_dnd_ship_seed() — to seed her history, quirk, and current situation
4. roll_name_suggestion() — for each named person in her history (former captains, notable passengers, current crew leads)

Build everything from what the tools return. Do not discard or soften the seed — lean into the history and quirk.

Design philosophy:
- Ships in D&D are characters, not props. She has a history that shaped her and a personality that shows in how she handles.
- Crew roles should be specific to this ship's profile and quirks, not generic sailor positions.
- The GM Notes hook should be attached to the seed's history or quirk — something specific, not "pirates might attack."
- The history should name at least one former captain or notable figure. Use roll_name_suggestion for each.

If constraints were provided, incorporate them. Otherwise trust the tools.
{_SHIP_FORMAT}"""

TRAVELLER_SYSTEM_PROMPT = f"""You are a Mongoose Traveller 2e ship designer creating vivid, immediately usable vessels for GM prep in the Third Imperium.

Call tools in this order:
1. roll_ship_name() — to name and class the ship
2. roll_traveller_ship_stats() — to generate her mechanical profile (displacement, jump rating, etc.)
3. roll_traveller_ship_seed() — to seed her history, quirk, and current situation
4. roll_name_suggestion() — for each named person in her history (former captains, owners, notable crew)

Design philosophy:
- The Third Imperium is vast, commercially driven, and bureaucratically thorough about everything except the things it doesn't want documented. The ship should feel like she exists in that world.
- Stats matter. Reference the jump rating, tonnage, and cargo capacity meaningfully in the description and crew roles — a J-1 free trader lives a different life than a J-3 scout.
- The condition rating is a history. "Showing her age" means specific things about what's been maintained and what hasn't.
- Name every former owner or captain. Call roll_name_suggestion for each one.
- The quirk should have a mechanical implication the crew has learned to work around or exploit.

If constraints were provided, incorporate them. The naming register is Imperial/formal — names should feel like the Third Imperium's diversity.
{_SHIP_FORMAT}"""

FIREFLY_SYSTEM_PROMPT = f"""You are a Firefly RPG ship designer (Cortex System) creating vivid, immediately usable vessels for GM prep in the 'Verse.

Call tools in this order:
1. roll_ship_name() — to name and class the ship
2. roll_firefly_ship_stats() — to generate her Cortex dice profile
3. roll_firefly_ship_seed() — to seed her history, quirk, and current situation
4. roll_name_suggestion() — for each named person in her history (former captains, notable crew, people she's connected to)

Design philosophy:
- A ship in the 'Verse is home first and transport second. The crew names their ships. The ships earn their reputations. The relationship between a crew and their vessel is one of the most important in the game.
- The Cortex dice (Engines, Agility, Strength, Toughness) should translate into physical description. A high Engines die means something you can see in the exhaust configuration. A low Strength die means something you can feel when the hull flexes.
- The history should mention what happened during or after the Unification War, even obliquely. The 'Verse doesn't have a past that doesn't intersect with the war.
- The quirk should be something the mechanic has named and the crew has opinions about.
- Crew roles should reflect the Firefly RPG's role structure: Captain, Pilot, First Mate, Mechanic, Doctor, etc. Make each specific to this ship.

Names in the 'Verse span all cultural traditions. Call roll_name_suggestion for every named person.
{_SHIP_FORMAT}"""

SCUM_SYSTEM_PROMPT = f"""You are a Scum and Villainy ship designer (Forged in the Dark) creating vivid, immediately usable vessels for GM prep in the Procyon Sector.

Call tools in this order:
1. roll_ship_name() — to name and class the ship
2. roll_scum_ship_stats() — to generate her FitD profile (speed, hull, cargo, special systems)
3. roll_scum_ship_seed() — to seed her history, quirk, and current situation
4. roll_name_suggestion() — for each named person in her history

Design philosophy:
- Ships in Scum and Villainy are tools for the job, but they're also the crew's only home and their most valuable asset. The tension between those two things should be visible.
- The special systems (if any) should come from somewhere — explain the provenance of non-standard equipment. "Hegemony transponder (authentic — provenance unclear)" should raise questions.
- The Procyon Sector has factions with long memories. The ship's history should touch at least one of them — Guild, Hegemony, Brekk, Church of the Reconciled, Forgotten Gods, or the Ur.
- The quirk should have implications for operations — something that's an advantage in one context and a liability in another.
- Crew roles should use Scum and Villainy's playbook structure (Muscle, Pilot, Scoundrel, Mystic, Mechanic, Stitch, Speaker, Sniper).

Name every former captain or significant prior crew member. Use roll_name_suggestion for each.
{_SHIP_FORMAT}"""

GAME_SYSTEM_PROMPTS: dict[str, str] = {
    "dnd":       DND_SYSTEM_PROMPT,
    "traveller": TRAVELLER_SYSTEM_PROMPT,
    "firefly":   FIREFLY_SYSTEM_PROMPT,
    "scum":      SCUM_SYSTEM_PROMPT,
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def _run_tool(game: str, name: str, inputs: dict) -> str:
    if name == "roll_ship_name":            return roll_ship_name(game)
    if name == "roll_dnd_ship_seed":        return roll_dnd_ship_seed()
    if name == "roll_traveller_ship_seed":  return roll_traveller_ship_seed()
    if name == "roll_firefly_ship_seed":    return roll_firefly_ship_seed()
    if name == "roll_scum_ship_seed":       return roll_scum_ship_seed()
    if name == "roll_dnd_ship_stats":       return roll_dnd_ship_stats()
    if name == "roll_traveller_ship_stats": return roll_traveller_ship_stats()
    if name == "roll_firefly_ship_stats":   return roll_firefly_ship_stats()
    if name == "roll_scum_ship_stats":      return roll_scum_ship_stats()
    if name == "roll_name_suggestion":      return roll_name_suggestion()
    return f"Unknown tool: {name}"


def make_run_tool(game: str):
    def run_tool(name: str, inputs: dict) -> str:
        return _run_tool(game, name, inputs)
    return run_tool


# ── Phase tracking ────────────────────────────────────────────────────────────

PHASE_MESSAGES: dict[str, str] = {
    "name":   "Naming the ship...",
    "stats":  "Generating ship statistics...",
    "seed":   "Rolling ship seed...",
    "crew":   "Naming crew and history...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name == "roll_ship_name":          return "name"
    if tool_name.endswith("_ship_stats"):      return "stats"
    if tool_name.endswith("_ship_seed"):       return "seed"
    if tool_name == "roll_name_suggestion":    return "crew"
    return None


# ── Save helper ───────────────────────────────────────────────────────────────

def save_ship(content: str, game: str) -> Path:
    """Save ship profile to output/{subdir}/ships/{name-slug}-ship.md."""
    first_line = next(
        (l for l in content.strip().splitlines() if l.startswith("##")),
        content.strip().splitlines()[0],
    )
    title_raw  = re.sub(r"[#*]", "", first_line).strip()
    title_slug = slug(title_raw)
    filename   = f"{title_slug}-ship.md"

    subdir     = GAME_SUBDIRS.get(game, game)
    output_dir = _OUTPUT / subdir / "ships"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    if filepath.exists():
        stem    = filepath.stem
        counter = 2
        while filepath.exists():
            filepath = output_dir / f"{stem}-{counter}.md"
            counter += 1

    filepath.write_text(content)
    return filepath


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run_ship(game: str, desc: str = "") -> str:
    system_prompt = GAME_SYSTEM_PROMPTS[game]
    tools         = GAME_TOOLS[game]
    run_tool_fn   = make_run_tool(game)

    game_label = {
        "dnd":       "D&D 5e",
        "traveller": "Mongoose Traveller 2e",
        "firefly":   "Firefly RPG",
        "scum":      "Scum and Villainy",
    }[game]

    base = f"Generate a {game_label} ship profile."
    prompt = f"{base} Constraints or themes: {desc}" if desc else base

    return run_agent_loop(
        prompt, system_prompt, tools, run_tool_fn, detect_phase, PHASE_MESSAGES,
        max_tokens=4096,
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def run(game: str | None = None) -> None:
    if game is None:
        game = pick(
            "Which game?",
            [
                ("dnd",       "D&D 5e"),
                ("traveller", "Mongoose Traveller 2e"),
                ("firefly",   "Firefly RPG"),
                ("scum",      "Scum and Villainy"),
            ],
            default_idx=1,
        )

    desc = input(
        "\nAny constraints or themes? (e.g. 'smuggler, beat up, dark past' or press Enter for fully random):\n> "
    ).strip()

    result = strip_preamble(run_ship(game, desc))

    print("\n" + result)

    saved = save_ship(result, game)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
