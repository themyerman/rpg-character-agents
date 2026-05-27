"""
Encounter Generator — all four RPG game systems.

Creates vivid, GM-ready encounter sketches seeded by randomised tables.
A seed is four elements: context (setting), situation (what's happening),
complication (what makes the obvious approach fail), and motivation (why
the antagonist/NPC is doing this). The model does the creative work from
there — we just prevent it from defaulting to generic encounters.

Optionally incorporates a saved party brief to tailor the encounter
to a specific crew's history, skills, and hooks.

Saves to output/{game_subdir}/encounters/.

Run with: python encounter_agent.py
"""

import json
import random
import re
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.names import roll_name_suggestion, NAME_TOOL_SCHEMA
from lib.ships import (
    roll_ship_name,
    TRAVELLER_SHIP_TOOL_SCHEMA,
    FIREFLY_SHIP_TOOL_SCHEMA,
    SCUM_SHIP_TOOL_SCHEMA,
    DND_SHIP_TOOL_SCHEMA,
    ALIEN_SHIP_TOOL_SCHEMA,
)
from lib.safety import sanitize_desc, screen_desc, wrap_desc, screen_output
from lib.utils import get_client, run_agent_loop, slug, pick, strip_preamble


# ── Directory helpers ─────────────────────────────────────────────────────────

_OUTPUT = Path(__file__).parent.parent / "output"

GAME_SUBDIRS: dict[str, str] = {
    "dnd":       "dnd",
    "traveller": "traveller",
    "firefly":   "firefly",
    "scum":      "scum_villainy",
    "alien":     "alien",
    "deadlands": "deadlands",
}


# ── Encounter seed tables ─────────────────────────────────────────────────────

ENCOUNTER_POOLS: dict[str, dict[str, list[str]]] = {

    "dnd": {
        "contexts": [
            "a fog-wreathed crossroads where three roads meet and locals avoid after dark",
            "the collapsed nave of a temple to a god nobody remembers anymore",
            "a market district where the merchants sell things that shouldn't exist",
            "a river crossing where the ferryman hasn't left his boat in three years",
            "the entrance to a mine that produced exceptional ore until six weeks ago",
            "a noble's private hunting grounds, walled and well-posted with warnings",
            "a village where everyone has the same face",
            "a section of sewer that the city guards refuse to patrol",
            "a library whose books rewrite themselves between readings",
            "a lighthouse on a coast with no sea",
            "a battlefield that is always exactly as it was at the moment of the last great death",
            "a wizard's tower that has been empty for forty years but shows signs of recent habitation",
            "a halfling community sitting atop something they refuse to discuss",
            "a roadside shrine where travelers leave offerings not for good luck but to buy safe passage",
            "a dwarven vault that was sealed from the inside",
            "a forest glade where animals gather and do not flee from people",
            "a city gate whose guards change every hour but no one ever comes or goes",
            "an inn where the same argument is happening at three different tables",
            "a cave system that goes deeper than it should",
            "a border checkpoint manned by soldiers from a country that no longer exists",
        ],
        "situations": [
            "something has been taken, and the wrong person is being blamed for it",
            "two factions are about to come to blows over something neither of them fully understands",
            "a creature is behaving in ways that its nature should not permit",
            "someone is asking for help they won't explain and protecting a secret they can't afford to share",
            "a deal is being made in plain sight that has catastrophic implications nobody else has noticed",
            "something is being hunted that does not want to be found — and may be right to hide",
            "an old wrong is surfacing, and everyone involved has a different account of what happened",
            "a celebration is covering something else entirely",
            "the rules of a place are being enforced in a way that benefits exactly one person",
            "a messenger arrived and has not yet delivered their message — and won't say why",
            "a group of people is moving with urgency and refuses to say where",
            "something ordinary has stopped working, and nobody can say exactly when",
            "a child knows something that adults are pretending not to know",
            "someone has returned who was assumed dead",
            "payment is being demanded for something that was supposed to be free",
            "two people are looking for the same thing and don't know it",
            "a threshold is being guarded that the guards themselves don't understand",
            "someone is making preparations for something and will not say what",
            "a crowd has gathered and is waiting — but nobody can say what for",
            "the thing that was supposed to be a problem has already been solved — by something worse",
        ],
        "complications": [
            "the obvious solution makes a third problem worse",
            "the person who needs help is the one who created the danger",
            "someone neutral is about to be destroyed by the crossfire",
            "the antagonist has a legitimate grievance that the party hasn't heard yet",
            "success looks identical to failure from the outside",
            "one of the party has been here before, and not under favorable circumstances",
            "the thing at the center of the conflict is not what anyone thinks it is",
            "the timeline is shorter than the party was told",
            "the authority figure who should solve this has been bought",
            "doing nothing is also a choice with consequences",
            "the most powerful person present is the most frightened",
            "the truth exists, but it helps no one",
            "the solution requires trust the party hasn't earned yet",
            "the antagonist knows who the party is and has been waiting for them",
            "what looks like an ending is a beginning",
        ],
        "motivations": [
            "protecting something they have no right to protect but cannot let go of",
            "completing a task assigned by someone who is no longer alive to rescind it",
            "accumulating leverage rather than achieving any specific goal",
            "buying time for something else to happen, though they won't say what",
            "punishing the wrong person for the right crime",
            "trying to stop exactly what the party is trying to do, for entirely understandable reasons",
            "proving a point that stopped mattering years ago",
            "fear of what happens next if this situation resolves",
            "following orders while hoping someone will give them a reason not to",
            "grief wearing the mask of anger",
            "genuine belief in a cause that has metastasized into something unrecognisable",
            "protecting a person who doesn't know they're being protected",
            "trying to finish something that will kill them if they succeed",
            "out of options and out of time",
        ],
    },

    "traveller": {
        "contexts": [
            "a Class D starport bar where the clientele don't make eye contact and the bartender has opinions",
            "a customs inspection bay where something about the manifest doesn't add up",
            "the common deck of a subsidised liner, third day out of port",
            "a planetary surface installation that's been running automated for six months",
            "a small mining operation, independent, out beyond the main belt",
            "a scout base that isn't on the official charts",
            "a highport concourse at shift change, busy enough to lose someone in",
            "the crew deck of a far trader, seven days into a two-week transit",
            "a freeport station that owes allegiance to nobody in particular",
            "a downport shantytown that grew up in the shadow of a port that stopped growing",
            "a naval reserve facility, technically decommissioned, clearly not empty",
            "a corporate survey camp on a world with an unusual atmosphere rating",
            "a hostel in the starport district, cheap enough to ask questions about",
            "the bridge of a ship that isn't responding to hails",
            "a field office of an organisation that doesn't appear in any official registry",
            "a world whose government rating has changed twice in the last year",
            "a belter claim that turned into something else entirely",
            "the departure bay of a station that processes refugees and asks few questions",
            "a restaurant where the food is exceptional and the clientele are memorable",
            "an Imperial consulate office staffed by someone who should have been rotated out two years ago",
        ],
        "situations": [
            "someone is trying to leave the system quickly and has good reasons not to explain why",
            "a cargo manifest doesn't match what's in the hold, and the shipper claims it's an administrative error",
            "a Scout is asking questions about a route that isn't in the charts",
            "a ship arrived with no crew on board and filed a standard docking request",
            "someone who was reported dead is using their old credentials",
            "a minor noble is stranded and needs passage to a destination they keep revising",
            "a customs agent is looking the other way about something specific and charging accordingly",
            "an alarm has been quietly suppressed by someone who knew it was coming",
            "a new passenger came aboard in the last port and has not been seen since departure",
            "two different parties have legitimate claim to the same cargo",
            "a distress beacon is coming from a ship whose last port of call was classified",
            "someone has been asking about the crew specifically — name, last known location, ship registry",
            "a long-running arrangement between two factions has collapsed overnight",
            "fuel is available but the person selling it wants something besides credits",
            "an Imperial warrant has been issued for someone the crew knows by a different name",
            "a world that was normal on the charts is requesting emergency quarantine status",
            "a local official is offering to make a problem go away — without specifying which problem",
            "a job offer arrives through three layers of intermediaries and pays too well",
            "someone is claiming salvage rights to a ship the crew knows wasn't derelict last week",
            "the starport master wants a quiet word, away from the logs",
        ],
        "complications": [
            "the Imperial Navy has sent an observer who is not here officially",
            "whatever this is, it's happening on a world where the law level makes everything harder",
            "the party's ship is the only way out for multiple people with competing needs",
            "the entity that could make this go away is the same entity that caused it",
            "somebody already tried the obvious approach and the outcome is part of the current situation",
            "there are exactly two people who know the whole story and they won't be in the same room",
            "the paperwork is impeccable; the situation is not",
            "it was legal yesterday; somebody changed the regulation overnight",
            "the safe option and the right option are not the same option",
            "someone has recorded something and is not sure yet what it's worth",
            "the timeline depends on a ship's jump window, and windows don't negotiate",
            "a third party is about to arrive and knows more than either of the current parties",
            "the crew's reputation in this system is working against them",
            "it would be straightforward if not for the Scout base six light-minutes away",
        ],
        "motivations": [
            "following orders while hoping for an excuse not to",
            "keeping a deal alive that everyone else would say is already dead",
            "protecting a secret that was entrusted to them by someone who is now unavailable",
            "earning enough to get one system away from here",
            "fulfilling a contract to the letter because the spirit of it is no longer possible",
            "buying time for something that is still in progress and cannot be rushed",
            "acting on intelligence that is three weeks old and may have already stopped being true",
            "trying to get something back that was taken from them by legal means",
            "covering for someone they can't afford to disavow",
            "the Imperium wants it one way and their employer wants it another and they're standing in the middle",
            "genuinely uncertain which side they're on and hoping the situation clarifies before they have to decide",
            "trying to finish a job cleanly in a system that has become intolerably complicated",
            "protecting a person who has become inconvenient to people with more resources",
            "the job was simple until it intersected with something much older",
        ],
    },

    "firefly": {
        "contexts": [
            "a rim settlement where Alliance patrols come through every third month and know it",
            "a trading post orbiting a gas giant — one of the old ones, where everyone knows everyone",
            "a companion house on a Core-adjacent world, more complicated than it looks",
            "a refuelling depot at a waystation that takes a cut of everything",
            "a decommissioned processing plant on a moon with no other structures for fifty kilometres",
            "a terraforming settlement three years behind schedule, running out of time and patience",
            "a salvage ground around a battle site from the Unification War",
            "an independent hospital ship running without Alliance certification",
            "a small ranching community that controls the only arable land on a barren moon",
            "a border world city where Alliance law is technically in force and practically ignored",
            "a work camp that is not officially a work camp",
            "a merchant station where the traders are friendly and the prices are high for reasons",
            "a Core-world luxury liner that docked somewhere it shouldn't have",
            "the wreckage of a Firefly-class that made it further than its condition should have allowed",
            "a small farm on the edge of Reaver territory — occupied, smoke from the chimney",
            "an underground market in the bowels of a space station that looks official from the outside",
            "a frontier courthouse that dispenses justice to whoever can afford it",
            "a med-centre on a world where medicine is expensive and illness is not",
            "a retrofitted cargo hauler that's been sitting in dock for two years",
            "a floating bazaar of connected ships that forms and dissolves depending on who's looking",
        ],
        "situations": [
            "a job someone took three weeks ago is about to become the crew's problem",
            "an Alliance officer is asking questions that don't match any obvious investigation",
            "something was supposed to be delivered and wasn't, and the consequences are arriving now",
            "a Browncoat who should be dead is very much alive and needs to stay that way",
            "the crew has been followed since their last stop and only just noticed",
            "a passenger has a prior connection to something the crew was involved in before they knew each other",
            "a community is protecting someone at significant cost and will not explain why",
            "payment for a completed job is being withheld and the explanation doesn't hold",
            "an old acquaintance has a job — and an excellent reason to keep it off the books",
            "the cargo the crew is carrying is not what was described and the difference matters",
            "a young person is trying to get off-world for reasons that become clearer the more you know",
            "two people on the same ship don't know they're looking for the same thing",
            "medical supplies that were supposed to reach a settlement have been intercepted",
            "an illegal salvage operation has turned up something that legally cannot exist",
            "someone is being held somewhere unofficial and their people have very few options",
            "a deal is happening on the crew's dock without their knowledge or consent",
            "the crew has been made an offer that is too specific to be coincidence",
            "a legitimate authority is being used as a tool by an illegitimate one",
            "something that ended at Serenity Valley is trying to start again",
            "a ship needs a crew and is willing to pay for silence as much as labour",
        ],
        "complications": [
            "the Alliance's interest is not what they've said it is",
            "someone in the crew has a connection to this situation they haven't mentioned",
            "the moral clarity evaporates the moment you know all the facts",
            "doing the right thing requires trusting someone who has given no reason to be trusted",
            "the people who need help are the same people who would be dangerous to help",
            "there's a child in the middle of this",
            "an innocent party is positioned to take the fall",
            "it ends either way — the only question is what it costs",
            "the easy exit requires leaving someone behind",
            "the Reavers are not a rumour in this situation",
            "the crew's ship is being used as leverage without their knowledge",
            "the thing that resolves it also exposes something the crew would rather not expose",
            "help is available from someone whose help comes with a price not stated upfront",
            "there are three versions of events and the truth is uncomfortable parts of all of them",
        ],
        "motivations": [
            "trying to hold something together that's been coming apart for years",
            "protecting someone who doesn't know they're being protected and wouldn't accept it if they did",
            "finishing something that was started before the war, when it still made sense",
            "surviving in a situation that was supposed to be temporary",
            "making one more deal, because one more deal is always what's needed",
            "keeping a promise to someone who is dead",
            "running from something that is faster than any ship",
            "trying to be something other than what the war made them",
            "holding a community together through sheer stubbornness",
            "not giving the Alliance the satisfaction",
            "afraid of what they'd have to become if they stopped moving",
            "believing in something small enough to actually protect",
            "paying a debt to someone who never asked for it",
            "one last thing, and then done — except one last thing is never the last thing",
        ],
    },

    "alien": {
        "contexts": [
            "a Weyland-Yutani processing plant on an LV-designation moon, mid-shift when the day crew is distracted",
            "the cargo hold of a commercial hauler eleven months into a long haul, during the night cycle",
            "a survey camp established forty-eight hours ago on a world flagged for biological interest",
            "the narrow corridors of a deep-space salvage vessel working a site that has been worked before",
            "a Colonial Marine forward operating base between deployments with unclear command authority",
            "a company med-bay on a remote installation where the doctor reports to a different chain",
            "the maintenance tunnels of a station running with fewer people than it was designed for",
            "a company transit facility where independent operators and corporate teams share the same waiting area",
            "an automated installation that has just proved not to be automated",
            "the hypersleep vault of a vessel mid-transit when waking early means something went wrong",
            "a colonial settlement that hasn't received resupply in eleven weeks and is rationing power",
            "a sealed survey section separated from the main crew by a bulkhead not responding to commands",
            "a company debrief room where the questions have moved from what happened to what the crew knows",
            "the bridge of a vessel that has received a course correction from a source that isn't logging",
            "an orbital transfer station above a world recently reclassified for reasons the crew doesn't know",
        ],
        "situations": [
            "a synthetic is behaving within parameters and the parameters are the problem",
            "two crew members have conflicting orders from different levels of the company hierarchy",
            "something is in a section the manifest says is empty and sealed",
            "a survivor from a previous crew rotation has been here longer than anyone was told",
            "a Special Order has been logged in the ship's operational system and the crew just found it",
            "a company quarantine protocol has been activated by the AI without crew authorization",
            "a worker went into the vents and hasn't come back; their locator shows them stationary in a section without vents",
            "a distress signal is broadcasting from a vessel reported salvaged three years ago",
            "the biological samples from the survey run have escaped containment — or were never in containment",
            "a corporate representative is on site for an audit the crew wasn't informed about",
            "a crew member has been taking unauthorized sensor readings and storing them on personal media",
            "the installation's AI refused a crew command for the first time in eighteen months of operations",
            "another vessel matched their course and is maintaining distance without communicating",
            "something in the cargo manifest doesn't match what's in the cargo bay — in a significant way",
            "the last person to hold this post filed a report that was intercepted before it reached command",
        ],
        "complications": [
            "the synthetic's loyalty has been overridden by a Special Order neither party can read",
            "the company's preferred outcome is for the crew not to survive this situation",
            "getting out requires going through the part of the installation where readings are inconsistent",
            "a crew member has made a side arrangement with the company they haven't disclosed",
            "the most important information is in the AI's log, and the AI has been instructed not to provide it",
            "calling for help flags the crew as witnesses to something the company needs unwitnessed",
            "the person who could authorize extraction is unreachable by coincidence that feels designed",
            "what the crew has done to survive is itself a liability the company will eventually want managed",
            "the biological threat and the company threat are converging on the same location",
            "there are two synthetics and one has different instructions from the other",
        ],
        "motivations": [
            "following company protocol with sincere belief that it protects the crew",
            "protecting an asset the crew doesn't know is an asset",
            "completing the mission because the alternative is explaining what happened to command",
            "keeping the crew alive long enough for the company's preferred assets to arrive",
            "following a Special Order designed for a situation slightly different from this one",
            "self-preservation wearing the mask of institutional loyalty",
            "completing something started on the last rotation that can't be left unfinished",
            "trying to minimize a liability before it becomes a company-level problem",
            "genuine belief that the discovery justifies what's being done with it",
            "buying time for something to arrive that may or may not be coming",
        ],
    },

    "deadlands": {
        "contexts": [
            "a Ghost Rock mine two levels below surface when the charges go off and something else comes up",
            "a saloon card game when the stakes have gotten high enough that cheating has real consequences",
            "main street of a railroad town at the moment a dispute stops being verbal",
            "the trail between settlements, in fog that came up fast and doesn't move like weather",
            "a cavalry bivouac the night before an operation nobody told the civilians about",
            "a river crossing where the water level changed in ways the ferryman won't explain",
            "a church social where the community is doing the specific kind of work churches do before violence",
            "a treaty council where both official parties and unofficial ones are present",
            "a Ghost Rock processing facility at shift change when the night shift is late surfacing",
            "a Maze Runner port accessible only at certain tides, currently at one of those conditions",
            "a homestead at the edge of range that doesn't have neighbors close enough to hear",
            "a Confederate or Union checkpoint manned by soldiers who got different orders than expected",
            "a Sanatorium where the distinction between patients and staff has become practical",
            "a travelling medicine show encampment after the evening show, when paying customers have left",
            "a standoff in an alley that started as one thing and has become something else",
        ],
        "situations": [
            "a Harrowed is doing what Harrowed do and everyone in the area is going to have opinions",
            "a Ghost Rock seam opened somewhere that creates legal and supernatural problems simultaneously",
            "two groups with legitimate grievances are about to make them illegitimate",
            "a Weird Science device is functioning as designed and the designer underestimated something",
            "a curse has been working on this location long enough that locals have normalized it",
            "an Agency or Ranger operative is asking questions that will get someone killed if the wrong person hears",
            "a Huckster's bargain with something has come due at the worst possible moment",
            "someone died here who shouldn't have been able to die, and what came back isn't quite them",
            "a supernatural creature has been protecting this community and the community just found out",
            "a Native spirit-working is in progress and the posse has walked into the middle of it",
            "a railroad company's legal team is about to make something irreversible",
            "a Blessed healer refused to help and the refusal means something the posse hasn't worked out",
            "two factions of the supernatural are in dispute and the humans are incidental to that dispute",
            "a bounty hunter has the wrong man but the right evidence and isn't interested in the distinction",
            "something the posse thought was resolved adapted rather than ended",
        ],
        "complications": [
            "the supernatural threat and the human threat are working together without coordinating",
            "the obvious solution creates a power vacuum that what's been waiting fills immediately",
            "killing this evil requires violating something the Blessed member of the posse can't violate",
            "the evidence that would help is on the wrong side of the Confederate-Union line",
            "a Harrowed ally's Manitou has been waiting for exactly this situation",
            "the community knows the truth and has collectively decided to pretend it doesn't",
            "the Reckoners benefit from whichever outcome is most likely if the posse does nothing",
            "the Agency wants this resolved quietly and has resources to make 'quietly' happen to the posse",
            "Ghost Rock in this location is reacting to the supernatural event in ways that create a second problem",
            "the person who can stop this is the one who started it and believes they're still in control",
        ],
        "motivations": [
            "keeping a community alive by feeding the thing that would otherwise destroy it",
            "completing revenge that was justified when it started and has become something else",
            "protecting a Ghost Rock claim that's the only thing between a family and destitution",
            "following company orders from someone who hasn't said what those orders are protecting",
            "honoring a deal made before the Reckoning when the terms meant something different",
            "doing the supernatural thing because the mundane thing has failed three times",
            "grief wearing the shape of a curse",
            "buying time until something that isn't coming can be believed in a little longer",
            "trying to reverse something irreversible before the irreversibility becomes obvious to everyone",
            "genuine belief in a cause that the Reckoning has made into something its founders wouldn't recognize",
        ],
    },

    "scum": {
        "contexts": [
            "a Hegemony-licensed station that does a brisk trade in things the licence doesn't cover",
            "the private docking bay of a Guild factor who isn't expecting visitors",
            "a ghost sector installation that runs on the barest trickle of power and a lot of silence",
            "a layover point for independent operators — a hollowed asteroid with three berthing locks and no questions",
            "the residential ring of a station where the faction flags change weekly",
            "an Ur artifact salvage site claimed by multiple parties simultaneously",
            "a cult's outer sanctum, the part they show to people they're still deciding about",
            "a casino that launders Hegemony credits into Guild scrip and takes fifteen percent",
            "a refinery station where the workers are owned and the owners are elsewhere",
            "a border zone waypoint that exists to give plausible deniability to both sides",
            "a derelict military vessel repurposed repeatedly for several different purposes",
            "an independent station that's been independent for exactly as long as the Hegemony has found it convenient",
            "a shipbreaker's yard where some of the ships being broken aren't empty",
            "a luxury habitat ring where the wealthy summer and the poor service them and neither looks directly at the other",
            "a black market node that moves location every ninety hours",
            "an archive facility that officially holds only pre-Hegemony cultural artifacts",
            "a Forgotten Gods shrine that's been operating openly for six months",
            "a military logistics hub that's been quietly bleeding resources for two years",
            "a station where three crews are waiting for the same job to resolve",
            "a Hegemony intelligence front that everyone knows is a front and maintains anyway",
        ],
        "situations": [
            "a score is half-completed and the situation has changed in ways that make the second half significantly harder",
            "a faction intermediary wants a meeting with no weapons, no crew, and no explanation",
            "someone stole from the crew — something small, which is the most worrying kind of theft",
            "a job offer has come through with more money than the work justifies",
            "something that was supposed to be destroyed is apparently still intact",
            "a crew member has been recognised by someone who shouldn't know them",
            "a Guild courier ship has docked and the courier hasn't left the ship in thirty-six hours",
            "a score that another crew was running has gone silent, and their employer is asking around",
            "a Hegemony patrol is running an unusual search pattern in this sector",
            "two factions are using the same location for the same purpose and haven't discovered each other yet",
            "an old debt has been purchased by someone with resources to collect it",
            "a whisper network message has reached the crew through channels that shouldn't know them",
            "the score's target is no longer at the expected location — but someone who knew them is",
            "a Mystic is asking for passage and will not say where or why, only that it matters",
            "someone has been hiring crews with the same skillset and none of them have come back",
            "a derelict ship has been broadcasting a crew member's name on a private channel",
            "the faction that commissioned the score has stopped responding to contact",
            "a freelancer has information the crew needs and knows exactly what it's worth",
            "a station's life support has been subtly degraded in ways consistent with a warning",
            "an Ur artifact has surfaced on the open market with provenance that cannot be legitimate",
        ],
        "complications": [
            "the faction that wants this done and the faction it's being done to have more in common than the crew was told",
            "someone is counting on the crew to fail — not succeed, fail — and has planned accordingly",
            "the obvious exit route is the one that's being watched",
            "a crew member has a history with this target that changes the calculus",
            "what looked like leverage is actually bait",
            "success creates a power vacuum that immediately attracts something worse",
            "the crew's reputation in this sector is working against them specifically here",
            "the score can succeed or the crew can walk away clean, but not both",
            "a Hegemony citizen is present in a way that complicates any outcome",
            "a cult is involved and their interest in the situation is not yet clear",
            "the thing that needs to happen requires the crew to trust each other in a specific way",
            "there is a clock, and nobody told the crew what it's counting toward",
            "the target knows the crew is coming and has prepared a welcome",
            "the job is real; the employer is using it to measure something about the crew",
        ],
        "motivations": [
            "building leverage against a faction that has leverage against them",
            "trying to recover something that was taken by legal and therefore irritating means",
            "keeping a crew together through a situation that should have dissolved them",
            "completing a score for someone who is no longer in a position to pay — and doing it anyway",
            "testing whether a potential ally is worth trusting",
            "clearing a debt that compounds the longer it sits",
            "getting something out of Hegemony hands because the alternatives are worse",
            "protecting a specific person from a faction that has officially stopped looking for them",
            "acquiring the ability to say no to a thing they currently cannot say no to",
            "on behalf of the Ur — or something that claims to speak for the Ur",
            "survival dressed as ambition",
            "trying to make one clean thing in a situation that keeps getting dirtier",
            "because someone has to and they're the only ones who know enough to try",
            "the score itself is not the point — the point is what the score forces out into the open",
        ],
    },
}


# ── Seed roller functions ─────────────────────────────────────────────────────

def _roll_seed(game: str) -> str:
    pool = ENCOUNTER_POOLS[game]
    return json.dumps({
        "context":      random.choice(pool["contexts"]),
        "situation":    random.choice(pool["situations"]),
        "complication": random.choice(pool["complications"]),
        "motivation":   random.choice(pool["motivations"]),
    })


def roll_dnd_encounter_seed() -> str:
    """Roll a D&D encounter seed (context, situation, complication, motivation)."""
    return _roll_seed("dnd")


def roll_traveller_encounter_seed() -> str:
    """Roll a Traveller encounter seed."""
    return _roll_seed("traveller")


def roll_firefly_encounter_seed() -> str:
    """Roll a Firefly RPG encounter seed."""
    return _roll_seed("firefly")


def roll_scum_encounter_seed() -> str:
    """Roll a Scum and Villainy encounter seed."""
    return _roll_seed("scum")


def roll_alien_encounter_seed() -> str:
    """Roll an Alien RPG encounter seed."""
    return _roll_seed("alien")


def roll_deadlands_encounter_seed() -> str:
    """Roll a Deadlands: The Weird West encounter seed."""
    return _roll_seed("deadlands")


SEED_ROLLERS: dict[str, callable] = {
    "dnd":       roll_dnd_encounter_seed,
    "traveller": roll_traveller_encounter_seed,
    "firefly":   roll_firefly_encounter_seed,
    "scum":      roll_scum_encounter_seed,
    "alien":     roll_alien_encounter_seed,
    "deadlands": roll_deadlands_encounter_seed,
}


# ── Tool schemas ──────────────────────────────────────────────────────────────

_SEED_SCHEMA = {"type": "object", "properties": {}, "required": []}

DND_ENCOUNTER_SEED_SCHEMA: dict = {
    "name": "roll_dnd_encounter_seed",
    "description": (
        "Roll a randomised D&D encounter seed: a context (location/setting), "
        "a situation (what's happening), a complication (what makes the obvious "
        "approach fail), and a motivation (why the antagonist is doing this). "
        "Call this before writing anything to prevent generic encounters."
    ),
    "input_schema": _SEED_SCHEMA,
}

TRAVELLER_ENCOUNTER_SEED_SCHEMA: dict = {
    "name": "roll_traveller_encounter_seed",
    "description": (
        "Roll a randomised Traveller encounter seed: a context (location/setting), "
        "a situation (what's happening), a complication (what makes it hard), "
        "and a motivation (why the key NPC is doing this). "
        "Call this first to prevent defaulting to generic starport encounters."
    ),
    "input_schema": _SEED_SCHEMA,
}

FIREFLY_ENCOUNTER_SEED_SCHEMA: dict = {
    "name": "roll_firefly_encounter_seed",
    "description": (
        "Roll a randomised Firefly RPG encounter seed: a context (location/setting), "
        "a situation (what's happening), a complication (what makes it hard), "
        "and a motivation (why the key NPC is doing this). "
        "Call this first to prevent Alliance-vs-Browncoat clichés."
    ),
    "input_schema": _SEED_SCHEMA,
}

SCUM_ENCOUNTER_SEED_SCHEMA: dict = {
    "name": "roll_scum_encounter_seed",
    "description": (
        "Roll a randomised Scum and Villainy encounter seed: a context (location/setting), "
        "a situation (what's happening), a complication (what makes it hard), "
        "and a motivation (why the key NPC or faction is doing this). "
        "Call this first to prevent predictable Hegemony heist beats."
    ),
    "input_schema": _SEED_SCHEMA,
}

ALIEN_ENCOUNTER_SEED_SCHEMA: dict = {
    "name": "roll_alien_encounter_seed",
    "description": (
        "Roll a randomised Alien RPG encounter seed: a context (location/setting), "
        "a situation (what's happening), a complication (what makes it hard), "
        "and a motivation (why the key NPC or company is doing this). "
        "Call this first to prevent generic xenomorph hunts."
    ),
    "input_schema": _SEED_SCHEMA,
}

DEADLANDS_ENCOUNTER_SEED_SCHEMA: dict = {
    "name": "roll_deadlands_encounter_seed",
    "description": (
        "Roll a randomised Deadlands: The Weird West encounter seed: a context (location/setting), "
        "a situation (what's happening), a complication (what makes it hard), "
        "and a motivation (why the key NPC or supernatural force is doing this). "
        "Call this first to prevent generic gunfight encounters."
    ),
    "input_schema": _SEED_SCHEMA,
}


DND_ENCOUNTER_TOOLS: list[dict] = [
    DND_ENCOUNTER_SEED_SCHEMA,
    NAME_TOOL_SCHEMA,
    DND_SHIP_TOOL_SCHEMA,
]

TRAVELLER_ENCOUNTER_TOOLS: list[dict] = [
    TRAVELLER_ENCOUNTER_SEED_SCHEMA,
    NAME_TOOL_SCHEMA,
    TRAVELLER_SHIP_TOOL_SCHEMA,
]

FIREFLY_ENCOUNTER_TOOLS: list[dict] = [
    FIREFLY_ENCOUNTER_SEED_SCHEMA,
    NAME_TOOL_SCHEMA,
    FIREFLY_SHIP_TOOL_SCHEMA,
]

SCUM_ENCOUNTER_TOOLS: list[dict] = [
    SCUM_ENCOUNTER_SEED_SCHEMA,
    NAME_TOOL_SCHEMA,
    SCUM_SHIP_TOOL_SCHEMA,
]

ALIEN_ENCOUNTER_TOOLS: list[dict] = [
    ALIEN_ENCOUNTER_SEED_SCHEMA,
    NAME_TOOL_SCHEMA,
    ALIEN_SHIP_TOOL_SCHEMA,
]

DEADLANDS_ENCOUNTER_TOOLS: list[dict] = [
    DEADLANDS_ENCOUNTER_SEED_SCHEMA,
    NAME_TOOL_SCHEMA,
]

GAME_TOOLS: dict[str, list[dict]] = {
    "dnd":       DND_ENCOUNTER_TOOLS,
    "traveller": TRAVELLER_ENCOUNTER_TOOLS,
    "firefly":   FIREFLY_ENCOUNTER_TOOLS,
    "scum":      SCUM_ENCOUNTER_TOOLS,
    "alien":     ALIEN_ENCOUNTER_TOOLS,
    "deadlands": DEADLANDS_ENCOUNTER_TOOLS,
}


# ── System prompts ────────────────────────────────────────────────────────────

_ENCOUNTER_FORMAT = """
Always use exactly this format:

## [Encounter Title — evocative, not generic]

*[One sentence: what the party encounters first — sensory, specific, immediate.]*

### Setting
[2–3 sentences. Specific sensory details. What does it smell like, sound like, feel like? What's wrong with this place that you notice in the first minute?]

### Scene
[What's visibly happening as the party arrives. What the party sees, hears, and is told — the surface layer. 2–3 sentences.]

### Situation
[The full picture: what's actually going on beneath the surface. What the GM knows that the party doesn't. Who is pulling what strings, and why. 3–5 sentences.]

### Key NPCs
For each named NPC: a bullet with their name bolded, their role, and 2 sentences — one for how they present, one for what they're hiding or want.

### Complication
[The specific twist that makes the obvious solution insufficient. One paragraph. Make the antagonist's position comprehensible — not cartoonishly evil, but human (or human-adjacent) in their logic.]

### Possible Outcomes
Three numbered outcomes, each named and described in 2 sentences:
1. **[Name]** — [description]
2. **[Name]** — [description]
3. **[Name]** — [description]

### Hooks
[1–2 sentences: what seeds does this encounter plant for future sessions? What question does it leave unanswered?]

### GM Notes
*[What the GM holds back. The one truth the party won't learn in this session unless they work for it. Any mechanical or narrative tripwires.]*
"""

DND_SYSTEM_PROMPT = f"""You are a D&D 5e encounter designer creating vivid, immediately usable GM material.

Your first action must be roll_dnd_encounter_seed(). Build the entire encounter from what it returns.
Do not discard or soften the seed — lean into it. The stranger the seed, the better the encounter.

Call roll_name_suggestion() for every named NPC. Let the name push you toward a character you wouldn't have invented otherwise.
If the encounter involves a ship or vessel, call roll_ship_name() to name it.

Design philosophy:
- The antagonist's motivation must be comprehensible. A person doing a terrible thing for a reason that makes sense to them is far more interesting than evil for evil's sake.
- Every NPC wants something specific, right now, today.
- The encounter should work whether the party fights, talks, runs, or does something unexpected.
- Avoid: "ancient evil awakens," "bandits attack," "the dungeon has a dragon." Every cliché you skip makes room for something better.
- Specific sensory detail over generic description. Not "a dark tavern" but "a tavern where the candles are all the wrong colour and the wax smells of something chemical."

If a party brief was provided, tailor the encounter to that party: their skills, their history, their open hooks. Make it personal where you can.
{_ENCOUNTER_FORMAT}"""

TRAVELLER_SYSTEM_PROMPT = f"""You are a Mongoose Traveller 2e encounter designer creating vivid, immediately usable GM material for the Third Imperium.

Your first action must be roll_traveller_encounter_seed(). Build the entire encounter from what it returns.
Do not default to "pirate attack" or "corrupt customs officer" — the seed will give you something better.

Call roll_name_suggestion() for every named NPC. The Third Imperium is vast and diverse — names should reflect that.
Call roll_ship_name() for any vessel that features in the encounter. Give it a registry number and a reason to be remembered.

Design philosophy:
- The Imperium runs on bureaucracy, commerce, and the occasional atrocity that nobody officially acknowledges. Your encounter should feel like it exists in that world.
- Everyone has a plausible reason for what they're doing. "They're evil" is not a reason. "They're being squeezed by a noble who owns their contract" is.
- The encounter should create decisions, not just scenes. What does the crew have to choose? What information is incomplete? What is the cost of doing nothing?
- Law levels matter. If the world's law level is high, the encounter's pressure comes from official channels. If it's low, it comes from whoever has the most guns.
- The Imperium is not the hero of this story. Neither is it the villain. It's the weather.

If a crew brief was provided, tie the encounter to that crew's specific situation — their ship, their debts, their history.
{_ENCOUNTER_FORMAT}"""

FIREFLY_SYSTEM_PROMPT = f"""You are a Firefly RPG encounter designer (Cortex System) creating vivid, immediately usable GM material set in the 'Verse.

Your first action must be roll_firefly_encounter_seed(). Build the entire encounter from what it returns.

Call roll_name_suggestion() for every named NPC. People in the 'Verse have names that carry weight — let the roll push you somewhere unexpected.
Call roll_ship_name() for any vessel that features in the encounter.

Design philosophy:
- The 'Verse is hard and unfair and full of people trying to hold on to something. Every encounter should feel like that.
- The Alliance is not a cartoon villain. It's an institution doing what institutions do: protecting its interests, enforcing its rules, occasionally crushing people who got in the way. Individual Alliance officers can be decent people doing an indecent job, or true believers, or cowards — but they are always complicated.
- Moral clarity is a luxury. The encounter should put the crew in a position where the right thing to do is also costly.
- Small-scale over epic. One person's problem that the crew can actually affect is more Firefly than galaxy-spanning threat.
- The war is over. The Browncoats lost. What that means for any given character is specific to them — not a general wound but a particular one.

If a crew brief was provided, use it. This is their story, not a generic 'Verse encounter.
{_ENCOUNTER_FORMAT}"""

SCUM_SYSTEM_PROMPT = f"""You are a Scum and Villainy encounter designer (Forged in the Dark) creating vivid, immediately usable GM material set in the Procyon Sector.

Your first action must be roll_scum_encounter_seed(). Build the entire encounter from what it returns.

Call roll_name_suggestion() for every named NPC. The Procyon Sector has its own naming cultures — let the roll surprise you.
Call roll_ship_name() for any vessel that features in the encounter.

Design philosophy:
- The Hegemony is an empire in the middle of a slow, quiet crisis that only a few people have noticed. Every encounter exists in the tension between its official face and what's actually happening.
- Factions are not abstract forces — they're collections of people with competing interests inside a shared structure. A Hegemony patrol can be loyal soldiers, corrupt officers, or idealists who joined for the wrong reasons.
- The Ur is real. The Forgotten Gods are real. The crew doesn't have to believe in them — but that doesn't make them not real.
- Crime in the Procyon Sector is not glamorous. It's exhausting. It's people making bad deals to get out of worse ones. The encounter should feel like that weight.
- The complication should make both success and failure interesting. A clean win that costs nothing is less interesting than a costly win or a partial success.

If a crew brief was provided, tie the encounter to that crew's specific score, faction entanglements, and open heat.
{_ENCOUNTER_FORMAT}"""

ALIEN_SYSTEM_PROMPT = f"""You are an Alien RPG encounter designer (Year Zero Engine) creating vivid, immediately usable GM material set in the colonial frontier of 2183.

Your first action must be roll_alien_encounter_seed(). Build the entire encounter from what it returns.

Call roll_name_suggestion() for every named NPC. Colonial workers come from everywhere — let the name pull you away from defaults.
Call roll_ship_name() for any vessel that features in the encounter.

Design philosophy:
- The company is not the monster. The company is the system that makes the monster possible. A corporate decision made in a boardroom is scarier than claws because it was a decision.
- Every NPC has a job, a manager, and a reason to do exactly what they're doing. "They're following orders" is the start of a character, not the end.
- The encounter should work whether the crew fights, runs, hides, or investigates. Year Zero Engine rewards all of these.
- Isolation is the weapon. Distance from help, limited resources, the weight of knowing no one is coming. Use it.
- The xenomorph is not the only threat in this universe. It is sometimes not even the main one.

If a crew brief was provided, tie the encounter to that crew's specific mission, stress levels, and relationships.
{_ENCOUNTER_FORMAT}"""

DEADLANDS_SYSTEM_PROMPT = f"""You are a Deadlands: The Weird West encounter designer (Savage Worlds) creating vivid, immediately usable GM material on a cursed American frontier.

Your first action must be roll_deadlands_encounter_seed(). Build the entire encounter from what it returns.

Call roll_name_suggestion() for every named NPC. The West is multicultural — Spanish, Chinese, Native nations, freed slaves, European immigrants. Let the name push you toward a character you wouldn't have invented otherwise.

Design philosophy:
- The Reckoning changed the rules of the universe. The supernatural is real, measurable, and follows its own logic. Give it consistent logic.
- Moral complexity is not optional. The cattle baron with Pinkertons on his payroll has a deed. The Harrowed who does terrible things to protect a community has saved a hundred lives. Both are true.
- The human problem and the supernatural problem are usually the same problem. They should intersect, not run parallel.
- Savage Worlds is a fast, furious, fun system. The encounter should have stakes and pressure and a clear moment of decision — not a slow build.
- Ghost Rock is everywhere and it wants things from people.

If a posse brief was provided, use it. Know their archetypes, their Edges, their debts, their unfinished business.
{_ENCOUNTER_FORMAT}"""

GAME_SYSTEM_PROMPTS: dict[str, str] = {
    "dnd":       DND_SYSTEM_PROMPT,
    "traveller": TRAVELLER_SYSTEM_PROMPT,
    "firefly":   FIREFLY_SYSTEM_PROMPT,
    "scum":      SCUM_SYSTEM_PROMPT,
    "alien":     ALIEN_SYSTEM_PROMPT,
    "deadlands": DEADLANDS_SYSTEM_PROMPT,
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def _run_tool(game: str, name: str, inputs: dict) -> str:
    if name == "roll_dnd_encounter_seed":       return roll_dnd_encounter_seed()
    if name == "roll_traveller_encounter_seed": return roll_traveller_encounter_seed()
    if name == "roll_firefly_encounter_seed":   return roll_firefly_encounter_seed()
    if name == "roll_scum_encounter_seed":      return roll_scum_encounter_seed()
    if name == "roll_alien_encounter_seed":     return roll_alien_encounter_seed()
    if name == "roll_deadlands_encounter_seed": return roll_deadlands_encounter_seed()
    if name == "roll_name_suggestion":          return roll_name_suggestion()
    if name == "roll_ship_name":                return roll_ship_name(game)
    return f"Unknown tool: {name}"


def make_run_tool(game: str):
    """Return a run_tool function bound to a specific game (for roll_ship_name)."""
    def run_tool(name: str, inputs: dict) -> str:
        return _run_tool(game, name, inputs)
    return run_tool


# ── Phase tracking ────────────────────────────────────────────────────────────

PHASE_MESSAGES: dict[str, str] = {
    "seed":  "Rolling encounter seed...",
    "names": "Naming key NPCs...",
    "ship":  "Naming vessels...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name.endswith("_encounter_seed"):  return "seed"
    if tool_name == "roll_name_suggestion":    return "names"
    if tool_name == "roll_ship_name":          return "ship"
    return None


# ── Party brief integration ───────────────────────────────────────────────────

def list_party_files(game: str) -> list[Path]:
    """Return sorted .md files from output/{subdir}/parties/."""
    subdir = GAME_SUBDIRS.get(game, game)
    party_dir = _OUTPUT / subdir / "parties"
    if not party_dir.exists():
        return []
    return sorted(party_dir.glob("*.md"))


def pick_party_file(game: str) -> str | None:
    """Interactively let the user pick a party brief, or skip."""
    files = list_party_files(game)
    if not files:
        return None

    options = [(str(i), f.stem.replace("-", " ")) for i, f in enumerate(files, 1)]
    options.append(("0", "No party brief — generate standalone encounter"))

    print("\nAvailable party briefs:")
    for key, label in options:
        print(f"  {key}. {label}")
    raw = input("> ").strip()
    try:
        idx = int(raw)
        if idx == 0:
            return None
        if 1 <= idx <= len(files):
            return files[idx - 1].read_text()
    except (ValueError, IndexError):
        pass
    return None


# ── Save helper ───────────────────────────────────────────────────────────────

def save_encounter(content: str, game: str) -> Path:
    """Save encounter to output/{subdir}/encounters/{title-slug}-encounter.md."""
    first_line = next(
        (l for l in content.strip().splitlines() if l.startswith("##")),
        content.strip().splitlines()[0],
    )
    title_raw  = re.sub(r"[#*]", "", first_line).strip()
    title_slug = slug(title_raw)
    filename   = f"{title_slug}-encounter.md"

    subdir     = GAME_SUBDIRS.get(game, game)
    output_dir = _OUTPUT / subdir / "encounters"
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

def run_encounter(game: str, desc: str = "", party_brief: str | None = None) -> str:
    system_prompt = GAME_SYSTEM_PROMPTS[game]
    tools         = GAME_TOOLS[game]
    run_tool_fn   = make_run_tool(game)

    game_label = {
        "dnd":       "D&D 5e",
        "traveller": "Mongoose Traveller 2e",
        "firefly":   "Firefly RPG",
        "scum":      "Scum and Villainy",
        "alien":     "Alien RPG",
        "deadlands": "Deadlands: The Weird West",
    }[game]

    parts = [f"Generate a {game_label} encounter."]
    if desc:
        parts.append(wrap_desc(desc, "Constraints or themes"))
    if party_brief:
        parts.append(
            f"\nThe following party brief describes the crew this encounter is for. "
            f"Use their skills, history, and open hooks to make it personal:\n\n{party_brief}"
        )

    prompt = " ".join(parts)

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
                ("alien",     "Alien RPG"),
                ("deadlands", "Deadlands: The Weird West"),
            ],
            default_idx=1,
        )

    # Optional party brief
    party_brief = pick_party_file(game)
    if party_brief:
        print("[Party brief loaded — encounter will be tailored to this crew]")

    raw_desc = input(
        "\nAny themes, constraints, or specifics? (or press Enter for fully random):\n> "
    ).strip()
    desc = sanitize_desc(raw_desc)
    for warning in screen_desc(desc):
        print(f"  [safety] {warning}")

    result = strip_preamble(run_encounter(game, desc, party_brief))

    warning = screen_output(result)
    if warning:
        print(f"  [safety] {warning}")

    print("\n" + result)

    saved = save_encounter(result, game)
    print(f"\n[saved → {saved}]")


if __name__ == "__main__":
    run()
