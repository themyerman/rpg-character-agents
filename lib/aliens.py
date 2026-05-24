"""
lib/aliens.py
Alien races and first contact generation for Traveller (and notes for S&V / Firefly).

Story-first, not rules-complete. Three layers:

  Major races   — the six non-human major races of the Third Imperium:
                  Aslan, Vargr, Droyne, K'kree, Hivers, Zhodani.
                  Full cultural profile, characteristic mods, campaign hooks.

  Minor races   — a curated set of the Imperium's documented minor races:
                  Bwaps, Darrians, Llellewyoly, Virushi, Hhkar, Jonkeereen,
                  Uplifted Dolphins. Lighter treatment — enough to play and
                  write them convincingly.

  First contact — procedural generator for unknown species. Produces a species
                  profile (body plan, diet, social structure, communication,
                  tech level) and then seeds a contact situation from those
                  facts. Diet drives initial posture. Communication method
                  determines the contact barrier. Tech level defines the
                  power dynamic. The two outputs are returned together so the
                  agent can write a coherent encounter from one tool call.

Firefly note: the 'Verse has no alien life. Do not use this file for Firefly
characters or encounters. If a Firefly scenario involves "alien contact" it is
a scam, a misidentified phenomenon, or an Alliance cover story.

S&V note: the Ur are handled in psi.py (Ur-web, artifacts, Mystic flavor).
This file is not needed for standard S&V character generation. It may be
useful for generating unknown xeno species in frontier-exploration S&V arcs.
"""

import json
import random


# ═══════════════════════════════════════════════════════════════════════════════
# MAJOR RACES — Mongoose Traveller 2e
# ═══════════════════════════════════════════════════════════════════════════════

MAJOR_RACES: dict = {
    "aslan": {
        "name": "Aslan",
        "homeworld": "Kusyu (Trojan Reach 1919)",
        "characteristic_mods": {"STR": +2, "DEX": -2},
        "natural_weapons": [
            {
                "name": "Dewclaw",
                "damage": "1d6",
                "note": (
                    "Retractable. Used in ritualized challenge combat and "
                    "genuine violence alike — Aslan rarely threaten with them "
                    "without meaning it."
                ),
            }
        ],
        "soc_note": (
            "SOC reflects clan standing rather than Imperial bloodline. "
            "A high-SOC Aslan is powerful within Aslan society; that status "
            "does not automatically transfer to Imperial contexts."
        ),
        "social_structure": (
            "Clan-based feudal hierarchy. Males fight, hunt, and defend "
            "territory; females handle trade, business, and technical roles. "
            "These roles are rigid in traditional clans and more flexible "
            "among spacefaring Aslan. Playing against gender role is a "
            "character arc, not a casual trait."
        ),
        "key_drives": [
            "territorial acquisition — land is the ultimate measure of worth, "
            "especially for male Ihatei (landless second sons)",
            "honor maintenance — a slight must be addressed or explained; "
            "backing down without justification is social death",
            "clan obligation — individual decisions are rarely only individual",
            "truth-telling — lying violates honor codes; Aslan negotiators "
            "are known for bluntness that startles humans",
        ],
        "campaign_presence": (
            "Very common throughout the Imperium and beyond. Ihatei second "
            "sons expand in every direction — space is just territory with "
            "no gravity. Natural fit for scouts, mercenaries, warriors, and "
            "any character with something to prove."
        ),
        "psi_note": (
            "Psionics exist but are viewed with deep suspicion — associated "
            "with deception, which violates honor codes. Psionic Aslan are "
            "rare and usually concealed."
        ),
        "npc_hooks": [
            "An Ihatei warlord who has claimed a disputed moon and needs "
            "crew to hold it — land acquired, but not yet kept",
            "A female trade-master who needs off-world operatives; she "
            "negotiates and they act, and she is very good at her job",
            "A dishonored male seeking a final act that will restore his "
            "clan's name, possibly posthumously — he has made peace with "
            "the 'possibly'",
        ],
    },

    "vargr": {
        "name": "Vargr",
        "homeworld": "Lair (Gvurrdon 1140)",
        "characteristic_mods": {"STR": -1, "DEX": +1, "END": -1},
        "soc_replacement": (
            "SOC is replaced by CHA (Charisma) — measures personal magnetism "
            "and current pack standing, not bloodline. A Vargr with CHA 12 "
            "commands a room; one with CHA 4 is being tolerated."
        ),
        "natural_weapons": [
            {
                "name": "Bite",
                "damage": "1d6",
                "note": (
                    "Natural attack. Used as threat display before actual "
                    "violence — visible baring is usually sufficient."
                ),
            }
        ],
        "social_structure": (
            "Charismatic pack hierarchy — leadership is earned and lost "
            "through personal magnetism, not heredity. Loyalty shifts when "
            "strength shifts. Not treachery; this is how they're wired."
        ),
        "key_drives": [
            "following strength — a Vargr follows who deserves following, "
            "and reassesses constantly",
            "pack cohesion — alone is wrong; belonging matters",
            "proving worth through action — reputation is currency",
            "freedom from static hierarchy — Vargr distrust systems that "
            "promote by seniority regardless of merit",
        ],
        "campaign_presence": (
            "Extremely common as corsairs, crew members, traders, and "
            "mercenaries. Found throughout Gvurrdon sector and deep in "
            "Imperial space. Natural fit for almost any role — especially "
            "where social reading and adaptability matter."
        ),
        "psi_note": (
            "No special psionic tradition. Use imperial context (3%) for "
            "standard psi chance rolls."
        ),
        "npc_hooks": [
            "A corsair captain whose crew is starting to question her "
            "leadership — she needs a win fast, and she knows it",
            "A pack-mate who followed a weak leader into a disaster and is "
            "looking for someone worth following again",
            "A lone Vargr far from any pack — unusual enough to require "
            "explanation, and the explanation is probably bad",
        ],
    },

    "droyne": {
        "name": "Droyne",
        "homeworld": (
            "Multiple scattered worlds — no single homeworld. Ancient "
            "dispersal, possibly by the Ancients themselves."
        ),
        "characteristic_mods": "Varies by caste — see caste_mods.",
        "caste_mods": {
            "Worker":     {"STR": 0,  "DEX": +1, "END": +1, "INT": -2, "EDU": -1, "SOC": -2},
            "Warrior":    {"STR": +2, "DEX": +2, "END": +2, "INT": -2, "EDU": -1, "SOC": -2},
            "Drone":      {"STR": -2, "DEX": 0,  "END": 0,  "INT": +1, "EDU": +1, "SOC": +1},
            "Technician": {"STR": -1, "DEX": +2, "END": 0,  "INT": +2, "EDU": +2, "SOC": -1},
            "Sport":      {"STR": 0,  "DEX": 0,  "END": 0,  "INT": +1, "EDU": +1, "SOC": +1},
            "Leader":     {"STR": 0,  "DEX": 0,  "END": 0,  "INT": +2, "EDU": +2, "SOC": +4},
        },
        "social_structure": (
            "Rigid caste system — caste is assigned by ritual at adolescence "
            "and determines life role absolutely within traditional Droyne "
            "communities. Six castes: Worker, Warrior, Drone, Technician, "
            "Sport, Leader."
        ),
        "key_drives": [
            "caste fulfillment — a Warrior doing Technician work is "
            "disturbing to other Droyne at a deep level",
            "community coherence — individual and community are nearly "
            "inseparable in traditional Droyne thought",
            "ancient mystery — Droyne may be related to the Ancients; "
            "they neither confirm nor deny this",
            "psionic tradition — psionics are woven into Droyne culture "
            "at every level",
        ],
        "campaign_presence": (
            "Rare outside Droyne worlds. A Droyne encountered in the wider "
            "Imperium is almost certainly a Sport — the caste designated for "
            "external contact. Treat as exceptional; require a reason."
        ),
        "psi_note": (
            "Psionics are central to Droyne culture and virtually universal. "
            "Use droyne context (100%) for psi chance rolls. Caste affects "
            "which talents manifest and how they are used."
        ),
        "npc_hooks": [
            "A Sport interpreter whose community needs something from the "
            "wider Imperium — they will not ask for it directly, and the "
            "Sport's job is to make the need legible without saying it",
            "A Warrior caste member separated from their community, "
            "following caste instinct with no legitimate target",
            "A Leader caste Droyne who has made deliberate contact — nearly "
            "without precedent, which means something significant is at stake",
        ],
    },

    "k_kree": {
        "name": "K'kree",
        "homeworld": "Kirur (Two Thousand Worlds, K'kree space)",
        "characteristic_mods": {"STR": +4, "DEX": -4, "END": +2},
        "social_structure": (
            "Family-centered herds. K'kree cannot psychologically tolerate "
            "solitude — isolation causes genuine mental breakdown. Even a "
            "small group (2-3) is insufficient; they need their family "
            "herd present."
        ),
        "dietary_note": (
            "Militant herbivores. The presence of meat causes physical "
            "revulsion and social offense. Meat-eating species are not "
            "merely different — they are morally threatening to K'kree "
            "worldview. This is not a preference; it is closer to ideology."
        ),
        "key_drives": [
            "herd cohesion — being with family is not comfort, it is "
            "psychological necessity",
            "elimination of meat-eating — the Two Thousand Worlds have "
            "prosecuted wars over this",
            "territorial expansion — K'kree space grows",
            "status within the herd — rank matters enormously in social "
            "interactions",
        ],
        "campaign_presence": (
            "Very rare outside K'kree space. A lone K'kree is a deeply "
            "disturbed or suicidal K'kree. Most K'kree contact occurs at "
            "the frontier of their space, in diplomatic or trade contexts "
            "involving entire family groups. Excellent as faction obstacle "
            "or diplomatic antagonist; very difficult to integrate into "
            "a standard party."
        ),
        "psi_note": (
            "Psionics exist but are uncommon and viewed with some fear. "
            "Use imperial context (3%) as a rough baseline."
        ),
        "npc_hooks": [
            "A K'kree trade delegation requiring entire adjacent sections "
            "of the starport for their family group — the port authority "
            "is having a difficult week",
            "A lone K'kree: something terrible happened to their family, "
            "and they are not coping in ways that are increasingly visible",
            "A K'kree ideological agent who views the party's dietary habits "
            "as a moral emergency requiring immediate correction",
        ],
    },

    "hivers": {
        "name": "Hivers",
        "homeworld": "Guaran (Hive Federation space)",
        "characteristic_mods": {"DEX": +4, "STR": -4},
        "social_structure": (
            "Loose, non-hierarchical, manipulative. No government in the "
            "traditional sense. Individual Hivers pursue long-term agendas "
            "through indirect influence — they engineer situations rather "
            "than issuing directives."
        ),
        "key_drives": [
            "manipulation as default mode — every interaction is potentially "
            "an influence operation; this is not malice, it is cognition",
            "security through indirection — Hivers never expose themselves "
            "to direct risk",
            "extreme patience — Hivers think in decades; a 'recent' "
            "Hiver initiative may have begun before the PCs were born",
            "curiosity — genuine, deep, and occasionally the only thing "
            "that breaks their indirect approach",
        ],
        "campaign_presence": (
            "Rare but significant when present. Hivers never fight directly — "
            "if one is in the room, they are there for a reason, and the "
            "reason is almost certainly not what it appears to be. Excellent "
            "as patrons, information brokers, and long-game conspirators."
        ),
        "psi_note": (
            "No significant psionic tradition. Use imperial context (3%) "
            "as a baseline."
        ),
        "npc_hooks": [
            "A Hiver patron whose stated goal is clearly not their actual "
            "goal — the question is whether the real goal is also in the "
            "party's interest",
            "A Hiver who needs the party to do something dangerous that "
            "the Hiver cannot be seen doing or arranging",
            "Evidence that someone the party has trusted for months has "
            "been a Hiver asset — not coerced, just gradually and "
            "expertly influenced",
        ],
    },

    "zhodani": {
        "name": "Zhodani",
        "homeworld": "Zhdant (Zhodani Consulate, Zhdant sector)",
        "characteristic_mods": {},
        "caste_note": (
            "Three castes: Nobles (psionic, rule), Intendants (psionic, "
            "administer), Proles (usually non-psionic, work). Social "
            "mobility via psionic testing — a Prole child who manifests "
            "ability can be elevated."
        ),
        "social_structure": (
            "Meritocracy anchored to psionic ability. Psionics are legal, "
            "celebrated, and institutionalized. Mental health is a genuine "
            "civic priority — the Consulate invests heavily in psychological "
            "wellbeing and it shows."
        ),
        "key_drives": [
            "Consulate loyalty — deeply felt, not merely political",
            "psionic excellence — the highest social value",
            "mental health and stability — genuinely valued, not "
            "performative",
            "distrust of Imperials who reject the mind as a tool of "
            "governance",
        ],
        "campaign_presence": (
            "Encountered primarily in the Spinward Marches, site of five "
            "Frontier Wars. Within the Consulate they are ordinary citizens. "
            "In Imperial space they are political lightning rods — enemies, "
            "spies, or refugees depending on context and who's watching."
        ),
        "psi_note": (
            "All Nobles and Intendants are psionic. Proles have elevated "
            "rates. Use zhodani_noble context (95%) for Nobles/Intendants, "
            "zhodani_prole context (15%) for Proles."
        ),
        "npc_hooks": [
            "A Zhodani Noble diplomat who knows what everyone in the room "
            "is feeling and is being scrupulously polite about it — the "
            "politeness itself is somewhat unnerving",
            "A Zhodani Prole defector who chose the Imperium and now trusts "
            "no one on either side completely",
            "A Zhodani Intelligence operative — the question is whether "
            "their mission aligns with the party's interests or cuts "
            "against them",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# MINOR RACES — curated selection for NPC and flavor use
# ═══════════════════════════════════════════════════════════════════════════════

MINOR_RACES: dict = {
    "bwaps": {
        "name": "Bwaps (Newts)",
        "homeworld": "Marhaban (Empty Quarter sector)",
        "characteristic_mods": {"DEX": +2, "END": -2},
        "description": (
            "Amphibious bipeds resembling upright newts — damp-skinned, "
            "precise in movement, and devoted to procedure. Bwaps are the "
            "Imperium's administrators: obsessive about record-keeping, "
            "protocol, and correct process. For Bwaps, following proper "
            "procedure is not merely efficient — it is morally right. "
            "Shortcuts are a kind of small violence."
        ),
        "behavioral_notes": [
            "Found throughout Imperial bureaucracy — port authorities, "
            "customs officials, tax offices, archives. If paperwork matters, "
            "a Bwap is probably involved.",
            "Socially awkward with species who improvise — improvisation "
            "reads to Bwaps as alarming rather than creative.",
            "Patient and thorough beyond human norms — a Bwap will find "
            "the irregularity eventually.",
        ],
        "typical_roles": (
            "Port authority, customs inspector, administrative clerk, "
            "archivist, logistics coordinator"
        ),
        "npc_hook": (
            "The Bwap port authority officer who has found an irregularity "
            "in the ship's documentation — not corrupt, not negotiable, "
            "but possibly persuadable that the correct process for resolving "
            "it is one that works for everyone."
        ),
    },

    "darrians": {
        "name": "Darrians",
        "homeworld": "Darrian (Darrian Confederation, Spinward Marches)",
        "characteristic_mods": {"INT": +2, "SOC": +1, "STR": -1},
        "description": (
            "Near-human in appearance. Their civilization predates Imperial "
            "contact by millennia and includes the Maghiz — the accidental "
            "stellar detonation caused by their own weapons research roughly "
            "1,000 years ago. They spent centuries rebuilding. They possess "
            "the Star Trigger, a weapon capable of inducing stellar ignition, "
            "and everyone is very polite to them about it."
        ),
        "behavioral_notes": [
            "Survivor culture — the Maghiz is living memory for Darrian "
            "civilization. They are careful in ways that read as paranoia "
            "until you know the history.",
            "Scientific humility earned through catastrophe — they know "
            "they are brilliant, and they know what that cost them.",
            "The Star Trigger question — nobody asks directly. Everyone "
            "wonders. Darrians change the subject.",
        ],
        "typical_roles": (
            "Scientists, researchers, explorers, diplomats, "
            "Confederation agents"
        ),
        "npc_hook": (
            "A Darrian researcher who has found something in an ancient "
            "site that changes their understanding of the Maghiz — and is "
            "deciding whether to tell anyone."
        ),
    },

    "llellewyoly": {
        "name": "Llellewyoly (Dandelions)",
        "homeworld": "Junidy (Aramis subsector, Spinward Marches)",
        "characteristic_mods": {"DEX": +4, "STR": -4, "INT": +1},
        "description": (
            "Five-limbed ambulatory plant-animal hybrids — mobile root "
            "structures, touch-sensing fronds, and a body plan that looks "
            "decorative until you see how fast they move. Communication "
            "is primarily tactile and chemical. Among the most genuinely "
            "alien of the Imperium's documented minor races."
        ),
        "behavioral_notes": [
            "Touch as primary communication channel — physical contact is "
            "normal and expected. Refusing contact reads as hostility; "
            "accepting it is an act of significant trust.",
            "Chemical sensing — a Llellewyoly in a room can tell you what "
            "everyone ate and broadly how they're feeling.",
            "Inscrutable to most species — emotional and cognitive states "
            "are very difficult to read from the outside. Patient "
            "interpreters are essential.",
        ],
        "typical_roles": "Rarely encountered off Junidy; travellers are usually diplomats or scholars",
        "npc_hook": (
            "A Llellewyoly delegate attempting contact with the party "
            "through repeated gentle touching of their hands — nobody "
            "quite knows what is being communicated, but the repetition "
            "suggests urgency."
        ),
    },

    "virushi": {
        "name": "Virushi",
        "homeworld": "Virusah (Magyar sector)",
        "characteristic_mods": {"STR": +6, "END": +4, "DEX": -2, "INT": -1},
        "description": (
            "Enormous hexapodal herbivores — the scale of a large bear, "
            "built like a tank, and philosophically pacifist. The contrast "
            "between their physical capability and their actual intentions "
            "is a recurring theme in every interaction. Warm, patient, "
            "remembered fondly by everyone who has met one."
        ),
        "behavioral_notes": [
            "Pacifism as deep conviction — Virushi will not initiate "
            "violence. They will endure significant harm to avoid causing it.",
            "Physical logistics — Virushi require appropriately scaled "
            "environments. Standard starship quarters do not apply.",
            "Slow to speak, warm in manner — conversations with Virushi "
            "take time and are usually worth it.",
        ],
        "typical_roles": "Mediators, pacifist advisors, philosophers, laborers (willing)",
        "npc_hook": (
            "A Virushi mediator asked to arbitrate a dispute between two "
            "factions — both assumed the mediator could be intimidated "
            "and are in the process of learning otherwise."
        ),
    },

    "hhkar": {
        "name": "Hhkar",
        "homeworld": "Shakhurem (Solomani Rim sector)",
        "characteristic_mods": {"STR": +2, "END": +2, "EDU": -1},
        "description": (
            "Bipedal reptilians — scaled, warm-blooded, with strong "
            "territorial instincts and a reputation for direct confrontation. "
            "Proud of their warrior history. Found primarily near the "
            "Solomani Rim, where they serve as mercenaries and soldiers "
            "throughout the sector."
        ),
        "behavioral_notes": [
            "Direct in negotiation — Hhkar consider hedging and indirection "
            "dishonest. They say what they mean.",
            "Territorial pride — strongly attached to space they consider "
            "theirs, physical or social.",
            "Respected fighters — a Hhkar mercenary's reputation is usually "
            "accurate in both directions.",
        ],
        "typical_roles": "Mercenaries, soldiers, planetary security, traders in Rim sectors",
        "npc_hook": (
            "A Hhkar mercenary captain evaluating whether this contract is "
            "worth the risk — doing so directly, out loud, in front of "
            "everyone, which some find refreshing and others find alarming."
        ),
    },

    "jonkeereen": {
        "name": "Jonkeereen",
        "homeworld": "Jonkeer (Deneb sector)",
        "characteristic_mods": {"END": +2, "STR": -1},
        "description": (
            "A minor human race adapted to extreme desert conditions — lean, "
            "dark-eyed, with efficient moisture retention physiology. "
            "Culturally conservative, exceptional in survival conditions "
            "that kill standard humans. Largely indistinguishable from "
            "baseline humans at a glance."
        ),
        "behavioral_notes": [
            "Desert pragmatism — no waste, no excess, every resource "
            "accounted for before committing to anything.",
            "Quiet endurance — Jonkeereen tend toward patience over "
            "action; they have outlasted problems others tried to fight.",
            "Water-conscious off-world — habits that read as frugality "
            "or formality are usually just old instinct.",
        ],
        "typical_roles": "Scouts, surveyors, wilderness guides, merchants on desert worlds",
        "npc_hook": (
            "A Jonkeereen guide who knows exactly where the party needs "
            "to go and will take them there — for a price that seems odd "
            "until you understand what the trip costs them personally."
        ),
    },

    "dolphins": {
        "name": "Dolphins (Uplifted)",
        "homeworld": "Terra / various — uplifted by the Imperium",
        "characteristic_mods": {"INT": +1, "STR": +2, "DEX": -3},
        "description": (
            "Uplifted from terran dolphins. Spacefaring in adapted "
            "environments — ships with wet sections, vacc suits built for "
            "cetacean anatomy. Highly intelligent, socially complex, and "
            "somewhat alarming to interact with until you calibrate to "
            "their communication style, which layers metaphor and sonic "
            "imagery in ways humans find beautiful and difficult to parse."
        ),
        "behavioral_notes": [
            "Non-linear communication — speak in layers, metaphor, and "
            "sonic imagery; parsing takes time and patience.",
            "Exceptional spatial intelligence — navigation, "
            "three-dimensional thinking, and systems modeling.",
            "Physical adaptation required — dolphin crew positions assume "
            "modified quarters and specialist work environments.",
        ],
        "typical_roles": "Navigation specialists, pilots, scouts, researchers",
        "npc_hook": (
            "A dolphin navigator who has detected something wrong in the "
            "route data and is explaining it in imagery that nobody else "
            "can follow yet — but the urgency is clear."
        ),
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# FIRST CONTACT — DATA POOLS
# ═══════════════════════════════════════════════════════════════════════════════

_FC_BODY_SYMMETRY: list[str] = [
    "bilateral (left-right mirror)",
    "radial — three-fold",
    "radial — six-fold",
    "trilateral (three primary axes)",
    "asymmetric (no consistent symmetry)",
    "modular/colonial (no fixed body plan — individuals are nodes)",
]

_FC_LOCOMOTION: list[str] = [
    "bipedal",
    "quadrupedal",
    "hexapodal",
    "serpentine (limbless, undulatory)",
    "aquatic (fully water-bound)",
    "semi-aquatic (amphibious)",
    "aerial (winged, primary locomotion is flight)",
    "arboreal (brachiating, tree-adapted)",
    "sessile-rooted (fixed in place, limited reach mobility)",
    "rolling/tumbling (spherical or near-spherical body plan)",
]

_FC_PRIMARY_SENSE: list[str] = [
    "visual — human-spectrum",
    "visual — infrared",
    "visual — ultraviolet",
    "echolocation (active sonar)",
    "chemosensory (smell/taste primary)",
    "electromagnetic sensing (detects fields and current)",
    "mechanosensory (vibration and pressure in substrate)",
    "thermosensory (heat detection primary)",
    "psionic perception (no conventional senses dominate)",
]

_FC_SIZE: list[str] = [
    "small (cat-sized — roughly 3–8kg)",
    "medium (human-sized — 40–120kg)",
    "large (horse-sized — 200–600kg)",
    "very large (elephant-sized — 1,000–5,000kg)",
    "massive (whale-sized — above 5,000kg)",
]

_FC_DIET: list[str] = [
    "apex carnivore",
    "pursuit predator",
    "ambush predator",
    "omnivore (opportunistic)",
    "omnivore (selective)",
    "grazer",
    "browser",
    "filter feeder",
    "chemosynthetic",
    "photosynthetic",
    "parasitic",
    "scavenger",
]

_FC_SOCIAL: list[str] = [
    "solitary (territory-defending)",
    "mated pairs (lifelong bond)",
    "small pack (3–8, kin-based)",
    "band (10–40, flexible membership)",
    "tribal (50–500, hierarchical)",
    "hive (eusocial, reproductive caste)",
    "colonial organism (individuals are nodes of a distributed whole)",
]

_FC_COMMUNICATION: list[str] = [
    "tonal/verbal",
    "subsonic rumble (below human hearing)",
    "infrasonic (far below human hearing)",
    "chemical/pheromonal",
    "gestural/postural",
    "bioluminescent patterning",
    "electromagnetic pulse (structured field modulation)",
    "tactile/haptic (contact-required)",
    "psionic (requires PSI to perceive)",
    "compound — verbal and chemical",
    "compound — visual and gestural",
]

_FC_COGNITIVE: list[str] = [
    "individual (autonomous — each individual decides independently)",
    "consensus (must confer before any decision)",
    "hierarchical (defer to dominant individual or caste)",
    "emergent hive (no individual authority — distributed intelligence)",
]

_FC_LIFESPAN: list[str] = [
    "short (10–25 years)",
    "human-range (60–100 years)",
    "long (200–500 years)",
    "very long (500–2,000 years)",
    "potentially immortal (no observed senescence)",
]

_FC_DISCOVERY_VECTORS: list[str] = [
    "orbital survey detected settlements below",
    "distress signal — origin unclear; they may have sent it or it may "
    "have drawn them",
    "ship made emergency landing on their world",
    "they approached the vessel — deliberately, at close range",
    "Scout Service first-contact team came through; party is the "
    "follow-up",
    "ruins investigation — the site is still inhabited",
    "mistaken for indigenous fauna on initial approach",
    "a trader or prospector found them and word got out before "
    "anyone could control it",
    "structured EM signal detected during jump transit — passive "
    "contact may have already occurred",
    "a character experienced psionic contact en route — unsolicited "
    "and impossible to explain",
]

_FC_WANTS: list[str] = [
    "unclear — motivations are opaque and may require time to read",
    "to be left alone",
    "resources or materials the party carries or represents",
    "protection from an external threat they haven't named yet",
    "information about the wider galaxy",
    "formal recognition of their sovereignty — to be acknowledged "
    "as existing by something larger than themselves",
    "trade",
    "to understand what the party IS — category confusion, not hostility",
    "help with an internal crisis they cannot solve alone",
    "to leave their world — they have been waiting for this",
]

_FC_COMPLICATIONS: list[str] = [
    "they mistake the party for mythological figures (gods, demons, "
    "ancestors, or prophesied visitors)",
    "communication is currently impossible without significant effort "
    "or specialist equipment",
    "a megacorp vessel is already in-system with the same idea",
    "they are in active danger from something environmental or "
    "political that they haven't disclosed",
    "they are not the dominant species on this world — something else "
    "is, and it's nearby",
    "Imperial non-interference protocol technically applies and is "
    "being quietly bent",
    "factionalized — one group wants contact; another faction is "
    "actively hostile to it",
    "the previous contact team came through — and didn't leave",
    "they possess something of significant value and appear to "
    "know it",
    "they've already made contact with someone else — someone "
    "problematic — and the party is the second visit",
]

_FC_IMPERIAL_STAKES: list[dict] = [
    {
        "stake": "Scout Service first contact report",
        "value": "Cr 50,000 + formal commendation; IISS tracking number required",
        "complication": "Filing means the system is now on the Admiralty's map.",
    },
    {
        "stake": "Territorial claim — trade route rights",
        "value": "Exclusive trade rights for 50 years if filed before anyone else",
        "complication": "Megacorp charter hunters are exactly as motivated as you are.",
    },
    {
        "stake": "Non-interference violation risk",
        "value": "Criminal charges under IISS Code if species is pre-spaceflight",
        "complication": (
            "Enforcement depends entirely on who finds out and whether "
            "they care enough to act."
        ),
    },
    {
        "stake": "Xenological significance",
        "value": (
            "This species rewrites something in established xenological theory — "
            "journals, the Imperial Science Bureau, academic institutions "
            "will all want access"
        ),
        "complication": "Significant attention follows; some of it will be unwelcome.",
    },
    {
        "stake": "Ancient connection suspected",
        "value": (
            "Preliminary evidence suggests a relationship to the Ancients — "
            "IISS Xenological Branch will want everything"
        ),
        "complication": "That interest may not be optional.",
    },
    {
        "stake": "Military or strategic value",
        "value": (
            "The system's position or the species' knowledge is tactically "
            "significant to Naval Intelligence"
        ),
        "complication": "Naval Intelligence will supersede Scout Service jurisdiction.",
    },
    {
        "stake": "Megacorp extraction interest",
        "value": (
            "Biological compounds, unique technology, or resource rights — "
            "someone will pay well for exclusivity"
        ),
        "complication": "The species' welfare is not written into any contract.",
    },
    {
        "stake": "Minor race classification pending",
        "value": (
            "Formal Imperial classification as a minor race changes "
            "diplomatic and legal standing"
        ),
        "complication": "Until classified, they have no protection under Imperial law.",
    },
]


# ── Contact barrier by communication method ───────────────────────────────────

_COMMUNICATION_BARRIER: dict[str, dict] = {
    "tonal/verbal": {
        "barrier": "moderate",
        "note": (
            "A shared acoustic channel exists. Language pattern analysis "
            "may yield structure within hours to days. Most promising "
            "opening for unaided contact."
        ),
    },
    "subsonic rumble (below human hearing)": {
        "barrier": "high",
        "note": (
            "Below human hearing range unaided. Ship sensors or specialist "
            "equipment required to detect intentional communication. "
            "They may not know you cannot hear them."
        ),
    },
    "infrasonic (far below human hearing)": {
        "barrier": "high",
        "note": (
            "Completely inaudible to unaided human senses. Detection "
            "requires equipment. Communication has almost certainly "
            "already been attempted without result."
        ),
    },
    "chemical/pheromonal": {
        "barrier": "very high",
        "note": (
            "No acoustic channel at all. Without specialist chemical "
            "analysis equipment, every exchange is meaningless noise "
            "to one or both parties."
        ),
    },
    "gestural/postural": {
        "barrier": "moderate",
        "note": (
            "Potentially interpretable — visual signal analysis may yield "
            "pattern and meaning with observation time and patience."
        ),
    },
    "bioluminescent patterning": {
        "barrier": "moderate",
        "note": (
            "Detectable by optical sensors. Pattern complexity suggests "
            "deliberate structure. Active response with lights may be "
            "possible."
        ),
    },
    "electromagnetic pulse (structured field modulation)": {
        "barrier": "low",
        "note": (
            "Interceptable by ship systems. Structured signal analysis "
            "is feasible. Passive contact may have already occurred "
            "during approach."
        ),
    },
    "tactile/haptic (contact-required)": {
        "barrier": "very high",
        "note": (
            "Requires close physical contact to communicate. Establishing "
            "that such contact is safe for both parties is the first "
            "challenge."
        ),
    },
    "psionic (requires PSI to perceive)": {
        "barrier": "critical",
        "note": (
            "Without a character with PSI ability, intentionality cannot "
            "even be confirmed. The species may be communicating constantly "
            "and be completely inaudible to everyone present."
        ),
    },
    "compound — verbal and chemical": {
        "barrier": "high",
        "note": (
            "Verbal component is accessible; chemical component — "
            "potentially the more nuanced half — is lost without equipment."
        ),
    },
    "compound — visual and gestural": {
        "barrier": "moderate",
        "note": (
            "Both channels are visually detectable. Combined signal may "
            "be semantically rich. Observation before response is "
            "strongly advisable."
        ),
    },
}


# ── Tech level → power dynamic ────────────────────────────────────────────────

_TL_POWER_DYNAMIC: dict[int, str] = {
    0: (
        "Overwhelming Imperium advantage. Pre-tool species. "
        "Non-interference protocol almost certainly applies and "
        "will be very hard to enforce once word spreads."
    ),
    1: (
        "Overwhelming advantage. Stone-age technology. "
        "Non-interference protocol applies. Contact will reshape "
        "their civilization regardless of intent."
    ),
    2: (
        "Significant gap. Metal tools and agriculture, but no "
        "understanding of what you arrived in. Non-interference "
        "protocol applies."
    ),
    3: (
        "Substantial gap. Early industrial. They understand "
        "flying machines in principle; they do not understand "
        "jump drive."
    ),
    4: (
        "Significant gap. Industrial society. They understand "
        "that you came from somewhere else, and are processing "
        "what that means."
    ),
    5: (
        "Moderate gap. Pre-spaceflight but technologically "
        "sophisticated. Radio capability likely. They may have "
        "been watching your approach."
    ),
    6: (
        "They have reached space themselves, or are very close. "
        "Power dynamic is asymmetric but closing. They have "
        "context for what you are."
    ),
    7: (
        "Peer-level interstellar capability. Genuine diplomatic "
        "situation — they have leverage and alternatives."
    ),
    8: (
        "Advanced interstellar. They are peers or ahead. "
        "Contact is negotiated, not imposed."
    ),
    9: (
        "Possibly more advanced than Imperial average. Contact "
        "is on their terms if they choose to set terms."
    ),
    10: (
        "Ancient or transcendent technology. The power dynamic "
        "may be entirely reversed. Proceed with extreme caution."
    ),
}


# ── Social structure → negotiation shape ─────────────────────────────────────

_SOCIAL_NEGOTIATION: dict[str, str] = {
    "solitary (territory-defending)": (
        "No representative is possible — each individual speaks only for "
        "itself. Whatever you agree with this one, others are not bound by."
    ),
    "mated pairs (lifelong bond)": (
        "Decisions are joint. Finding and addressing the bonded pair "
        "together matters; one alone may be genuinely unable to commit."
    ),
    "small pack (3–8, kin-based)": (
        "The dominant individual has real authority within the pack. "
        "Find them. Others will defer — or defer to the group."
    ),
    "band (10–40, flexible membership)": (
        "Leadership is fluid. The current dominant figure may not hold "
        "position — agreements may need renewal after internal shifts."
    ),
    "tribal (50–500, hierarchical)": (
        "You are talking to the wrong person unless you found the right "
        "person. Hierarchy matters enormously; misidentifying rank is "
        "a significant error."
    ),
    "hive (eusocial, reproductive caste)": (
        "Individuals may not be autonomous decision-makers. What looks "
        "like a conversation partner may be a relay. Find the decision "
        "node — which may not be physically present."
    ),
    "colonial organism (individuals are nodes of a distributed whole)": (
        "The being in front of you may be a temporary manifestation of "
        "a distributed intelligence. Disengaging it may end the "
        "conversation without warning."
    ),
}


# ── Diet → initial posture weights ───────────────────────────────────────────
# Format: list of (posture_label, weight) pairs.
# Weights are relative; they do not need to sum to 100.

_POSTURES = [
    "actively hostile",
    "territorial",
    "fearful",
    "watchful",
    "ritualistic",
    "cautiously curious",
    "openly curious",
    "indifferent",
    "welcoming",
]

_DIET_POSTURE_WEIGHTS: dict[str, list[int]] = {
    # weights align with _POSTURES order above
    "apex carnivore":          [15, 35, 5,  25, 10, 5,  3,  2, 0],
    "pursuit predator":        [10, 30, 5,  30, 10, 10, 3,  2, 0],
    "ambush predator":         [20, 30, 5,  30, 5,  5,  2,  3, 0],
    "omnivore (opportunistic)":[5,  20, 15, 20, 15, 15, 5,  3, 2],
    "omnivore (selective)":    [3,  15, 15, 20, 15, 20, 8,  2, 2],
    "grazer":                  [0,  5,  40, 20, 15, 15, 3,  2, 0],
    "browser":                 [0,  5,  35, 20, 15, 15, 5,  5, 0],
    "filter feeder":           [0,  3,  20, 10, 10, 20, 10, 25,2],
    "chemosynthetic":          [0,  2,  10, 5,  15, 20, 15, 30,3],
    "photosynthetic":          [0,  2,  5,  5,  10, 20, 20, 35,3],
    "parasitic":               [5,  25, 15, 30, 10, 10, 3,  2, 0],
    "scavenger":               [5,  10, 25, 30, 10, 15, 3,  2, 0],
}


# ═══════════════════════════════════════════════════════════════════════════════
# FIRST CONTACT — NAME GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

_FC_NAME_ONSETS = [
    "Kh", "Str", "Vel", "Zh", "Ts", "Ngr", "Rl", "Ss", "Th",
    "Gr", "Dvr", "Mk", "Yrr", "Ct", "Zr", "Tl", "Vr", "Ek",
    "Irr", "Ul", "Phth", "Ksv",
]
_FC_NAME_NUCLEI = [
    "aal", "eith", "uun", "oor", "aev", "iakh", "uiss", "eur",
    "oaz", "airn", "elh", "urr", "aakh", "iel", "orn", "aelv",
]
_FC_NAME_CODAS = [
    "rn", "th", "ss", "kh", "lv", "ng", "rt", "zh",
    "mn", "xt", "ll", "rr", "vn", "sk", "ff", "nk",
]


def _generate_alien_name() -> str:
    """
    Generate a provisional alien species name from phoneme pools.
    This is the Scout Service field designation — a placeholder until
    the species names itself or receives formal Admiralty classification.
    """
    onset  = random.choice(_FC_NAME_ONSETS)
    nucleus = random.choice(_FC_NAME_NUCLEI)
    coda   = random.choice(_FC_NAME_CODAS)
    name   = f"{onset}{nucleus}{coda}"
    if random.random() < 0.45:
        name += (
            f"-{random.choice(_FC_NAME_ONSETS).lower()}"
            f"{random.choice(_FC_NAME_NUCLEI).lower()}"
        )
    return name


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_major_race_profile(race: str) -> str:
    """
    Return the full profile for a Traveller major race as a JSON string.

    Accepted race values (case-insensitive, tolerates common variants):
      aslan, vargr, droyne, k'kree / kkree / k_kree,
      hivers / hiver, zhodani
    """
    key = race.lower().strip().replace("'", "").replace("-", "").replace(" ", "_")
    # Normalise common variants
    aliases = {
        "kkree":    "k_kree",
        "k_kree":   "k_kree",
        "hiver":    "hivers",
        "hivers":   "hivers",
        "zhodani":  "zhodani",
        "aslan":    "aslan",
        "vargr":    "vargr",
        "droyne":   "droyne",
    }
    key = aliases.get(key, key)

    if key not in MAJOR_RACES:
        available = ", ".join(MAJOR_RACES.keys())
        return json.dumps({
            "error": f"Unknown major race: '{race}'",
            "available": available,
        }, indent=2)

    result = dict(MAJOR_RACES[key])
    result["usage_note"] = (
        "Use characteristic_mods when generating this race's UPP. "
        "Reference npc_hooks for encounter seeds, key_drives for "
        "motivation, and psi_note before calling psi chance roll."
    )
    return json.dumps(result, indent=2)


def get_minor_race_profile(race: str) -> str:
    """
    Return the profile for a Traveller minor race as a JSON string.

    Accepted race values (case-insensitive):
      bwaps / newts, darrians, llellewyoly / dandelions,
      virushi, hhkar, jonkeereen, dolphins
    """
    key = race.lower().strip().replace("'", "").replace(" ", "_")
    aliases = {
        "newts":        "bwaps",
        "bwaps":        "bwaps",
        "dandelions":   "llellewyoly",
        "llellewyoly":  "llellewyoly",
        "darrians":     "darrians",
        "darrian":      "darrians",
        "virushi":      "virushi",
        "hhkar":        "hhkar",
        "jonkeereen":   "jonkeereen",
        "dolphins":     "dolphins",
        "dolphin":      "dolphins",
    }
    key = aliases.get(key, key)

    if key not in MINOR_RACES:
        available = ", ".join(MINOR_RACES.keys())
        return json.dumps({
            "error": f"Unknown minor race: '{race}'",
            "available": available,
        }, indent=2)

    result = dict(MINOR_RACES[key])
    result["usage_note"] = (
        "Minor races are lighter treatment — use for NPC flavor, "
        "encounter texture, and brief character concepts. For "
        "playable characters, supplement with Mongoose 2e alien "
        "supplements as needed."
    )
    return json.dumps(result, indent=2)


def generate_species_profile() -> dict:
    """
    Generate a procedural first-contact alien species profile.
    Returns a dict (not a JSON string) so generate_contact_situation()
    can read the fields directly.
    """
    diet = random.choice(_FC_DIET)
    tl   = random.choices(
        population=list(range(11)),
        weights=[8, 10, 12, 12, 12, 15, 10, 8, 6, 4, 3],
        k=1,
    )[0]

    provisional_name = _generate_alien_name()

    return {
        "provisional_name":   provisional_name,
        "designation_note":   (
            f"Scout Service field designation '{provisional_name}' — "
            "provisional pending formal Admiralty classification or "
            "self-identification."
        ),
        "body_symmetry":      random.choice(_FC_BODY_SYMMETRY),
        "locomotion":         random.choice(_FC_LOCOMOTION),
        "primary_sense":      random.choice(_FC_PRIMARY_SENSE),
        "size":               random.choice(_FC_SIZE),
        "diet":               diet,
        "social_structure":   random.choice(_FC_SOCIAL),
        "communication":      random.choice(_FC_COMMUNICATION),
        "cognitive_style":    random.choice(_FC_COGNITIVE),
        "lifespan":           random.choice(_FC_LIFESPAN),
        "tech_level":         tl,
        "tech_level_label":   f"TL {tl}",
    }


def generate_contact_situation(species: dict) -> dict:
    """
    Generate a first contact situation seeded from a species profile dict.
    Reads diet, social_structure, communication, tech_level, and size
    to produce weighted, coherent results rather than random noise.
    """
    diet   = species.get("diet", "omnivore (opportunistic)")
    social = species.get("social_structure", "band (10–40, flexible membership)")
    comm   = species.get("communication", "tonal/verbal")
    tl     = species.get("tech_level", 4)
    size   = species.get("size", "medium (human-sized — 40–120kg)")

    # Weighted posture from diet
    weights = _DIET_POSTURE_WEIGHTS.get(diet, _DIET_POSTURE_WEIGHTS["omnivore (opportunistic)"])
    posture = random.choices(_POSTURES, weights=weights, k=1)[0]

    # Communication barrier
    barrier_data = _COMMUNICATION_BARRIER.get(
        comm,
        {"barrier": "moderate", "note": "Non-standard communication — assessment required."},
    )

    # Tech level power dynamic
    tl_clamped = max(0, min(10, tl))
    power_dynamic = _TL_POWER_DYNAMIC[tl_clamped]

    # Non-interference protocol applies if TL ≤ 5
    nip_applies = tl <= 5

    # Social → negotiation shape
    negotiation = _SOCIAL_NEGOTIATION.get(social, "Negotiation structure unclear — observe before engaging.")

    # Size → physical note
    size_notes = {
        "small (cat-sized — roughly 3–8kg)": (
            "Scale difference is significant — they may not immediately "
            "categorize humanoid-sized contacts as the same kind of being."
        ),
        "medium (human-sized — 40–120kg)": (
            "Comparable scale. Physical comfort and intimidation dynamics "
            "are broadly legible to both sides."
        ),
        "large (horse-sized — 200–600kg)": (
            "PCs are physically smaller. Posture and approach matter "
            "regardless of the species' intent."
        ),
        "very large (elephant-sized — 1,000–5,000kg)": (
            "PCs are significantly smaller. Even incidental contact could "
            "be dangerous. Give them space."
        ),
        "massive (whale-sized — above 5,000kg)": (
            "PCs are negligible in scale. Whether you're perceived as a "
            "threat, a curiosity, or irrelevant may depend entirely on "
            "their cognitive style."
        ),
    }
    size_note = size_notes.get(size, "")

    # Pick stake and 1–2 complications
    stake = random.choice(_FC_IMPERIAL_STAKES)
    complications = random.sample(_FC_COMPLICATIONS, k=random.randint(1, 2))

    return {
        "discovery_vector":    random.choice(_FC_DISCOVERY_VECTORS),
        "initial_posture":     posture,
        "posture_note": (
            f"Weighted from diet ({diet}). Not fixed — "
            "circumstances and first actions can shift it."
        ),
        "what_they_want":      random.choice(_FC_WANTS),
        "communication_barrier": barrier_data,
        "negotiation_shape":   negotiation,
        "power_dynamic":       power_dynamic,
        "non_interference_protocol_applies": nip_applies,
        "nip_note": (
            "Imperial law requires non-interference with pre-spaceflight species. "
            "Enforcement is inconsistent and depends on who finds out."
            if nip_applies else
            "Species has reached or is approaching spaceflight capability. "
            "Non-interference protocol does not apply."
        ),
        "size_note":           size_note,
        "imperial_stake":      stake,
        "complications":       complications,
    }


def generate_first_contact() -> str:
    """
    Generate a complete first contact encounter: species profile + contact
    situation. Returns a single JSON string suitable for agent use.

    The species profile is generated first, then the situation is seeded
    from it — diet drives posture, communication drives barrier, tech level
    drives power dynamic.
    """
    species  = generate_species_profile()
    situation = generate_contact_situation(species)

    result = {
        "species_profile": species,
        "contact_situation": situation,
        "gm_note": (
            "The species profile establishes the facts; the contact situation "
            "establishes what is happening when the party arrives. Use both "
            "together. The complications are the adventure."
        ),
    }
    return json.dumps(result, indent=2)


def list_major_races() -> str:
    """Return a list of available major races with one-line summaries."""
    summaries = {
        "aslan":    "Lion-like bipeds. STR +2, DEX -2. Honor culture, territorial, Ihatei second sons everywhere.",
        "vargr":    "Wolf-derived. STR -1, DEX +1, END -1. CHA replaces SOC. Pack loyalty, charisma-driven.",
        "droyne":   "Small winged reptilians. Caste-dependent stats. Near-universal psionics. Deeply enigmatic.",
        "k_kree":   "Centaur-like herbivores. STR +4, DEX -4, END +2. Cannot tolerate solitude. Militant vegans.",
        "hivers":   "Starfish-bodied. DEX +4, STR -4. Never fight directly. Master manipulators. Ancient agendas.",
        "zhodani":  "Human. Psionics legal and celebrated. Noble/Intendant/Prole caste system. Five wars with Imperium.",
    }
    return json.dumps({"major_races": summaries}, indent=2)


def list_minor_races() -> str:
    """Return a list of available minor races with one-line summaries."""
    summaries = {
        "bwaps":       "Amphibian newts. DEX +2, END -2. Imperial bureaucrats. Protocol as moral practice.",
        "darrians":    "Near-human. INT +2. Accidentally detonated their sun. Possess the Star Trigger. Very careful.",
        "llellewyoly": "Five-limbed plant-animals. DEX +4, STR -4. Tactile/chemical communication. Very alien.",
        "virushi":     "Enormous herbivores. STR +6, END +4. Pacifist. Physically imposing, personally gentle.",
        "hhkar":       "Bipedal reptilians. STR +2, END +2. Direct, territorial. Common as Rim mercenaries.",
        "jonkeereen":  "Desert-adapted humans. END +2, STR -1. Pragmatic, patient. Barely distinguishable from baseline.",
        "dolphins":    "Uplifted terrans. INT +1. Non-linear communication. Exceptional navigation. Need wet quarters.",
    }
    return json.dumps({"minor_races": summaries}, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

MAJOR_RACE_TOOL_SCHEMA: dict = {
    "name": "get_major_race_profile",
    "description": (
        "Return the full cultural profile, characteristic modifiers, "
        "social structure, key drives, campaign presence notes, "
        "psionic notes, and NPC hooks for one of the six Traveller "
        "major non-human races. Call this when generating an Aslan, "
        "Vargr, Droyne, K'kree, Hiver, or Zhodani character or NPC — "
        "read characteristic_mods before rolling UPP, and check "
        "psi_note before calling psi chance roll."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "race": {
                "type": "string",
                "enum": ["aslan", "vargr", "droyne", "k'kree", "hivers", "zhodani"],
                "description": "The major race to retrieve.",
            },
        },
        "required": ["race"],
    },
}

MINOR_RACE_TOOL_SCHEMA: dict = {
    "name": "get_minor_race_profile",
    "description": (
        "Return the profile for one of the Traveller minor races "
        "in the library: Bwaps, Darrians, Llellewyoly, Virushi, "
        "Hhkar, Jonkeereen, or Dolphins. Use for NPC flavor, "
        "encounter texture, and brief character concepts. "
        "Lighter treatment than major race profiles."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "race": {
                "type": "string",
                "enum": [
                    "bwaps", "darrians", "llellewyoly",
                    "virushi", "hhkar", "jonkeereen", "dolphins",
                ],
                "description": "The minor race to retrieve.",
            },
        },
        "required": ["race"],
    },
}

FIRST_CONTACT_TOOL_SCHEMA: dict = {
    "name": "generate_first_contact",
    "description": (
        "Generate a complete first contact encounter for a Traveller "
        "scenario: an unknown alien species profile (body plan, diet, "
        "social structure, communication method, tech level) followed "
        "by a contact situation seeded from those facts. Diet drives "
        "initial posture. Communication method determines the contact "
        "barrier. Tech level defines the power dynamic and whether "
        "Imperial non-interference protocol applies. Returns both "
        "profile and situation as a single result. Call this for "
        "exploration, survey, and frontier scenarios involving "
        "undocumented species. Do NOT call for Firefly scenarios "
        "(the 'Verse has no alien life)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

LIST_MAJOR_RACES_TOOL_SCHEMA: dict = {
    "name": "list_major_races",
    "description": (
        "Return a summary list of the six Traveller major races with "
        "one-line descriptions. Call this if you are unsure which "
        "major race to use or want to present options."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

LIST_MINOR_RACES_TOOL_SCHEMA: dict = {
    "name": "list_minor_races",
    "description": (
        "Return a summary list of the Traveller minor races in the "
        "library with one-line descriptions. Call this if you are "
        "unsure which minor race to use or want to present options."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}
