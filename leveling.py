import math

import aiosqlite
from fishing import DB_FILE

# We will be using the same database file as fishing.py, so we import DB_FILE from there.

level_progresion = {
    1: 0,
    2: 83,
    3: 174,
    4: 276,
    5: 388,
    6: 512,
    7: 650,
    8: 801,
    9: 969,
    10: 1154,
    11: 1358,
    12: 1584,
    13: 1833,
    14: 2107,
    15: 2411,
    16: 2746,
    17: 3115,
    18: 3523,
    19: 3973,
    20: 4470,
    21: 5018,
    22: 5624,
    23: 6291,
    24: 7028,
    25: 7842,
    26: 8740,
    27: 9730,
    28: 10824,
    29: 12031,
    30: 13363,
    31: 14833,
    32: 16456,
    33: 18247,
    34: 20224,
    35: 22406,
    36: 24815,
    37: 27473,
    38: 30408,
    39: 33648,
    40: 37224,
    41: 41171,
    42: 45529,
    43: 50339,
    44: 55649,
    45: 61512,
    46: 67983,
    47: 75127,
    48: 83014,
    49: 91721,
    50: 101333, 
    51: 111945,
    52: 123660,
    53: 136594,
    54: 150872,
    55: 166636,
    56: 184040,
    57: 203254,
    58: 224466,
    59: 247886,
    60: 273742,
    61: 302288,
    62: 333804,
    63: 368599,
    64: 407015,
    65: 449428,
    66: 496254,
    67: 547953,
    68: 605032,
    69: 668051,
    70: 737627,
    71: 814445,
    72: 899257,
    73: 992895,
    74: 1096278,
    75: 1210421,
    76: 1336443,
    77: 1475581,
    78: 1629200,
    79: 1798808,
    80: 1986068,
    81: 2192818,
    82: 2421087,
    83: 2673114,
    84: 2951373,
    85: 3258594,
    86: 3597792,
    87: 3972294,
    88: 4385776,
    89: 4842295,
    90: 5346332,
    91: 5902831,
    92: 6517253,
    93: 7195629,
    94: 7944614,
    95: 8771558,
    96: 9684577,
    97: 10692629,
    98: 11805606,
    99: 13034431
}

async def init_leveling_db():
    try:
        with open("leveling_db.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()
            
        async with aiosqlite.connect(DB_FILE) as db:
            await db.executescript(sql_script)
            await db.commit()
        print("Database schema successfully synchronized from schema.sql.")
    except FileNotFoundError:
        print("Error: schema.sql file not found. Database was not initialized.")
    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")

async def get_or_create_user_level(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM user_levels WHERE user_id = ?", (user_id,))
        user_level = await cursor.fetchone()
        
        if user_level is None:
            # User does not exist, create a new entry
            await db.execute("INSERT INTO user_levels (user_id, experience) VALUES (?, ?)", (user_id, 0))
            await db.commit()
            return {"user_id": user_id, "experience": 0}
        
        return dict(user_level)

async def update_user_experience(user_id, experience):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE user_levels SET experience = ? WHERE user_id = ?", (experience, user_id))
        await db.commit()

def calculate_level(experience):
    level = 1
    for lvl, exp in sorted(level_progresion.items()):
        if experience >= exp:
            level = lvl
        else:
            break
    return level


def calculate_experience_for_level(current_level):
    return level_progresion[current_level]

def calculate_experience_for_level_new(current_level):
    if current_level < 2:
        return 0
    summation = 0
    for lvl in range(1, current_level + 1):
        value = int(lvl + 300 * (2 ** (lvl / 7)))
        summation += math.floor(value)
    return int(math.floor(summation / 4))
