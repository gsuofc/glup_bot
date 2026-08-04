from datetime import datetime
import json
import random
import secrets
import sys

import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

import nltk
from nltk.tokenize import word_tokenize

import fishing
import leveling

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

all_messages = None
try:
    with open('images/media_links.json', 'r') as file:
        all_messages = json.load(file)
except FileNotFoundError:
    print("Error: media_links.json not found.")
except json.JSONDecodeError:
    print("Error: media_links.json is not a valid JSON file.")

def log_to_server(message, channel_name='glup-logs'):
    guild = discord.utils.get(bot.guilds, name='globalpositioningsystem\'s server')
    if guild:
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            bot.loop.create_task(channel.send(message))

def is_bot_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        # Check if the user ID matches the bot application owner ID
        return await bot.is_owner(interaction.user)
    return app_commands.check(predicate)

def whenitis906():
    now = datetime.now()
    # 12 PM is hour 12 in 24-hour format, with 0 minutes
    return (now.hour == 9 or now.hour == 9+12) and now.minute == 6

def fishing_fridays():
    now = datetime.now()
    return now.astimezone().weekday() == 4 and now.hour >= 6 and now.hour <= 10

def big_catch_monday():
    now = datetime.now()
    return now.astimezone().weekday() == 0 and now.hour >= 6 and now.hour <= 10

@bot.event
async def on_ready():

    await fishing.init_db()
    await leveling.init_leveling_db()

    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    try:
        # Syncing registers your slash commands with Discord globally
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} application command(s).")
        log_to_server(f"Startup complete! Successfully synced {len(synced)} application command(s).", channel_name='glup-logs')
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    for resource in (
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
    ):
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('hello'):
        #await message.delete()
        await message.channel.send(f'Hello, {message.author.mention}!')

    # if this is a DM to the bot, send message to a specific channel in the server
    if isinstance(message.channel, discord.DMChannel):
        log_to_server(f'DM from {message.author}: {message.content}', channel_name='glup-responses')

    rng_roll = random.randint(1, 100)
    #log_to_server(f'Random roll: {rng_roll}', channel_name='glup-logs')
    if rng_roll > 95 and message.content.startswith('why'):
        await message.channel.send(f'because bread tastes better than key!!!!!!!!!!')

    await bot.process_commands(message)

@bot.tree.command(name="ping", description="Check the bot's response time")
async def ping(interaction: discord.Interaction):
    # Always use interaction.response.send_message for slash commands
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="time", description="Check the bot's time")
async def ping(interaction: discord.Interaction):
    # Always use interaction.response.send_message for slash commands
    await interaction.response.send_message(f"The time is {datetime.now()}")

@bot.tree.command(name="glup", description="Glup command")
async def glup(interaction: discord.Interaction):
    # Always use interaction.response.send_message for slash commands
    await interaction.response.send_message(f"Hello I am Glup bot!")

@bot.tree.command(name="tate", description="Promote a totally legit and not at all suspicious website")
async def tate(interaction: discord.Interaction):
    # Check if files exist before sending
    if not all(os.path.exists(f"images/t{i}.jpeg") for i in range(1, 5)):
        await interaction.response.send_message("Cannot use command. Server is missing required images.", ephemeral=True)
        return
    await interaction.response.defer()
    file1 = discord.File("images/t4.jpeg")
    file2 = discord.File("images/t3.jpeg")
    file3 = discord.File("images/t2.jpeg")
    file4 = discord.File("images/t1.jpeg")
    await interaction.followup.send(files=[file1, file2, file3, file4])

@bot.tree.command(name="neofetch", description="Get system information")
async def neofetch(interaction: discord.Interaction):
    # Run the neofetch command and capture its output
    import subprocess
    result = subprocess.run(['neofetch', '--stdout','--disable', 'title'], capture_output=True, text=True)
    output = result.stdout
    # Send as embed to avoid message length issues
    embed = discord.Embed(title="System Information", description=f"```\n{output}\n```", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="random_image", description="Get a random image from over 4000+ images")
async def random_image(interaction: discord.Interaction):
    global all_messages
    if not all_messages:
        await interaction.response.send_message("No messages available.", ephemeral=True)
        return

    #reroll if a video is selected, since videos are not supported in embeds
    while True:
        message = random.choice(all_messages)
        url = message["url"]

        # Accept only images
        if not url.lower().endswith((".mp4", ".webm", ".mov")):
            break
    
    embed = discord.Embed(
        title="Image from Random",
        description=f"Image by {message['author']}\n Link: {message['post']}",
        color=0x00ff00
    )
    url = message["url"]

    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed)


@bot.command()
async def assign(ctx):
    # Check if the role exists in the guild
    role = discord.utils.get(ctx.guild.roles, name='test')
    if role:
        member = ctx.author
        await member.add_roles(role)
        await ctx.send(f'Assigned {role.name} to {member.mention}')


@bot.command()
async def remove(ctx):
    # Check if the role exists in the guild
    role = discord.utils.get(ctx.guild.roles, name='test')
    if role:
        member = ctx.author
        await member.remove_roles(role)
        await ctx.send(f'Removed {role.name} from {member.mention}')

@bot.command()
async def dm(ctx, member: discord.Member, *, message):
    # check to see if dm disabled role is assigned
    dm_disabled_role = discord.utils.get(ctx.guild.roles, name='DM Disabled')
    if dm_disabled_role in member.roles:
        await ctx.send(f'User has DMs disabled.')
        return
    #check to see if the bot can send a DM to the user
    try:
        await member.send(message)
        await ctx.send(f'Sent a DM to {member.name}')
    except discord.Forbidden:
        await ctx.send(f'Could not send a DM to {member.name}. They may have DMs disabled.')

@bot.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send("Shutting down...")
    await bot.close()
    sys.exit(0)

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

@bot.tree.context_menu(name="Duskullify")
async def duskullify(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer()

    # Inline function - because we dont really need this elsewhere
    def replace_nouns_nltk(text, replacement_word="[NOUN]"):
        tokens = word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        
        result = []
        for word, tag in tagged:
            # NLTK noun tags start with 'NN' (NN, NNS, NNP, NNPS)
            if tag.startswith('NN'):
                result.append(replacement_word)
            else:
                result.append(word)
                
        return " ".join(result)

    if not message.content.strip():
        await interaction.followup.send(
            "That message doesn't contain any text. (Make sure it isn't an embed`)",
            ephemeral=True,
        )
        return

    
    await interaction.followup.send(
        replace_nouns_nltk(message.content, "Duskull"), 
        ephemeral=True
    )

@bot.hybrid_command(name="elevate", description="Elevate your erudition!")
async def elevate(ctx):
    # First, check to see if the user has a profile, if not create one
    user_profile = await fishing.get_user_profile(ctx.author.id)
    if not user_profile:
        await fishing.create_user_profile(ctx.author.id)
        user_profile = await fishing.get_user_profile(ctx.author.id)

    # Now, get or create the user leveling profile
    user_level = await leveling.get_or_create_user_level(user_profile["user_id"])
    user_experience = user_level["experience"]
    user_level = leveling.calculate_level(user_experience)


    exp_roll = (secrets.SystemRandom().random()*user_level*10)+1
    new_experience = user_experience + int(exp_roll)

    new_level = leveling.calculate_level(new_experience)

    level_progression_message = "Max Level Achieved!\n"
    this_level_exp = leveling.calculate_experience_for_level(user_level)
    if user_level < 99:  # Assuming 99 is the max level
        next_level_exp = leveling.calculate_experience_for_level(user_level + 1)
        user_level_difference = new_experience - this_level_exp
        next_level_difference = next_level_exp - this_level_exp
        level_progression_message = f"Level Progress: {user_level_difference}/{next_level_difference}\n"

    if new_level > user_level:
        level_progression_message = f"Level up! You are now level {new_level}!"

    await leveling.update_user_experience(user_profile["user_id"], new_experience)
    embed = discord.Embed(
        title="Erudition Elevated!",
        description=f"You gained {int(exp_roll)} erudition points!\n{level_progression_message}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name="erudition", description="Check your erudition!")
async def erudition(ctx):
    # First, check to see if the user has a profile, if not create one
    user_profile = await fishing.get_user_profile(ctx.author.id)
    if not user_profile:
        await fishing.create_user_profile(ctx.author.id)
        user_profile = await fishing.get_user_profile(ctx.author.id)

    # Now, get or create the user leveling profile
    user_level = await leveling.get_or_create_user_level(user_profile["user_id"])
    user_experience = user_level["experience"]
    user_level = leveling.calculate_level(user_experience)

    this_level_exp = leveling.calculate_experience_for_level(user_level)
    next_level_exp = leveling.calculate_experience_for_level(user_level + 1) if user_level < 99 else None

    level_progression_message = "Max Level Achieved!\n"
    if next_level_exp is not None:
        user_level_difference = user_experience - this_level_exp
        next_level_difference = next_level_exp - this_level_exp
        level_progression_message = f"Level Progress: {user_level_difference}/{next_level_difference}\n"

    embed = discord.Embed(
        title="Erudition Profile",
        description=f"Level: {user_level} ({user_experience} total erudition)\n{level_progression_message}",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def set_erudition(ctx, member: discord.Member, amount: int):
    # First, check to see if the user has a profile, if not create one
    user_profile = await fishing.get_user_profile(member.id)
    if not user_profile:
        await fishing.create_user_profile(member.id)
        user_profile = await fishing.get_user_profile(member.id)

    # Now, get or create the user leveling profile
    user_level = await leveling.get_or_create_user_level(user_profile["user_id"])
    
    # Update the user's experience to the specified amount
    await leveling.update_user_experience(user_profile["user_id"], amount)
    
    # Calculate the new level based on the updated experience
    new_level = leveling.calculate_level(amount)

    await ctx.send(f"Set {member.mention}'s erudition to {amount}. New level is {new_level}.")

"""
Fishing Minigame Commands
"""

@bot.command()
@commands.is_owner()
async def get_all_fishes(ctx):
    #get fishes + ids for debugging
    fishes = await fishing.get_all_fishes()
    message = ""
    for fish in fishes:
        message += f"ID: {fish[0]}, Name: {fish[1]}\n"
        islands = await fishing.get_island_with_fish(fish[0]) 
        for island_id in islands:
            island = await fishing.get_island_by_id(island_id)
            message += f"Island ID: {island[0]}, Name: {island[1]}\n"
    await ctx.send(f"Available fishes:\n{message}")

@bot.command()
@commands.is_owner()
async def add_island(ctx, *, island_name):
    await fishing.create_island(island_name)
    await ctx.send(f"Island '{island_name}' added to the database.")


@bot.command()
@commands.is_owner()
async def fish_sql(ctx, *, sql):
    result = await fishing.execute_sql(sql)
    if result is None:
        await ctx.send("No results.")
        return

    text = str(result)
    if len(text) > 1900:
        await ctx.send(f"```{text[:1900]}```")
    else:
        await ctx.send(f"```{text}```")

@bot.command()
@commands.is_owner()
async def get_all_islands(ctx):
    islands = await fishing.get_all_islands()
    message = ""
    for island in islands:
        message += f"ID: {island[0]}, Name: {island[1]}\n"
        fishes = await fishing.get_fish_with_island(island[0])
        for fish_id in fishes:
            fish = await fishing.get_fish_by_id(fish_id)
            message += f"Fish: {fish[1]}\n"
    await ctx.send(f"Available islands:\n{message}")

@bot.tree.command(name="add_fish_to_island", description="(ADMIN ONLY) Adds a new fish to an island")
@app_commands.describe(fish_name="Name of the fish to add", island_name="Name of the island to add the fish to")
@is_bot_owner()
async def add_fish_to_island(interaction: discord.Interaction, fish_name: str, island_name: str):
    await interaction.response.defer()

    # Get the fish by name
    fishes = await fishing.get_all_fishes()
    fish = next((f for f in fishes if f[1].lower() == fish_name.lower()), None)
    if not fish:
        await interaction.followup.send(f"Fish '{fish_name}' not found.", ephemeral=True)
        return

    # Get the island by name
    islands = await fishing.get_all_islands()
    island = next((i for i in islands if i[1].lower() == island_name.lower()), None)
    if not island:
        await interaction.followup.send(f"Island '{island_name}' not found.", ephemeral=True)
        return

    # Associate the fish with the island
    try:
        await fishing.associate_fish_with_island(fish[0], island[0])
        await interaction.followup.send(f"Successfully associated fish '{fish_name}' with island '{island_name}'.")
    except Exception as e:
        await interaction.followup.send(f"Error occurred while associating fish with island: {e}", ephemeral=True)

@bot.tree.command(name="add_fish", description="(ADMIN ONLY) Adds a new fish, usng an emote")
@app_commands.describe(emoji_string="Type or paste the custom emoji here", fish_name="Name of the fish", rarity="Rarity of the fish", ave_size="Average size of the fish")
@is_bot_owner()
async def add_fish(interaction: discord.Interaction, emoji_string: str, fish_name: str, rarity: str, ave_size: float):
    await interaction.response.defer()

    try:
        emoji = discord.PartialEmoji.from_str(emoji_string)
    except ValueError:
        await interaction.followup.send("Invalid emoji format. Please provide a valid custom emoji.", ephemeral=True)
        return

    # Check if the parsed emoji is an actual custom Discord emoji
    if not emoji.id:
        await interaction.followup.send("That is a standard Unicode emoji. I can only download custom emojis!", ephemeral=True)
        return

    extension = "gif" if emoji.animated else "png"
    file_name = f"fishing_data/images/{emoji.name}.{extension}"

    # Asynchronously download the image data
    async with aiohttp.ClientSession() as session:
        async with session.get(emoji.url) as response:
            if response.status == 200:
                image_data = await response.read()
                
                # Save locally
                with open(file_name, "wb") as f:
                    f.write(image_data)
                
                # Send confirmation message
                try: 
                    await fishing.create_fish(fish_name, rarity, ave_size, file_name)
                    await interaction.followup.send(f"Successfully downloaded {emoji.name} as `{file_name}`!")
                except Exception as e:
                    await interaction.followup.send(f"Error occurred while creating fish: {e}")
            else:
                await interaction.followup.send("Failed to download the emoji image from Discord.")


@bot.tree.command(name="fish", description="Fish for Discord Emotes!")
async def fish(interaction: discord.Interaction):
    await interaction.response.defer()

    # First, check to see if the user has a profile, if not create one
    user_profile = await fishing.get_user_profile(interaction.user.id)
    if not user_profile:
        await fishing.create_user_profile(interaction.user.id)
        user_profile = await fishing.get_user_profile(interaction.user.id)

    db_id = user_profile["user_id"]
    user_catches = user_profile["total_fish"]
    #await interaction.followup.send(f"Loaded user profile for you! {db_id} {user_id} You can now fish!")

    # Get what island the user is fishing on
    user_last_island = user_profile["last_island"]
    island = await fishing.get_island_by_id(user_last_island)
    if not island:
        await interaction.followup.send(f"You are in a bugged state! {user_last_island} is not an island")
        return

    # We are now at an island! Get all fish at the island and construct a table of odds based on weights
    fishes_for_island = await fishing.get_fish_with_island(island[0])
    fish_odds_table = fishing.fish_roller()
    for fish_id in fishes_for_island:
        fish = await fishing.get_fish_by_id(fish_id)
        fish_odds_table.add_fish(fish,fish["rarity"])

    fish_roll = secrets.SystemRandom().random()

    big_fish_boost = 1
    if big_catch_monday():
        big_fish_boost = 2

    lowest_odds = 1
    fish_rolled = None
    for i in range(0, big_fish_boost):
        (fish_candidate,odds) = fish_odds_table.get_fish_using_roll(fish_roll)
        if odds < lowest_odds:
            lowest_odds = odds
            fish_rolled = fish_candidate

    fish_id = fish_rolled["fish_id"]

    # We have a fish, now we roll for rarity
    boost = 1
    if whenitis906():
        boost = 6
    if fishing_fridays():
        boost*= 2

    rarity_roll = fishing.roll_rarity(boost)

    # If the user has a multiple of 5000 catches, give them a free A+ catch
    if user_catches>0 and (user_catches+1)%5000==0:
        rarity_roll = 0.995 + (0.005 * secrets.SystemRandom().random())

    (rank, hue) = fishing.convert_roll_to_rank_and_hue(rarity_roll)
    size = fishing.convert_roll_to_weight(rarity_roll,fish_rolled["ave_size"])

    # Now update the fish stats
    fishes_caught_by_user = await fishing.get_user_fish_with_fish_id(db_id, fish_id)
    if not fishes_caught_by_user:
        await fishing.first_catch(db_id, fish_id)
        fishes_caught_by_user = await fishing.get_user_fish_with_fish_id(db_id, fish_id)

    last_biggest_weight = fishes_caught_by_user["largest_roll"]
    last_quantity = fishes_caught_by_user["quantity"]

    biggest_size_message = f"First Catch!"

    if last_biggest_weight>0:
        last_biggest_rank = fishing.convert_roll_to_rank(last_biggest_weight)
        last_biggest_size = fishing.convert_roll_to_weight(last_biggest_weight,fish_rolled["ave_size"])
        biggest_size_message = f"Biggest Catch: {last_biggest_size:.3f} ({last_biggest_rank})"

    if whenitis906():
        biggest_size_message+="\nWhen it is 9:06: :POG:"
    if fishing_fridays():
        biggest_size_message+="\nFishing Fridays: 2x Size Boost!"
    if big_catch_monday():
        biggest_size_message+="\nBig Catch Monday: 2x Fish Boost!"

    new_quantity = last_quantity + 1
    new_biggest_weight = last_biggest_weight
    if rarity_roll > last_biggest_weight:
        new_biggest_weight = rarity_roll
        biggest_size_message = "New Largest Catch!"

    await fishing.update_user_fish(db_id, fish_id,new_biggest_weight,new_quantity)

    # Also update catches on profile
    
    await fishing.user_update_catches(db_id,user_catches+1)

    # Send embed with fish catch

    file_name = fish_rolled["emote_file"]
    file = discord.File(file_name, filename="image.png")
    embed = discord.Embed(
        title="Caught Fish",
        description=f"Fished {fish_rolled["fish_name"]}!\nSize: {size:.3f}\nRank: {rank}\n{biggest_size_message}",
        color=fishing.get_discord_embed_color(hue,0,1)
    )
    
    embed.set_image(url="attachment://image.png")
    await interaction.followup.send(file=file, embed=embed)

@bot.tree.command(name="change_island", description="Change what island you are fishing at")
@app_commands.describe(island_name="Name of the island to fish at")
async def fish(interaction: discord.Interaction,  island_name: str):
    # First, check to see if the user has a profile
    user_profile = await fishing.get_user_profile(interaction.user.id)
    if not user_profile:
        await interaction.response.send_message(f"Please run /fish first, to create a user profile")
        return

    # Get the island from the name
    island_choice = await fishing.get_island_by_name(island_name)
    if not island_choice:
        islands = await fishing.get_all_islands()
        message = ""
        for island in islands:
            island_name = island["name"]
            required_b_catches = island["required_b_catches"]
            required_a_catches = island["required_a_catches"]
            unlisted = island["unlisted"]
            if unlisted==0:
                message += f"{island_name} "
                if required_b_catches>0 or required_a_catches>0:
                    message+=f"(Requirements: {required_b_catches}xB, {required_a_catches}xA)"
                message += "\n"

        await interaction.response.send_message(f"Island does not exist! Valid choices:\n{message}")
        return

    # Determine if you have caught enough B and A ranks
    user_b_catches = 0
    user_a_catches = 0

    fish_caught_by_user = await fishing.get_user_fish(user_profile["user_id"])
    for fish_stat in fish_caught_by_user:
        largest_roll = fish_stat["largest_roll"]
        largest_rank = fishing.convert_roll_to_rank(largest_roll)

        if "B" in largest_rank.capitalize():
            user_b_catches+=1
        elif "A" in largest_rank.capitalize():
            user_a_catches+=1
            user_b_catches+=1

    required_b_catches = island_choice["required_b_catches"]
    required_a_catches = island_choice["required_a_catches"]

    if user_b_catches<required_b_catches or user_a_catches<required_a_catches:
        await interaction.response.send_message(f"You do not meet the requirements to fish at this island!\nB or better catches: {user_b_catches}/{required_b_catches}\nA or better catches: {user_a_catches}/{required_a_catches}\n")
    
    await fishing.user_visit_island(user_profile["user_discord_id"],island_choice["island_id"])
    await interaction.response.send_message(f"Changed to {island_choice["name"]}")


@bot.tree.command(name="fish_profile", description="See what fish you caught")
async def fish_profile(interaction: discord.Interaction):
    user_profile = await fishing.get_user_profile(interaction.user.id)
    if not user_profile:
        await interaction.followup.send(f"Please run /fish first, to create a user profile")
        return

    fish_caught_by_user = await fishing.get_user_fish(user_profile["user_id"])
    user_catches = user_profile["total_fish"]
    message = f"Total Fish Caught: {user_catches}\n"
    for fish_stat in fish_caught_by_user:
        fish = await fishing.get_fish_by_id(fish_stat["fish_id"])
        catches = fish_stat["quantity"]
        largest_roll = fish_stat["largest_roll"]
        largest_size = fishing.convert_roll_to_weight(largest_roll,fish["ave_size"])
        largest_rank = fishing.convert_roll_to_rank(largest_roll)
        message+=f"{fish["fish_name"]} | Catches: {catches} | Largest: {largest_size:.3f} ({largest_rank})\n"


    embed = discord.Embed(
        title=f"Fishing Profile for {interaction.user.name}",
        description=message,
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="fish_leaderboards", description="See who caught the biggest fishes")
async def fish_leaderboards(interaction: discord.Interaction):
    await interaction.response.defer()
    records = await fishing.get_fish_records()

    per_fish_rank_message = ""

    for record in records:
        largest_roll = record["largest_roll"]
        largest_size = 0
        if fish:
            largest_size = fishing.convert_roll_to_weight(largest_roll,record["ave_size"])
        largest_rank = fishing.convert_roll_to_rank(largest_roll)
        per_fish_rank_message += f"{record["fish_name"]}: <@{record['user_discord_id']}> — {largest_size:.3f} ({largest_rank})\n"

    embed = discord.Embed(
        title="Fish Leaderboards",
        description=per_fish_rank_message,
        color=discord.Color.blue()
    )

    """)
    embed.add_field(
        name="Best Catches","""

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="fake_fish", description="Simulates a fish without actually counting it")
@app_commands.describe(island_id="Island ID number", fish_roll="Roll for fish", rarity_roll="Rarity roll for fish")
async def add_fish(interaction: discord.Interaction, island_id: int, fish_roll: float, rarity_roll: float):
    await interaction.response.defer()
    island = await fishing.get_island_by_id(island_id)
    if not island:
        await interaction.followup.send(f"Invalid Island! {island_id} is not an island")
        return

    # We are now at an island! Get all fish at the island and construct a table of odds based on weights
    fishes_for_island = await fishing.get_fish_with_island(island[0])
    fish_odds_table = fishing.fish_roller()
    for fish_id in fishes_for_island:
        fish = await fishing.get_fish_by_id(fish_id)
        fish_odds_table.add_fish(fish,fish["rarity"])

    (fish_rolled,odds) = fish_odds_table.get_fish_using_roll(fish_roll)
    fish_id = fish_rolled["fish_id"]

    # Fish and rarity rolls are done as args

    (rank, hue) = fishing.convert_roll_to_rank_and_hue(rarity_roll)
    size = fishing.convert_roll_to_weight(rarity_roll,fish_rolled["ave_size"])

    file_name = fish_rolled["emote_file"]
    file = discord.File(file_name, filename="image.png")
    embed = discord.Embed(
        title="Simulated Fish",
        description=f"Simulation rolled {fish_rolled["fish_name"]}!\nSize: {size:.3f}\nRank: {rank}\nNote: This will not be counted as to your profile",
        color=fishing.get_discord_embed_color(hue,0,1)
    )
    
    embed.set_image(url="attachment://image.png")
    await interaction.followup.send(file=file, embed=embed)





bot.run(token, log_handler=handler, log_level=logging.DEBUG)
