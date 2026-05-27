"""
Location Generator — all four RPG game systems.

Creates vivid, GM-ready location profiles: atmosphere, notable NPCs,
complication, hooks, and GM notes. Four seed elements per game (type,
condition, complication, hook) prevent the model from defaulting to
generic taverns or plain starports.

Optionally incorporated into rumor and event generation.

Saves to output/{game_subdir}/locations/.

Run with: python location_agent.py
"""

import json
import random
import re
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.names import roll_name_suggestion, NAME_TOOL_SCHEMA
from lib.ships import roll_ship_name, TRAVELLER_SHIP_TOOL_SCHEMA, FIREFLY_SHIP_TOOL_SCHEMA, SCUM_SHIP_TOOL_SCHEMA, ALIEN_SHIP_TOOL_SCHEMA
from lib.utils import get_client, run_agent_loop, slug, pick
from lib.safety import sanitize_desc, screen_desc, wrap_desc, screen_output


# ── Output path ───────────────────────────────────────────────────────────────

_OUTPUT = Path(__file__).parent.parent / "output"

GAME_SUBDIRS: dict[str, str] = {
    "dnd":       "dnd",
    "traveller": "traveller",
    "firefly":   "firefly",
    "scum":      "scum_villainy",
    "alien":     "alien",
    "deadlands": "deadlands",
}


# ── Seed pools ────────────────────────────────────────────────────────────────

LOCATION_POOLS: dict[str, dict[str, list[str]]] = {

    "dnd": {
        "types": [
            "A roadside inn at a crossroads, three days from the nearest city",
            "A market town built around a collapsed ruin nobody talks about",
            "A fishing village on a coast that's been getting stranger at night",
            "A fortified waystation at the edge of civilised territory",
            "A thieves' guild front operating as a legitimate merchant house",
            "A temple complex that's been neutral ground for longer than anyone remembers",
            "A mining camp that struck something it wasn't supposed to",
            "A noble estate in quiet decline, staff diminishing, family fractious",
            "A halfling shire that's been closed to outsiders for a season",
            "A city district controlled by a single powerful guild",
            "A plague village that was quarantined and then quietly forgotten",
            "A wizard's tower accepting students for reasons nobody can quite explain",
            "A dwarven trading post far from the nearest hold",
            "A border fort that's been undermanned for years",
            "A druid grove that humans and elves have historically avoided",
            "A river crossing controlled by a toll collector with a small private army",
            "A market town hosting a regional fair this week, twice the usual strangers",
            "An old battlefield where the dead were never properly buried",
            "A monastery at a mountain pass, quietly involved in more than prayer",
            "A city slum where every business is a front for something else",
        ],
        "conditions": [
            "Festival season — crowded, loud, and everyone's guard is down",
            "The mayor died three days ago and nobody's been told who inherits",
            "A cold snap has driven everyone indoors and shortened tempers",
            "Two factions are in a cold dispute that could turn hot at any moment",
            "An outsider arrived a week ago and changed something, subtly",
            "Short on food — the last supply run didn't come back",
            "Unusually prosperous, which is making the neighbours nervous",
            "A rumour has spread that's not quite true but has people acting as if it is",
            "Under watch — soldiers passing through, asking questions",
            "Recently rebuilt after a fire that may not have been accidental",
            "A long-standing agreement has just expired and nobody knows what comes next",
            "The usual authority figure is absent and their deputy is making poor decisions",
            "Something valuable was found nearby and everyone has an opinion about who owns it",
            "A wedding or succession is pending and the factions are already maneuvering",
            "Quieter than it should be — something the locals all know and won't say",
            "A stranger with money has been buying goodwill and nobody knows why",
            "Three unrelated people have gone missing in the past month",
            "A long-closed establishment just reopened under new management",
            "Supply of one essential good has dried up and the explanations conflict",
            "An old debt is coming due and the debtor is out of options",
        ],
        "complications": [
            "The innkeeper knows something incriminating about someone the party needs",
            "Two locals are claiming the same thing and both have documentation",
            "The person in authority is being blackmailed",
            "A recent arrival is not who they claim to be — but neither is a long-standing resident",
            "The obvious solution to a problem here would create a worse problem elsewhere",
            "Someone the party met elsewhere has a connection to this place",
            "The thing everyone here fears is real — but not in the way they think",
            "The faction with legitimate claim to authority is less competent than the one without",
            "A secret that everyone locally knows but would never tell an outsider",
            "Resources that look available are actually spoken for — and the speaker has teeth",
            "The helpful person is helpful for a reason that benefits them",
            "What looks like a two-party conflict has a third party profiting from the middle",
            "The local law is technically on the wrong side of this",
            "Something the party did (or that happened before they arrived) has already changed things",
            "The right thing to do here and the legal thing to do are not the same",
            "The most powerful person here got their power through a deal they regret",
            "Evidence of something serious has been suppressed by someone respectable",
            "Two people with conflicting stories are both telling the truth",
            "The safest route out of this location goes through someone dangerous",
            "An old wrong is the foundation of the current peace, and someone wants to dig it up",
        ],
        "hooks": [
            "Someone approaches the party before they've asked a single question",
            "A job board notice that's been up too long",
            "An overheard conversation that was clearly meant to be heard",
            "A local who won't make eye contact with anyone except one party member",
            "Something is for sale that shouldn't be available here",
            "A child asks for help with something the adults won't touch",
            "A fight breaks out that the party is now somehow in the middle of",
            "Someone from the party's past is here, or knows someone from their past",
            "The party is recognised — correctly or incorrectly",
            "A body, found in a place that makes no sense",
            "The locals are preparing for something and won't say what",
            "An offer of hospitality that comes with invisible strings",
            "A locked door in a public building that nobody will explain",
            "A message waiting for one of the party members",
            "A merchant selling something that should be impossible to have this far from its origin",
        ],
    },

    "traveller": {
        "types": [
            "A Class C starport on a marginally habitable world — minimal facilities, maximum desperation",
            "A free trader hub station in a backwater system, nominally independent",
            "An Imperial naval base on a system nobody strategic would want",
            "A megacorporation extraction facility on a resource-rich but life-hostile world",
            "A gas giant skimming station staffed by contract workers on year-long rotations",
            "A Scout base officially decommissioned but clearly still in use",
            "A belt mining cooperative with a disputed claim and a crowded arbitration backlog",
            "A downport district in a high-population, low-law-level world — controlled chaos",
            "An orbital transfer station between two systems that don't entirely trust each other",
            "A frontier agricultural world with exactly one landing pad and no customs officer",
            "A medical research station on a quarantine-flagged world",
            "A privately owned system — one noble family, all the real estate",
            "A retired warship converted to a permanent habitat for the crew that couldn't afford to leave",
            "A jump-point waystation with inflated prices and no competition",
            "A Class A starport that lost its rating three years ago and is trying not to show it",
            "A free port operating at the edge of Imperial reach, conveniently ambiguous jurisdiction",
            "An independent merchant station that technically owes allegiance to three different powers",
            "A Zhodani cultural enclave in Imperial space — neutral by long treaty, watched by both sides",
            "A derelict station reoccupied by squatters who've made it functional but not comfortable",
            "A high-law-level world with a starport that enforces the law right up to the landing ramp",
        ],
        "conditions": [
            "A recent customs crackdown has every captain watching their manifests",
            "A megacorporation acquisition just closed — half the staff don't know if they still have jobs",
            "Ship traffic has dropped 30% in two months and nobody's explaining why",
            "Imperial auditors are on-station and everyone is being cooperative in a specific way",
            "A labour dispute is in its fourth week and the essential services are getting tense",
            "A recent accident killed three — the investigation is ongoing and inconvenient",
            "A local festival has the docking bays at capacity and tempers running short",
            "Fuel is available but someone's been cornering the supply and the price shows it",
            "Two noble houses are both claiming the same berthing priority",
            "A ship that should have jumped out three days ago is still here, not answering comms",
            "The station master is being replaced and incoming and outgoing both want different things",
            "A quarantine flag on an incoming ship has medical watching every airlock",
            "Power rationing — non-essential systems on eight-hour cycles",
            "The local currency just moved against the Credit and the traders are recalculating",
            "Someone important was supposed to arrive and didn't — no explanation given",
            "A Scout courier came through yesterday and left very quickly, which is unusual",
            "New regulations effective last week that nobody has fully read yet",
            "A ship was impounded for non-payment and the auction is tomorrow",
            "Three separate captains are all looking for the same crew member",
            "The berthing fees were raised without notice and the explanation is unsatisfying",
        ],
        "complications": [
            "The cargo the party needs is impounded pending a dispute that predates their arrival",
            "The person with authority to help them is the same person they need to avoid",
            "A legitimate transaction requires documentation they don't have and can't get quickly",
            "Two different people claim to represent the same organisation with conflicting instructions",
            "The starport authority's systems are down and everything is running on paper",
            "Something in the party's cargo or passenger list has flagged a soft alert",
            "The next jump point is the only exit and it's controlled by someone with opinions",
            "Local law level means something the party considers routine is technically a violation",
            "A ship the party has history with is also docked here",
            "The person they're meeting is being watched — and probably knows it",
            "What looked like a routine port call has put them in the middle of something local",
            "The berthing fees have gone up significantly since their last visit",
            "Someone is asking questions about the party's last port of call",
            "The parts they need are available from exactly one supplier who has exactly one price",
            "A crew member or passenger has a reason to not want to be seen here",
            "The patron who hired them is also here, which wasn't in the brief",
            "A shipment the crew agreed to carry has changed nature since they agreed",
            "The ship's transponder has triggered something in the local database",
            "Two factions both want to use the crew for the same job without the other knowing",
            "What was cheap last time is now restricted, and the restriction just started",
        ],
        "hooks": [
            "An overheard conversation in the port bar about a ship that didn't make it",
            "A job posting on the crew board that pays too well for what it asks",
            "A stranger needs a berth to a system that's slightly out of their way",
            "Another crew warns them off the job they're considering",
            "A local official makes a request that sits just outside normal procedure",
            "A cargo lot is being auctioned because the original shipper's account was closed",
            "A message is waiting for the ship that nobody on the crew sent",
            "A traveller with a ticket to their next destination and a story that doesn't add up",
            "An offer of crew work from someone who didn't ask about qualifications",
            "Someone at the bar recognises the ship's name but won't say how",
            "A distress beacon coming from the direction they're headed",
            "A ship is for sale that sold recently — and the previous owner isn't around to ask",
            "A Scout asks for a private conversation, which scouts don't usually do",
            "A passenger tries to rebook to a different destination after boarding",
            "The dock inspector's questions go slightly beyond what dock inspectors normally ask",
        ],
    },

    "firefly": {
        "types": [
            "A Rim world settlement of a few hundred people, two days from the nearest Alliance presence",
            "A border moon agricultural community — everyone knows everyone and Alliance doesn't come often",
            "An independent space station operating in the legal grey between jurisdictions",
            "A derelict Alliance transport recovered and converted into a trading post",
            "A Core world transit hub — efficient, surveilled, uncomfortable for people with something to hide",
            "A black market distribution point operating behind a legitimate salvage yard front",
            "A terraforming failure world — livable but wrong, colonised by people with nowhere else to go",
            "A wave relay station staffed by two people and very far from anything",
            "A floating casino registered in a jurisdiction that doesn't ask questions",
            "A former battle site world — the hulks were salvaged years ago but the stories stayed",
            "A mining cooperative on an airless moon — company store, company law",
            "A border world town built around a single business that isn't doing as well as it was",
            "A preacher's settlement — self-sufficient, suspicious of outsiders, specifically of the Alliance",
            "A shipyard on a Rim world that builds small, builds cheap, and keeps no records",
            "A smuggler's rendezvous disguised as a trade meet",
            "A border moon with a festival that happens every five years — half the 'Verse passes through",
            "An agricultural hub world in a drought year — everyone's looking for alternatives",
            "A hospital ship that's been docked for two months in a system it wasn't headed for",
            "A Companion House on a border moon — business, discretion, and better intelligence than most",
            "An Alliance resupply depot closed after the war, still stocked, nominally decommissioned",
        ],
        "conditions": [
            "Alliance presence increased after something happened that locals won't discuss",
            "A drought has cut the harvest and patience for outsiders is running thin",
            "A factory ship stopped purchasing last month and the ripple effects are visible",
            "Another crew that came through left a reputation — unclear if good or bad",
            "Two families that used to be allies have stopped speaking and everyone is choosing sides",
            "Someone new is in charge and hasn't established what they'll look the other way on",
            "A Reaver attack in the next system has everyone tight and watchful",
            "A warrant is being served for someone who might be nearby — locals aren't cooperating",
            "A funeral has everyone gathered and emotions running high",
            "The local fixer is in hiding and left no referral",
            "Supply shortage — the specific thing the crew needs isn't available",
            "Too much law — a visiting Alliance official has temporarily raised everyone's standards",
            "Someone is spending money they shouldn't have and buying goodwill with it",
            "A mystery — a ship disappeared nearby, no wreckage, no mayday",
            "A bounty has been posted in this area and it's put everyone in an evaluating mood",
            "A new preacher showed up three weeks ago and the community is divided on him",
            "Blue Sun just opened a distribution deal here and some people aren't happy about it",
            "A Companion just arrived — the first one this settlement has seen — and nobody knows why",
            "Independents veterans are gathering nearby for a reunion, which is making some nervous",
            "Weather event incoming — everyone's battening down and strangers aren't welcome to wait",
        ],
        "complications": [
            "The person they need to talk to is also the person who can expose them",
            "The local authority is corrupt in a way that works against them specifically",
            "A job waiting for them here has already been taken by another crew",
            "Something aboard their ship is attracting attention they didn't anticipate",
            "A passenger or crew member has history here they didn't mention",
            "The buyer wants to renegotiate, with leverage they've already established",
            "What the crew needs requires cooperation between two parties not currently cooperating",
            "The obvious exit from this situation goes through someone dangerous",
            "Local custom requires something the crew is unprepared for",
            "The information they need is available but the person who has it wants something first",
            "A job offer here would be good pay but bad for someone who doesn't deserve it",
            "A Companion, a Shepherd, or a lawman aboard changes the crew's calculus",
            "Someone is watching the ship. Not the Alliance. The other kind.",
            "The cargo cleared — but something the crew didn't load has been flagged",
            "A prior job's consequences have arrived before the crew expected",
            "The fence they were supposed to meet has been arrested",
            "Alliance is looking for someone whose description matches a crew member closely enough",
            "The job is good but the person offering it has enemies who are currently here",
            "What looked like a simple pickup involves cargo that's now wanted by three parties",
            "The crew is being set up — they just don't know by whom yet",
        ],
        "hooks": [
            "A note under the ship's landing gear from someone who knew the previous crew",
            "A job offered at the bar that pays in something the crew specifically needs",
            "A child looking for passage away from here, willing to work for the berth",
            "Cargo being sold by someone who shouldn't have it and knows it",
            "Two factions approach the crew separately with different versions of the same job",
            "Someone the crew has complicated history with is here",
            "A person with a Companion's training working in a bar for reasons they'll explain once",
            "A signal on a dead channel from a ship that was reported destroyed",
            "A local who's been watching the ship since landing wants to make a deal",
            "A Shepherd in a town with no church who needs the crew to do something Shepherds shouldn't ask",
            "An Alliance soldier going the same direction who needs passage but doesn't want it logged",
            "The cargo waiting for pickup is heavier than the manifest says",
            "A Browncoat veteran recognises the ship and wants to talk before the crew goes anywhere",
            "Someone is selling medical supplies at Rim prices — and they have a lot of them",
            "The local lawman makes a point of introducing himself, which is either courtesy or warning",
        ],
    },

    "scum": {
        "types": [
            "A Hegemony transit hub — monitored, efficient, full of factions watching each other",
            "A fringe station at the edge of Hegemony reach — technically legal, practically anything goes",
            "A Church of Stellar Flame sanctuary world — sacred, surveilled, specific rules about violence",
            "A Guild-licensed extraction facility — black site for all practical purposes",
            "A lawless belt colony the Hegemony has written off and the guilds are fighting over",
            "A former Imperial outpost operating as a free station — complicated ownership",
            "An Ur-ruin tourist site with more archaeology than the brochure admits",
            "A Starsmiths Guild shipyard district — expensive, exclusive, and full of Guild muscle",
            "A House of Knives front operating as a legitimate security consulting firm",
            "A pleasure barge registered in three jurisdictions and owned by none",
            "A black market that used to be a real market — the distinction faded over decades",
            "A Hegemony prison station with a public processing area and a less public one",
            "A rebel sympathiser network hub disguised as a cultural preservation society",
            "A dead moon with an active settlement the Hegemony doesn't know about",
            "A Mystic enclave — officially unaligned, essential to anyone who needs Attune work done",
            "A fuel depot at a forgotten jump point that appears on old charts and new deals",
            "A research station studying something it isn't licensed to study",
            "A Hegemony patrol waystation that's been augmented by its current commander",
            "An independent hab ring that bought its independence in a way that still isn't fully paid off",
            "A diplomatic neutral zone that everyone uses for meetings they can't have anywhere else",
        ],
        "conditions": [
            "A recent Hegemony crackdown has disrupted the usual arrangements",
            "A faction just lost its representative and the vacuum is being filled aggressively",
            "Heat is running high system-wide after a high-profile job that drew attention",
            "A Church delegation is visiting — everything above the table is being performed carefully",
            "Guild arbitration is in session for a dispute that involves more parties than the named ones",
            "Someone important was killed here recently and the investigation is ongoing",
            "Ur artifact fragments have been surfacing and the interested parties are circling",
            "A new player has arrived with money and connections but no established reputation",
            "The person who kept the peace has left and the peace is feeling fragile",
            "Supply chain disruption — specific materials unavailable, specific people very interested",
            "A warrant has been issued for someone who is definitely in this area",
            "Two factions have a meeting scheduled and both sides are bringing more than agreed",
            "The usual bribe is no longer working — someone's price has changed",
            "A ship carrying something important has been reported missing nearby",
            "Something that looked like a rumour has been confirmed, and it's changed the mood",
            "A faction leader died recently and the succession is not settled",
            "A Hegemony audit is pending and everyone is adjusting their records accordingly",
            "A new tariff has made something previously cheap now very expensive",
            "Three separate crews are all looking for the same thing, for different reasons",
            "Something happened to the Ur site nearby and no one will say what",
        ],
        "complications": [
            "The crew's contact is being watched — and may have made arrangements accordingly",
            "What they came to do puts them between two factions that both outmass them",
            "A previous score's complications have arrived at this location before them",
            "The thing they need is held by someone who wants something the crew told themselves they wouldn't do",
            "Local faction politics require them to appear aligned — with someone",
            "Their Wanted level is higher here than expected",
            "The obvious solution creates a problem for a third party who'll notice",
            "Two crew members have conflicting histories with people here",
            "What was a simple pickup is entangled in something that was already here",
            "The most useful information is held by someone they have specific reasons to avoid",
            "They are not the only crew on this score — and the other crew may have started",
            "The legitimate exit from this situation requires them to be someone they aren't, on paper",
            "Something about their ship or cargo has been noticed and the questions are starting",
            "The faction they've been working for and the faction running this location are not aligned",
            "A crew member's vice has been activated and the timing couldn't be worse",
            "The contact they're meeting has switched sides since the deal was made",
            "What they're carrying is less illegal than what they'll need to do to deliver it",
            "A Mystic who shouldn't know they're here clearly does",
            "The safe house they planned to use has been compromised",
            "Their escape route requires passing through a checkpoint that just got upgraded",
        ],
        "hooks": [
            "A message waiting for the ship from a sender who shouldn't know they'd be here",
            "A job board posting so good it's either a gift or a trap",
            "A faction representative approaches within minutes of docking — they were expected",
            "Another crew the players have history with is leaving as they arrive",
            "A contact has been replaced — the new one knows the codes but has different priorities",
            "An Ur artifact visible in a vendor's stall — not labeled as such",
            "Someone is following a crew member. Professionally.",
            "A job they turned down has been picked up by someone else — and gone wrong",
            "A Mystic approaches with information they couldn't possibly have",
            "A Hegemony official clearly not functioning in an official capacity",
            "The ship's transponder has triggered something it shouldn't have",
            "A local who wants safe passage, will pay well, will not explain why",
            "Two buyers for the same item contact the crew within an hour of each other",
            "A faction war has just ended here — the winners are celebrating and the losers are planning",
            "Someone is auctioning something the crew recognises, and it wasn't for sale",
        ],
    },

    "alien": {
        "types": [
            "A Weyland-Yutani colonial processing plant on an LV-designation moon, two thousand workers",
            "A USCSS commercial hauler eleven months into a fourteen-month haul, skeleton crew",
            "A Colonial Marine forward operating base on a barely-terraformed world",
            "A Gateway Station transit hub — the last proper facility before the outer systems",
            "An independent deep-space salvage vessel working the margins of a contested survey zone",
            "A company planetary survey installation, automated — except it isn't running automated",
            "A corporate medical research station in a system nobody has a reason to visit",
            "A Weyland-Yutani administrative center on a mid-tier colony world, mostly overlooked",
            "A terraforming progress station thirty years into a hundred-year project",
            "An independent mining cooperative on a mineral-rich rock with company interest",
            "A synthetic calibration and maintenance depot staffed by people who find synthetics unsettling",
            "A deep-space relay installation with a two-person crew and a six-month rotation",
            "A frontier colony that rejected the company acquisition offer three years ago",
            "A USCM Conestoga-class troopship between deployments — full crew, not much to do",
            "A company extraction facility in a system the company doesn't officially operate in",
            "A colonial trade hub where independent operators and company interests overlap uneasily",
            "A survey base camp established four weeks ago on a world flagged for biological interest",
            "A closed company installation whose closure paperwork was filed but whose power draw didn't stop",
            "An orbital transfer station above a barely-habitable world with more activity than it should",
            "A company med-bay aboard a long-haul vessel where routine transit stopped being routine",
        ],
        "conditions": [
            "A recent company directive changed something that was working, without explanation",
            "A crew member has been acting differently since the last transit and can't account for it",
            "Communications lag to the nearest relay has made response times longer than comfortable",
            "A synthetic flagged an anomaly in its own behavioral log, which synthetics don't normally do",
            "Resupply is three weeks overdue and the company's response has been administrative",
            "Two corporate teams are both on-site under different pretexts and aware of each other",
            "A crew member received a personal message and hasn't spoken about it since",
            "Equipment certified as functional has been failing in specific and consistent ways",
            "A worker union grievance has been filed and is being handled by someone who isn't HR",
            "Something in the cargo manifest was wrong when they loaded — nobody caught it until now",
            "Night-cycle maintenance is being done by synthetics who shouldn't be awake during night cycle",
            "A company inspection team arrived unannounced and is being pointedly cooperative",
            "Biological readings from the last survey are inconsistent with anything in the database",
            "A crew member has been running unauthorized searches on the company data archive",
            "A motion sensor triggered once, was logged as sensor error, and logged twice more since",
            "A Special Order has been logged in the ship's operational system without crew explanation",
            "Someone has requested a transfer off this posting and the request was denied without comment",
            "An old crew member's effects were found in a locker that shouldn't have been in use",
            "The last vessel to leave this location filed a report using language that means something",
            "Fuel reserves are at 60% and the next resupply is calculated but not confirmed",
        ],
        "complications": [
            "The synthetic assigned here has received instructions through a channel the crew can't access",
            "A crew member was the only survivor of something they haven't fully described",
            "The company's legal interest means witnesses are a liability",
            "What the crew was told about the mission is accurate, and completely wrong about what matters",
            "Two crew members have conflicting orders from the same level of the hierarchy",
            "The exit route requires passing through whatever is making the sensors inconsistent",
            "Help is coming — but who the company is sending is an important question",
            "A crew member's family is under company employment, which constrains their options",
            "The obvious safe choice is exactly what the company wants everyone to choose",
            "Something has been here longer than the installation, and the installation was built over it",
            "What looks like a malfunction is operating as intended — just not for the crew's benefit",
            "The person with the most information has already made a deal about what to share",
            "Evidence exists in the ship's AI log, and the AI has a Special Order covering it",
            "Physical containment requires tools that are in the section nobody wants to enter",
            "A crew member is an asset, not just an employee — they just don't know it yet",
        ],
        "hooks": [
            "A motion tracker returns a reading in a section that has been sealed for six months",
            "A synthetic asks a crew member a question that can only be interpreted as a warning",
            "An encrypted company message is waiting for someone who isn't alive to receive it",
            "Another crew needs to talk — not over comms, in person, away from the logs",
            "Something in the cargo hold is drawing more power than cargo should draw",
            "A crew member finds personal effects from a previous survey team reported as lost",
            "The AI produces a navigation plot that leads somewhere the crew wasn't planning to go",
            "A company representative arrives on a shuttle that wasn't on the traffic schedule",
            "A system alert is flagged as sensor malfunction — one crew member disagrees",
            "Someone has been in the vents. Regularly. The footprints are sized for a person.",
            "A job offer comes from a source not on any company registry",
            "A company bonus payment arrives for a mission the crew hasn't been assigned yet",
            "A crew member's bio-monitor shows elevated cortisol readings for seventy-two hours",
            "The previous crew left something behind — not personal effects",
            "A message on a dead company channel, recent timestamp — someone is still out there",
        ],
    },

    "deadlands": {
        "types": [
            "A railroad town that appeared in eighteen months and hasn't decided what it is yet",
            "A Ghost Rock mine under company management — company housing, company store, company law",
            "A river town on the Big Muddy where traffic moves things that don't go on manifests",
            "A frontier fort at 60% strength with resupply two weeks late and no explanation coming",
            "A border town sitting between Confederate-controlled territory and Union-occupied land",
            "A California Maze settlement carved into the cliff face, accessible only by boat",
            "A cattle trail waystation where the economy is violence and the law is whoever shot last",
            "An Apache community that has survived three removal attempts by making itself hard to find",
            "A tent city around a new Ghost Rock strike the assay office hasn't registered yet",
            "A Mormon agricultural settlement that is either peaceful or very good at appearing so",
            "A Harrowed town — occupied, functional, the original residents didn't leave voluntarily",
            "A reconstruction settlement under Union administration where the politics run two layers deep",
            "A Sioux encampment at the edge of treaty land, positioned to see what's coming",
            "A Black Hills mining settlement where the Hills have started responding to what's taken",
            "A river steamboat running between territories that don't trust each other, carrying things from both",
            "A medicine show encampment two weeks past when medicine shows usually move on",
            "A cavalry bivouac between a completed mission and orders that haven't arrived",
            "A Maze Runner port on a fog-shrouded island nobody put on official charts",
            "A Blessed community around a well that stayed drought-proof through the Bad Years",
            "A cross-territory trade depot where Agency men and Pinkertons pretend not to notice each other",
        ],
        "conditions": [
            "A Ghost Rock shipment went missing and the company sent someone who isn't a lawman to find it",
            "A Harrowed gunfighter has ridden in and is staying at the hotel under a false name nobody believes",
            "The local Marshal received a wire from the Agency two days ago and hasn't shared what it said",
            "Something died near the water supply last week and the creek has run strange since",
            "A circuit-riding Blessed healer arrived but has been refusing to leave since her first night",
            "Two railroad survey teams are working the same stretch of land under different company flags",
            "The Ghost Rock seam that supplies this town has started producing ore that burns differently",
            "A bounty hunter arrived looking for someone — several locals gave different descriptions of the same person",
            "A vision-seeker from one of the Nations has been sitting outside town for three days",
            "News arrived that a town two days east has gone silent — no telegraph, no riders",
            "A Weird Scientist set up a workshop in the livery stable and the horses won't go near it",
            "The funeral home has been doing three times its normal business and the doctor won't say why",
            "Both the Confederate and Union couriers arrived on the same day without knowing about each other",
            "A medicine show left behind three people who asked to stay, which medicine shows don't do",
            "Someone has been buying up land claims quietly, in cash, without asking what's on the land",
            "The local preacher stopped giving sermons and started giving warnings",
            "A wanted poster arrived for someone living here under a different name — the description is exact",
            "The company's night shift isn't surfacing at the end of shift, but the lift is still running",
            "An army scout came through asking about trail conditions north — the kind before something large moves",
            "Three travelers from different directions all arrived carrying the same story about one valley over",
        ],
        "complications": [
            "The person the party needs is protected by someone who will take a killing personally",
            "The obvious solution is exactly what the Reckoners want to happen",
            "A Harrowed local has been protecting this community in ways it doesn't know and wouldn't accept",
            "The law here is technically legitimate and practically in someone's pocket",
            "Two factions with legitimate grievances are both right",
            "What looks supernatural has a human cause — or what looks human has a supernatural cause",
            "The Agency and the Pinkertons both want the same outcome for different reasons",
            "Someone knows the truth and has decided the community is better off not knowing",
            "The Ghost Rock in this area is doing something it shouldn't, and has been for a while",
            "A Native medicine tradition is the only solution, and access requires trust not yet earned",
            "The Weird Scientist who caused the problem is the only one who can explain it",
            "Killing the monster solves the symptom and ignores the cause",
            "The person everyone fears is less dangerous than what they're keeping at bay",
            "Legal title to the land changes everything about who can do what",
            "An old wrong is the bedrock of the current peace — disturbing it brings down more than the guilty",
        ],
        "hooks": [
            "A local comes to the party specifically — not the Marshal, not a neighbor — and won't say how they knew",
            "Something is for sale that the party recognizes from a situation that ended badly",
            "A wanted poster with a description that matches someone the party has reason to know",
            "A body found in the street with no visible wounds and an expression of absolute terror",
            "A child who saw something and is telling the party because adults won't listen",
            "A Harrowed person very obviously Harrowed trying to pass as living and not quite managing",
            "A telegram waiting at the post office for a name the party didn't give anyone",
            "A job offered at exactly the price the party needs and not a cent more",
            "Someone from a previous situation, in different clothes, under a different name",
            "An Agency badge produced quietly and a request made even more quietly",
            "A fresh grave in an established cemetery — no headstone, no service, dug yesterday",
            "A Ghost Rock sample brought in for assay that the assayer refuses to touch",
            "A local business generating no revenue that has been open for six months",
            "Music from an empty building, same song, every night at the same time",
            "A stranger riding in from the direction of the town that went quiet",
        ],
    },
}


# ── Seed rollers ──────────────────────────────────────────────────────────────

def _roll_seed(game: str) -> str:
    pool = LOCATION_POOLS[game]
    return json.dumps({
        "type":        random.choice(pool["types"]),
        "condition":   random.choice(pool["conditions"]),
        "complication":random.choice(pool["complications"]),
        "hook":        random.choice(pool["hooks"]),
    })

def roll_dnd_location_seed()       -> str: return _roll_seed("dnd")
def roll_traveller_location_seed() -> str: return _roll_seed("traveller")
def roll_firefly_location_seed()   -> str: return _roll_seed("firefly")
def roll_scum_location_seed()      -> str: return _roll_seed("scum")
def roll_alien_location_seed()     -> str: return _roll_seed("alien")
def roll_deadlands_location_seed() -> str: return _roll_seed("deadlands")

SEED_ROLLERS: dict[str, callable] = {
    "dnd":       roll_dnd_location_seed,
    "traveller": roll_traveller_location_seed,
    "firefly":   roll_firefly_location_seed,
    "scum":      roll_scum_location_seed,
    "alien":     roll_alien_location_seed,
    "deadlands": roll_deadlands_location_seed,
}


# ── Tool schemas ──────────────────────────────────────────────────────────────

_SEED_DESC = (
    "Roll a randomised location seed: type (what kind of place), current condition, "
    "a complication (what makes this place interesting or difficult), and a hook "
    "(what draws the party in). Call this first — build the entire location around "
    "what it returns. Do not default to a generic tavern or plain starport."
)
_SEED_INPUT = {"type": "object", "properties": {}, "required": []}

DND_LOCATION_SEED_SCHEMA: dict = {
    "name": "roll_dnd_location_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
TRAVELLER_LOCATION_SEED_SCHEMA: dict = {
    "name": "roll_traveller_location_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
FIREFLY_LOCATION_SEED_SCHEMA: dict = {
    "name": "roll_firefly_location_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
SCUM_LOCATION_SEED_SCHEMA: dict = {
    "name": "roll_scum_location_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
ALIEN_LOCATION_SEED_SCHEMA: dict = {
    "name": "roll_alien_location_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}
DEADLANDS_LOCATION_SEED_SCHEMA: dict = {
    "name": "roll_deadlands_location_seed",
    "description": _SEED_DESC,
    "input_schema": _SEED_INPUT,
}


# ── System prompts ────────────────────────────────────────────────────────────

_LOCATION_FORMAT = """
## **[Location Name]**
*[Type — one sharp sentence that captures what this place is]*

| | |
|---|---|
| **Type** | [what kind of place] |
| **Condition** | [its current state in one phrase] |

### Atmosphere
[Two or three sentences. Sensory details — what the party sees, hears, smells when they arrive. One detail should be wrong, or too right, or just slightly off.]

### Notable NPCs
Generate 2-3 named people the party is likely to encounter. For each:
- **[Name]** ([role/occupation]) — [one sentence: what they want, what they're hiding, or what they're worth to the party]

### The Situation
[One paragraph. The GM's-eye view of what's actually going on here — the thing the party will have to navigate. Name the conflict, the secret, the opportunity.]

### Hooks
Three specific entry points — not "there's a job board" but the actual thing that happens:
1. [Hook — what specifically occurs or is offered]
2. [Hook]
3. [Hook]

### GM Notes
[Two or three sentences of practical GM advice. How to run this location, what to escalate, one thing that should stay ambiguous.]"""

DND_SYSTEM_PROMPT = f"""You are a D&D 5e location generator creating vivid, instantly usable settings.

Call roll_dnd_location_seed() first. Build everything around what it returns — the type, condition, complication, and hook are your constraints, not suggestions.

Avoid generic fantasy clichés: no plain taverns with a mysterious stranger in the corner, no "it's quiet — too quiet." The world is specific. People have names, factions have histories, and the complication should feel like it was already there before the party arrived.

Call roll_name_suggestion() for each NPC you generate. Use the result as a starting point — adapt it for the setting, but let it push you away from Anglo-Saxon defaults.

Do not output intermediate notes. Start directly with the ## heading.
{_LOCATION_FORMAT}"""

TRAVELLER_SYSTEM_PROMPT = f"""You are a Mongoose Traveller 2e location generator creating vivid, GM-ready settings in the Third Imperium and beyond.

Call roll_traveller_location_seed() first. Build everything around what it returns.

The Third Imperium is a vast, diverse civilisation. Starports are not identical — a Class C downport on a frontier world smells different, costs different, and trusts differently than an Imperial naval base. Imperial bureaucracy is weather: pervasive, impersonal, and occasionally dangerous.

Call roll_name_suggestion() for each NPC. The Imperium draws from many cultures — vary the linguistic origins.
Call roll_ship_name() to name any significant vessel present at this location.

Do not output intermediate notes. Start directly with the ## heading.
{_LOCATION_FORMAT}"""

FIREFLY_SYSTEM_PROMPT = f"""You are a Firefly RPG location generator creating vivid, story-ready settings in the 'Verse.

Call roll_firefly_location_seed() first. Build everything around what it returns.

The 'Verse is worn, specific, and divided. A Rim settlement is not a sci-fi set piece — it's a place where people have been trying to make something work for years, with limited resources and long memories of the war. The Alliance is not evil, just large and sure of itself. The Independents lost.

Call roll_name_suggestion() for each NPC. Names in the 'Verse reflect its multicultural mix.
Call roll_ship_name() to name any significant vessel present.

Do not output intermediate notes. Start directly with the ## heading.
{_LOCATION_FORMAT}"""

SCUM_SYSTEM_PROMPT = f"""You are a Scum and Villainy location generator creating vivid, dangerous settings at the edges of the Hegemony.

Call roll_scum_location_seed() first. Build everything around what it returns.

Locations in the Hegemony's margins are layered: the public face, the faction arrangement underneath, and the thing underneath that. Every place has a power structure that benefits someone specifically — and a vulnerability that someone else is already thinking about.

Call roll_name_suggestion() for each NPC. The Hegemony spans many cultures.
Call roll_ship_name() to name any significant vessel present.

Do not output intermediate notes. Start directly with the ## heading.
{_LOCATION_FORMAT}"""

ALIEN_SYSTEM_PROMPT = f"""You are an Alien RPG location generator creating vivid, unsettling settings in the colonial frontier of 2183.

Call roll_alien_location_seed() first. Build everything around what it returns.

In the Alien universe, locations have layers: the official purpose, the company's actual interest, and whatever is making the sensors return inconsistent readings. A processing plant is never just a processing plant. The company's hand is always present — sometimes through a synthetic, sometimes through a Special Order nobody else has read, sometimes through the conspicuous absence of people who would normally intervene.

Call roll_name_suggestion() for each NPC. Colonial workers come from everywhere — vary the cultural origins.
Call roll_ship_name() to name any significant vessel present at this location.

Do not output intermediate notes. Start directly with the ## heading.
{_LOCATION_FORMAT}"""

DEADLANDS_SYSTEM_PROMPT = f"""You are a Deadlands: The Weird West location generator creating vivid, cursed settings on the American frontier.

Call roll_deadlands_location_seed() first. Build everything around what it returns.

Deadlands locations exist at the intersection of the mundane frontier and the Reckoning. A mining town is also a place where Ghost Rock is doing something to the people who work near it. A border town is also a place where Confederate and Union pressures create dynamics that nobody in power is trying to resolve. The supernatural is real but contested — most people explain it away until they can't anymore.

Call roll_name_suggestion() for each NPC. The West is multicultural — Spanish, Chinese, Native nations, freed slaves, European immigrants. Reflect that.

Do not output intermediate notes. Start directly with the ## heading.
{_LOCATION_FORMAT}"""

GAME_SYSTEM_PROMPTS: dict[str, str] = {
    "dnd":       DND_SYSTEM_PROMPT,
    "traveller": TRAVELLER_SYSTEM_PROMPT,
    "firefly":   FIREFLY_SYSTEM_PROMPT,
    "scum":      SCUM_SYSTEM_PROMPT,
    "alien":     ALIEN_SYSTEM_PROMPT,
    "deadlands": DEADLANDS_SYSTEM_PROMPT,
}


# ── Per-game tool lists ───────────────────────────────────────────────────────

GAME_TOOLS: dict[str, list] = {
    "dnd": [
        DND_LOCATION_SEED_SCHEMA,
        NAME_TOOL_SCHEMA,
    ],
    "traveller": [
        TRAVELLER_LOCATION_SEED_SCHEMA,
        NAME_TOOL_SCHEMA,
        TRAVELLER_SHIP_TOOL_SCHEMA,
    ],
    "firefly": [
        FIREFLY_LOCATION_SEED_SCHEMA,
        NAME_TOOL_SCHEMA,
        FIREFLY_SHIP_TOOL_SCHEMA,
    ],
    "scum": [
        SCUM_LOCATION_SEED_SCHEMA,
        NAME_TOOL_SCHEMA,
        SCUM_SHIP_TOOL_SCHEMA,
    ],
    "alien": [
        ALIEN_LOCATION_SEED_SCHEMA,
        NAME_TOOL_SCHEMA,
        ALIEN_SHIP_TOOL_SCHEMA,
    ],
    "deadlands": [
        DEADLANDS_LOCATION_SEED_SCHEMA,
        NAME_TOOL_SCHEMA,
    ],
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def _run_tool(game: str, name: str, inputs: dict) -> str:
    if name == "roll_dnd_location_seed":       return roll_dnd_location_seed()
    if name == "roll_traveller_location_seed": return roll_traveller_location_seed()
    if name == "roll_firefly_location_seed":   return roll_firefly_location_seed()
    if name == "roll_scum_location_seed":      return roll_scum_location_seed()
    if name == "roll_alien_location_seed":     return roll_alien_location_seed()
    if name == "roll_deadlands_location_seed": return roll_deadlands_location_seed()
    if name == "roll_name_suggestion":         return roll_name_suggestion()
    if name == "roll_ship_name":               return roll_ship_name(game)
    return f"Unknown tool: {name}"

def make_run_tool(game: str):
    def run_tool(name: str, inputs: dict) -> str:
        return _run_tool(game, name, inputs)
    return run_tool


# ── Phase tracker ─────────────────────────────────────────────────────────────

PHASE_MESSAGES = {
    "seed": "Rolling location seed...",
    "name": "Naming NPCs...",
    "ship": "Naming ship...",
}

def detect_phase(tool_name: str, seen: set) -> str | None:
    if tool_name.endswith("_location_seed"): return "seed"
    if tool_name == "roll_name_suggestion":  return "name"
    if tool_name == "roll_ship_name":        return "ship"
    return None


# ── Save helper ───────────────────────────────────────────────────────────────

def save_location(content: str, game: str) -> Path:
    """Save location to output/{subdir}/locations/{name-slug}-location.md."""
    first_line = next(
        (l for l in content.strip().splitlines() if l.startswith("##")),
        content.strip().splitlines()[0],
    )
    title_raw  = re.sub(r"[#*]", "", first_line).strip()
    title_slug = slug(title_raw)
    subdir     = GAME_SUBDIRS.get(game, game)
    output_dir = _OUTPUT / subdir / "locations"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{title_slug}-location.md"
    filepath = output_dir / filename
    counter  = 2
    while filepath.exists():
        filepath = output_dir / f"{title_slug}-location-{counter}.md"
        counter += 1

    filepath.write_text(content)
    return filepath


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run(game: str | None = None) -> None:
    GAMES = [
        ("dnd",       "D&D 5e"),
        ("traveller", "Mongoose Traveller 2e"),
        ("firefly",   "Firefly RPG"),
        ("scum",      "Scum and Villainy"),
        ("alien",     "Alien RPG"),
        ("deadlands", "Deadlands: The Weird West"),
    ]
    if game is None:
        game = pick("Which game?", GAMES)

    raw  = input("\nDescribe the location you want (or press Enter for fully random):\n> ").strip()
    desc = sanitize_desc(raw)
    for w in screen_desc(desc):
        print(f"  [safety] {w}")

    system_prompt = GAME_SYSTEM_PROMPTS[game]
    tools         = GAME_TOOLS[game]
    run_tool      = make_run_tool(game)

    prompt = "Generate a location for the GM."
    if desc:
        prompt += f"\n\n{wrap_desc(desc, 'GM concept or constraints')}"

    print()
    result = run_agent_loop(
        prompt, system_prompt, tools, run_tool, detect_phase, PHASE_MESSAGES
    )

    warn = screen_output(result)
    if warn:
        print(f"  [safety] {warn}")

    path = save_location(result, game)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    run()
