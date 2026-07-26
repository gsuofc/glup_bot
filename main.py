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

import fishing

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

@bot.event
async def on_ready():

    await fishing.init_db()

    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    try:
        # Syncing registers your slash commands with Discord globally
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} application command(s).")
        log_to_server(f"Startup complete! Successfully synced {len(synced)} application command(s).", channel_name='glup-logs')
    except Exception as e:
        print(f"Failed to sync commands: {e}")

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
    result = subprocess.run(['neofetch', '--stdout'], capture_output=True, text=True)
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

    fish_roll = random.random()

    (fish_rolled,odds) = fish_odds_table.get_fish_using_roll(fish_roll)
    fish_id = fish_rolled["fish_id"]

    # We have a fish, now we roll for rarity
    #rarity_roll = random.random()
    rarity_roll = secrets.SystemRandom().random() # Using better random because random.random() feels like it is too generous
    rank = fishing.convert_roll_to_rank(rarity_roll)
    size = fishing.convert_roll_to_weight(rarity_roll,fish_rolled["ave_size"])

    # Now update the fish stats
    fishes_caught_by_user = await fishing.get_user_fish_with_fish_id(db_id, fish_id)
    if not fishes_caught_by_user:
        await fishing.first_catch(db_id, fish_id)
        fishes_caught_by_user = await fishing.get_user_fish_with_fish_id(db_id, fish_id)

    last_biggest_weight = fishes_caught_by_user["largest_roll"]
    last_quantity = fishes_caught_by_user["quantity"]

    new_quantity = last_quantity + 1
    new_biggest_weight = last_biggest_weight
    if rarity_roll > last_biggest_weight:
        new_biggest_weight = rarity_roll

    await fishing.update_user_fish(db_id, fish_id,new_biggest_weight,new_quantity)

    # Also update catches on profile
    
    await fishing.user_update_catches(db_id,user_catches+1)

    # Send embed with fish catch

    file_name = fish_rolled["emote_file"]
    file = discord.File(file_name, filename="image.png")
    embed = discord.Embed(
        title="Caught Fish",
        description=f"Fished {fish_rolled["fish_name"]}!\nSize: {size:.3f}\nRank: {rank}",
        color=discord.Color.red()
    )
    
    # 3. Reference the attached file matching the filename exactly
    embed.set_image(url="attachment://image.png")
    
    # 4. You MUST send BOTH the file and the embed together
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
            message += f"- {island[1]}\n"

        await interaction.response.send_message(f"Island does not exist! Valid choices:\n{message}")
        return
    else: 
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
    


bot.run(token, log_handler=handler, log_level=logging.DEBUG)