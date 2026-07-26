import os
import random

import aiosqlite
import discord
from discord.ext import commands
from statistics import NormalDist


DB_FILE = "fishing_data/bot_database.db"

async def init_db():
    try:
        os.makedirs("fishing_data/images", exist_ok=True)

        with open("fishing_db.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()
            
        async with aiosqlite.connect(DB_FILE) as db:
            await db.executescript(sql_script)
            await db.commit()
        print("Database schema successfully synchronized from schema.sql.")
    except FileNotFoundError:
        print("Error: schema.sql file not found. Database was not initialized.")
    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")

async def create_island(name):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO islands (name) VALUES (?)", (name,))
        await db.commit()

async def create_fish(fish_name, rarity, ave_size, emote_file):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO fishes (fish_name, rarity, ave_size, emote_file) VALUES (?, ?, ?, ?)", (fish_name, rarity, ave_size, emote_file))
        await db.commit()

async def associate_fish_with_island(fish_id, island_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO fish_islands (fish_id, island_id) VALUES (?, ?)", (fish_id, island_id))
        await db.commit()

async def get_island_with_fish(fish_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT island_id FROM fish_islands WHERE fish_id = ?", (fish_id,))
        island_ids = await cursor.fetchall()
        return [island_id[0] for island_id in island_ids]

async def get_fish_with_island(island_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT fish_id FROM fish_islands WHERE island_id = ?", (island_id,))
        fish_ids = await cursor.fetchall()
        return [fish_id[0] for fish_id in fish_ids]

async def get_all_fishes():
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM fishes")
        fishes = await cursor.fetchall()
        return fishes

async def get_fish_by_id(fish_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM fishes WHERE fish_id = ?", (fish_id,))
        fish = await cursor.fetchone()
        return fish

async def get_island_by_id(island_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM islands WHERE island_id = ?", (island_id,))
        island = await cursor.fetchone()
        return island

async def get_all_islands():
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM islands")
        islands = await cursor.fetchall()
        return islands

async def get_fish_by_name(fish_name):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM fishes WHERE fish_name = ?", (fish_name,))
        fish = await cursor.fetchone()
        return fish

async def get_island_by_name(island_name):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM islands WHERE name = ?", (island_name,))
        island = await cursor.fetchone()
        return island

async def get_user_profile(discord_user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM user_profiles WHERE user_discord_id = ?", (discord_user_id,))
        user = await cursor.fetchone()
        return user

async def create_user_profile(discord_user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO user_profiles (user_discord_id) VALUES (?)", (discord_user_id,))
        await db.commit()

async def user_visit_island(discord_user_id,island_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE user_profiles SET last_island = ? WHERE user_discord_id = ?", (island_id,discord_user_id))
        await db.commit()

async def get_user_fish(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM user_fish WHERE user_id = ?", (user_id,))
        fishes = await cursor.fetchall()
        return fishes

async def get_user_fish_with_fish_id(user_id,fish_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM user_fish WHERE user_id = ? AND fish_id = ?", (user_id,fish_id))
        fish = await cursor.fetchone()
        return fish

async def first_catch(user_id,fish_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("INSERT INTO user_fish (user_id, fish_id) VALUES (?, ?)", (user_id, fish_id))
            await db.commit()


async def update_user_fish(user_id, fish_id, roll, catches):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            """
            UPDATE user_fish
            SET quantity = ?, largest_roll = ?
            WHERE user_id = ? AND fish_id = ?
            """,
            (catches, roll, user_id, fish_id)
        )

        await db.commit()


async def user_update_catches(discord_user_id,fishes_caught):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE user_profiles SET total_fish = ? WHERE user_id = ?", (fishes_caught,discord_user_id))
        await db.commit()


class fish_roller:
    def __init__(self):
        self.all_fishes = []
        self.total_weight = 0

    def add_fish(self,obj,weight):
        dict = {
            "fish": obj,
            "this_weight": weight,
            "weight_before": self.total_weight
        }
        self.all_fishes.append(dict)
        self.total_weight+=weight

    def get_fish_using_roll(self,roll):
        fish_to_pick = roll*self.total_weight
        for fish in self.all_fishes:
            roll_weight = fish["weight_before"]+fish["this_weight"]
            if roll_weight>fish_to_pick:
                odds_of_this_roll = fish["this_weight"]/self.total_weight
                return (fish["fish"],odds_of_this_roll)

        print("Something happened, we shouldnt be here")



# Non DB Helper functions
def convert_roll_to_rank(roll):
    if roll < 0.40:
        return "D"
    elif roll < 0.70:
        return "C"
    elif roll < 0.97:
        return "B"
    elif roll < 0.99:
        return "A"
    else:
        return "A+"

def convert_roll_to_weight(roll,average_weight):
    sigma = average_weight * 0.25
    normal = NormalDist()
    z = normal.inv_cdf(roll)
    return average_weight + z * sigma