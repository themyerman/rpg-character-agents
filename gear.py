"""
Gear rollers — small, specific kits for each character type, all four games.

Returns 4-5 items: a signature weapon or tool (always appropriate for the
class/career/role), 2-3 supporting items, and one personal touch that hints
at history. Story-first — items have brief characterful descriptions, not
stat blocks. The personal item is the last one returned; let it land.
"""

import json
import random


# ── D&D gear by class ─────────────────────────────────────────────────────────

_DND_GEAR: dict[str, dict[str, list[str]]] = {
    "Barbarian": {
        "weapons": [
            "a greataxe with a repaired haft, iron-banded where it split last year",
            "a pair of handaxes — one balanced for throwing, one not",
            "a two-handed maul, head wrapped in leather between uses",
        ],
        "kit": [
            "a bedroll sewn from a tanned bear pelt",
            "a hunting knife worn smooth at the handle from daily use",
            "a waterskin and a week of dried meat rolled in cloth",
            "a whetstone carried loose in a belt pouch",
            "a length of rope braided with gut for extra grip in wet conditions",
        ],
    },
    "Bard": {
        "weapons": [
            "a rapier in a cracked leather scabbard, still perfectly balanced",
            "a hand crossbow worn under the coat with twelve bolts in a sewn pocket",
            "a shortsword with a scratched pommel and grip rewound in red cord",
        ],
        "kit": [
            "a well-traveled instrument case, reinforced at the corners",
            "a dog-eared book of collected songs written in three different hands",
            "a disguise kit tucked into the instrument case's false bottom",
            "three sets of clothes, one noticeably better than the others",
            "a sealed bottle of something drinkable saved for the right moment",
        ],
    },
    "Cleric": {
        "weapons": [
            "a mace, the head wrapped in cloth when not in use",
            "a warhammer with the deity's symbol stamped into the head",
            "a flail, heavier than it looks, with a grip worn to the wood",
        ],
        "kit": [
            "a holy symbol worn at the throat, not the chest — a deliberate choice",
            "a healer's kit, half-depleted and neatly restocked",
            "a prayer book with a cracked spine and several pages annotated",
            "candle stubs and a tinderbox carried for vigil",
            "a small wooden case containing the sacraments of their faith",
        ],
    },
    "Druid": {
        "weapons": [
            "a wooden staff with a carved serpent wrapping the upper third",
            "a scimitar, grip wrapped in braided vine and re-wrapped periodically",
            "a sickle with a handle carved from a tree struck by lightning",
        ],
        "kit": [
            "a leather satchel of gathered seeds and dried plants",
            "an herbalism kit rolled in waxed canvas",
            "a waterskin filled from a spring the druid considers sacred",
            "a fire kit — flint, steel, and tinder kept dry in an oilskin",
            "a smooth wooden bowl, darkened from years of use",
        ],
    },
    "Fighter": {
        "weapons": [
            "a longsword with a notch in the blade from a fight they still think about",
            "a handaxe and a battered shield reinforced with iron along the rim",
            "a spear and a belt dagger — two things for two kinds of problem",
        ],
        "kit": [
            "armor maintained to a higher standard than anything else they own",
            "a whetstone and an oil rag, used every evening without fail",
            "a belt knife they think of as a tool rather than a weapon",
            "a standard-issue kit bag, organized to a system outsiders find opaque",
            "a set of dice from a gambling habit they'd describe as occasional",
        ],
    },
    "Monk": {
        "weapons": [
            "a quarterstaff with grips worn smooth from years of daily use",
            "a short weighted staff wrapped in dark cloth",
            "a pair of handaxes carried as weapons of last resort",
        ],
        "kit": [
            "simple traveling robes, patched at the elbows but clean",
            "a wrapped calligraphy kit, rarely opened outside the monastery",
            "a spare pair of sandals, worn soft with use",
            "a cloth bundle of personal items — barely anything in it",
            "a small pot and a pinch of incense for morning practice",
        ],
    },
    "Paladin": {
        "weapons": [
            "a longsword with the deity's symbol engraved at the base of the blade",
            "a warhammer, heavier than it needs to be, which is the point",
            "a bastard sword used two-handed, with the shield kept on the back",
        ],
        "kit": [
            "armor kept polished enough to see your reflection in it",
            "a holy symbol in silver or iron, depending on what they swore to",
            "a single candle carried for vigil, half-burned from the last one",
            "a riding kit — spurs, saddle oil, a lead rope",
            "a small box with medicines and bandages from the last time they needed them",
        ],
    },
    "Ranger": {
        "weapons": [
            "a longbow of yew, strung only when needed, with 20 arrows fletched in grey",
            "a shortsword worn cross-draw and a hunting knife at the hip",
            "a pair of short blades suited for both thrown and held work",
        ],
        "kit": [
            "leather armor broken in over years of use in rough terrain",
            "a set of six wire snares on a belt hook",
            "50 feet of hempen rope, wound tight",
            "a field tracking kit — charcoal sticks, waxed cloth squares, a small compass",
            "a week of trail rations, efficiently packed and resupplied regularly",
        ],
    },
    "Rogue": {
        "weapons": [
            "a shortsword at the left hip and three daggers in places that are less obvious",
            "four daggers in various states of concealment — the fifth is in the boot",
            "a hand crossbow folded under the coat and a dozen bolts in a sewn pocket",
        ],
        "kit": [
            "leather armor dark enough to lose detail in poor light",
            "a thieves' tool set in a chamois roll, one pick slightly bent from recent use",
            "a shuttered lantern and a flask of lamp oil",
            "a set of dark, unremarkable working clothes",
            "a length of silk rope — quieter than hemp on stone",
        ],
    },
    "Sorcerer": {
        "weapons": [
            "a quarterstaff — the magic is the weapon; this is the last resort",
            "a single dagger worn at the belt, mostly ornamental, occasionally not",
        ],
        "kit": [
            "a component pouch, the contents slightly singed at the edges",
            "a travel cloak with scorch marks along the hem from an earlier incident",
            "a notebook of spell observations written in a cramped, urgent hand",
            "a second cloak kept clean — for when the first one burns",
            "a spare set of clothes kept for the same reason",
        ],
    },
    "Warlock": {
        "weapons": [
            "a dagger with the patron's mark burned into the handle",
            "a light crossbow with bolts tipped in something dark and unasked-about",
            "a shortsword they haven't drawn in months — they haven't needed to",
        ],
        "kit": [
            "leather armor worked with a symbol they try not to think about",
            "an arcane focus: a carved idol, a twisted wand, or a bottled shadow",
            "a patron's token — something given, not chosen",
            "a journal with the earliest entries blacked out",
            "a spare robe kept rolled and bound with cord",
        ],
    },
    "Wizard": {
        "weapons": [
            "a quarterstaff — occasionally useful, more often a walking stick",
            "a dagger for emergencies, not frequently cleaned",
        ],
        "kit": [
            "a spellbook in a leather case, spine cracked, pages annotated in three colors of ink",
            "a component pouch worn at the hip, always a little heavier than expected",
            "a scholar's satchel with ink, three quills, and a penknife",
            "a pair of reference texts, one of which is overdue at a library",
            "a spare travelling robe, the good one",
        ],
    },
}

_DND_PERSONAL: list[str] = [
    "a letter they've never sent, kept folded in an inner pocket",
    "a coin with a hole drilled through it, worn on a cord around the wrist",
    "a miniature portrait of someone they haven't seen in years",
    "a small stone from the place they grew up, carried without thinking about it",
    "a sealed letter they were told to deliver and never did",
    "a military badge from a unit that was dissolved",
    "a ring that doesn't fit any of their fingers, kept on a chain",
    "a dog-eared book, half the pages annotated in their own hand",
    "a carved wooden figure, roughly made, clearly by someone who tried hard",
    "a spare key to a door whose lock they're not sure still exists",
    "a strip of cloth with a name embroidered on it in a language they can't read",
    "a broken compass that points somewhere consistent but not north",
    "a small bottle of sand from a place with a name they won't say",
    "a sketch of someone's face, charcoal on brown paper, worn at the folds",
    "a medal they didn't earn, and a reason they kept it anyway",
]


def roll_dnd_gear(class_name: str) -> str:
    """Return a starting gear kit for a D&D character by class."""
    gear     = _DND_GEAR.get(class_name, {
        "weapons": ["a hand weapon appropriate to their station"],
        "kit":     ["practical travelling clothes", "a belt pouch with coin and small necessities"],
    })
    weapon   = random.choice(gear["weapons"])
    kit      = random.sample(gear["kit"], min(2, len(gear["kit"])))
    personal = random.choice(_DND_PERSONAL)
    return json.dumps({
        "gear": [weapon] + kit + [personal],
        "note": (
            "Include every item in the Equipment section. "
            "Each should read as something this specific person carries — worn in, "
            "maintained or neglected in a way that says something about them. "
            "The personal item hints at history; give it one sentence."
        ),
    })


# ── Traveller gear by career ──────────────────────────────────────────────────

_TRAVELLER_GEAR: dict[str, dict[str, list[str]]] = {
    "Navy": {
        "weapons": [
            "an autopistol in a service holster, navy-issue, scuffed at the retention clip",
            "a cutlass with a regulation grip and an unremarkable blade, well maintained",
            "a snub pistol carried off-duty, technically not regulation",
        ],
        "kit": [
            "a dress uniform tunic, worn rarely and maintained to a high standard",
            "a vacc suit patch kit kept in a chest pocket",
            "a navigation manual, two editions out of date, heavy with margin notes",
            "a naval identification badge clipped to a lanyard",
            "a flask, for off-watch hours",
        ],
    },
    "Army": {
        "weapons": [
            "a rifle, battered from use but maintained at the breech",
            "an SMG in a worn chest rig with two spare magazines",
            "a combat knife, military issue, sharpened every week",
        ],
        "kit": [
            "a field kit in a kit bag: repair tools, patches, wire, waterproofing",
            "combat dress worn thin at the knees and elbows",
            "a map case with the last deployment's terrain charts still inside",
            "dog tags — their own and one that isn't",
            "a flask of something local from the last posting",
        ],
    },
    "Marines": {
        "weapons": [
            "a gauss rifle maintained to a standard that would satisfy an inspector",
            "a combat shotgun in a sling clip, chamber empty",
            "a combat knife in a thigh sheath and an autopistol as backup",
        ],
        "kit": [
            "a regimental badge worn inside the collar, not visible unless shown",
            "a combat medkit, half-used and restocked with whatever was available",
            "armor repair patches and two spare seals",
            "a letter, unsealed, that someone should have received by now",
            "a dog-eared copy of the regimental manual used as a journal on the back pages",
        ],
    },
    "Scout": {
        "weapons": [
            "a scout carbine with a worn stock and a reliable action",
            "a body pistol, small enough to clear most port scanners",
            "a knife — technically a survival tool, practically a sidearm",
        ],
        "kit": [
            "a personal vacc suit, patched twice at the left shoulder",
            "a battered survey scanner with a cracked casing but accurate readings",
            "a rolled chart case, the charts inside annotated heavily by hand",
            "a survival kit: rations, water purifier, emergency beacon, trauma patches",
            "a comm unit modified for IISS frequencies",
        ],
    },
    "Merchant": {
        "weapons": [
            "a cutlass kept behind the pilot's seat, not on the hip",
            "an autopistol worn at the belt, registered and declared",
            "a stunner — handles disputes without damaging cargo",
        ],
        "kit": [
            "a cargo manifest tablet, scratched across the display",
            "a trade contact book in three languages",
            "a set of cargo hooks and a personal seal for crates",
            "a portable scale calibrated for mass rather than volume",
            "a credit chip with a backup account nobody knows about",
        ],
    },
    "Drifter": {
        "weapons": [
            "a knife — the one constant through every port and every year",
            "a worn autopistol held together by familiarity as much as parts",
            "a telescoping baton folded into a coat pocket",
        ],
        "kit": [
            "a bedroll that has been in worse places than this one",
            "a deck of cards missing one face card, worn smooth",
            "a change of clothes, the second set marginally better than the first",
            "a tin cup and a spork, scratched with someone else's initials",
            "a small amount of local currency, always slightly wrong for wherever they are",
        ],
    },
    "Noble": {
        "weapons": [
            "a dress rapier in a formal scabbard — ceremonial, but the blade is real",
            "a concealed body pistol in a holster sewn into the jacket lining",
            "an autopistol in a fine leather holster, discreet",
        ],
        "kit": [
            "fine clothes in a sealed travel case",
            "a comm device of noticeably higher quality than those around them",
            "a letter of introduction signed by someone whose name opens doors",
            "a personal signet ring, not always worn",
            "a household retainer's emergency contact, in case things go badly",
        ],
    },
    "Agent": {
        "weapons": [
            "an autopistol in a shoulder rig under the jacket",
            "a body pistol and a blade — neither in an obvious place",
            "a snub pistol registered to a name that isn't quite theirs",
        ],
        "kit": [
            "a false identification set with two complete identities",
            "a surveillance kit: micro-recorder, passive scanner, bug-detection sweep",
            "a burner comm unit, already activated",
            "a field kit with lock bypass tools and a signal scrambler",
            "an emergency data chip that erases on three failed access attempts",
        ],
    },
    "Scholar": {
        "weapons": [
            "a knife carried for field work, which is technically true",
            "an autopistol obtained for a previous expedition, rarely used since",
        ],
        "kit": [
            "a data pad loaded with research notes in a proprietary format",
            "a reference library on six data chips, indexed by hand",
            "a field notebook — the kind that survives weather",
            "specimen collection tools in a hard case",
            "a recording device that doubles as a comm unit",
        ],
    },
    "Entertainer": {
        "weapons": [
            "a small blade kept for personal security, rarely thought about",
            "nothing visible — they rely on the people around them, which is either smart or optimistic",
        ],
        "kit": [
            "an instrument or performance props in a travel case, the case well-traveled",
            "three sets of performance clothing in a sealed bag",
            "a contract folder with current and pending engagements",
            "a portable comm with a media account of some distinction",
            "a makeup kit with more contingencies in it than most people carry weapons",
        ],
    },
    "Rogue": {
        "weapons": [
            "a knife and a holdout pistol — the knife gets more use",
            "two blades in different places and a snub pistol in a third",
            "a blade and a garrote, neither obviously a weapon until needed",
        ],
        "kit": [
            "a false ID set on two chips",
            "lockpicks in a flat case sewn into the jacket lining",
            "a portable scanner for reading security systems",
            "dark, practical clothes without distinctive features",
            "a personal comm with contacts in four systems",
        ],
    },
    "Citizen": {
        "weapons": [
            "a knife carried more for habit than threat",
            "a small autopistol, licensed, in a belt holster",
        ],
        "kit": [
            "a work kit specific to their trade, worn and practical",
            "a personal comm with mostly local contacts",
            "practical clothes for a working life",
            "a toolkit appropriate to their occupation",
            "a credit chip and a union card",
        ],
    },
}

_TRAVELLER_PERSONAL: list[str] = [
    "a physical photograph — rare enough to be significant",
    "a folded star chart with one system circled and no explanation given",
    "a data chip that won't open without a key they haven't shared with anyone",
    "a small metal token from a ship that no longer exists",
    "a letter they were supposed to deliver five years ago",
    "a journal kept in a language they learned specifically to keep it private",
    "a commemorative coin from an action they weren't supposed to survive",
    "a family crest on a chain, from a family that isn't theirs",
    "a holographic chip of someone they haven't seen since their last jump",
    "a name and a system written on a piece of hull plating",
    "a personal comm with a contact list that no longer connects",
    "a small carved figure from a world they'd rather not explain",
]


def roll_traveller_gear(career: str) -> str:
    """Return a starting gear kit for a Traveller character by career."""
    # Case-insensitive lookup with substring fallback
    key = None
    career_low = career.lower().strip()
    for k in _TRAVELLER_GEAR:
        if k.lower() == career_low:
            key = k
            break
    if not key:
        for k in _TRAVELLER_GEAR:
            if k.lower() in career_low or career_low in k.lower():
                key = k
                break
    gear = _TRAVELLER_GEAR.get(key, {
        "weapons": ["a knife or short blade, appropriate to their background"],
        "kit":     ["working clothes suited to their trade", "a personal comm unit"],
    })
    weapon   = random.choice(gear["weapons"])
    kit      = random.sample(gear["kit"], min(2, len(gear["kit"])))
    personal = random.choice(_TRAVELLER_PERSONAL)
    return json.dumps({
        "gear": [weapon] + kit + [personal],
        "note": (
            "Include every item in the Equipment section. "
            "Items should feel earned — worn in, maintained or neglected in ways "
            "that say something about the career and the years. "
            "The personal item raises a question; let it stay unanswered."
        ),
    })


# ── Firefly gear by role ──────────────────────────────────────────────────────

_FIREFLY_GEAR: dict[str, dict[str, list[str]]] = {
    "Captain": {
        "weapons": [
            "a pistol worn at the hip, always visible, always loaded",
            "a revolver in a cross-draw holster — old-fashioned and reliable",
            "a sidearm and a boot knife, one for problems and one for everything else",
        ],
        "kit": [
            "a long coat, battered enough to be a biography",
            "ship's papers and cargo manifests in an inner pocket",
            "a small lockbox key on a cord around their neck",
            "a cortex reader loaded with crew files and back-channel contacts",
            "a flask, kept for decisions that need to feel inevitable",
        ],
    },
    "Pilot": {
        "weapons": [
            "a sidearm worn mostly for credibility rather than preference",
            "a compact pistol tucked in a flight suit thigh pocket",
        ],
        "kit": [
            "a worn flight suit with patches from three ships they've served on",
            "navigation charts on a personal cortex reader, heavily customized",
            "a lucky charm of some kind — the specifics are personal and non-negotiable",
            "a spare set of flight gloves, the first pair worn through at the thumbs",
            "a small toolkit for cockpit quick-fixes",
        ],
    },
    "First Mate": {
        "weapons": [
            "a sidearm and a backup blade — they learned about backups the hard way",
            "a pistol and a collapsible baton, both within reach at all times",
            "a combat shotgun for when things get past manageable",
        ],
        "kit": [
            "a worn combat vest with practical pockets",
            "a battered journal, half scheduling and half private",
            "a crew roster on a laminated card, updated by hand",
            "a medpatch kit for field use",
            "a set of restraints — zip ties and one pair of proper cuffs",
        ],
    },
    "Mechanic": {
        "weapons": [
            "a large wrench that is also, in a pinch, a weapon",
            "a pistol found in the engine room and kept as much as a question as a precaution",
        ],
        "kit": [
            "a tool belt worn most of the day",
            "a grease-stained diagnostic tablet",
            "a personal kit bag with specialty tools that wouldn't survive crew sharing",
            "a spare set of work clothes, the original set beyond saving",
            "a small notebook of engine observations, modifications, and standing complaints",
        ],
    },
    "Doctor": {
        "weapons": [
            "a pistol carried reluctantly, accuracy uncertain under stress",
            "a compact surgical blade that isn't meant as a weapon and occasionally isn't",
        ],
        "kit": [
            "a medkit stocked to professional standards with field-work additions",
            "a portable cortex reader with medical references loaded",
            "surgical tools in a padded case, kept sterile regardless of circumstances",
            "stims and trauma patches in a dedicated inner pocket",
            "a small notebook of patient observations in a cipher nobody else has decoded",
        ],
    },
    "Shepherd": {
        "weapons": [
            "a walking stick — heavy, solid, and not really a weapon",
            "nothing visible, which doesn't necessarily mean nothing",
        ],
        "kit": [
            "a worn copy of a holy text, spine replaced twice",
            "simple clothes of noticeably good quality if examined closely",
            "a travelling kit for performing rites — candles, a cloth, a small vessel",
            "a personal comm with contacts that don't look like much",
            "food for sharing, always",
        ],
    },
    "Muscle": {
        "weapons": [
            "a shotgun slung across the back and a pistol at the hip",
            "a rifle for distance and a blade for when distance isn't available",
            "a heavy pistol and a combat knife, both hands occupied when required",
        ],
        "kit": [
            "a combat vest worn by default",
            "extra ammunition distributed across three different pockets",
            "a medpatch kit — they go through more than most",
            "a set of restraints and a set of opinions about why they carry them",
            "a personal comm with exactly six contacts",
        ],
    },
    "Grifter": {
        "weapons": [
            "a compact pistol worn where it won't break the silhouette of good clothes",
            "a blade in a wrist sheath — harder to find, just as final",
        ],
        "kit": [
            "three complete outfits ranging from laborer to minor gentry, all in one bag",
            "a forgery kit with a dedicated power cell",
            "a false ID set: two full identities, a third in progress",
            "a pocket cortex unit for real-time background research mid-conversation",
            "a small personal safe that opens with a combination no one else knows",
        ],
    },
    "Thief": {
        "weapons": [
            "a blade, quiet and compact — not for fighting but for conversations that need to end",
            "a compact pistol and a throwing knife; which they reach for first depends on the room",
        ],
        "kit": [
            "dark working clothes that don't catch light",
            "a lockpick set in a flat leather case",
            "a grappling line and a motorized ascender",
            "a scanner for detecting motion sensors and active comm traffic",
            "a compact cutting torch for when lockpicking isn't the right answer",
        ],
    },
}

_FIREFLY_PERSONAL: list[str] = [
    "a photograph from before the war — or after — that they look at when no one's watching",
    "a medallion from the Battle of Serenity Valley or something that reminds them of it",
    "a letter they wrote and never sent, kept folded in a coat pocket",
    "a personal comm with a contact list they've mostly stopped updating",
    "a piece of jewelry that doesn't match their usual register",
    "a small toy or trinket that belongs to someone they're trying to get back to",
    "a map of the 'Verse with three systems circled and no notes explaining why",
    "a coin from a world they swore they'd never go back to",
    "a clipping from an old Cortex news item, creased from years of folding",
    "a personal item belonging to someone they outlived",
    "a photograph of a ship they used to fly on",
    "a warranty card for something that no longer exists",
]


def roll_firefly_gear(role: str) -> str:
    """Return a starting gear kit for a Firefly character by role."""
    # Case-insensitive lookup
    key = None
    role_low = role.lower().strip()
    for k in _FIREFLY_GEAR:
        if k.lower() == role_low:
            key = k
            break
    if not key:
        for k in _FIREFLY_GEAR:
            if k.lower() in role_low or role_low in k.lower():
                key = k
                break
    gear = _FIREFLY_GEAR.get(key, {
        "weapons": ["a sidearm, nothing fancy"],
        "kit":     ["practical working clothes", "a personal comm"],
    })
    weapon   = random.choice(gear["weapons"])
    kit      = random.sample(gear["kit"], min(2, len(gear["kit"])))
    personal = random.choice(_FIREFLY_PERSONAL)
    return json.dumps({
        "gear": [weapon] + kit + [personal],
        "note": (
            "Include every item in the Equipment section of the character sheet. "
            "Gear in the 'Verse is personal — things are worn, repaired, and accumulated. "
            "The personal item carries weight; let it."
        ),
    })


# ── Scum and Villainy gear by playbook ───────────────────────────────────────

_SCUM_GEAR: dict[str, dict[str, list[str]]] = {
    "Muscle": {
        "weapons": [
            "a heavy two-handed weapon — a monoblade, a powered maul, or a custom slug-thrower",
            "a pair of brutal melee weapons and a pistol in a chest holster",
            "a scatter gun and a long-knife, the combination that ends arguments",
        ],
        "kit": [
            "light armor, patched at the left shoulder and the right thigh",
            "stim injectors in a belt pouch — enough for the job",
            "a set of restraints, used professionally",
            "a med-patch kit mostly used on themselves",
            "a personal comm with six contacts, at least four of them violent",
        ],
    },
    "Pilot": {
        "weapons": [
            "a sidearm worn for credibility rather than preference",
            "a compact pistol in a thigh pocket, license current for this system",
        ],
        "kit": [
            "a flight suit with patches from two crews they'd rather not talk about",
            "a personal nav computer, heavily customized and backed up three times",
            "a lucky charm they won't explain and won't travel without",
            "a set of piloting tools for field maintenance of the ship's systems",
            "a personal comm with direct links to a fence, a shipwright, and someone they owe money",
        ],
    },
    "Scoundrel": {
        "weapons": [
            "a blade at the hip and a holdout pistol in the coat lining",
            "two pistols — one declared to the right people, one not",
            "a monoblade and a compact stun weapon for conversations that need to stay quiet",
        ],
        "kit": [
            "fine clothes in acceptable condition, one set that's genuinely good",
            "a forgery kit in a sealed travel case",
            "a false ID set: three identities, one recently compromised",
            "a personal comm with an encrypted contact list",
            "a small lockbox key and not much else to show for the current contract",
        ],
    },
    "Mystic": {
        "weapons": [
            "no conventional weapon — which somehow makes people more uncomfortable",
            "a blade of unusual material, given rather than bought",
        ],
        "kit": [
            "an attunement focus — a crystal, carved bone, or shard of Ur material",
            "unusual clothing that doesn't belong to any recognizable culture or era",
            "an old text in a language that predates the Hegemony by a significant margin",
            "a personal comm used rarely and only for specific contacts",
            "a meditation kit: incense, a cloth, a small vessel of water from somewhere unspecified",
        ],
    },
    "Speaker": {
        "weapons": [
            "a compact pistol, tasteful, the kind that can be explained satisfactorily",
            "a blade worn as an accessory — thin, formal, sharp",
        ],
        "kit": [
            "fine clothing, two complete sets, one for each kind of meeting",
            "a recording device disguised as a personal accessory",
            "a calling card set — physical cards, still meaningful in certain circles",
            "a dossier on three key contacts, encrypted on a personal comm",
            "a personal gift chosen for the next meeting, wrapped and ready",
        ],
    },
    "Stitch": {
        "weapons": [
            "a surgical tool that is technically a weapon — not recommended",
            "a compact pistol carried without enthusiasm but without hesitation",
        ],
        "kit": [
            "a medical kit stocked beyond standard, with field additions",
            "stim supplies in a dedicated inner pocket — the expensive kind",
            "surgical tools in a padded case, kept clean regardless of circumstances",
            "a clinical notebook in an encrypted format nobody else has decoded",
            "a personal comm with a short list of medical contacts and a longer list of suppliers",
        ],
    },
}

_SCUM_PERSONAL: list[str] = [
    "a data chip with a dead drop message that was never picked up",
    "a personal token from a crew that no longer exists",
    "a photograph — physical, not digital — of someone they owe something to",
    "a small carved figure from a world that isn't on current Hegemony charts",
    "a fragment of something that might be Ur material, kept in a sealed case",
    "a personal comm with one contact listed only as a symbol",
    "a ring from a faction they're not supposed to have survived",
    "a journal in a cipher only they know, which has nothing dangerous in it at all",
    "a warrant for someone else, acquired and not turned in",
    "a key to a lockbox in a station they're not planning to visit again",
    "a folded note with a name and a system, no other context",
    "a playing card with a handwritten message on the back",
]


def roll_scum_gear(playbook: str) -> str:
    """Return a starting gear kit for a Scum and Villainy character by playbook."""
    # Case-insensitive lookup
    key = None
    pb_low = playbook.lower().strip()
    for k in _SCUM_GEAR:
        if k.lower() == pb_low:
            key = k
            break
    gear = _SCUM_GEAR.get(key, {
        "weapons": ["a blade or pistol appropriate to the job"],
        "kit":     ["practical working clothes", "a personal comm"],
    })
    weapon   = random.choice(gear["weapons"])
    kit      = random.sample(gear["kit"], min(2, len(gear["kit"])))
    personal = random.choice(_SCUM_PERSONAL)
    return json.dumps({
        "gear": [weapon] + kit + [personal],
        "note": (
            "Include every item in the Load section of the character sheet. "
            "Items should feel used — worn in, maintained or improvised. "
            "The personal item is the one that raises a question; let it stay open."
        ),
    })


# ── Tool schemas ──────────────────────────────────────────────────────────────

DND_GEAR_TOOL_SCHEMA: dict = {
    "name": "roll_dnd_gear",
    "description": (
        "Get a starting equipment kit for a D&D character based on their class. "
        "Returns 4-5 items: the signature weapon or tool for this class, "
        "2 class-appropriate supporting items, and one personal item that hints at history. "
        "Call this after choosing the character's class. "
        "Every returned item must appear in the Equipment section."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "The character's class.",
                "enum": list(_DND_GEAR.keys()),
            },
        },
        "required": ["class_name"],
    },
}

TRAVELLER_GEAR_TOOL_SCHEMA: dict = {
    "name": "roll_traveller_gear",
    "description": (
        "Get a starting equipment kit for a Traveller character based on their most recent career. "
        "Returns 4-5 items: the career's signature weapon or tool, 2 career-appropriate items, "
        "and one personal item. "
        "Call this after completing career generation. "
        "Every returned item must appear in the Equipment section."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "career": {
                "type": "string",
                "description": (
                    "The character's most recent or defining career. "
                    "Examples: Navy, Scout, Drifter, Merchant, Army, Marines, Noble, Agent, Scholar."
                ),
            },
        },
        "required": ["career"],
    },
}

FIREFLY_GEAR_TOOL_SCHEMA: dict = {
    "name": "roll_firefly_gear",
    "description": (
        "Get a starting gear kit for a Firefly character based on their role. "
        "Returns 4-5 items specific to that role — always includes the appropriate weapon. "
        "Call this right after choosing the character's role. "
        "Every returned item must appear in the Equipment section of the character sheet."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "role": {
                "type": "string",
                "description": "The character's role.",
                "enum": list(_FIREFLY_GEAR.keys()),
            },
        },
        "required": ["role"],
    },
}

SCUM_GEAR_TOOL_SCHEMA: dict = {
    "name": "roll_scum_gear",
    "description": (
        "Get a starting load for a Scum and Villainy character based on their playbook. "
        "Returns 4-5 items specific to the playbook — always includes the playbook's signature weapon or tool. "
        "Call this right after choosing the playbook. "
        "Every returned item must appear in the Load section of the character sheet."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "playbook": {
                "type": "string",
                "description": "The character's playbook.",
                "enum": list(_SCUM_GEAR.keys()),
            },
        },
        "required": ["playbook"],
    },
}
