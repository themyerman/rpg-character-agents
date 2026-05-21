"""
Shared name pools for all RPG character generators.

Call roll_name_suggestion() before naming any character to prevent cultural
clustering across generated output. The model is free to adapt the suggestion —
changing first name, last name, or blending traditions — but it should use the
result as a starting point rather than defaulting to familiar patterns.
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

def roll_name_suggestion() -> str:
    """Pick a random cultural tradition and return a name drawn from it."""
    tradition = random.choice(list(NAME_POOLS.keys()))
    pool      = NAME_POOLS[tradition]
    first     = random.choice(pool["first"])
    last      = random.choice(pool["last"])
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
