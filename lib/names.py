"""
Shared name pools for all RPG character generators.

Two separate pool sets:

  NAME_POOLS  — Real-world cultural traditions.  Used by all games but
                especially the sci-fi titles (Traveller, Firefly, Scum &
                Villainy).  Supports cross-tradition blending (~25% of rolls).

  DND_POOLS   — Fantasy race pools for D&D 5e, keyed by race name.  Passing
                race="Human" redirects to NAME_POOLS for maximum diversity.

Call roll_name_suggestion() (sci-fi / cultural) or roll_dnd_name_suggestion()
(D&D) before naming any character.  The model may adapt the result freely.
"""

import json
import random


# ── Name pools by cultural tradition ─────────────────────────────────────────

NAME_POOLS: dict[str, dict[str, list[str]]] = {
    "West African": {
        "first": [
            "Adaeze", "Amara", "Kofi", "Kwame", "Ama", "Chioma", "Emeka", "Ngozi",
            "Tunde", "Sola", "Yaw", "Abena", "Kwesi", "Efua", "Nana", "Esi",
            "Kojo", "Adjoa", "Kweku", "Akosua", "Fiifi", "Maame", "Akua", "Kwabena", "Afia",
        ],
        "last": [
            "Mensah", "Asante", "Okafor", "Adeyemi", "Boateng", "Nkrumah", "Owusu",
            "Asamoah", "Acheampong", "Darko", "Antwi", "Adjei", "Attah", "Bonsu",
            "Agyeman", "Duah", "Sarpong", "Amponsah",
        ],
    },
    "Arabic / Middle Eastern": {
        "first": [
            "Layla", "Omar", "Fatima", "Khalid", "Yasmin", "Tariq", "Nadia", "Rashid",
            "Zara", "Karim", "Hana", "Yusuf", "Rania", "Samir", "Leila", "Faris",
            "Dina", "Sami", "Amira", "Jamal", "Soraya", "Nasser", "Maryam", "Hassan", "Sana",
        ],
        "last": [
            "Al-Hassan", "Karimi", "Mansour", "Nouri", "Abboud", "Farouk", "Saleh",
            "Khoury", "Nassar", "Daoud", "Aziz", "Rashidi", "Jaber", "Hamdan", "Qasim",
        ],
    },
    "East Asian": {
        "first": [
            "Wei", "Lin", "Mei", "Jun", "Xin", "Yuki", "Kenji", "Akira", "Hana",
            "Sora", "Ren", "Yuna", "Jian", "Lan", "Ryo", "Miho", "Tao", "Ling",
            "Haruto", "Sakura", "Zhen", "Mio", "Nori", "Aoi", "Yoko",
        ],
        "last": [
            "Zhang", "Li", "Wang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu",
            "Tanaka", "Suzuki", "Sato", "Yamamoto", "Watanabe", "Kobayashi",
            "Kim", "Park", "Choi", "Lee", "Jung", "Nakamura", "Ito",
        ],
    },
    "South Asian": {
        "first": [
            "Priya", "Arjun", "Kavya", "Ravi", "Ananya", "Vikram", "Divya", "Kiran",
            "Nisha", "Aditya", "Pooja", "Rahul", "Meera", "Suresh", "Asha", "Rohan",
            "Shreya", "Amit", "Lakshmi", "Dev", "Sunita", "Nikhil", "Parvati", "Sanjay", "Reena",
        ],
        "last": [
            "Sharma", "Patel", "Singh", "Gupta", "Kumar", "Nair", "Rao", "Iyer",
            "Reddy", "Pillai", "Bose", "Menon", "Joshi", "Verma", "Mehta",
            "Kapoor", "Chatterjee", "Mukherjee",
        ],
    },
    "Slavic": {
        "first": [
            "Natasha", "Ivan", "Oksana", "Dmitri", "Sonya", "Yuri", "Marta", "Pavel",
            "Vanya", "Katya", "Alexei", "Mila", "Borya", "Vera", "Piotr", "Zoya",
            "Sasha", "Galya", "Kostya", "Tamara", "Andrei", "Lena", "Vasily", "Dasha", "Sergei",
        ],
        "last": [
            "Volkov", "Petrov", "Ivanov", "Sokolov", "Morozov", "Lebedev", "Novikov",
            "Kozlov", "Popov", "Smirnov", "Kovalev", "Fedorov", "Kuznetsov",
            "Zhukov", "Rykov", "Orlov", "Nikitin", "Frolov", "Bogdanov", "Voronov",
        ],
    },
    "Spanish / Latin American": {
        "first": [
            "Valentina", "Carlos", "Isabela", "Mateo", "Lucia", "Diego", "Sofia",
            "Alejandro", "Camila", "Sebastián", "Gabriela", "Andrés", "Natalia",
            "Miguel", "Daniela", "Emilio", "Paola", "Rodrigo", "Elena", "Marco",
            "Catalina", "Javier", "Alba", "Fernando", "Paz",
        ],
        "last": [
            "García", "Rodríguez", "López", "Martínez", "González", "Hernández",
            "Ruiz", "Sánchez", "Pérez", "Torres", "Vargas", "Morales", "Reyes",
            "Vega", "Castro", "Mendoza", "Rojas", "Flores", "Salinas", "Cruz",
        ],
    },
    "Norse / Scandinavian": {
        "first": [
            "Sigrid", "Bjorn", "Astrid", "Leif", "Freya", "Erik", "Ingrid", "Gunnar",
            "Solveig", "Harald", "Ragnhild", "Olaf", "Gudrun", "Eirik", "Helga",
            "Ragnar", "Tove", "Magnus", "Sif", "Dag", "Hildur", "Ulf", "Runa", "Ivar", "Thyra",
        ],
        "last": [
            "Eriksen", "Andersen", "Larsen", "Hansen", "Pedersen", "Nilsson",
            "Lindqvist", "Bergström", "Magnusson", "Sigurdsson", "Björnsson",
        ],
    },
    # Icelandic names use a patronymic (or matronymic) system rather than hereditary
    # surnames.  The last name is formed from a parent's first name in the genitive
    # case plus -son (sons) or -dóttir (daughters).  The values under
    # "patronymic_bases" are already declined; roll_name_suggestion() appends the
    # suffix at generation time.
    "Icelandic": {
        "first": [
            "Helga", "Björn", "Sigríður", "Gunnar", "Þóra", "Kristján", "Fjóla",
            "Dagur", "Vigdís", "Snorri", "Guðrún", "Bjarni", "Hildur", "Arnar",
            "Þorgerður", "Eiríkur", "Ingibjörg", "Ólafur", "Ragnheiður", "Jón",
            "Hákon", "Ísabel", "Einar", "Steinunn", "Stefán",
        ],
        # Genitive-form bases: append "son" or "dóttir" to form the patronymic.
        # e.g. "Jóns" + "son" → Jónsson  |  "Jóns" + "dóttir" → Jónsdóttir
        #      "Bjarna" + "son" → Bjarnason (Bjarni)
        #      "Sigurðar" + "dóttir" → Sigurðardóttir (Sigurður)
        "patronymic_bases": [
            "Jóns",      # Jón
            "Gunnars",   # Gunnar
            "Sigurðar",  # Sigurður
            "Björns",    # Björn
            "Ólafs",     # Ólafur
            "Kristjáns", # Kristján
            "Eiríks",    # Eiríkur
            "Haralds",   # Haraldur
            "Ingvars",   # Ingvar
            "Egils",     # Egill
            "Bjarna",    # Bjarni
            "Snorra",    # Snorri
            "Árna",      # Árni
            "Stefáns",   # Stefán
            "Einars",    # Einar
        ],
    },
    "Māori": {
        "first": [
            "Aroha", "Hemi", "Mere", "Hinemoa", "Rangi", "Māia", "Wiremu", "Kura",
            "Moana", "Ngāio", "Huia", "Roimata", "Paora", "Hine", "Waimārie",
            "Rāwiri", "Kāhu", "Manaia", "Āwhina", "Piripi", "Tāne", "Pita",
            "Āpirana", "Tāmati", "Hana",
        ],
        "last": [
            "Waititi", "Henare", "Harawira", "Pōhatu", "Parata", "Kīngi",
            "Reweti", "Rikihana", "Tāmahere", "Tūhourangi", "Ngaropo",
            "Te Aho", "Ngāpō", "Māhoe", "Tūwharetoa",
        ],
    },
    # A broad pool drawing from multiple North American nations — Plains (Lakota/
    # Dakota), Eastern Woodlands (Ojibwe/Anishinaabe), and Pacific Northwest.
    # These are names actively used as given names today; ceremonial or sacred
    # names are intentionally excluded.
    "North American Indigenous": {
        "first": [
            "Winona", "Aiyana", "Takoda", "Kimi", "Kohana", "Wambli", "Tala",
            "Nashoba", "Halona", "Kaya", "Mingan", "Hotah", "Chayton", "Chenoa",
            "Aponi", "Mika", "Mahpee", "Ayasha", "Koda", "Luyu", "Sequoia",
            "Sora", "Taini", "Elan", "Kiona",
        ],
        "last": [
            "Swifthawk", "Yellowbird", "Morningstar", "Greywolf", "Littlebear",
            "Ironhorse", "Whitehorse", "Strongbow", "Eagleheart", "Thunderbird",
            "Cloudwalker", "Redcloud", "Blackhorse", "Windwalker", "Runningwater",
        ],
    },
    # Names drawn from Nahuatl (Aztec/Central Mexican) and Maya traditions.
    # Given names here are commonly used in modern Mexico and Central America.
    "Nahuatl / Maya": {
        "first": [
            "Xochitl", "Citlali", "Itzel", "Ixchel", "Nayeli", "Metzli",
            "Yolotl", "Quetzal", "Tonalli", "Yaretzi", "Cuauhtémoc", "Itzcoatl",
            "Ixim", "Canek", "Hunahpu", "Mayeli", "Ek", "Chaac", "Ix",
            "Xitlali", "Nochtli", "Zolin", "Meztli", "Izel", "Ixchell",
        ],
        "last": [
            "Cuauhtémoc", "Tenoch", "Itzcoatl", "Canek", "Yaxkin", "Mixtli",
            "Copil", "Tula", "Chalco", "Acatl", "Xolotl", "Tecuani",
            "Itzam", "Bacalar", "Uxmal",
        ],
    },
    # Quechua / Aymara (Andean) and Mapuche (Chile / Argentina) traditions.
    "Andean / Mapuche": {
        "first": [
            "Tupac", "Inti", "Sisa", "Wayra", "Mallku", "Amaru", "Lautaro",
            "Rayén", "Antü", "Kuntur", "Qori", "Manquén", "Sumak", "Paine",
            "Aynuk", "Coya", "Atoc", "Rimac", "Lliclla", "Caupolican",
            "Colocolo", "Tika", "Milla", "Ñanku", "Cayul",
        ],
        "last": [
            "Yupanqui", "Quispe", "Mamani", "Condori", "Cusi", "Puma", "Huanca",
            "Cayupan", "Millao", "Nahuelpan", "Painequeo", "Quilaqueo",
            "Lican", "Ñanculef", "Catrileo",
        ],
    },
    "East African / Horn of Africa": {
        "first": [
            "Amara", "Dawit", "Hana", "Tesfaye", "Liya", "Haile", "Miriam", "Yonas",
            "Selam", "Bereket", "Tigist", "Girma", "Senait", "Mesfin", "Mahlet",
            "Natnael", "Bethlehem", "Tadesse", "Almaz", "Biniam", "Selamawit",
            "Eyob", "Mekdes", "Amanuel", "Tsion",
        ],
        "last": [
            "Tadesse", "Haile", "Bekele", "Tekle", "Gebre", "Wolde", "Tesfaye",
            "Meles", "Girma", "Alemu", "Assefa", "Negash", "Mehari", "Desta", "Kiros",
        ],
    },
    "Celtic / Irish / Welsh": {
        "first": [
            "Aoife", "Ciarán", "Siobhán", "Ewan", "Niamh", "Callum", "Brigid", "Fergus",
            "Sorcha", "Declan", "Maeve", "Cormac", "Saoirse", "Oisín", "Riona",
            "Tadhg", "Catriona", "Seán", "Fionuala", "Ruairí", "Eibhlín", "Conal",
            "Líadan", "Pádraig", "Áine",
        ],
        "last": [
            "O'Brien", "Murphy", "Walsh", "Ryan", "O'Connor", "Byrne", "Kelly",
            "O'Neill", "McCarthy", "MacLeod", "Campbell", "MacDonald", "McKenna",
            "Quinn", "Gallagher", "O'Sullivan", "Flanagan", "McLoughlin",
            "Kavanagh", "Hennessy",
        ],
    },
    "Southeast Asian": {
        "first": [
            "Malinee", "Budi", "Chanya", "Eko", "Suriya", "Dewi", "Arif", "Wati",
            "Prapat", "Siti", "Theerawat", "Nira", "Reza", "Mala", "Vihara",
            "Arun", "Nuttida", "Farid", "Chanida", "Dian", "Prapas", "Layla",
            "Agus", "Pimchanok", "Ratna",
        ],
        "last": [
            "Suriyawong", "Prasetyo", "Wahyudi", "Chaisombat", "Santoso",
            "Putra", "Wongso", "Limthongkul", "Hidayat",
            "Petcharat", "Kusumo", "Jirayu", "Setiawan", "Srisawat",
            "Nugroho", "Suphan", "Lertpanyarak",
        ],
    },
}


# ── Functions ─────────────────────────────────────────────────────────────────

def _draw_last(pool: dict) -> str:
    """Return a last name from a pool, handling patronymic pools (e.g. Icelandic)."""
    if "patronymic_bases" in pool:
        base   = random.choice(pool["patronymic_bases"])
        suffix = random.choice(["son", "dóttir"])
        return base + suffix
    return random.choice(pool["last"])


def roll_name_suggestion() -> str:
    """Pick a random cultural tradition and return a name drawn from it.

    Roughly 25 % of the time the first name and last name come from *different*
    traditions, modelling mixed-heritage characters (e.g. a Māori first name
    with a Norse/Scandinavian surname, or vice versa).  The returned JSON
    includes a ``note`` field explaining the blend so the model can write
    authentic backstory rather than treating it as an arbitrary pairing.
    """
    all_traditions = list(NAME_POOLS.keys())

    if random.random() < 0.25:
        # Cross-tradition blend
        t_first, t_last = random.sample(all_traditions, 2)
        first = random.choice(NAME_POOLS[t_first]["first"])
        last  = _draw_last(NAME_POOLS[t_last])
        return json.dumps({
            "suggested_name":  f"{first} {last}",
            "first":           first,
            "last":            last,
            "tradition":       f"{t_first} × {t_last}",
            "is_blend":        True,
            "first_tradition": t_first,
            "last_tradition":  t_last,
            "note": (
                f"First name from {t_first} heritage, surname from {t_last} heritage. "
                "Suggests mixed ancestry, adoption, marriage across cultures, or a family "
                "that deliberately chose to honour more than one heritage in the name."
            ),
        })

    # Single-tradition name
    tradition = random.choice(all_traditions)
    pool  = NAME_POOLS[tradition]
    first = random.choice(pool["first"])
    last  = _draw_last(pool)
    return json.dumps({
        "suggested_name": f"{first} {last}",
        "first":          first,
        "last":           last,
        "tradition":      tradition,
    })


# ── Tool schema ───────────────────────────────────────────────────────────────

NAME_TOOL_SCHEMA: dict = {
    "name": "roll_name_suggestion",
    "description": (
        "Get a name suggestion drawn from a randomly selected cultural tradition. "
        "Call this before naming any character, NPC, or contact to prevent cultural "
        "clustering across generated output. You may adapt the suggestion freely — "
        "change the first name, the last name, or blend traditions — but use it as "
        "a starting point rather than defaulting to familiar patterns."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


# ── D&D name pools by race ────────────────────────────────────────────────────
#
# Surnames for races that don't traditionally use them are invented here:
#
#   Dwarf      — compound descriptive epithets (Stronginthearm, Ironfoot…)
#   Halfling   — compound family names in the Tolkien/cosy-village tradition
#                (Strongfeet, Warmhearth, Goodbarrel…)
#   Elf        — house / family names in an elvish register
#   Tiefling   — compound words built from infernal imagery, carried with
#                defiance or wry pride (Ashveil, Emberscar, Voidmark…)
#   Half-Orc   — orcish clan names or earned epithets
#                (Gorehand, Blacktusk, Skullmend…)
#   Dragonborn — Draconic clan names (long and unpronounceable is correct)
#   Gnome      — clan names, a mix of PHB entries and whimsical coinages
#
# "Human" is NOT a key here — pass race="Human" to roll_dnd_name_suggestion()
# and it redirects to the real-world NAME_POOLS for full cultural diversity.

DND_POOLS: dict[str, dict[str, list[str]]] = {
    "Dwarf": {
        "first": [
            "Orin", "Baern", "Tordek", "Darrak", "Harbek", "Kildrak", "Rurik",
            "Ulfgar", "Vondal", "Thorin", "Flint", "Einkil", "Fargrim", "Eberk",
            "Brottor", "Artin", "Dagnal", "Eldeth", "Gunnloda", "Helja",
            "Kathra", "Riswynn", "Torbera", "Vistra", "Hlin",
        ],
        "last": [
            "Stronginthearm", "Ironfoot", "Goldvein", "Hammerfall", "Stoneback",
            "Deepdelver", "Brighteye", "Broadshoulders", "Heavybrow", "Rockfist",
            "Ironbeard", "Silverpick", "Gemheart", "Axebiter", "Boulderchest",
            "Oathkeeper", "Fireforge", "Flintbrow", "Steelgrip", "Coldforge",
        ],
    },
    "Halfling": {
        "first": [
            "Milo", "Cade", "Merric", "Corrin", "Roscoe", "Eldon", "Alton",
            "Wellby", "Lindal", "Finnan", "Posso", "Errich", "Redd", "Garret",
            "Lyle", "Callie", "Bree", "Kithri", "Lidda", "Portia",
            "Seraphina", "Nedda", "Lavinia", "Andry", "Cora",
        ],
        "last": [
            "Strongfeet", "Warmhearth", "Sweetriver", "Goodharvest", "Merryfoot",
            "Brightwater", "Barleycorn", "Rushybank", "Thorngage", "Tealeaf",
            "Goodbarrel", "Greenbottle", "Brushgather", "Hilltopple", "Tosscobble",
            "Underbough", "Cornwhisker", "Mossberry", "Bramblewick", "Quickthorn",
        ],
    },
    "Elf": {
        "first": [
            "Adrie", "Caelynn", "Enna", "Felosial", "Keyleth", "Lia", "Mialee",
            "Sariel", "Vadania", "Valanthe", "Silaqui", "Shava", "Naivara",
            "Quillathe", "Jelenneth", "Adran", "Aelar", "Berrian", "Erdan",
            "Galinndan", "Hadarai", "Peren", "Rolen", "Thamior", "Varis",
        ],
        "last": [
            "Amakiir", "Galanodel", "Naïlo", "Siannodel", "Moonwhisper",
            "Starweave", "Dawnsong", "Silverthorn", "Leafwhisper", "Mistwalker",
            "Dawnfire", "Evenwind", "Goldleaf", "Willowdawn", "Shimmerleaf",
        ],
    },
    # Tiefling first names: a mix of virtue names (carried defiantly or
    # aspirationally) and Infernal-sounding given names from the PHB.
    # Surnames: compound words from fire/shadow/ash/void imagery — not shame,
    # but a kind of dark poetry the lineage has made its own.
    "Tiefling": {
        "first": [
            "Hope", "Torment", "Patience", "Sorrow", "Honor", "Vengeance",
            "Serenity", "Grace", "Spite", "Mercy", "Damaia", "Kallista",
            "Makaria", "Lerissa", "Orianna", "Akta", "Bryseis", "Kairon",
            "Mordai", "Leucis", "Akmenos", "Melech", "Skamos", "Iados", "Therai",
        ],
        "last": [
            "Ashveil", "Emberscar", "Darkmantle", "Voidmark", "Cinderfall",
            "Coalmark", "Smokewreath", "Cinderveil", "Ironbrand", "Hearthless",
            "Ashmark", "Flamebrand", "Emberveil", "Shadowmark", "Voidborn",
            "Duskfall", "Cinderscar", "Ashborn", "Darkscar", "Nightveil",
        ],
    },
    "Dragonborn": {
        "first": [
            "Arjhan", "Balasar", "Bharash", "Donaar", "Ghesh", "Kriv", "Medrash",
            "Nadarr", "Rhogar", "Torinn", "Heskan", "Patrin", "Shedinn", "Mehen",
            "Pandjed", "Akra", "Biri", "Farideh", "Havilar", "Korinn",
            "Mishann", "Perra", "Raiann", "Sora", "Thava",
        ],
        "last": [
            "Clethtinthiallor", "Daardendrian", "Delmirev", "Drachedandion",
            "Kepeshkmolik", "Kerrhylon", "Kimbatuul", "Myastan", "Nemmonis",
            "Norixius", "Ophinshtalajiir", "Shestendeliath", "Turnuroth",
            "Verthisathurgiesh", "Yarjerit",
        ],
    },
    "Gnome": {
        "first": [
            "Dimble", "Erky", "Fonkin", "Gimble", "Namfoodle", "Orryn", "Seebo",
            "Warryn", "Zook", "Alvyn", "Burgell", "Glim", "Jebeddo", "Roondar",
            "Sindri", "Bimpnottin", "Breena", "Caramip", "Ellyjobell", "Lilli",
            "Loopmottin", "Nissa", "Tana", "Waywocket", "Zanna",
        ],
        "last": [
            "Beren", "Daergel", "Folkor", "Garrick", "Nackle", "Murnig",
            "Ningel", "Raulnor", "Scheppen", "Timbers", "Turen",
            "Fizzlewick", "Sparksworth", "Cogsworth", "Fiddlewick",
        ],
    },
    # Half-Orc surnames: orcish clan names or earned epithets.
    # Those raised among humans may instead carry a human cultural surname
    # (redirect via race="Human" in that case).
    "Half-Orc": {
        "first": [
            "Dench", "Feng", "Gell", "Henk", "Holg", "Krusk", "Mhurren",
            "Ront", "Shump", "Thokk", "Imsh", "Keth", "Baggi", "Emen",
            "Engong", "Kansif", "Myev", "Neega", "Nome", "Shautha",
            "Sutha", "Vola", "Volen", "Yevelda", "Paya",
        ],
        "last": [
            "Gorehand", "Blacktusk", "Bloodhowl", "Grimfang", "Ironhide",
            "Boneshield", "Greystone", "Duskhowl", "Stoneshard", "Coldspire",
            "Darkwater", "Flintback", "Bonebreaker", "Skullmend", "Grimfist",
            "Warborn", "Ashborn", "Coldblood", "Scarhand", "Steelback",
        ],
    },
}

_DND_RACES: list[str] = sorted(DND_POOLS.keys()) + ["Human"]


# ── D&D name function ─────────────────────────────────────────────────────────

def roll_dnd_name_suggestion(race: str = None) -> str:
    """Return a name suggestion for a D&D character of the given race.

    If race is omitted a race is chosen at random, with Human included so the
    full cultural NAME_POOLS get occasional use.  Passing race="Human" always
    redirects to NAME_POOLS (and may produce a cross-tradition blend).
    """
    if race is None:
        race = random.choice(_DND_RACES)

    if race == "Human":
        data = json.loads(roll_name_suggestion())
        data["race"] = "Human"
        return json.dumps(data)

    if race not in DND_POOLS:
        return json.dumps({
            "error": f"Unknown race {race!r}. Valid: {_DND_RACES}",
        })

    pool  = DND_POOLS[race]
    first = random.choice(pool["first"])
    last  = random.choice(pool["last"])
    return json.dumps({
        "suggested_name": f"{first} {last}",
        "first":          first,
        "last":           last,
        "race":           race,
    })


# ── D&D tool schema ───────────────────────────────────────────────────────────

DND_NAME_TOOL_SCHEMA: dict = {
    "name": "roll_dnd_name_suggestion",
    "description": (
        "Get a name suggestion for a D&D character. "
        "Pass the character's race for race-appropriate naming conventions — "
        "Dwarves get compound epithets (Stronginthearm, Ironfoot), Halflings get "
        "cosy compound family names (Strongfeet, Warmhearth), Tieflings get names "
        "that carry their infernal heritage with dark poetry, and so on. "
        "Omit race to pick randomly. Pass race='Human' to draw from real-world "
        "cultural traditions for maximum diversity. "
        "You may adapt the suggestion freely — it is a starting point, not a mandate."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "race": {
                "type": "string",
                "description": "Character race. Omit to pick randomly.",
                "enum": _DND_RACES,
            },
        },
        "required": [],
    },
}
