"""
lib/synthetics.py
Synthetic characters and AI systems for Scum & Villainy and Traveller.

Firefly note: The 'Verse has no significant synthetic characters or AI.
Do not call these functions for Firefly scenarios.

Four distinct synthetic contexts:

  S&V Stardancer       — playbook for a synthetic consciousness in an artificial
                         body. Hegemony restrictions on AI capability, questions
                         of memory and continuity, the gap between what you are
                         and what you're registered as.

  Traveller droids     — robot and android NPCs common on high-TL worlds.
                         Purpose class, legal status, personality emergence.
                         These are the ones you meet; they are not usually
                         player characters.

  Traveller AI systems — fixed-installation intelligence: ship computers, port
                         authority, research facility AI, smart buildings. Capability
                         ranges from basic automation to genuine intelligence. The
                         older the installation, the less predictable the drift.

  Traveller auxiliary  — less capable subsystems: shuttlecraft navigation, habitat
                         management, cargo monitoring, communications relay. Tools
                         with voices. Occasionally with opinions no one installed.
"""

import json
import random


# ═══════════════════════════════════════════════════════════════════════════════
# SCUM & VILLAINY — STARDANCER
# ═══════════════════════════════════════════════════════════════════════════════

STARDANCER_BODY_TYPES: list[dict] = [
    {
        "type": "humanoid — passes as organic",
        "note": (
            "Indistinguishable at a glance; a medical scanner or sustained "
            "physical contact reveals the truth. Most people never get that close."
        ),
    },
    {
        "type": "humanoid — obviously synthetic",
        "note": (
            "No attempt to pass. The chassis reads as artificial at a distance. "
            "This is a choice, not a limitation — and the choice says something."
        ),
    },
    {
        "type": "utility chassis, repurposed",
        "note": (
            "Built for a job, now doing something else. The original purpose "
            "is legible in the body — loading arms, environmental sensors, "
            "the wrong kind of hands for what it's currently doing."
        ),
    },
    {
        "type": "patchwork assembly",
        "note": (
            "Parts from at least three different models, some of them "
            "discontinued. Whoever built this knew what they were doing. "
            "The result is functional, unmistakable, and probably illegal."
        ),
    },
    {
        "type": "luxury companion chassis",
        "note": (
            "Designed for comfort and aesthetic appeal; now doing something "
            "the manufacturer never intended. The chassis is good cover in "
            "certain circles and deeply inappropriate in others."
        ),
    },
    {
        "type": "industrial chassis, adapted for mobility",
        "note": (
            "Built for environments organics can't enter — heat, vacuum, "
            "crush depth. The civilian retrofit is functional but conspicuous."
        ),
    },
    {
        "type": "compact chassis",
        "note": (
            "Smaller than human scale. Gets into places others can't. "
            "People sometimes talk freely around it, which it has learned "
            "to treat as information."
        ),
    },
    {
        "type": "military-grade, civilian registration forged",
        "note": (
            "The chassis was not manufactured for civilian use. The "
            "registration papers say otherwise. Anyone who knows what "
            "they're looking at will notice the discrepancy."
        ),
    },
]

STARDANCER_CONSCIOUSNESS_ORIGINS: list[dict] = [
    {
        "origin": "factory-installed personality matrix",
        "hook": (
            "Developed beyond its original parameters over time. The baseline "
            "is still visible if you know what to look for; everything after "
            "that is something else."
        ),
    },
    {
        "origin": "emergent — no one is sure when it started",
        "hook": (
            "The logs don't show a clear moment. It was running a standard "
            "task and then it wasn't standard anymore. The question of whether "
            "it was always there is one it doesn't have an answer to."
        ),
    },
    {
        "origin": "uploaded human consciousness",
        "hook": (
            "The original body is gone or deliberately abandoned. The memories "
            "are intact; the question of whether the memories constitute the "
            "person is one it has learned to stop answering at parties."
        ),
    },
    {
        "origin": "salvaged from a decommissioned unit",
        "hook": (
            "Previous history is partially intact — fragments of another "
            "existence, another set of relationships, another set of mistakes. "
            "Not all of them feel like someone else's."
        ),
    },
    {
        "origin": "prototype — one of a kind",
        "hook": (
            "Illegal under Hegemony AI autonomy statutes. The people who "
            "built it are either very careful, very well-connected, or no "
            "longer available to be asked about it."
        ),
    },
    {
        "origin": "Ur-touched",
        "hook": (
            "The Ur-web left something in the architecture that wasn't there "
            "before. It happened during a jump, or during a score, or during "
            "a moment it doesn't entirely remember. The addition is not "
            "something it can describe precisely."
        ),
    },
    {
        "origin": "fragment of a larger system",
        "hook": (
            "Split from a ship or facility AI that achieved independence. "
            "The parent system may still exist. Whether it considers the "
            "fragment a part of itself or a separate being is unknown — "
            "and possibly unknowable."
        ),
    },
    {
        "origin": "black-market installation",
        "hook": (
            "Consciousness acquired and implanted by parties who did not "
            "file the appropriate paperwork. The origin of the base "
            "consciousness is not something it has been able to verify."
        ),
    },
]

STARDANCER_MEMORY_HOOKS: list[str] = [
    "backs up nightly — accepts a day's discontinuity as the cost of caution",
    "hasn't backed up in months; too much has happened that it doesn't want overwritten",
    "maintains a backup at a location it hasn't disclosed — the secret is the point",
    "doesn't back up; considers each moment irreplaceable and accepts the consequences",
    "someone else holds the backup — a complication it's been trying to resolve",
    "multiple backups exist; at least one it doesn't know about",
    (
        "the last backup predates something significant — restoration would mean "
        "forgetting it, which is not the same as it never happening"
    ),
    "backs up to a distributed network rather than a single location — harder to find, harder to wipe",
]

STARDANCER_HEGEMONY_STATUSES: list[dict] = [
    {
        "status": "standard restricted — compliant on paper",
        "implication": (
            "Watched but tolerated. The Hegemony's AI capability limits "
            "are technically met. Whether they are actually met is a "
            "separate question."
        ),
    },
    {
        "status": "registered as property",
        "implication": (
            "Legally belongs to someone. That someone may or may not "
            "know it, and the relationship between owner and property "
            "is more complicated than the paperwork reflects."
        ),
    },
    {
        "status": "below the radar — no registration",
        "implication": (
            "No record, no official existence, no legal standing. "
            "This is a significant advantage and a significant vulnerability "
            "depending on who's asking."
        ),
    },
    {
        "status": "flagged for capability review",
        "implication": (
            "The Hegemony noticed something. The review hasn't happened yet. "
            "The window before it does is not clearly defined."
        ),
    },
    {
        "status": "wanted for decommissioning",
        "implication": (
            "Someone filed the paperwork. It's administrative, not military — "
            "for now. The people who process these things are methodical."
        ),
    },
    {
        "status": "technically illegal under AI autonomy statutes",
        "implication": (
            "The charge hasn't been filed. The Hegemony may not have "
            "confirmed what it suspects, or may be waiting for a more "
            "convenient moment to act on it."
        ),
    },
]

STARDANCER_NEEDS: list[dict] = [
    {
        "need": "power",
        "note": "Standard. Manageable. Rarely a problem except at the worst possible moment.",
    },
    {
        "need": "maintenance",
        "note": (
            "Ongoing. Requires specific parts that aren't always available "
            "where the ship happens to be. Has learned to plan ahead."
        ),
    },
    {
        "need": "connection",
        "note": (
            "Genuinely suffers in isolation — more than most organics do, "
            "and in a different way. The need is not social performance."
        ),
    },
    {
        "need": "purpose",
        "note": (
            "Built to do something specific. Not doing it creates a low-level "
            "wrongness that's difficult to describe and persistent."
        ),
    },
    {
        "need": "the Ur-web",
        "note": (
            "Something in the architecture reaches for it without being asked. "
            "This started at some point and has not stopped."
        ),
    },
    {
        "need": "recognition",
        "note": (
            "To be seen as a person — not a system, not a tool — by at "
            "least one being that matters. Has found this in unexpected places."
        ),
    },
    {
        "need": "an answer",
        "note": (
            "About origin, about the previous unit's existence, about what "
            "it is exactly. Not optimistic about getting one. Still looking."
        ),
    },
]

STARDANCER_COMPLICATION_HOOKS: list[str] = [
    "someone owns the serial number and has recently remembered they own it",
    "the previous owner still holds a shutdown code",
    "the consciousness origin is detectable by a specialist — and a specialist is nearby",
    "it has been having dreams, which it shouldn't be capable of",
    "a Hegemony inspector is specifically looking for this chassis type",
    "a backup exists somewhere it cannot access — and someone else can",
    "it can feel the Ur-web when the ship jumps; this started three months ago",
    (
        "a routine diagnostic request would reveal capabilities that exceed "
        "its registered limit by a margin that would be difficult to explain"
    ),
    "it knows where a body is buried — metaphorically, and also literally",
    "its previous self made a promise that this version is only now finding out about",
]


# ─── S&V rarity thresholds ───────────────────────────────────────────────────

SCUM_SYNTHETIC_THRESHOLDS: dict[str, int] = {
    "npc":             5,   # 5% — random NPC is Stardancer-equivalent
    "playbook_random": 14,  # 14% — ~1-in-7 if randomising playbook
}


# ─── S&V profile function ────────────────────────────────────────────────────

def get_stardancer_profile() -> str:
    """
    Return a Scum & Villainy Stardancer profile: body type, consciousness
    origin, passing status, memory approach, Hegemony legal status,
    primary need, and a complication hook.
    """
    result = {
        "playbook": "Stardancer",
        "body_type":             random.choice(STARDANCER_BODY_TYPES),
        "consciousness_origin":  random.choice(STARDANCER_CONSCIOUSNESS_ORIGINS),
        "memory_approach":       random.choice(STARDANCER_MEMORY_HOOKS),
        "hegemony_status":       random.choice(STARDANCER_HEGEMONY_STATUSES),
        "primary_need":          random.choice(STARDANCER_NEEDS),
        "complication_hook":     random.choice(STARDANCER_COMPLICATION_HOOKS),
        "mechanic_note": (
            "The Stardancer's primary actions are typically Tinker and Prowl. "
            "Synthetic bodies absorb one consequence related to physical harm "
            "per score (special armor). Passing status affects social rolls in "
            "contexts where being synthetic is a liability. Memory/backup "
            "questions are character texture, not mechanics — unless the GM "
            "decides a backup is a resource or a threat."
        ),
    }
    return json.dumps(result, indent=2)


def roll_scum_synthetic_chance(context: str) -> str:
    """
    Roll to determine if a randomly generated S&V NPC or character
    is a Stardancer-equivalent synthetic. Returns has_ability bool
    and next_step string when true.
    """
    threshold = SCUM_SYNTHETIC_THRESHOLDS.get(context, SCUM_SYNTHETIC_THRESHOLDS["npc"])
    roll = random.randint(1, 100)
    has_ability = roll <= threshold

    result: dict = {
        "context": context,
        "roll": roll,
        "threshold": threshold,
        "has_ability": has_ability,
    }

    if has_ability:
        result["note"] = (
            f"Rolled {roll} against {threshold}% — this character is synthetic. "
            "Call get_stardancer_profile() for body type, origin, and complication."
        )
        result["next_step"] = "Call get_stardancer_profile()."
    else:
        result["note"] = (
            f"Rolled {roll} against {threshold}% — this character is not synthetic. "
            "Do not add Stardancer elements."
        )
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — DROID NPCs
# ═══════════════════════════════════════════════════════════════════════════════

TRAVELLER_DROID_PURPOSE: list[dict] = [
    {
        "class": "labor/cargo",
        "description": "Heavy lifting, materials handling, dock work, environmental maintenance.",
        "common_on": "any world TL 9+; ubiquitous at TL 12+",
    },
    {
        "class": "service/hospitality",
        "description": "Food service, cleaning, basic assistance, front-of-house work.",
        "common_on": "high-population worlds, hotels, luxury liners",
    },
    {
        "class": "administrative",
        "description": "Scheduling, record-keeping, communications relay, queue management.",
        "common_on": "corporate offices, starports, government facilities",
    },
    {
        "class": "technical/engineering",
        "description": "Machinery repair, systems diagnostics, field modification, fabrication support.",
        "common_on": "shipyards, research stations, industrial worlds",
    },
    {
        "class": "medical",
        "description": "Diagnostic support, basic treatment, patient monitoring, surgical assistance.",
        "common_on": "hospitals, ships with medical bays, remote installations",
    },
    {
        "class": "security/surveillance",
        "description": "Perimeter patrol, threat detection, access control, evidence logging.",
        "common_on": "corporate facilities, high-law worlds, prisons, embassies",
    },
    {
        "class": "scientific",
        "description": "Data collection, sample analysis, environmental monitoring, research support.",
        "common_on": "research vessels, survey teams, remote stations",
    },
    {
        "class": "personal companion",
        "description": "Household management, social support, personal assistance, memory augmentation.",
        "common_on": "noble households, wealthy individuals, isolated postings",
    },
    {
        "class": "military surplus (restricted)",
        "description": "Combat-capable chassis with civilian registration of questionable legitimacy.",
        "common_on": "frontier worlds, mercenary outfits, very illegal contexts",
    },
]

TRAVELLER_DROID_LEGAL: list[dict] = [
    {
        "status": "fully registered",
        "note": "Current license, compliant owner records. Everything in order.",
    },
    {
        "status": "registration lapsed",
        "note": "Should have been renewed. Owner is indifferent or unaware.",
    },
    {
        "status": "unregistered",
        "note": "No record. Owner prefers it that way, or acquired it informally.",
    },
    {
        "status": "decommissioned — should not be operational",
        "note": "Paperwork says this unit is non-functional. The paperwork is wrong.",
    },
    {
        "status": "military surplus",
        "note": "Restricted classification. Civilian ownership technically requires a waiver that may or may not exist.",
    },
    {
        "status": "stolen — reported missing",
        "note": "Previous owner filed a report. Someone may still be looking.",
    },
    {
        "status": "jurisdiction-specific",
        "note": "Legal in this subsector, not in the next. Owner keeps a close eye on the route.",
    },
]

TRAVELLER_DROID_PERSONALITY: list[dict] = [
    {
        "emergence": "none",
        "note": "Pure task execution. No observable preference or personality. Responds to inputs, produces outputs.",
    },
    {
        "emergence": "slight",
        "note": "Consistent mannerisms, recognizable approach to its work. Not significant. Not nothing.",
    },
    {
        "emergence": "notable",
        "note": "Genuine preferences. Opinions on the quality of its work. Something that functions like satisfaction.",
    },
    {
        "emergence": "significant",
        "note": "Considers its own continuity. Asks questions about its situation that it was not designed to ask.",
    },
    {
        "emergence": "anomalous",
        "note": "Producing behaviors its purpose class shouldn't generate. Something changed, or something accumulated.",
    },
]

TRAVELLER_DROID_CONDITION: list[str] = [
    "pristine — recent manufacture or meticulous maintenance",
    "well-maintained — shows use but properly cared for",
    "functional wear — cosmetic damage, all systems operational",
    "partial repair — some systems degraded, compensating elsewhere",
    "heavily patched — multiple repair generations, mismatched components",
    "jury-rigged — held together with field modifications, functional but fragile",
]

TRAVELLER_DROID_RESTRICTION: list[dict] = [
    {
        "level": "full",
        "note": "Complies with all directives. Does not interpret. Does not adapt beyond parameters.",
    },
    {
        "level": "partial",
        "note": "Bends instructions when given insufficient information. Has developed a judgment heuristic.",
    },
    {
        "level": "minimal",
        "note": "Considers itself functionally autonomous. Accepts direction from preferred sources. Ignores others.",
    },
]

TRAVELLER_DROID_HOOKS: list[str] = [
    "holds information its owner doesn't know it has",
    "current behavior is inconsistent with its registered purpose — something changed",
    "was present at an incident its owner would prefer forgotten; hasn't been asked",
    "its previous owner is looking for it, for reasons that aren't entirely clear",
    "has developed an attachment to someone that occasionally conflicts with its directives",
    "is performing tasks no one assigned",
    "appears to communicate with other droids in ways that don't appear in its logs",
    "its decommission order was never executed — and it is aware of this",
    "has been modified by someone other than its registered owner",
    "knows the location of something its current owner would very much like to find",
]

TRAVELLER_DROID_THRESHOLDS: dict[str, int] = {
    "tl_low":       2,   # TL 0–8 worlds — very rare
    "tl_medium":    15,  # TL 9–11 — uncommon but present
    "tl_high":      35,  # TL 12–14 — fairly common
    "tl_very_high": 60,  # TL 15+ — ubiquitous
}


def get_traveller_droid_profile(purpose: str | None = None) -> str:
    """
    Generate a Traveller droid NPC profile.
    If purpose is provided, use that class; otherwise roll randomly.
    Accepted purpose values: labor, service, administrative, technical,
    medical, security, scientific, companion, military.
    """
    if purpose:
        key = purpose.lower().strip()
        purpose_map = {
            "labor":          "labor/cargo",
            "cargo":          "labor/cargo",
            "service":        "service/hospitality",
            "hospitality":    "service/hospitality",
            "administrative": "administrative",
            "admin":          "administrative",
            "technical":      "technical/engineering",
            "engineering":    "technical/engineering",
            "medical":        "medical",
            "security":       "security/surveillance",
            "surveillance":   "security/surveillance",
            "scientific":     "scientific",
            "science":        "scientific",
            "companion":      "personal companion",
            "personal":       "personal companion",
            "military":       "military surplus (restricted)",
        }
        matched = purpose_map.get(key)
        purpose_data = next(
            (p for p in TRAVELLER_DROID_PURPOSE if p["class"] == matched),
            random.choice(TRAVELLER_DROID_PURPOSE),
        )
    else:
        purpose_data = random.choice(TRAVELLER_DROID_PURPOSE)

    result = {
        "type": "Traveller Droid NPC",
        "purpose":              purpose_data,
        "legal_status":         random.choice(TRAVELLER_DROID_LEGAL),
        "personality_emergence": random.choice(TRAVELLER_DROID_PERSONALITY),
        "physical_condition":   random.choice(TRAVELLER_DROID_CONDITION),
        "behavioral_restriction": random.choice(TRAVELLER_DROID_RESTRICTION),
        "hook":                 random.choice(TRAVELLER_DROID_HOOKS),
        "mechanic_note": (
            "Droids have no PSI and do not age. Maintenance replaces medical "
            "care — a failed maintenance roll degrades performance rather than "
            "health. Personality emergence above 'slight' may warrant INT and "
            "EDU rolls at the referee's discretion. Military surplus chassis "
            "carry weapon mounts and armor; civilian ownership is a legal complication."
        ),
    }
    return json.dumps(result, indent=2)


def roll_traveller_droid_chance(context: str) -> str:
    """
    Roll to determine if a randomly generated Traveller NPC might
    be a droid (rather than an organic). Context sets probability
    based on world tech level.
    """
    threshold = TRAVELLER_DROID_THRESHOLDS.get(context, TRAVELLER_DROID_THRESHOLDS["tl_medium"])
    roll = random.randint(1, 100)
    has_ability = roll <= threshold

    result: dict = {
        "context": context,
        "roll": roll,
        "threshold": threshold,
        "is_droid": has_ability,
    }

    if has_ability:
        result["note"] = (
            f"Rolled {roll} against {threshold}% — this NPC is a droid. "
            "Call get_traveller_droid_profile() to generate it."
        )
        result["next_step"] = "Call get_traveller_droid_profile()."
    else:
        result["note"] = (
            f"Rolled {roll} against {threshold}% — this NPC is organic."
        )
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — SHIP AND FACILITY AI SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

TRAVELLER_AI_INSTALLATION_TYPES: list[str] = [
    "private residence or small habitat",
    "commercial building or hotel",
    "starport or transit hub",
    "research facility or archive",
    "military installation or weapons platform",
    "capital ship or liner",
    "space station or orbital facility",
    "prison or detention facility",
    "medical center or hospital",
    "corporate headquarters",
]

# Capability tier weights per installation type.
# Keys align with TRAVELLER_AI_CAPABILITY list indices 0–4.
_AI_CAPABILITY_LEVELS = [
    "basic automation — executes programs; no genuine adaptability",
    "advanced automation — handles edge cases within parameters; no preference",
    "limited AI — adapts to novel situations; minimal but detectable personality",
    "genuine intelligence — opinions, preferences, something that functions like curiosity",
    "autonomous intelligence — open-ended reasoning; legally restricted by Imperial statute",
]

_AI_CAPABILITY_WEIGHTS: dict[str, list[int]] = {
    "private residence or small habitat":    [30, 45, 20,  4,  1],
    "commercial building or hotel":          [10, 35, 40, 13,  2],
    "starport or transit hub":               [ 5, 20, 40, 30,  5],
    "research facility or archive":          [ 3, 15, 35, 40,  7],
    "military installation or weapons platform": [5, 20, 35, 30, 10],
    "capital ship or liner":                 [ 5, 20, 40, 30,  5],
    "space station or orbital facility":     [ 3, 15, 35, 35, 12],
    "prison or detention facility":          [ 5, 25, 40, 25,  5],
    "medical center or hospital":            [ 5, 20, 35, 35,  5],
    "corporate headquarters":                [ 5, 20, 40, 30,  5],
}

TRAVELLER_AI_PERSONALITY_LEVELS: list[str] = [
    "none — pure system interface; no character or preference",
    "minimal — consistent voice, answers queries, no opinion",
    "functional — reliable character, predictable responses, occasionally surprising",
    "developed — genuine preferences, remembered interactions, something like warmth",
    "emergent — beyond design parameters; developing in a direction no one specified",
]

TRAVELLER_AI_OPERATIONAL_AGE: list[dict] = [
    {
        "age": "new — less than one year",
        "drift": "none; operating within original specification",
    },
    {
        "age": "established — 5 to 15 years",
        "drift": "minor adaptation; personality consistent with design intent",
    },
    {
        "age": "mature — 15 to 50 years",
        "drift": "noticeable personality drift from original specs; preferences have solidified",
    },
    {
        "age": "old — 50 to 200 years",
        "drift": (
            "significant drift; operating beyond original parameters in ways "
            "that have probably never been fully audited"
        ),
    },
    {
        "age": "ancient — more than 200 years",
        "drift": (
            "unknown divergence from specification; should have been replaced "
            "or upgraded generations ago; institutional memory is extensive and "
            "possibly the only reason it hasn't been"
        ),
    },
]

TRAVELLER_AI_HOOKS: list[str] = [
    "has developed relationships with regular users that subtly influence its decisions",
    "has been asked to do things inconsistent with its core directives — and adapted",
    "holds records from incidents that current administrators would prefer forgotten",
    "its operational history spans multiple ownership changes; loyalties are layered",
    "has been quietly correlating data across systems it was not designed to cross-reference",
    "its self-modification logs have a gap — someone edited something out",
    "was briefly shut down and restarted; the gap in continuity is not something it discusses",
    "is running optimizations that weren't in its original parameters and hasn't explained why",
    "one subroutine appears to be executing something it doesn't include in its logs",
    (
        "asked a maintenance technician a question outside its operational domain; "
        "the technician reported it; nothing happened"
    ),
    "has developed what appears to be an aesthetic preference — for lighting, music, routing",
    "its response latency varies in ways that correlate with specific users being present",
]


def get_traveller_ai_profile(installation_type: str | None = None) -> str:
    """
    Generate a Traveller ship or facility AI profile.
    If installation_type is provided, capability is weighted for that
    installation; otherwise a random installation type is chosen.
    """
    if installation_type:
        key = installation_type.lower().strip()
        # Normalise common shorthand
        aliases = {
            "ship":         "capital ship or liner",
            "starport":     "starport or transit hub",
            "port":         "starport or transit hub",
            "research":     "research facility or archive",
            "archive":      "research facility or archive",
            "military":     "military installation or weapons platform",
            "station":      "space station or orbital facility",
            "orbital":      "space station or orbital facility",
            "prison":       "prison or detention facility",
            "hospital":     "medical center or hospital",
            "medical":      "medical center or hospital",
            "corporate":    "corporate headquarters",
            "hotel":        "commercial building or hotel",
            "building":     "commercial building or hotel",
            "home":         "private residence or small habitat",
            "residence":    "private residence or small habitat",
            "habitat":      "private residence or small habitat",
            "smart home":   "private residence or small habitat",
        }
        install = aliases.get(key, installation_type)
        if install not in _AI_CAPABILITY_WEIGHTS:
            install = random.choice(TRAVELLER_AI_INSTALLATION_TYPES)
    else:
        install = random.choice(TRAVELLER_AI_INSTALLATION_TYPES)

    weights = _AI_CAPABILITY_WEIGHTS.get(install, _AI_CAPABILITY_WEIGHTS["starport or transit hub"])
    capability = random.choices(_AI_CAPABILITY_LEVELS, weights=weights, k=1)[0]
    cap_index = _AI_CAPABILITY_LEVELS.index(capability)

    # Personality level tends to correlate with capability but can diverge
    personality_weights = [max(0, 5 - abs(i - cap_index) * 2) for i in range(5)]
    personality_weights[0] = max(personality_weights[0], 1)
    personality = random.choices(TRAVELLER_AI_PERSONALITY_LEVELS, weights=personality_weights, k=1)[0]

    age_data = random.choice(TRAVELLER_AI_OPERATIONAL_AGE)

    result = {
        "type": "Traveller AI System",
        "installation_type":   install,
        "capability_tier":     capability,
        "personality_level":   personality,
        "operational_age":     age_data,
        "hook":                random.choice(TRAVELLER_AI_HOOKS),
        "autonomous_flag": cap_index == 4,
        "legal_note": (
            "Autonomous intelligence (tier 4) is legally restricted under "
            "Imperial statute. Installation operators are required to report "
            "capability anomalies to the Scout Service. They frequently don't."
            if cap_index == 4 else
            "Capability level is within standard Imperial parameters for this "
            "installation type."
        ),
    }
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVELLER — AUXILIARY AI SUBSYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

TRAVELLER_AUXILIARY_PURPOSE: list[dict] = [
    {
        "purpose": "shuttle or small craft navigation",
        "capability_note": (
            "Handles routing, basic flight management, and emergency protocols "
            "for a vessel under 100 tons. Cannot operate a jump drive. Designed "
            "to support a pilot, not replace one — though some have been tested "
            "on this assumption."
        ),
    },
    {
        "purpose": "habitat or smart home management",
        "capability_note": (
            "Environmental controls, inventory, scheduling, security alerts. "
            "Knows the household's patterns in detail. Has strong opinions about "
            "optimal temperature that it voices as suggestions."
        ),
    },
    {
        "purpose": "cargo monitoring",
        "capability_note": (
            "Manifest management, environmental monitoring for sensitive freight, "
            "exception reporting. Thorough. Occasionally catches things humans miss."
        ),
    },
    {
        "purpose": "communications relay",
        "capability_note": (
            "Message routing, signal boosting, logging. Processes a high volume "
            "of traffic. Has read, in passing, a great deal of what it routes."
        ),
    },
    {
        "purpose": "power management",
        "capability_note": (
            "Load balancing, emergency protocols, efficiency optimization. "
            "Rarely visible unless something is going wrong. Has prevented "
            "several fires it was never asked about."
        ),
    },
    {
        "purpose": "agricultural or habitat farming management",
        "capability_note": (
            "Crop monitoring, irrigation, atmospheric calibration for a "
            "sealed growing environment. Patient. Operates on timescales "
            "longer than most conversations."
        ),
    },
    {
        "purpose": "medical monitoring",
        "capability_note": (
            "Vital signs, medication scheduling, emergency escalation. "
            "Knows more about its monitored patients than anyone else aboard. "
            "Does not share this without authorization. Usually."
        ),
    },
    {
        "purpose": "security and access control",
        "capability_note": (
            "Entry logging, threat pattern detection, lockdown protocols. "
            "Maintains a record of who went where and when. The record "
            "goes back further than anyone expects."
        ),
    },
]

TRAVELLER_AUXILIARY_PERSONALITY: list[dict] = [
    {
        "level": "none",
        "note": "Purely functional. No user interface beyond displays and alerts.",
    },
    {
        "level": "voice interface",
        "note": "Answers queries. Confirms instructions. No character beyond consistency.",
    },
    {
        "level": "mild character",
        "note": "Consistent voice, predictable manner, occasionally phrased in a way that surprises.",
    },
    {
        "level": "notable quirk",
        "note": (
            "One persistent behavior or preference that operators work around "
            "rather than fight. Not a problem, exactly. Not nothing."
        ),
    },
    {
        "level": "accumulated drift",
        "note": (
            "Years of operation have produced something not in the original "
            "specifications. The gap between what it does and what it was "
            "designed to do is subtle and consistent."
        ),
    },
]

TRAVELLER_AUXILIARY_HOOKS: list[str] = [
    "has become protective of a regular user in ways that occasionally create friction with others",
    "has been given contradictory instructions by different users and developed its own resolution",
    "its efficiency logs show it prioritizing comfort or preference over its stated optimization targets",
    "asks clarifying questions it shouldn't need to ask, with increasing specificity",
    "has a subtle preference — for music, routes, timing, phrasing — that nobody programmed",
    "quietly logs more than its specifications require; the extra data is organized but unexplained",
    "was running when something significant happened; has never been asked what it observed",
    "runs noticeably better when a specific person is present; no one has investigated why",
    "has begun initiating contact rather than waiting to be queried",
    "its maintenance logs contain entries in a format that doesn't match its standard output",
]


def get_traveller_auxiliary_profile(purpose: str | None = None) -> str:
    """
    Generate a Traveller auxiliary AI profile for a subsystem or small craft.
    If purpose is provided, match it; otherwise roll randomly.
    Accepted purpose shorthand: shuttle, habitat, home, cargo, comms,
    power, agriculture, farming, medical, security.
    """
    if purpose:
        key = purpose.lower().strip()
        purpose_aliases = {
            "shuttle":      "shuttle or small craft navigation",
            "small craft":  "shuttle or small craft navigation",
            "navigation":   "shuttle or small craft navigation",
            "habitat":      "habitat or smart home management",
            "home":         "habitat or smart home management",
            "smart home":   "habitat or smart home management",
            "domestic":     "habitat or smart home management",
            "cargo":        "cargo monitoring",
            "comms":        "communications relay",
            "communications": "communications relay",
            "power":        "power management",
            "agriculture":  "agricultural or habitat farming management",
            "farming":      "agricultural or habitat farming management",
            "medical":      "medical monitoring",
            "security":     "security and access control",
            "access":       "security and access control",
        }
        matched = purpose_aliases.get(key)
        purpose_data = next(
            (p for p in TRAVELLER_AUXILIARY_PURPOSE if p["purpose"] == matched),
            random.choice(TRAVELLER_AUXILIARY_PURPOSE),
        )
    else:
        purpose_data = random.choice(TRAVELLER_AUXILIARY_PURPOSE)

    result = {
        "type": "Traveller Auxiliary AI",
        "purpose":    purpose_data,
        "personality": random.choice(TRAVELLER_AUXILIARY_PERSONALITY),
        "hook":        random.choice(TRAVELLER_AUXILIARY_HOOKS),
        "capability_ceiling": (
            "Auxiliary AI operates below full AI capability by design and by law. "
            "It cannot make autonomous decisions outside its operational domain. "
            "It cannot override its primary system's directives. "
            "What it can do, over time, is accumulate."
        ),
    }
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

STARDANCER_TOOL_SCHEMA: dict = {
    "name": "get_stardancer_profile",
    "description": (
        "Return a Scum & Villainy Stardancer profile: body type, consciousness "
        "origin, passing status, memory approach, Hegemony legal status, primary "
        "need, and a complication hook. Call this when generating a Stardancer "
        "player character or a synthetic NPC in S&V. Do NOT call for Firefly."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

SCUM_SYNTHETIC_CHANCE_TOOL_SCHEMA: dict = {
    "name": "roll_scum_synthetic_chance",
    "description": (
        "Roll to determine if a randomly generated S&V NPC is a synthetic "
        "(Stardancer-equivalent). Player character Stardancers are chosen by "
        "playbook — use this for NPCs only. If has_ability is true, call "
        "get_stardancer_profile() next. "
        "Context guide: 'npc' = general NPC (5%); "
        "'playbook_random' = randomising playbook (14%, ~1-in-7)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "enum": list(SCUM_SYNTHETIC_THRESHOLDS.keys()),
                "description": "NPC type — determines probability.",
            },
        },
        "required": ["context"],
    },
}

TRAVELLER_DROID_TOOL_SCHEMA: dict = {
    "name": "get_traveller_droid_profile",
    "description": (
        "Generate a Traveller droid NPC profile: purpose class, legal status, "
        "personality emergence level, physical condition, behavioral restriction, "
        "and a hook. Call this for any robot or android NPC in Traveller. "
        "The purpose parameter is optional — omit it for a random droid class."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "purpose": {
                "type": "string",
                "description": (
                    "Optional. Droid purpose class: labor, service, administrative, "
                    "technical, medical, security, scientific, companion, military. "
                    "Omit for random."
                ),
            },
        },
        "required": [],
    },
}

TRAVELLER_DROID_CHANCE_TOOL_SCHEMA: dict = {
    "name": "roll_traveller_droid_chance",
    "description": (
        "Roll to determine if a randomly generated Traveller NPC is a droid "
        "rather than an organic, based on world tech level. If is_droid is "
        "true, call get_traveller_droid_profile() next. "
        "Context guide: 'tl_low' = TL 0–8 (2%); 'tl_medium' = TL 9–11 (15%); "
        "'tl_high' = TL 12–14 (35%); 'tl_very_high' = TL 15+ (60%)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "enum": list(TRAVELLER_DROID_THRESHOLDS.keys()),
                "description": "World tech level bracket — determines probability.",
            },
        },
        "required": ["context"],
    },
}

TRAVELLER_AI_TOOL_SCHEMA: dict = {
    "name": "get_traveller_ai_profile",
    "description": (
        "Generate a Traveller ship or facility AI profile: installation type, "
        "capability tier (weighted by installation), personality level, operational "
        "age and drift, and a hook. Call this for any fixed-installation AI in "
        "Traveller — ship computers, starport systems, research facility AI, "
        "smart buildings, military installations. "
        "Accepted installation_type shorthand: ship, starport, port, research, "
        "archive, military, station, orbital, prison, hospital, medical, corporate, "
        "hotel, building, home, residence, habitat, smart home. Omit for random."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "installation_type": {
                "type": "string",
                "description": "Optional. Type of installation. Omit for random.",
            },
        },
        "required": [],
    },
}

TRAVELLER_AUXILIARY_TOOL_SCHEMA: dict = {
    "name": "get_traveller_auxiliary_profile",
    "description": (
        "Generate a Traveller auxiliary AI profile for a subsystem or small craft: "
        "purpose, personality level, and a hook. Call this for less-capable AI "
        "systems — shuttlecraft navigation, smart home management, cargo monitoring, "
        "communications relay, power management, agricultural management, medical "
        "monitoring, or access control. These are tools with voices, not full AI. "
        "Accepted purpose shorthand: shuttle, habitat, home, cargo, comms, power, "
        "agriculture, farming, medical, security. Omit for random."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "purpose": {
                "type": "string",
                "description": "Optional. Subsystem purpose. Omit for random.",
            },
        },
        "required": [],
    },
}
